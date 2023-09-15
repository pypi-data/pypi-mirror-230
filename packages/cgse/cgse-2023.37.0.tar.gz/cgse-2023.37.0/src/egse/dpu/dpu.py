"""
This module contains commanding functions that are used by the DPU Controller / Processor.

The commanding functions (starting with `command_`) are put on the command_queue by the
DPUController when a user executes a DPU command. The DPU processor picks up the command from the
queue and executes the command in the RMAP commanding window, i.e. when the N-FEE is ready to
accept RMAP commands. All these commands shall start with `command_`.

There are also priority commands which are treated different by the DPU processor. The DPU
processor executes the priority commands also outside the RMAP window. Priority commands can
either act only within the context of the DPU processor, i.e. return a register value without
consulting the N-FEE, or special RMAP commands can also be sent to the N-FEE outside the normal
RMAP window. An example of the latter is the _Immediate ON_ mode. These commands shall all start
with `prio_command_`.

"""
import logging
from collections import namedtuple
from typing import Optional

import numpy as np

from egse.fee import n_fee_mode
from egse.reg import Register
from egse.reg import RegisterMap
from egse.spw import SpaceWireInterface
from egse.state import GlobalState
from egse.system import Timer

MODULE_LOGGER = logging.getLogger(__name__)

DEFAULT_CCD_READOUT_ORDER = 0b11100100
"""The default for pFM -> CCD 1, 2, 3, 4 (reading from the right).
We use this default value only for going to DUMP mode because there the ccd_readout_order parameter
is not passed. For all other command functions, the ccd_readout_order is explicitly passed."""

SENSOR_SEL_BOTH_SIDES = 3


class NFEEState:
    """
    This class represents the state of the N-FEE FPGA as close as possible in terms of register
    values during the different stages of a readout cycle. The difference between this class and
    the register map is that the register map is updated on RMAP write requests (commands on the
    DPU Processor Queue), while this class is updated on sync pulses from the content of the
    register map. Therefore, the N-FEE Internals represent the actual state, while the register
    map represents the commanded state.

    The following parameters are tracked by this class:

    Every long pulse (400ms):

        * v_start, v_end, h_end, n_final_dump, ccd_mode_config, ccd_readout_order,
          sync_sel, digitise_en, DG_en, int_sync_period
        * sensor_sel, ccd_read_en

    Every short pulse (200ms):

        * sensor_sel, ccd_read_en
    """

    FIELDS = (
        "v_start",
        "v_end",
        "h_end",
        "n_final_dump",
        "ccd_mode_config",
        "ccd_readout_order",
        "sync_sel",
        "digitise_en",
        "DG_en",
        "int_sync_period",
        "sensor_sel",  # also updated on 200ms pulse
        "ccd_read_en",  # also updated on 200ms pulse
    )

    StateTuple = namedtuple("StateTuple", FIELDS)

    def __init__(self):

        self._internals = {k: 0 for k in NFEEState.FIELDS}

    @property
    def v_start(self):
        return self._internals["v_start"]

    @property
    def v_end(self):
        return self._internals["v_end"]

    @property
    def h_end(self):
        return self._internals["h_end"]

    @property
    def n_final_dump(self):
        return self._internals["n_final_dump"]

    @property
    def ccd_mode_config(self):
        return self._internals["ccd_mode_config"]

    @property
    def ccd_readout_order(self):
        return self._internals["ccd_readout_order"]

    @property
    def sync_sel(self):
        return self._internals["sync_sel"]

    @property
    def digitise_en(self):
        return self._internals["digitise_en"]

    @property
    def dg_en(self):
        return self._internals["DG_en"]

    @property
    def int_sync_period(self):
        return self._internals["int_sync_period"]

    @property
    def sensor_sel(self):
        return self._internals["sensor_sel"]

    @property
    def ccd_read_en(self):
        return self._internals["ccd_read_en"]

    def get_value(self, name: str):
        return self._internals[name]

    def get_parameter_names(self):
        return self._internals.keys()

    def update_at_400ms(self, reg_map: RegisterMap):
        """
        Update the state from all the relevant values of the Register Map. In principle, triggered
        by the 400ms pulse, the N-FEE will update it's internal state from all the values in the
        Register Map. For the purpose of the DPU Processor, we only need a sub-set of these values.
        Since the DPU Processor doesn't know about pulses, it decides if a 400ms pulse was received
        from the content of the HK packet header. A 400ms pulse was received when the
        frame number is the housekeeping packet is zero, frame_number==0.

        Args:
            reg_map (RegisterMap): the DPU Processor register map

        """

        MODULE_LOGGER.debug("Updating N-FEE State at 400ms..")

        for par_name in self._internals:
            self._internals[par_name] = reg_map[par_name]

    def update_at_200ms(self, reg_map: RegisterMap):
        """
        Update the state from selected values of the Register Map. Only the following parameters
        are updated at a 200ms pulse. We only have 200ms pulses when in external sync mode. The
        update shall be done on frame_number == 1, 2, or 3.

        * sensor_sel: the CCD side 'E=0b10' or 'F=0b01' or BOTH=0b11. This is a 2-bit number.
        * ccd_read_en: flag to enable/disable CCD readout

        Args:
            reg_map (RegisterMap): the DPU Processor register map

        """

        MODULE_LOGGER.debug("Updating N-FEE State at 200ms..")

        for par_name in "sensor_sel", "ccd_read_en":
            self._internals[par_name] = reg_map[par_name]

    def get_state(self):
        return NFEEState.StateTuple(**self._internals)


def read_register_from_n_fee(
        transport: SpaceWireInterface, register_map: RegisterMap, reg_name: str
) -> bytes:
    """
    Reads the data for the given register from the N-FEE memory map.

    This function sends an RMAP read request for the register to the N-FEE.
    The returned data is then compared to the data read from the local copy
    of the register map. If the data is different, the local data is replaced
    with the retrieved data and a warning message is issued. The function
    finally returns the retrieved data as a bytes object of length 4.

    Args:
        transport (SpaceWireInterface): the transport method
        register_map (RegisterMap): a local copy of the register map
        reg_name (str): the name of the register to fetch from the N-FEE

    Returns:
        data: the 32-bit data that was read from the N-FEE.

    """

    reg: Register = register_map.get_register(reg_name)
    address = reg.address

    rx_data = transport.read_register(address)
    data = register_map.get_register_data(reg_name)

    if rx_data != data:
        MODULE_LOGGER.warning(
            f"Data received for {reg.name} is different from local copy: {rx_data} != {data}"
        )

        # update the local copy of the registry
        register_map.set_register_data(reg_name, rx_data)

    return rx_data


def write_register_on_n_fee(
        transport: SpaceWireInterface, register_map: RegisterMap, reg_name: str
):
    """
    Writes the data from the given register to the N-FEE memory map.

    The function reads the data for the registry from the local register map
    and then sends an RMAP write request for the register to the N-FEE.

    .. note:: it is assumed that the local register map is up-to-date.

    Args:
        transport (SpaceWireInterface): the transport method
        register_map (RegisterMap): a local copy of the register map
        reg_name (str): the name of the register to fetch from the N-FEE

    Raises:
        RMAPError: when data can not be written on the target, i.e. the N-FEE.
    """

    reg: Register = register_map.get_register(reg_name)
    address = reg.address

    data = register_map.get_register_data(reg_name)

    # Prepare and send the RMAP write request command
    # This function can generate an RMAPError, but we let it pass so that it
    # can be caught at a higher level.

    _ = transport.write_register(address, data)


def command_noop(*args, **kwargs):
    MODULE_LOGGER.debug("No commanding during this sync period.")


def command_sync_register_map(transport: SpaceWireInterface, register_map: RegisterMap):
    """
    Reads the full register from the N-FEE and initializes the local register map with
    the returned data.

    Args:
        transport (SpaceWireInterface): interface to use for SpaceWire communication
        register_map (RegisterMap): the N-FEE register map
    """

    # In principle, we should request each register separately, but the N-FEE allows even in
    # critical memory to read the full register at once. I leave the original code here should
    # the behaviour of the N-FEE become more restrictive again.
    #
    # for reg_name in register_map:
    #     read_register_from_n_fee(transport, register_map, reg_name)

    with Timer("Request full register from N-FEE"):
        data = transport.read_register(0x0000_0000, 0x800, strict=False)
        register_map.set_data(0x0000_0000, data, 0x800)

    return register_map


def command_get_hk_information(transport: SpaceWireInterface, register_map: RegisterMap, address: int, data_length: int) -> bytes:
    """
    Reads the memory area of the N-FEE where the housekeeping information is saved. This area is located between
    0x0700 – 0x07FC (inclusive) [see PLATO-DLR-PL-ICD-010].

    Args:
        transport (SpaceWireInterface): interface to use for SpaceWire communication
        register_map (RegisterMap): the N-FEE register map -> not used in this function
        address (int): start address
        data_length (int): number of bytes

    Returns:
        A bytes object containing the housekeeping information.
    """

    return transport.read_memory_map(address, data_length)


def command_set_nfee_fpga_defaults(transport: SpaceWireInterface, register_map: RegisterMap):
    """ Set the default FPGA parameters for the N-FEE.

    Args:
        transport (SpaceWireInterface): interface to use for SpaceWire communication
        register_map (RegisterMap): the N-FEE register map
    """

    MODULE_LOGGER.info("Set default values for the FPGA")

    default_values = GlobalState.setup.camera.fee.fpga_defaults

    for reg_name in default_values:
        hex_string = str(default_values[reg_name])
        byte_string = int(hex_string, 16).to_bytes(length=4, byteorder='big', signed=False)

        MODULE_LOGGER.info(f"Set default value for {reg_name} ({default_values[reg_name]})")

        register_map.set_register_data(reg_name, byte_string)
        write_register_on_n_fee(transport, register_map, reg_name)

    return True


def command_get_mode(transport: SpaceWireInterface, register_map: RegisterMap):
    MODULE_LOGGER.info("Request mode from N-FEE.")

    reg: Register = register_map.get_register("reg_21_config")

    read_register_from_n_fee(transport, register_map, reg.name)

    return register_map.get_value("reg_21_config", "ccd_mode_config")


def prio_command_is_dump_mode(n_fee_state: NFEEState.StateTuple,
                              dpu_internals: "DPUInternals", register_map: RegisterMap) -> bool:
    MODULE_LOGGER.info("Request N-FEE if in DUMP mode (prio).")

    # This is a prio command which means it will be executed as soon as possible and return quickly.
    # Mode change in the N-FEE happens only on long (400ms) pulses, therefore prio commands act on
    # the N-FEE State instead of the RegisterMap.

    return (
        not n_fee_state.digitise_en and n_fee_state.DG_en and
        n_fee_state.ccd_mode_config == n_fee_mode.FULL_IMAGE_MODE
    )


def prio_command_get_register_map(n_fee_state: NFEEState.StateTuple,
                                  dpu_internals: "DPUInternals", register_map: RegisterMap):
    MODULE_LOGGER.info("Request register map from DPU Processor (prio).")

    # This is a prio command which means it will be executed as soon as possible and return quickly.
    # Mode change in the N-FEE happens only on long (400ms) pulses, therefore prio commands act on
    # the N-FEE State instead of the RegisterMap.

    return register_map


def prio_command_get_mode(n_fee_state: NFEEState.StateTuple,
                          dpu_internals: "DPUInternals", register_map: RegisterMap):
    MODULE_LOGGER.info("Request mode from N-FEE (prio).")

    # This is a prio command which means it will be executed as soon as possible and return quickly.
    # Mode change in the N-FEE happens only on long (400ms) pulses, therefore prio commands act on
    # the N-FEE State instead of the RegisterMap.

    return n_fee_state.ccd_mode_config


def prio_command_get_sync_mode(n_fee_state: NFEEState.StateTuple,
                               dpu_internals: "DPUInternals", register_map: RegisterMap):
    MODULE_LOGGER.info("Request sync mode from N-FEE (prio).")

    # This is a prio command which means it will be executed as soon as possible and return quickly.
    # Mode change in the N-FEE happens only on long (400ms) pulses, therefore prio commands act on
    # the N-FEE State instead of the RegisterMap.

    return n_fee_state.sync_sel


def prio_command_set_slicing(n_fee_state: namedtuple,
                             dpu_internals: "DPUInternals", register_map: RegisterMap, num_cycles: int):
    MODULE_LOGGER.info(f"Set slicing parameter: {num_cycles = } (prio)")

    # This is a prio command which means it will be executed as soon as possible and return quickly.
    # Mode change in the N-FEE happens only on long (400ms) pulses, therefore prio commands act on
    # the N-FEE State instead of the RegisterMap.

    dpu_internals.slicing_num_cycles = num_cycles

    return num_cycles


def prio_command_get_slicing(n_fee_state: namedtuple,
                             dpu_internals: "DPUInternals", register_map: RegisterMap) -> int:
    MODULE_LOGGER.info("Request slicing parameter (prio)")

    # This is a prio command which means it will be executed as soon as possible and return quickly.
    # Mode change in the N-FEE happens only on long (400ms) pulses, therefore prio commands act on
    # the N-FEE State instead of the RegisterMap.

    return dpu_internals.slicing_num_cycles


def command_set_immediate_on_mode(transport: SpaceWireInterface, register_map: RegisterMap):
    # TODO (Rik): this command shall become a prio_command
    #     Check what the N-FEE does and what is returned as a response, especially since in the
    #     mean time other packets can be returned. This method I think will return a
    #     WriteRequestReply, but it is probably asynchronously!
    MODULE_LOGGER.info("Commanding N-FEE into IMMEDIATE ON mode.")

    reg: Register = register_map.get_register("reg_21_config")

    read_register_from_n_fee(transport, register_map, reg.name)

    register_map.set_value(reg.name, "ccd_mode_config", n_fee_mode.IMMEDIATE_ON_MODE)

    MODULE_LOGGER.debug("Sending write request to N-FEE for IMMEDIATE ON mode.")

    write_register_on_n_fee(transport, register_map, reg.name)

    return n_fee_mode.IMMEDIATE_ON_MODE.value


def command_set_high_precision_hk_mode(transport: SpaceWireInterface, register_map: RegisterMap,
                                       flag: bool):
    MODULE_LOGGER.info("Commanding N-FEE into HIGH PRECISION HK mode.")

    reg: Register = register_map.get_register("reg_5_config")

    read_register_from_n_fee(transport, register_map, reg.name)

    register_map.set_value(reg.name, "High_precision_HK_en", flag)

    MODULE_LOGGER.debug("Sending write request to N-FEE for High Precision HK mode.")

    write_register_on_n_fee(transport, register_map, reg.name)

    return flag


def command_set_on_mode(transport: SpaceWireInterface, register_map: RegisterMap):
    MODULE_LOGGER.info("Commanding N-FEE into ON mode.")

    _set_register(transport, register_map, "reg_21_config", ccd_mode_config=n_fee_mode.ON_MODE)

    return register_map["ccd_mode_config"]


def command_set_standby_mode(transport: SpaceWireInterface, register_map: RegisterMap):
    MODULE_LOGGER.info("Commanding N-FEE into StandBy mode.")

    _set_register(transport, register_map, "reg_21_config", ccd_mode_config=n_fee_mode.STAND_BY_MODE)

    return register_map["ccd_mode_config"]


def command_set_dump_mode(
        transport: SpaceWireInterface,
        register_map: RegisterMap,
        v_start: int = 0, v_end: int = 0, sensor_sel_=SENSOR_SEL_BOTH_SIDES,
        ccd_readout_order: int = DEFAULT_CCD_READOUT_ORDER,
        n_final_dump: int = 4510, sync_sel: int = 0
):
    MODULE_LOGGER.info("Commanding N-FEE into dump mode.")

    MODULE_LOGGER.info(
        f"Setting {v_start=} and {v_end=}, {v_end - v_start + 1} lines, {sensor_sel_=}")

    _set_register(transport, register_map, "reg_0_config", v_start=v_start, v_end=v_end)
    _set_register(transport, register_map, "reg_2_config", ccd_readout_order=ccd_readout_order)
    _set_register(transport, register_map, "reg_3_config",
                  n_final_dump=n_final_dump, charge_injection_en=0, img_clk_dir=0, reg_clk_dir=0)
    _set_register(transport, register_map, "reg_5_config",
                  sensor_sel=sensor_sel_, digitise_en=0b00, DG_en=0b01, sync_sel=sync_sel)
    _set_register(transport, register_map, "reg_21_config",
                  ccd_mode_config=n_fee_mode.FULL_IMAGE_MODE)

    # Set (back) the default values for VGD as they might have been changed by charge injection

    # _set_register(transport, register_map, "reg_19_config", ccd_vgd_config=0xE)
    # _set_register(transport, register_map, "reg_20_config", ccd_vgd_config=0xCF)

    return register_map["ccd_mode_config"]


def command_set_dump_mode_int_sync(
        transport: SpaceWireInterface,
        register_map: RegisterMap,
        v_start: int = 0, v_end: int = 0, sensor_sel_=SENSOR_SEL_BOTH_SIDES,
        ccd_readout_order: int = DEFAULT_CCD_READOUT_ORDER,
        n_final_dump: int = 4510, int_sync_period: int = 600, sync_sel: int = 1
):
    MODULE_LOGGER.info("Commanding N-FEE into internal sync dump mode.")

    MODULE_LOGGER.info(
        f"Setting {v_start=} and {v_end=}, {v_end - v_start + 1} lines, {sensor_sel_=}, {n_final_dump=}")

    _set_register(transport, register_map, "reg_0_config", v_start=v_start, v_end=v_end)
    _set_register(transport, register_map, "reg_2_config", ccd_readout_order=ccd_readout_order)
    _set_register(transport, register_map, "reg_3_config",
                  n_final_dump=n_final_dump, charge_injection_en=0, img_clk_dir=0, reg_clk_dir=0)
    _set_register(transport, register_map, "reg_4_config", int_sync_period=int_sync_period)
    _set_register(transport, register_map, "reg_5_config",
                  sensor_sel=sensor_sel_, digitise_en=0b00, DG_en=0b01, sync_sel=sync_sel)
    _set_register(transport, register_map, "reg_21_config",
                  ccd_mode_config=n_fee_mode.FULL_IMAGE_MODE)

    return register_map["ccd_mode_config"]


def _set_register(transport: SpaceWireInterface, register_map: RegisterMap, reg_name: str, **kwarg: int):
    """
    Set a register from its individual parameters and sends the register to the N-FEE. This
    function first reads the register from the N-FEE and updates the local register if there is a
    mismatch.

    Args:
        transport: the transport layer for SpaceWire communication
        register_map (RegisterMap): a local copy of the register map (maintained by the DPU
            Processor)
        reg_name (str): the name of the register
        kwarg (dict): a dictionary with the parameter names and their values

    Returns:
        None.

    """
    reg: Register = register_map.get_register(reg_name)

    read_register_from_n_fee(transport, register_map, reg.name)

    for k, v in kwarg.items():
        register_map.set_value(reg.name, k, v)

    write_register_on_n_fee(transport, register_map, reg.name)
    read_register_from_n_fee(transport, register_map, reg.name)


def command_set_full_image_mode(
        transport: SpaceWireInterface,
        register_map: RegisterMap,
        v_start: int = 0, v_end: int = 4509, sensor_sel_=SENSOR_SEL_BOTH_SIDES,
        ccd_readout_order=None, n_final_dump=0
):
    MODULE_LOGGER.info("Commanding N-FEE into Full Image mode.")

    MODULE_LOGGER.debug(
        f"Setting {v_start=} and {v_end=}, {v_end - v_start + 1} lines, {sensor_sel_=}")

    _set_register(transport, register_map, "reg_0_config", v_start=v_start, v_end=v_end)
    _set_register(transport, register_map, "reg_2_config", ccd_readout_order=ccd_readout_order)
    _set_register(transport, register_map, "reg_3_config", n_final_dump=n_final_dump)
    _set_register(transport, register_map, "reg_5_config",
                  sensor_sel=sensor_sel_, digitise_en=0b01, DG_en=0b00, sync_sel=0)
    _set_register(transport, register_map, "reg_21_config", ccd_mode_config=n_fee_mode.FULL_IMAGE_MODE)

    return n_fee_mode.FULL_IMAGE_MODE.value


def command_set_full_image_mode_int_sync(
        transport: SpaceWireInterface,
        register_map: RegisterMap,
        v_start: int = 0, v_end: int = 4509, sensor_sel_=SENSOR_SEL_BOTH_SIDES,
        ccd_readout_order=None, n_final_dump=0,
        int_sync_period=6250
):
    MODULE_LOGGER.info("Commanding N-FEE into Full Image mode and internal sync.")

    MODULE_LOGGER.debug(
        f"Setting {v_start=} and {v_end=}, {v_end - v_start + 1} lines, {sensor_sel_=}, "
        f"{ccd_readout_order=}, {int_sync_period=}")

    _set_register(transport, register_map, "reg_0_config", v_start=v_start, v_end=v_end)
    _set_register(transport, register_map, "reg_2_config", ccd_readout_order=ccd_readout_order)
    _set_register(transport, register_map, "reg_3_config", n_final_dump=n_final_dump)
    _set_register(transport, register_map, "reg_4_config", int_sync_period=int_sync_period)
    _set_register(transport, register_map, "reg_5_config",
                  sensor_sel=sensor_sel_, digitise_en=0b01, DG_en=0b00, sync_sel=1)
    _set_register(transport, register_map, "reg_21_config", ccd_mode_config=n_fee_mode.FULL_IMAGE_MODE)

    return n_fee_mode.FULL_IMAGE_MODE.value


def command_set_register_value(
        transport: SpaceWireInterface,
        register_map: RegisterMap,
        reg_name: str, field_name: str, field_value: int
):
    MODULE_LOGGER.info(f"Commanding N-FEE to set register value {field_name=} to {field_value=}.")

    _set_register(transport, register_map, reg_name, **{field_name: field_value})

    return True


def command_reset(transport: SpaceWireInterface, register_map: RegisterMap):

    MODULE_LOGGER.info("Commanding N-FEE to reset to default settings.")

    _set_register(transport, register_map, "reg_21_config", ccd_mode_config=0x07)

    return True


def command_internal_clock(
        transport: SpaceWireInterface,
        register_map: RegisterMap,
        int_sync_period: int
):
    MODULE_LOGGER.info(f"Commanding N-FEE the internal clock to {int_sync_period=}ms and select it.")

    _set_register(transport, register_map, "reg_4_config", int_sync_period=int_sync_period)
    _set_register(transport, register_map, "reg_5_config", sync_sel=1)


def command_external_clock(
        transport: SpaceWireInterface,
        register_map: RegisterMap,
):
    MODULE_LOGGER.info("Commanding N-FEE to use the external clock.")

    _set_register(transport, register_map, "reg_5_config", sync_sel=0)


def command_set_full_image_pattern_mode(
        transport: SpaceWireInterface,
        register_map: RegisterMap,
        v_start: int = 0,
        v_end: int = 4509,
        sensor_sel_=SENSOR_SEL_BOTH_SIDES,
):
    """
    Command the N-FEE into Full Image Pattern mode. This mode can only be reached from the ON_MODE,
    but this is not checked by this function (it is an assumption that the caller has checked this).

    .. note:: this function is currently N-FEE specific.

    Args:
        transport: the transport layer for SpaceWire communication
        register_map (RegisterMap): a local copy of the register map
        v_start (int): the start line for the readout
        v_end (int): the last line for the readout
        sensor_sel_ (int): the side of the CCD that needs to be transferred

    Returns:
        None.
    """
    MODULE_LOGGER.info("Commanding N-FEE into Full Image Pattern mode.")

    MODULE_LOGGER.debug(
        f"Setting {v_start=} and {v_end=}, {v_end - v_start + 1} lines, {sensor_sel_=}")

    _set_register(transport, register_map, "reg_0_config", v_start=v_start, v_end=v_end)
    # _set_register(transport, register_map, "reg_2_config", ccd_readout_order=ccd_readout_order)
    _set_register(transport, register_map, "reg_5_config", sensor_sel=sensor_sel_)
    _set_register(transport, register_map, "reg_5_config", digitise_en=0b01)  # send data to DPU
    _set_register(transport, register_map, "reg_5_config", DG_en=0b00)  # dump gate low
    _set_register(transport, register_map, "reg_21_config", ccd_mode_config=n_fee_mode.FULL_IMAGE_PATTERN_MODE)

    return n_fee_mode.FULL_IMAGE_PATTERN_MODE.value


def command_set_clear_error_flags(transport: SpaceWireInterface, register_map: RegisterMap):
    """
    Clear all error flags generated by the N-FEE FPGA for non RMAP/SpW related functions immediately.

    The `clear_error_flag` bit in the register map is set to 1, meaning that all error flags that
    are generated by the N-FEE FPGA for non RMAP-SpW related functions are cleared immediately.
    This bit is cleared automatically, so that any future error flags can be latched again.  If
    the error conditions persist and no corrective measures are taken, then  error flags would be
    set again.
    """
    # keep debug level because this command is sent on each readout
    MODULE_LOGGER.debug("Commanding N-FEE to clear error flag.")

    _set_register(transport, register_map, "reg_21_config", clear_error_flag=1)

    return register_map["clear_error_flag"]


def command_set_readout_order(transport: SpaceWireInterface, register_map: RegisterMap, ccd_readout_order: int):
    """
    Sets the given ccd_readout_order in the register map, then sends this change to the N-FEE.
    """
    MODULE_LOGGER.info(f"Commanding N-FEE – set readout order to 0x{ccd_readout_order:02x}.")

    _set_register(transport, register_map, "reg_2_config", ccd_readout_order=ccd_readout_order)


def command_set_reverse_clocking(
        transport: SpaceWireInterface,
        register_map: RegisterMap,
        v_start: int = 0,
        v_end: int = 4509,
        sensor_sel_=SENSOR_SEL_BOTH_SIDES,
        ccd_readout_order=None,
        n_final_dump=0,
        img_clk_dir=0,
        reg_clk_dir=0,
):
    """
    Command the N-FEE into full image reverse clocking mode.
    """
    MODULE_LOGGER.info("Commanding N-FEE to reverse clocking.")

    _set_register(transport, register_map, "reg_0_config", v_start=v_start, v_end=v_end)
    _set_register(transport, register_map, "reg_2_config", ccd_readout_order=ccd_readout_order)
    _set_register(transport, register_map, "reg_3_config",
                  n_final_dump=n_final_dump, img_clk_dir=img_clk_dir, reg_clk_dir=reg_clk_dir)
    _set_register(transport, register_map, "reg_5_config",
                  sensor_sel=sensor_sel_, digitise_en=0b01, DG_en=0b00, sync_sel=0)
    _set_register(transport, register_map, "reg_21_config", ccd_mode_config=n_fee_mode.FULL_IMAGE_MODE)

    return True


def command_set_charge_injection(
        transport: SpaceWireInterface,
        register_map: RegisterMap,
        v_start: int = 0,
        v_end: int = 4509,
        n_final_dump=0,
        sensor_sel_=SENSOR_SEL_BOTH_SIDES,
        ccd_readout_order=None,
        charge_injection_width=0,
        charge_injection_gap=0,
):
    """
    TBW
    """
    MODULE_LOGGER.info("Commanding N-FEE to configure charge injection.")

    _set_register(
        transport, register_map, "reg_0_config",
        v_start=v_start, v_end=v_end)
    _set_register(
        transport, register_map, "reg_1_config",
        charge_injection_width=charge_injection_width,
        charge_injection_gap=charge_injection_gap)
    _set_register(
        transport, register_map, "reg_2_config",
        ccd_readout_order=ccd_readout_order)
    _set_register(
        transport, register_map, "reg_3_config",
        n_final_dump=n_final_dump, charge_injection_en=1)
    _set_register(
        transport, register_map, "reg_5_config",
        sensor_sel=sensor_sel_, digitise_en=0b01, DG_en=0b00)
    _set_register(
        transport, register_map, "reg_21_config",
        ccd_mode_config=n_fee_mode.FULL_IMAGE_MODE)

    return True


def command_set_vgd(
        transport: SpaceWireInterface,
        register_map: RegisterMap,
        ccd_vgd_config: Optional[float] = None,
):
    """
    Set the ccd_vgd_config register value.

    Note that the N-FEE shall be in ON mode for this to take effect!
    """

    MODULE_LOGGER.info(f"{ccd_vgd_config=}")

    if ccd_vgd_config is not None:

        # HARDCODED STUFF HERE
        # FIXME: these numbers should go into the Setup camera.fee section
        #     5.983 -> what is that value? where does it come from? see email Dave Walton
        # Explanation by Dave Walton in MSSL provided test script:
        #     V_GD control is 5.983V per bit (12bit DAC). So 17V=2842d, =0xB1A.
        #     DAC LS Nibble (0xA in this case) is programmed into MSNibble of reg_4C.
        #     DAC MSByte (0xB1 in this case) is programmed into LSByte of reg_50.

        converted_vgd = int(ccd_vgd_config/5.983*1000)

        value_reg_19 = converted_vgd & 0b1111
        value_reg_20 = (converted_vgd >> 4) & 0b11111111

        _set_register(transport, register_map, "reg_19_config", ccd_vgd_config=value_reg_19)
        _set_register(transport, register_map, "reg_20_config", ccd_vgd_config=value_reg_20)

        return True

    return False
