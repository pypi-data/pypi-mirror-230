"""
The FEE Simulator application. This app provides basic FEE functionality and is used mainly to
test the DPU Processor. The communication between the FEE Simulator and the DPU Processor is
abstracted by a SpaceWireInterface which currently has two implementations:

    1. a SpaceWireOverDSI, i.e. the 4Links Diagnostic SpaceWire Interface (DSI) or the
       EtherSpaceLink (ESL) device running over SpaceWire and TCP/IP, or
    2. a SpaceWireOverZeroMQ, i.e. all communication runs over ZeroMQ.

The FEE Simulator can be started as follows:

    $ feesim start --dsi-address <IP address of the DSI> --dsi-port <the SpW port on the DSI>
    $ feesim start --zeromq

The FEE Simulator can also be started to run over an ssh tunnel:

    $ feesim start --tunnel -ssh-user <name>

When connecting over a tunnel, the SSH passphrase is requested.
"""
import getpass
import logging
import multiprocessing
import random

import click
import numpy as np

from egse.hk import TmDictionaryColumns
from egse.randomwalk import RandomWalk
from egse.setup import SetupError
from egse.state import GlobalState
from egse.system import SignalCatcher

multiprocessing.current_process().name = "feesim"

import sys
import time
from typing import NamedTuple, List

import sshtunnel

from egse.dsi.spw import SpaceWireOverDSI
from egse.fee import n_fee_mode
from egse.fee import convert_ccd_order_value
from egse.fee.fee import create_pattern_data
from egse.fee.fee import generate_data_packets
from egse.fee.nfee import HousekeepingData
from egse.reg import RegisterMap
from egse.settings import Settings
from egse.spw import DataPacketHeader
from egse.spw import DataPacketType
from egse.spw import PacketType
from egse.spw import ReadRequest
from egse.spw import SpaceWireInterface
from egse.spw import SpaceWirePacket
from egse.spw import WriteRequest
from egse.spw import create_rmap_read_request_reply_packet
from egse.spw import create_rmap_write_request_reply_packet
from egse.zmq.spw import SpaceWireOverZeroMQ
from egse.fee.n_fee_hk import ORIGIN

logging.basicConfig(level=logging.DEBUG, format=Settings.LOG_FORMAT_FULL)

LOGGER = logging.getLogger("egse.fee.feesim")

fee_settings = Settings.load("FEE")
dsi_settings = Settings.load("DSI")
site_settings = Settings.load("SITE")
dpu_settings = Settings.load("DPU Processor")


# Define the possible states


class States(NamedTuple):
    ST_OFF: int
    ST_ON: int
    ST_FULL_IMAGE_PATTERN: int
    ST_WINDOWING_PATTERN: int
    ST_STANDBY: int
    ST_FULL_IMAGE: int
    ST_WINDOWING: int
    ST_PERFORMANCE_TEST: int
    ST_PARALLEL_TRAP_PUMPING_1: int
    ST_PARALLEL_TRAP_PUMPING_2: int
    ST_SERIAL_TRAP_PUMPING_1: int
    ST_SERIAL_TRAP_PUMPING_2: int


states = States(
    ST_OFF=-1,
    ST_ON=0,
    ST_FULL_IMAGE_PATTERN=1,
    ST_WINDOWING_PATTERN=2,
    ST_STANDBY=4,
    ST_FULL_IMAGE=5,
    ST_WINDOWING=6,
    ST_PERFORMANCE_TEST=7,
    ST_PARALLEL_TRAP_PUMPING_1=9,
    ST_PARALLEL_TRAP_PUMPING_2=10,
    ST_SERIAL_TRAP_PUMPING_1=11,
    ST_SERIAL_TRAP_PUMPING_2=12,
)

# Set the initial state

current_state: int = states.ST_OFF


# Define the transitions


def goto_on_mode(state):
    # N-FEE in ON-mode
    # * Power of the CCDs is disabled
    # * Power of subsystems is disabled
    # * N-FEE is ready for receiving RMAP command
    return states.ST_ON


def goto_standby_mode(state):
    # N-FEE in STANDBY-mode
    # * CCDs and subsystems are powered
    # * CCD timing signals are disabled
    # * no image data shall be transferred
    return states.ST_STANDBY


def goto_windowing_mode(state):
    # N-FEE in WINDOWING-mode
    # * The full CCDs are readout
    # * Only regions of interest (windows) are transmitted
    # * Configuration:
    #   * This configuration needs to be set via RMAP before changing from STANDBY to WINDOWING mode
    #   * Set first and last row to read-out
    #   * Set serial transfers size (column size)
    #   * Set number of overscan lines.
    #   * Enable or disable charge injection
    #   * Set first and last line for charge injection - Set width and gap for charge injection.
    #   * Enable or disable warm-up (= disable data transfer) - Set data-packet size
    #   * Set CCD read-out order (all CCDs)
    #   * Set CCD side E or F- Upload the window-lists
    #   * Set the window-lists pointers
    #   * Set the window-list lengths
    #   * Set the window size
    #   * Set the copy-order list (including list-length for side E and F) -
    #     Set dump-gate high or low
    return states.ST_WINDOWING


# Define all legal transitions

state_transitions = {
    (states.ST_OFF, "goto_on"): goto_on_mode,
    (states.ST_ON, "goto_standby"): goto_standby_mode,
    (states.ST_WINDOWING, "goto_standby"): goto_standby_mode,
    (states.ST_STANDBY, "goto_windowing"): goto_windowing_mode,
}


class NFEEInternals:
    """
    The N-FEE Internals class represents the actual state of the N-FEE. A bit like the FPGA status
    in the N-FEE hardware. The difference with the RegisterMap is that the register map is updated
    on RMAP write requests, while this class is updated on sync pulses (from the content of the
    register map). Therefore, the N-FEE Internals represent the actual state, while the register
    map represents the commanded state.
    """
    def __init__(self, reg_map: RegisterMap):
        self.reg_map = reg_map
        self.ccd_mode_config = self.reg_map["ccd_mode_config"]
        self.sensor_sel = self.reg_map["sensor_sel"]
        self.ccd_read_en = self.reg_map["ccd_read_en"]
        self.v_start = self.reg_map["v_start"]
        self.v_end = self.reg_map["v_end"]
        self.digitise_en = self.reg_map["digitise_en"]
        self.sync_sel = self.reg_map["sync_sel"]
        self.int_sync_period = self.reg_map["int_sync_period"]
        self.ccd_readout_order = self.reg_map["ccd_readout_order"]
        LOGGER.info(f"Initialised {self.v_start=}, {self.v_end=}")

    def update(self, pulse_type: int):
        """
        Update the internal state from the register. Depending on the pulse_type, specific state
        variables are updated from the current register map values.

        Args:
            pulse_type (int): a 200 or 400 ms pulse
        """
        if pulse_type == 200:
            self.sensor_sel = self.reg_map["sensor_sel"]
            self.ccd_read_en = self.reg_map['ccd_read_en']
        if pulse_type == 400:
            self.sensor_sel = self.reg_map["sensor_sel"]
            self.ccd_read_en = self.reg_map['ccd_read_en']
            self.ccd_mode_config = self.reg_map["ccd_mode_config"]
            self.v_start = self.reg_map["v_start"]
            self.v_end = self.reg_map["v_end"]
            self.digitise_en = self.reg_map["digitise_en"]
            self.sync_sel = self.reg_map["sync_sel"]
            self.int_sync_period = self.reg_map["int_sync_period"]
            self.ccd_readout_order = self.reg_map["ccd_readout_order"]
            LOGGER.info(f"Updated {self.v_start=}, {self.v_end=}, {self.ccd_mode_config=}")

    def get_sync_period(self) -> float:
        """
        Calculate and return the period between two successive sync pulses.

        Note:
            Please note that this value is calculated from what is known in the register map. The
            external sync period is however dependent from the sync signal received from the AEU,
            and the AEU might have been configured for extended sync periods.

        Returns:
            The sync period (time between two sync pulses) in seconds.
        """
        sync_sel = self.sync_sel
        if sync_sel:
            sync_period = self.int_sync_period + 400  # add the duration of the long pulse
        else:
            sync_period = 6250
        return sync_period / 1000

    def get_readout_order(self) -> List:
        """Returns the ccd readout order as a list of CCD numbers, e.g. [1, 2, 3, 4]."""
        return convert_ccd_order_value(self.ccd_readout_order)


temperature_walks = {
    "TOU_SENSE_1": RandomWalk(boundary=(0, 0x7FFF)),
    "TOU_SENSE_2": RandomWalk(boundary=(0, 0x7FFF)),
    "TOU_SENSE_3": RandomWalk(boundary=(0, 0x7FFF)),
    "TOU_SENSE_4": RandomWalk(boundary=(0, 0x7FFF)),
    "TOU_SENSE_5": RandomWalk(boundary=(0, 0x7FFF)),
    "TOU_SENSE_6": RandomWalk(boundary=(0, 0x7FFF)),
}


def initialise_hk_data(hk_data: HousekeepingData) -> HousekeepingData:
    """Initialises the housekeeping data to fake or simulated values."""

    try:
        hk_info_table = GlobalState.setup.telemetry.dictionary
    except AttributeError as exc:
        raise SetupError("Version of the telemetry dictionary not specified in the current setup.") from exc

    storage_mnemonic_col = hk_info_table[TmDictionaryColumns.STORAGE_MNEMONIC].values
    original_name_col = hk_info_table[TmDictionaryColumns.ORIGINAL_EGSE_HK_NAMES].values
    selection = np.where(storage_mnemonic_col == ORIGIN)
    original_names = original_name_col[selection]

    for name in temperature_walks:
        hk_data[name] = int(next(temperature_walks[name]))

    hk_data["CCD1_TS"] = 0x7FFF
    hk_data["CCD2_TS"] = 0x7FFF
    hk_data["CCD3_TS"] = 0x7FFF
    hk_data["CCD4_TS"] = 0x7FFF

    hk_data["PRT1"] = 0x7FFF
    hk_data["PRT2"] = 0x7FFF
    hk_data["PRT3"] = 0x7FFF
    hk_data["PRT4"] = 0x7FFF
    hk_data["PRT5"] = 0x7FFF

    hk_data["ZERO_DIFF_AMP"] = 0x8015

    if "CCD1_VOD_MON" in original_names:
        hk_data["CCD1_VOD_MON"] = 0x8055
    else:
        if "CCD1_VOD_MON_E" in original_names:
            hk_data["CCD1_VOD_MON_E"] = 0x8055
        if "CCD1_VOD_MON_F" in original_names:
            hk_data["CCD1_VOD_MON_F"] = 0x8055
    hk_data["CCD1_VOG_MON"] = 0x8056
    hk_data["CCD1_VRD_MON_E"] = 0x8056

    if "CCD2_VOD_MON" in original_names:
        hk_data["CCD2_VOD_MON"] = 0x8057
    else:
        if "CCD2_VOD_MON_E" in original_names:
            hk_data["CCD2_VOD_MON_E"] = 0x8057
        if "CCD2_VOD_MON_F" in original_names:
            hk_data["CCD2_VOD_MON_F"] = 0x8057
    hk_data["CCD2_VOG_MON"] = 0x8058
    hk_data["CCD2_VRD_MON_E"] = 0x8057

    if "CCD3_VOD_MON" in original_names:
        hk_data["CCD3_VOD_MON"] = 0x8058
    else:
        if "CCD3_VOD_MON_E" in original_names:
            hk_data["CCD3_VOD_MON_E"] = 0x8058
        if "CCD3_VOD_MON_F" in original_names:
            hk_data["CCD3_VOD_MON_F"] = 0x8058
    hk_data["CCD3_VOG_MON"] = 0x8058
    hk_data["CCD3_VRD_MON_E"] = 0x8058

    if "CCD4_VOD_MON" in original_names:
        hk_data["CCD4_VOD_MON"] = 0x8057
    else:
        if "CCD4_VOD_MON_E" in original_names:
            hk_data["CCD4_VOD_MON_E"] = 0x8057
        if "CCD4_VOD_MON_F" in original_names:
            hk_data["CCD4_VOD_MON_F"] = 0x8057
    hk_data["CCD4_VOG_MON"] = 0x8058
    hk_data["CCD4_VRD_MON_E"] = 0x8058

    hk_data["VCCD"] = 0x39BF
    hk_data["VRCLK_MON"] = 0xFC8A
    hk_data["VICLK"] = 0xFAE9
    if "VRCLK_LOW" in original_names:
        hk_data["VRCLK_LOW"] = 0x821A

    if "5VB_POS_MON" in original_names:
        hk_data["5VB_POS_MON"] = 0x1E6A
    hk_data["5VB_NEG_MON"] = 0x1A9F
    hk_data["3V3B_MON"] = 0xE75D
    hk_data["2V5A_MON"] = 0x1979
    hk_data["3V3D_MON"] = 0xE76E
    hk_data["2V5D_MON"] = 0x1A8C
    hk_data["1V5D_MON"] = 0xDF35
    hk_data["5VREF_MON"] = 0x1A80

    hk_data["VCCD_POS_RAW"] = 0x53BF
    hk_data["VCLK_POS_RAW"] = 0x40BA
    hk_data["VAN1_POS_RAW"] = 0x0744
    hk_data["VAN3_NEG_MON"] = 0xFB7C
    hk_data["VAN2_POS_RAW"] = 0x3AEC
    hk_data["VDIG_RAW"] = 0x0AB5
    if "5VB_POS_MON" in original_names:
        hk_data["VDIG_RAW_2"] = 0x0A32
    if "VICLK_LOW" in original_names:
        hk_data["VICLK_LOW"] = 0x8277

    hk_data["CCD1_VRD_MON_F"] = 0x8059
    hk_data["CCD1_VDD_MON"] = 0x94CA
    hk_data["CCD1_VGD_MON"] = 0x8056
    hk_data["CCD2_VRD_MON_F"] = 0x8058
    hk_data["CCD2_VDD_MON"] = 0x94C1
    hk_data["CCD2_VGD_MON"] = 0x8055
    hk_data["CCD3_VRD_MON_F"] = 0x8059
    hk_data["CCD3_VDD_MON"] = 0x94C1
    hk_data["CCD3_VGD_MON"] = 0x8058
    hk_data["CCD4_VRD_MON_F"] = 0x8058
    hk_data["CCD4_VDD_MON"] = 0x94BA
    hk_data["CCD4_VGD_MON"] = 0x8056

    hk_data["IG_HI_MON"] = 0x8057
    if "IG_LO_MON" in original_names:
        hk_data["IG_LO_MON"] = 0x8059
    hk_data["TSENSE_A"] = 0x8059
    hk_data["TSENSE_B"] = 0x805A

    hk_data["spw_timecode"] = 0x0000
    hk_data["rmap_target_status"] = 0x0000
    hk_data["rmap_target_indicate"] = 0x0000
    hk_data["spw_link_escape_error"] = 0x0000
    hk_data["spw_credit_error"] = 0x0000
    hk_data["spw_parity_error"] = 0x0000
    hk_data["spw_link_disconnect"] = 0x0000
    hk_data["spw_link_running"] = 0x0001

    hk_data["frame_counter"] = 0x0000
    hk_data["op_mode"] = 0x0000
    hk_data["frame_number"] = 0x0000

    hk_data["error_flags"] = 0x0000

    hk_data["FPGA minor version"] = 0x0018
    hk_data["FPGA major version"] = 0x0000
    hk_data["Board ID"] = 0x0000

    return hk_data

class FEESimulator:
    """
    A software simulator for the front-end electronics of the PLATO cameras.
    """

    def __init__(self, transport: SpaceWireInterface):
        """
        Args:
            transport: the SpaceWire transport method, e.g. DSI or ZeroMQ.
        """
        self._transport: SpaceWireInterface = transport
        self.register_map = RegisterMap("N-FEE")
        self._hk_data = HousekeepingData()
        self._hk_header = DataPacketHeader()

        self._IN = NFEEInternals(self.register_map)

        initialise_hk_data(self._hk_data)
        self.initialise_hk_header()

        self._killer = SignalCatcher()


    def initialise_hk_header(self):
        """
        Initialise the header for the HK data packet. Call this method only after the HK data itself
        has been initialised.
        """
        self._hk_header.length = self._hk_data.data_length()
        data_packet_type = DataPacketType()
        data_packet_type.packet_type = PacketType.HOUSEKEEPING_DATA
        data_packet_type.last_packet = True
        self._hk_header.type = data_packet_type.value

    def update_hk_header(self, pulse_type: int):
        """
        Update the header of the HK data packet.
        """
        data_packet_type = DataPacketType(self._hk_header.type)
        data_packet_type.frame_number = self._hk_data.frame_number
        data_packet_type.mode = self._IN.ccd_mode_config
        self._hk_header.type = data_packet_type.value
        self._hk_header.frame_counter = self._hk_data.frame_counter
        if pulse_type == 400:
            self._hk_header.sequence_counter = 0

    def update_hk_data(self):
        pass

    def get_mode(self):
        mode = self._IN.ccd_mode_config
        return n_fee_mode(mode)

    def get_sync_period(self) -> float:
        return self._IN.get_sync_period()

    def get_current_ccd_number(self):
        """Return the current CCD number [range=1-4]."""
        readout_order = self._IN.ccd_readout_order
        # The convert_ccd_order_value function returns CCD number [1-4]
        readout_order = convert_ccd_order_value(readout_order)
        # CCD number in the N-FEE is [0-3]
        return readout_order[self._hk_data.frame_number]

    @property
    def sensor_sel(self) -> int:
        return self._IN.sensor_sel

    @property
    def v_start(self) -> int:
        return self._IN.v_start

    @property
    def v_end(self) -> int:
        return self._IN.v_end

    @property
    def internal_sync(self) -> bool:
        return bool(self._IN.sync_sel)

    def decode_current_state(self) -> str:
        return self.get_mode().name

    def run(self):

        LOGGER.info(f"FEE Simulator Current State: {self.decode_current_state()}")
        n_fee_side = GlobalState.setup.camera.fee.ccd_sides.enum
        sensor_sel_enum = GlobalState.setup.camera.fee.sensor_sel.enum

        with self._transport:

            LOGGER.info("SpaceWire Transport has been connected.")

            self._transport.configure()

            LOGGER.info("SpaceWire Transport has been configured.")

            LOGGER.info("Listening for SpaceWire communication...")

            start_time = time.perf_counter()  # time in fractional seconds

            while True:

                sync_period = self.get_sync_period()

                if self._killer.term_signal_received:
                    LOGGER.warning(f"Terminating N-FEE Simulator after receiving {self._killer.signal_name}")
                    break

                if time.perf_counter() <= start_time + sync_period:
                    continue

                # LOGGER.debug(f"{'-'*80} {sync_period = }")

                start_time = time.perf_counter()

                # Send a timecode packet -----------------------------------------------------------

                timecode = self._hk_data.timecode
                LOGGER.info(f"Sending timecode=0x{timecode:02X}")
                self._transport.send_timecode(timecode)

                # Send a housekeeping packet -------------------------------------------------------

                LOGGER.info(f"Sending HK packet: frame_counter={self._hk_data.frame_counter}, "
                            f"sequence_counter={self._hk_header.sequence_counter}, "
                            f"type={self._hk_header.type_as_object}")
                LOGGER.debug(f"HK Packet: error_flags=0b{self._hk_data['error_flags']:0b}")

                data = self._hk_header.data_as_bytes() + self._hk_data.data_as_bytes()
                packet = SpaceWirePacket.create_packet(data)
                self._transport.write_packet(packet.packet_as_bytes)

                self._transport.flush()

                # Check if error flags must be cleared ---------------------------------------------

                if self.register_map['clear_error_flag']:
                    LOGGER.info("Clearing error flags")
                    self.register_map[('reg_21_config', 'clear_error_flag')] = 0
                    self._hk_data['error_flags'] = 0

                # Send the Data packets ------------------------------------------------------------

                LOGGER.info(f"mode={self.decode_current_state()}, "
                            f"Sensor={self.sensor_sel}, "
                            f"Digitising={bool(self._IN.digitise_en)}, "
                            f"Internal Sync={self.internal_sync}")

                # FIXME: N-FEE sends E- and F-side interlaced, in the code code below we always
                #        send E-side first, then F-side.

                if (self._IN.digitise_en and
                    self._IN.ccd_mode_config in (n_fee_mode.FULL_IMAGE_PATTERN_MODE,
                                                 n_fee_mode.FULL_IMAGE_MODE,)):

                    try:
                        ccd_id_to_bin = GlobalState.setup.camera.fee.ccd_numbering.CCD_ID_TO_BIN
                    except AttributeError:
                        raise SetupError("No entry in the setup for camera.fee.ccd_numbering.CCD_ID_TO_BIN")

                    LOGGER.info("Sending Data packets...")

                    ccd_number = ccd_id_to_bin[self.get_current_ccd_number()]  # N-FEE CCD number [0-3]
                    if self.sensor_sel & sensor_sel_enum.E_SIDE:
                        self.send_data_packets(timecode, ccd_id=ccd_number, ccd_side=n_fee_side.E_SIDE)
                    if self.sensor_sel & sensor_sel_enum.F_SIDE:
                        self.send_data_packets(timecode, ccd_id=ccd_number, ccd_side=n_fee_side.F_SIDE)

                if self._killer.user_signal_received and self._killer.signal_name == "SIGUSR1":
                    # On USR1 signal, set the error flags to a random number. There are currently 12 error flags.
                    self.set_error_flags(random.randint(0x0, 0b1111_1111_1111))
                    self._killer.clear()

                # Process any RMAP commands that were sent -----------------------------------------

                LOGGER.info("Processing RMAP commands...")

                while time.perf_counter() < start_time + sync_period - 0.2:
                    process_rmap_command(self._transport, self.register_map, self._hk_data)

                LOGGER.info("Updating internals...")

                self._hk_data.increment_timecode()

                if not self.internal_sync:
                    self._hk_data.increment_frame_number()

                if self._hk_data.frame_number == 0:
                    self._hk_data.increment_frame_counter()
                    self._IN.update(400)
                    self.update_hk_header(400)
                else:
                    self._IN.update(200)
                    self.update_hk_header(200)


    def set_error_flags(self, flags: int):
        """Set error_flags to the given number."""
        LOGGER.warning(f"Setting error flags to 0b{flags:012b}")
        self._hk_data["error_flags"] = flags

    def send_data_packets(self, timecode: int, ccd_id: int, ccd_side: int):

            data = create_pattern_data(timecode, ccd_id, ccd_side)

            header = DataPacketHeader()
            packet_type = header.type_as_object
            packet_type.ccd_side = ccd_side
            packet_type.ccd_number = ccd_id
            packet_type.last_packet = False
            packet_type.frame_number = self._hk_data.frame_number
            packet_type.mode = self._IN.ccd_mode_config
            header.type = packet_type

            LOGGER.info(f"**** {packet_type=!s}")
            LOGGER.info(f"Sending data packets...{self.v_start=} {self.v_end=}")

            for packet in generate_data_packets(data, header, self.v_start, self.v_end):
                self._transport.write_packet(packet.packet_as_bytes)
                self._transport.flush()


def process_rmap_command(transport: SpaceWireInterface, register: RegisterMap, hk_data: HousekeepingData):

    _, buffer = transport.read_packet(timeout=200)
    if not buffer:
        return

    # The following check is to cope with loss of connection when either the
    # DPU Processor crashed or the connection dropped for some other reason.
    # We will receive one packet with 0 or 1 bytes.

    if len(buffer) in {0, 1}:
        return

    packet = SpaceWirePacket.create_packet(buffer)

    LOGGER.debug(f"SpW packet received: {packet}")

    status = 0  # indicating OK

    if isinstance(packet, ReadRequest):
        # If address is start of HK memory area, read the data from the housekeeping data
        if packet.address == 0x700:
            data = hk_data.data_as_bytes()
        else:
            data = register.get_data(packet.address, packet.data_length)

        data = create_rmap_read_request_reply_packet(
            packet.instruction, packet.transaction_id, status, data, packet.data_length)

        LOGGER.debug(f"Sending a ReadRequestReply: {data[:10]=}")

        transport.write_packet(data)
        transport.flush()

    elif isinstance(packet, WriteRequest):
        if packet.is_verified():
            LOGGER.debug(f"Write data to register map: 0x{packet.address:x} {packet.data}")
            register.set_data(packet.address, packet.data)
            data = create_rmap_write_request_reply_packet(
                packet.instruction, packet.transaction_id, status
            )

            transport.write_packet(data)
            transport.flush()

        else:
            LOGGER.warning("Unverified Write Request not yet implemented!")


def start_fee_simulator(transport: SpaceWireInterface):

    try:
        fee_sim = FEESimulator(transport)
        fee_sim.run()
    except KeyboardInterrupt:
        print("Shutdown requested...exiting")
    except SystemExit as exit_code:
        print(f"System Exit with code {exit_code}.")
        return exit_code
    except Exception:
        import traceback

        traceback.print_exc(file=sys.stdout)


@click.group()
def cli():
    pass


@cli.command()
@click.option("--tunnel", is_flag=True,
              help="use an SSH tunnel to connect to the DSI")
@click.option("--zeromq", is_flag=True,
              help="use ZeroMQ to connect to the DPU Processor")
@click.option("--ssh-user", "-u",
              help="the username at the SSH server")
@click.option("--dsi-address", "-a",
              help="the hostname or IP address of the DSI to which this client "
                   "will connect (+ tcp socket port)")
@click.option("--dsi-port", "-p", type=int, default=1,
              help="the DSI port number to which this client needs to connect "
                   "(not the port on the socket) [type=int]")
def start(tunnel, zeromq, ssh_user, dsi_address, dsi_port):
    """
    Start the FEE Simulator.

    When --tunnel is specified, DSI_ADDRESS will default to 127.0.0.1
    unless explicitly provided.
    """
    print(f"{tunnel=}, {zeromq=}, {ssh_user=}, {dsi_address=}, {dsi_port=}")

    if tunnel:
        user = getpass.getuser()
        password = getpass.getpass("Enter SSH passphrase: ")

        # This is the IP address of the SSH server.

        server_host = site_settings.SSH_SERVER
        server_port = site_settings.SSH_PORT

        # The IP address of the DSI, i.e. the EtherSpaceLink device from 4Links and
        # the default port as defined in the Settings configuration file.

        remote_host = dsi_settings.DSI_FEE_IP_ADDRESS
        remote_port = dsi_settings.DSI_FEE_PORT

        # The host from which the connection will be established. Usually, this
        # is the 'localhost', but can be specified on the commandline if needed.

        if not dsi_address:
            local_host = "127.0.0.1"
            local_port = 4948  # this number is just an arbitrary choice
            dsi_address = f"{local_host}:{local_port}"
        else:
            local_host, local_port = dsi_address.split(":")
            local_port = int(local_port)

        LOGGER.debug(
            f"SSH server: {server_host}:{server_port}, "
            f"DSI: {remote_host}:{remote_port}, "
            f"{local_host=}:{local_port=}, "
            f"{dsi_address=}, {dsi_port=}"
        )

        with sshtunnel.open_tunnel(
            (server_host, server_port),
            ssh_username=user,
            # FIXME: hardcoded info should go into specific user settings or the file should
            #   be searched for in the user's home directory.
            ssh_private_key="/Users/rik/.ssh/id_rsa",
            ssh_private_key_password=password,
            remote_bind_address=(remote_host, remote_port),
            local_bind_address=(local_host, local_port),
        ):
            transport = SpaceWireOverDSI(dsi_address, dsi_port)
            return start_fee_simulator(transport)
    else:
        if zeromq:
            transport = SpaceWireOverZeroMQ(
                f"tcp://{dpu_settings.HOSTNAME}:5555", "DPU--FEE")
        else:
            if not dsi_address:
                dsi_address = f"{dsi_settings.DSI_FEE_IP_ADDRESS}:{dsi_settings.DSI_FEE_PORT}"

            transport = SpaceWireOverDSI(dsi_address, dsi_port)

        return start_fee_simulator(transport)


if __name__ == "__main__":
    sys.exit(cli())
