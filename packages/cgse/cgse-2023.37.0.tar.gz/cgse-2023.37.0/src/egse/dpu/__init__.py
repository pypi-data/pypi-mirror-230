"""
This module defines the commanding interfaces for the DPU—N-FEE interaction.


On the *client/user side*, the `DPUProxy` class shall be used for user interactions and commanding with both
the DPU simulator and the N-FEE. This class connects to the DPU control server which must be running before
any commands can be processed.

On the *server side*, the `DPUControlServer` class is located in the module `dpu_cs`.

The top-level classes that are of interest to the developer when inspecting this module are:

* `DPUController` which puts the requested commands on the command queue for the `DPUProcessor`
* `DPUProcessor` is the work horse of the DPU simulator and runs in a separate process. This process communicates
  directly with the N-FEE through the SpaceWire interface.
* `DPUInternals` keeps critical information about the DPU and provides information on the status of the
  readout progress, i.e. where we are in the readout cycle.
* `DPUMonitoring` provides methods to run a function at a certain time, e.g. right after a long pulse, or to wait
  for an event, e.g. when an HDF5 file is ready for processing.

The actual commanding is done in `dpu` module. That module also defines the `NFEEState` which acts as a
mirror of the FPGA status.

This module also defines a number of functions, but they all are for internal use and are not of any interest
unless you are maintaining this module.

"""

import logging
import multiprocessing
import pickle
import queue
from enum import Enum

import time
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Mapping
from typing import Tuple
from typing import Type

import zmq

from egse.command import ClientServerCommand
from egse.confman import ConfigurationManagerProxy
from egse.control import ControlServer
from egse.decorators import dynamic_interface
from egse.dpu.dpu import NFEEState, command_set_nfee_fpga_defaults
from egse.dpu.dpu import command_external_clock
from egse.dpu.dpu import command_get_hk_information
from egse.dpu.dpu import command_get_mode
from egse.dpu.dpu import command_internal_clock
from egse.dpu.dpu import command_reset
from egse.dpu.dpu import command_set_charge_injection
from egse.dpu.dpu import command_set_clear_error_flags
from egse.dpu.dpu import command_set_readout_order
from egse.dpu.dpu import command_set_dump_mode
from egse.dpu.dpu import command_set_dump_mode_int_sync
from egse.dpu.dpu import command_set_full_image_mode
from egse.dpu.dpu import command_set_full_image_mode_int_sync
from egse.dpu.dpu import command_set_full_image_pattern_mode
from egse.dpu.dpu import command_set_high_precision_hk_mode
from egse.dpu.dpu import command_set_immediate_on_mode
from egse.dpu.dpu import command_set_on_mode
from egse.dpu.dpu import command_set_register_value
from egse.dpu.dpu import command_set_reverse_clocking
from egse.dpu.dpu import command_set_standby_mode
from egse.dpu.dpu import command_set_vgd
from egse.dpu.dpu import command_sync_register_map
from egse.dpu.dpu import prio_command_get_mode
from egse.dpu.dpu import prio_command_get_register_map
from egse.dpu.dpu import prio_command_get_slicing
from egse.dpu.dpu import prio_command_get_sync_mode
from egse.dpu.dpu import prio_command_is_dump_mode
from egse.dpu.dpu import prio_command_set_slicing
from egse.dsi.esl import is_timecode
from egse.exceptions import Abort
from egse.fee import is_hk_data_packet
from egse.fee import n_fee_mode
from egse.fee.nfee import HousekeepingData
from egse.obsid import ObservationIdentifier
from egse.protocol import CommandProtocol
from egse.proxy import Proxy
from egse.reg import RegisterMap
from egse.settings import Settings
from egse.setup import SetupError
from egse.spw import DataDataPacket
from egse.spw import DataPacket
from egse.spw import DataPacketType
from egse.spw import HousekeepingPacket
from egse.spw import OverscanDataPacket
from egse.spw import SpaceWireInterface
from egse.spw import SpaceWirePacket
from egse.spw import TimecodePacket
from egse.spw import to_string
from egse.state import GlobalState
from egse.storage import StorageProxy
from egse.storage.persistence import FITS
from egse.storage.persistence import HDF5
from egse.storage.persistence import PersistenceLayer
from egse.system import SignalCatcher
from egse.system import Timer
from egse.system import format_datetime
from egse.system import wait_until
from egse.zmq import MessageIdentifier
from egse.zmq_ser import bind_address
from egse.zmq_ser import connect_address

LOGGER = logging.getLogger(__name__)

CTRL_SETTINGS = Settings.load("DPU Control Server")
N_FEE_SETTINGS = Settings.load("N-FEE")
COMMAND_SETTINGS = Settings.load(filename="dpu.yaml")
DEVICE_SETTINGS = Settings.load(filename="dpu.yaml")

CRUCIAL_REGISTER_PARAMETERS = (
    "ccd_readout_order", "sensor_sel", "v_start", "v_end", "h_end", "ccd_mode_config"
)

DATA_TYPE: Dict[str, Type[PersistenceLayer]] = {
    "HDF5": HDF5,
    "FITS": FITS,
}

CCD_NUMBERS = [1, 2, 3, 4]


def rotate_list(seq, n):
    if (size := len(seq)) < 2:
        return seq
    n = n % len(seq)
    return seq[n:] + seq[:n]


def _get_ccd_readout_order(order_list: list, ccd_id_mapping: list):
    return sum(ccd_id_mapping[ccd] << idx * 2 for idx, ccd in enumerate(order_list))


class NoDataPacketError(Exception):
    """Raised when the expected data packet turns out to be something else."""
    pass


class NoHousekeepingPacketError(Exception):
    """Raised when the expected Housekeeping packet turns out to be something else."""
    pass


class NoTimeCodeError(Exception):
    """Raised when the expected Timecode packet turns out to be something else."""
    pass


class NoBytesReceivedError(Exception):
    """Raised when the zero or one bytes were received."""
    pass


class TimecodeTimeoutError(Exception):
    """Raised when the read_packet times out while waiting for a timecode."""
    pass


class TimeExceededError(Exception):
    """Raised when retrieving the data packets from the N-FEE takes too long."""
    pass


class NFEECommandError(Exception):
    """Raised when sending a command to the N-FEE failed."""
    pass


class DPUInterface:
    """
    This interface is for sending commands to the DPU Control Server. The commands are user
    oriented and will be translated by the DPU Controller in proper FEE commands.

    The interface should be implemented by the `DPUController` and the `DPUProxy` (and possibly
    a `DPUSimulator` should we need that e.g. for testing purposes).

    The command shall also be added to the `dpu.yaml` command definitions file.
    """

    @dynamic_interface
    def marker(self, mark: str):
        raise NotImplementedError

    @dynamic_interface
    def get_slicing(self) -> int:
        raise NotImplementedError

    @dynamic_interface
    def set_slicing(self, num_cycles: int):
        raise NotImplementedError

    @dynamic_interface
    def is_simulator(self):
        raise NotImplementedError

    @dynamic_interface
    def get_register_map(self) -> RegisterMap:
        """
        Returns the RegisterMap
        """
        raise NotImplementedError

    @dynamic_interface
    def n_fee_sync_register_map(self):
        """
        Read the complete register map from the N-FEE.
        """
        raise NotImplementedError

    @dynamic_interface
    def n_fee_get_mode(self):
        """
        Returns the N-FEE mode.
        """
        raise NotImplementedError

    @dynamic_interface
    def n_fee_get_sync_mode(self):
        """
        Returns the N-FEE mode.
        """
        raise NotImplementedError

    @dynamic_interface
    def n_fee_set_on_mode(self):
        """Command the N-FEE to go into ON mode."""
        raise NotImplementedError

    @dynamic_interface
    def n_fee_is_dump_mode(self):
        """
        Returns True if the N-FEE is configured for DUMP mode.

        DUMP mode is not really an N-FEE mode, but more a set of register settings that allow to
        readout/dump all CCDs without transmitting any data. This mode is used in ambient to make
        sure the detectors do not get saturated between tests.
        """
        raise NotImplementedError

    @dynamic_interface
    def n_fee_set_immediate_on_mode(self):
        """Command the N-FEE to go into ON mode."""
        raise NotImplementedError

    @dynamic_interface
    def n_fee_set_standby_mode(self):
        """Command the N-FEE to go into STANDBY mode."""
        raise NotImplementedError

    @dynamic_interface
    def n_fee_set_dump_mode(self, n_fee_parameters: dict):
        """ Command the N-FEE to go into DUMP mode.

        n_fee_parameters:

        The n_fee_parameters argument is a dictionary with additional/specific parameters to
        set in the register when moving to full image pattern mode.

            * num_cycles (int): the number of readout cycles
            * v_start (int): the first line to readout
            * v_end (int): the last line to readout
            * sensor_sel (int): the CCD side to select for transfer

        Args:
             n_fee_parameters (dict): dictionary with N-FEE parameters to be set_
        """
        raise NotImplementedError

    @dynamic_interface
    def n_fee_set_dump_mode_int_sync(self, n_fee_parameters: dict):
        """ Command the N-FEE to go into DUMP mode and internal sync.

        The n_fee_parameters argument is a dictionary with additional/specific parameters to
        set in the register when moving to full image pattern mode.

            * num_cycles (int): the number of readout cycles
            * v_start (int): the first line to readout
            * v_end (int): the last line to readout
            * sensor_sel (int): the CCD side to select for transfer
            * int_sync_period (int): the period of the internal sync in milliseconds

        Args:
             n_fee_parameters (dict): dictionary with N-FEE parameters to be set_
        """
        raise NotImplementedError

    @dynamic_interface
    def n_fee_set_full_image_mode(self, n_fee_parameters):
        """
        Command the N-FEE to go into FULL_IMAGE mode.

        n_fee_parameters:

        The n_fee_parameters argument is a dictionary with additional/specific parameters to
        set in the register when moving to full image pattern mode.

            * num_cycles (int): the number of readout cycles
            * v_start (int): the first line to readout
            * v_end (int): the last line to readout
            * sensor_sel (int): the CCD side to select for transfer

        Args:
            n_fee_parameters (dict): dictionary with N-FEE parameters to be set
        """
        raise NotImplementedError

    @dynamic_interface
    def n_fee_set_full_image_mode_int_sync(self, n_fee_parameters):
        """
        Command the N-FEE to go into FULL_IMAGE mode and internal sync.

        n_fee_parameters:

        The n_fee_parameters argument is a dictionary with additional/specific parameters to
        set in the register when moving to full image pattern mode.

            * num_cycles (int): the number of readout cycles
            * v_start (int): the first line to readout
            * v_end (int): the last line to readout
            * sensor_sel (int): the CCD side to select for transfer

        Args:
            n_fee_parameters (dict): dictionary with N-FEE parameters to be set
        """
        raise NotImplementedError

    @dynamic_interface
    def n_fee_set_full_image_pattern_mode(self, n_fee_parameters):
        """
        Command the N-FEE to go into FULL_IMAGE_PATTERN mode.

        n_fee_parameters:

        The n_fee_parameters argument is a dictionary with additional/specific parameters to
        set in the register when moving to full image pattern mode.

            * num_cycles (int): the number of readout cycles
            * v_start (int): the first line to readout
            * v_end (int): the last line to readout
            * sensor_sel (int): the CCD side to select for transfer

        Args:
            n_fee_parameters (dict): dictionary with N-FEE parameters to be set
        """
        raise NotImplementedError

    @dynamic_interface
    def n_fee_high_precision_hk_mode(self, n_fee_parameters: dict):
        """Command the N-FEE to go into high precision housekeeping mode."""
        raise NotImplementedError

    @dynamic_interface
    def n_fee_set_internal_sync(self, n_fee_parameters: dict):
        """
        Command the N-FEE to go into internal sync mode.

        The method expects the following keys in n_fee_parameters:

        * int_sync_period: the internal sync period in milliseconds [default=6250]

        Args:
            n_fee_parameters (dict): N-FEE parameter dictionary
        """
        raise NotImplementedError

    @dynamic_interface
    def n_fee_set_external_sync(self, n_fee_parameters: dict):
        """
        Command the N-FEE to go into external sync mode.
        No keys are expected in n_fee_parameters, pass an empty dict.
        """
        raise NotImplementedError

    @dynamic_interface
    def n_fee_set_register_value(self, reg_name: str, field_name: str, field_value: int):
        """Command the N-FEE to set a register value."""
        raise NotImplementedError

    @dynamic_interface
    def n_fee_reset(self):
        """Command the N-FEE to reset to its default settings."""
        raise NotImplementedError

    @dynamic_interface
    def n_fee_set_clear_error_flags(self):
        """
        Command the N-FEE to clear all error flags for non RMAP/SpW related functions immediately.

        The `clear_error_flag` bit in the register map is set to 1, meaning that all error flags
        that are generated by the N-FEE FPGA for non RMAP-SpW related functions are cleared
        immediately.  This bit is cleared automatically, so that any future error flags can be
        latched again.  If the error conditions persist and no corrective measures are taken,
        then error flags would be set again.
        """

        raise NotImplementedError

    @dynamic_interface
    def n_fee_set_reverse_clocking(self, n_fee_parameters: dict):

        raise NotImplementedError

    @dynamic_interface
    def n_fee_set_charge_injection(self, n_fee_parameters: dict):
        raise NotImplementedError

    @dynamic_interface
    def n_fee_set_vgd(self, n_fee_parameters: dict):
        raise NotImplementedError

    @dynamic_interface
    def n_fee_set_fpga_defaults(self):
        raise NotImplementedError


class DPUSimulator(DPUInterface):
    # The DPUSimulator will stand by itself, which means it will not send commands to an FEE
    # nor will it request data or HK from the FEE. The methods in this implementation will return
    # a fake set of data.

    def n_fee_get_mode(self):
        return n_fee_mode.STAND_BY_MODE

    def n_fee_get_sync_mode(self):
        return NotImplemented

    def n_fee_set_on_mode(self):
        pass

    def n_fee_set_standby_mode(self):
        pass

    def n_fee_set_dump_mode(self, n_fee_parameters: dict):
        pass

    def n_fee_set_full_image_mode(self, n_fee_parameters):
        import pprint

        LOGGER.debug(f"called: n_fee_set_full_image_mode({pprint.pformat(n_fee_parameters)})")

    def n_fee_set_full_image_mode_int_sync(self, n_fee_parameters):
        import pprint

        LOGGER.debug(f"called: n_fee_set_full_image_mode_int_sync({pprint.pformat(n_fee_parameters)})")

    def n_fee_set_full_image_pattern_mode(self):
        pass

    def n_fee_high_precision_hk_mode(self, n_fee_parameters: dict):
        pass

    def n_fee_set_internal_sync(self, n_fee_parameters: dict):
        pass

    def n_fee_set_external_sync(self):
        pass

    def n_fee_set_clear_error_flags(self):
        pass

    def n_fee_set_fpga_defaults(self):
        pass


class DPUController(DPUInterface):
    """
    The DPU Controller puts commands on the command queue for processing by the DPU Processor.
    Any response from the DPU Processor will be available on the response queue as soon as the
    command has been executed. The DPU Processor is a separate process that is started by the
    DPU Command Protocol.
    """

    def __init__(self,
                 priority_queue: multiprocessing.Queue,
                 command_queue: multiprocessing.Queue,
                 response_queue: multiprocessing.Queue):
        self._priority_q = priority_queue
        self._command_q = command_queue
        self._response_q = response_queue

        try:
            self.default_ccd_readout_order = GlobalState.setup.camera.fee.ccd_numbering.DEFAULT_CCD_READOUT_ORDER
            self.sensor_sel_both_sides = GlobalState.setup.camera.fee.sensor_sel.enum.BOTH_SIDES.value
        except AttributeError:
            raise SetupError("No entry in the setup for camera.fee.ccd_numbering.DEFAULT_CCD_READOUT_ORDER")

    def marker(self, mark: str):
        LOGGER.info(f"{mark = }")

    def get_slicing(self) -> int:
        self._priority_q.put((prio_command_get_slicing, []))
        LOGGER.debug("Controller.get_slicing: Put prio_command_get_slicing on the Queue.")
        (cmd, response) = self._response_q.get()
        LOGGER.debug(f"Controller.get_slicing returned: ({cmd.__name__}, {response}).")
        return response

    def set_slicing(self, num_cycles: int):
        self._priority_q.put((prio_command_set_slicing, [num_cycles]))
        LOGGER.debug(
            "Controller.set_slicing: Put prio_command_set_slicing on the Queue."
        )
        (cmd, response) = self._response_q.get()
        LOGGER.debug(f"Controller.set_slicing returned: ({cmd.__name__}, {response}).")
        return response

    def is_simulator(self):
        return True

    def n_fee_sync_register_map(self) -> RegisterMap:
        self._command_q.put((command_sync_register_map, [], {}))
        LOGGER.debug(
            "Controller.n_fee_sync_register_map: Put command_sync_register_map on the Queue."
        )
        (cmd, response) = self._response_q.get()
        LOGGER.debug(f"Controller.n_fee_sync_register_map returned: ({cmd.__name__}, {response}).")
        return response

    def get_register_map(self) -> RegisterMap:
        self._priority_q.put((prio_command_get_register_map, []))
        LOGGER.debug("Controller.get_register_map: Put prio_command_get_register_map on the Queue.")
        (cmd, response) = self._response_q.get()
        LOGGER.debug(f"Controller.get_register_map returned: ({cmd.__name__}, {response}).")
        return response

    def n_fee_get_mode(self):
        self._priority_q.put((prio_command_get_mode, []))
        LOGGER.debug("Controller.n_fee_get_mode: Put prio_command_get_mode on the Queue.")
        (cmd, response) = self._response_q.get()
        LOGGER.debug(f"Controller.n_fee_get_mode returned: ({cmd.__name__}, {response}).")
        return response

    def n_fee_get_sync_mode(self):
        self._priority_q.put((prio_command_get_sync_mode, []))
        LOGGER.debug("Controller.n_fee_get_sync_mode: Put prio_command_get_sync_mode on the Queue.")
        (cmd, response) = self._response_q.get()
        LOGGER.debug(f"Controller.n_fee_get_sync_mode returned: ({cmd.__name__}, {response}).")
        return response

    def n_fee_is_dump_mode(self):
        self._priority_q.put((prio_command_is_dump_mode, []))
        LOGGER.debug("Controller.n_fee_is_dump_mode: Put prio_command_is_dump_mode on the Queue.")
        (cmd, response) = self._response_q.get()
        LOGGER.debug(f"Controller.n_fee_is_dump_mode returned: ({cmd.__name__}, {response}).")
        return response

    def n_fee_set_immediate_on_mode(self):
        self._command_q.put((command_set_immediate_on_mode, [], {}))
        LOGGER.debug(
            "Controller.n_fee_set_immediate_on_mode: Put command_set_immediate_on_mode "
            "on the Queue."
        )
        (cmd, response) = self._response_q.get()
        LOGGER.debug(
            f"Controller.n_fee_set_immediate_on_mode returned: ({cmd.__name__}, {response})"
        )
        return response

    def n_fee_set_on_mode(self):
        self._command_q.put((command_set_on_mode, [], {}))
        LOGGER.debug("Controller.n_fee_set_on_mode: Put command_set_on_mode on the Queue.")
        (cmd, response) = self._response_q.get()
        LOGGER.debug(f"Controller.n_fee_set_on_mode returned: ({cmd.__name__}, {response})")
        return response

    def n_fee_set_standby_mode(self):
        self._command_q.put((command_set_standby_mode, [], {}))
        LOGGER.debug(
            "Controller.n_fee_set_standby_mode: Put command_set_standby_mode on the Queue."
        )
        (cmd, response) = self._response_q.get()
        LOGGER.debug(f"Controller.n_fee_set_standby_mode returned: ({cmd.__name__}, {response})")
        return response

    def n_fee_set_dump_mode(self, n_fee_parameters: dict):
        v_start = n_fee_parameters.get("v_start", 0)
        v_end = n_fee_parameters.get("v_end", 0)
        sensor_sel_ = n_fee_parameters.get("sensor_sel", self.sensor_sel_both_sides)
        ccd_readout_order = n_fee_parameters.get("ccd_readout_order", self.default_ccd_readout_order)
        n_final_dump = n_fee_parameters.get("n_final_dump", 4510)
        sync_sel = n_fee_parameters.get("sync_sel", 0)
        num_cycles = n_fee_parameters.get("num_cycles", 0)
        self._command_q.put((command_set_dump_mode,
                             [v_start, v_end, sensor_sel_, ccd_readout_order, n_final_dump, sync_sel],
                             {'num_cycles': num_cycles}))
        LOGGER.debug(
            "Controller.n_fee_set_dump_mode: Put command_set_dump_mode on the Queue."
        )
        (cmd, response) = self._response_q.get()
        LOGGER.debug(f"Controller.n_fee_set_dump_mode returned: ({cmd.__name__}, {response})")
        return response

    def n_fee_set_dump_mode_int_sync(self, n_fee_parameters: dict):
        v_start = n_fee_parameters.get("v_start", 0)
        v_end = n_fee_parameters.get("v_end", 0)
        sensor_sel_ = n_fee_parameters.get("sensor_sel", self.sensor_sel_both_sides)
        n_final_dump = n_fee_parameters.get("n_final_dump", 4510)
        ccd_readout_order = n_fee_parameters.get("ccd_readout_order", self.default_ccd_readout_order)
        sync_sel = n_fee_parameters.get("sync_sel", 1)
        int_sync_period = n_fee_parameters.get("int_sync_period", 600)
        num_cycles = n_fee_parameters.get("num_cycles", 0)
        self._command_q.put(
            (
                command_set_dump_mode_int_sync,
                [v_start, v_end, sensor_sel_, ccd_readout_order, n_final_dump, int_sync_period, sync_sel],
                {'num_cycles': num_cycles}
            )
        )
        LOGGER.debug("Controller.n_fee_set_dump_mode_int_sync: "
                     "Put command_set_dump_mode_int_sync on the Queue.")
        (cmd, response) = self._response_q.get()
        LOGGER.debug(f"Controller.n_fee_set_dump_mode_int_sync returned: ({cmd.__name__}, {response})")
        return response

    def n_fee_set_full_image_mode(self, n_fee_parameters: dict):
        v_start = n_fee_parameters.get("v_start", 0)
        v_end = n_fee_parameters.get("v_end", 1)
        sensor_sel_ = n_fee_parameters.get("sensor_sel", self.sensor_sel_both_sides)
        ccd_readout_order = n_fee_parameters.get("ccd_readout_order", self.default_ccd_readout_order)
        n_final_dump = n_fee_parameters.get("n_final_dump", 0)
        num_cycles = n_fee_parameters.get("num_cycles", 0)
        dump_mode_int = n_fee_parameters.get("dump_mode_int", False)
        self._command_q.put((command_set_full_image_mode,
                             [v_start, v_end, sensor_sel_, ccd_readout_order, n_final_dump],
                             {'num_cycles': num_cycles, 'dump_mode_int': dump_mode_int}))
        LOGGER.debug(
            "Controller.n_fee_set_full_image_mode: Put command_set_full_image_mode on the Queue."
        )
        (cmd, response) = self._response_q.get()
        LOGGER.debug(f"Controller.n_fee_set_full_image_mode returned: ({cmd.__name__}, {response})")
        return response

    def n_fee_set_full_image_mode_int_sync(self, n_fee_parameters: dict):
        v_start = n_fee_parameters.get("v_start", 0)
        v_end = n_fee_parameters.get("v_end", 1)
        sensor_sel_ = n_fee_parameters.get("sensor_sel", self.sensor_sel_both_sides)
        ccd_readout_order = n_fee_parameters.get("ccd_readout_order", self.default_ccd_readout_order)
        n_final_dump = n_fee_parameters.get("n_final_dump", 0)
        int_sync_period = n_fee_parameters.get("int_sync_period", 6250)
        num_cycles = n_fee_parameters.get("num_cycles", 0)
        dump_mode_int = n_fee_parameters.get("dump_mode_int", True)
        self._command_q.put((command_set_full_image_mode_int_sync,
                             [v_start, v_end, sensor_sel_, ccd_readout_order, n_final_dump, int_sync_period],
                             {'num_cycles': num_cycles, 'dump_mode_int': dump_mode_int}))
        LOGGER.debug(
            "Controller.n_fee_set_full_image_mode_int_sync: Put command_set_full_image_mode_int_sync on the Queue."
        )
        (cmd, response) = self._response_q.get()
        LOGGER.debug(f"Controller.n_fee_set_full_image_mode_int_sync returned: ({cmd.__name__}, {response})")
        return response

    def n_fee_set_full_image_pattern_mode(self, n_fee_parameters: dict):
        v_start = n_fee_parameters.get("v_start", 0)
        v_end = n_fee_parameters.get("v_end", 1)
        sensor_sel_ = n_fee_parameters.get("sensor_sel", self.sensor_sel_both_sides)
        num_cycles = n_fee_parameters.get("num_cycles", 0)
        self._command_q.put((command_set_full_image_pattern_mode,
                             [v_start, v_end, sensor_sel_],
                             {'num_cycles': num_cycles}))
        LOGGER.debug(
            "Controller.n_fee_set_full_image_pattern_mode: Put command_set_full_image_pattern_mode "
            "on the Queue."
        )
        (cmd, response) = self._response_q.get()
        LOGGER.debug(
            f"Controller.n_fee_set_full_image_pattern_mode returned: ({cmd.__name__}, {response})"
        )
        return response

    def n_fee_high_precision_hk_mode(self, n_fee_parameters:dict):
        high_hk = n_fee_parameters.get("high_precision_hk", False)
        self._command_q.put((command_set_high_precision_hk_mode, [high_hk], {}))
        LOGGER.debug(
            "Controller.n_fee_set_high_precision_hk_mode: Put command_set_high_precision_hk_mode "
            "on the Queue."
        )
        (cmd, response) = self._response_q.get()
        LOGGER.debug(
            f"Controller.n_fee_set_high_precision_hk_mode returned: ({cmd.__name__}, {response})"
        )
        return response

    def n_fee_set_internal_sync(self, n_fee_parameters: dict):
        int_sync_period = n_fee_parameters.get("int_sync_period", 6250)
        self._command_q.put((command_internal_clock, [int_sync_period], {}))
        LOGGER.debug(
            "Controller.n_fee_set_internal_sync: Put command_internal_clock on the Queue."
        )
        (cmd, response) = self._response_q.get()
        LOGGER.debug(
            f"Controller.n_fee_set_internal_sync returned: ({cmd.__name__}, {response})"
        )
        return response

    def n_fee_set_external_sync(self, n_fee_parameters: dict):
        self._command_q.put((command_external_clock, [], {}))
        LOGGER.debug(
            "Controller.n_fee_set_internal_sync: Put command_internal_clock on the Queue."
        )
        (cmd, response) = self._response_q.get()
        LOGGER.debug(
            f"Controller.n_fee_set_internal_sync returned: ({cmd.__name__}, {response})"
        )
        return response

    def n_fee_set_register_value(self, reg_name: str, field_name: str, field_value: int):
        self._command_q.put((command_set_register_value, [reg_name, field_name, field_value], {}))
        LOGGER.debug(
            "Controller.n_fee_set_register_value: Put command_set_register_value on the Queue."
        )
        (cmd, response) = self._response_q.get()
        LOGGER.debug(
            f"Controller.n_fee_set_register_value returned: ({cmd.__name__}, {response})"
        )
        return response

    def n_fee_reset(self):
        self._command_q.put((command_reset, [], {}))
        LOGGER.debug(
            "Controller.n_fee_reset: Put command_reset on the Queue."
        )
        (cmd, response) = self._response_q.get()
        LOGGER.debug(f"Controller.n_fee_reset returned: ({cmd.__name__}, {response})")
        return response

    def n_fee_set_clear_error_flags(self):

        self._command_q.put((command_set_clear_error_flags, [], {}))

        LOGGER.debug("Controller.n_fee_set_clear_error_flags: "
                     "Put command_set_clear_error_flags on the Queue.")

        (cmd, response) = self._response_q.get()

        LOGGER.debug(f"Controller.n_fee_set_clear_error_flags returned: ({cmd.__name__}, {response})")
        return response

    def n_fee_set_reverse_clocking(self, n_fee_parameters: dict):
        v_start = n_fee_parameters.get("v_start", 0)
        v_end = n_fee_parameters.get("v_end", 4509)
        sensor_sel_ = n_fee_parameters.get("sensor_sel", self.sensor_sel_both_sides)
        ccd_readout_order = n_fee_parameters.get("ccd_readout_order", self.default_ccd_readout_order)
        n_final_dump = n_fee_parameters.get("n_final_dump", 0)
        num_cycles = n_fee_parameters.get("num_cycles", 0)
        img_clk_dir = n_fee_parameters.get("img_clk_dir", 1)
        reg_clk_dir = n_fee_parameters.get("reg_clk_dir", 0)
        dump_mode_int = n_fee_parameters.get("dump_mode_int", False)

        self._command_q.put((command_set_reverse_clocking,
                             [v_start, v_end, sensor_sel_, ccd_readout_order, n_final_dump, img_clk_dir, reg_clk_dir],
                             {'num_cycles': num_cycles, 'dump_mode_int': dump_mode_int}))
        LOGGER.debug(
            "Controller.n_fee_set_reverse_clocking: Put command_set_reverse_clocking on the Queue."
        )
        (cmd, response) = self._response_q.get()
        LOGGER.debug(f"Controller.n_fee_set_reverse_clocking returned: ({cmd.__name__}, {response})")
        return response

    def n_fee_set_charge_injection(self, n_fee_parameters: dict):
        num_cycles = n_fee_parameters.get("num_cycles", 0)
        v_start = n_fee_parameters.get("v_start", 0)
        v_end = n_fee_parameters.get("v_end", 4509)
        n_final_dump = n_fee_parameters.get("n_final_dump", 0)
        sensor_sel_ = n_fee_parameters.get("sensor_sel", self.sensor_sel_both_sides)
        ccd_readout_order = n_fee_parameters.get("ccd_readout_order", self.default_ccd_readout_order)
        charge_injection_width = n_fee_parameters.get("charge_injection_width", 0)
        charge_injection_gap = n_fee_parameters.get("charge_injection_gap", 0)

        self._command_q.put(
            (
                command_set_charge_injection,
                [
                    v_start, v_end, n_final_dump, sensor_sel_, ccd_readout_order,
                    charge_injection_width, charge_injection_gap
                ],
                {'num_cycles': num_cycles}
            ))
        LOGGER.debug(
            "Controller.n_fee_set_dump_mode: Put command_set_charge_injection on the Queue."
        )
        (cmd, response) = self._response_q.get()
        LOGGER.debug(f"Controller.n_fee_set_charge_injection returned: ({cmd.__name__}, {response})")
        return response

    def n_fee_set_vgd(self, n_fee_parameters: dict):

        # The default value for ccd_vgd_config is 0xCFE = hex(int(19.90/5.983*1000))
        # This value is taken from: PLATO-MSSL-PL-FI-0001_9.0_N-FEE_Register_Map Draft A

        ccd_vgd_config = n_fee_parameters.get("ccd_vgd_config", 19.90)

        self._command_q.put((command_set_vgd, [ccd_vgd_config], {}))

        LOGGER.debug("Controller.n_fee_set_vgd: Put command_set_vgd on the Queue.")

        (cmd, response) = self._response_q.get()

        LOGGER.debug(f"Controller.n_fee_set_vgd returned: ({cmd.__name__}, {response})")
        return response

    def n_fee_set_fpga_defaults(self):
        self._command_q.put((command_set_nfee_fpga_defaults, [], {}))

        LOGGER.debug("Controller.n_fee_set_fpga_defaults: Put n_fee_set_fpga_defaults on the Queue.")

        (cmd, response) = self._response_q.get()

        LOGGER.debug(f"Controller.n_fee_set_fpga_defaults returned: ({cmd.__name__}, {response})")
        return response


class DPUProxy(Proxy, DPUInterface):
    """
    The DPUProxy class is used to connect to the DPU Control Server and send commands to the FEE.
    """

    def __init__(
        self,
        protocol=CTRL_SETTINGS.PROTOCOL,
        hostname=CTRL_SETTINGS.HOSTNAME,
        port=CTRL_SETTINGS.COMMANDING_PORT,
    ):
        """
        Args:
            protocol: the transport protocol [default is taken from settings file]
            hostname: location of the control server (IP address)
                [default is taken from settings file]
            port: TCP port on which the control server is listening for commands
                [default is taken from settings file]
        """
        super().__init__(connect_address(protocol, hostname, port), timeout=10_000)


class DPUCommand(ClientServerCommand):
    pass


class DPUProtocol(CommandProtocol):
    def __init__(self, control_server: ControlServer, transport: SpaceWireInterface):

        super().__init__()

        self.control_server = control_server

        # Set up two queue's to communicate with the DPU Processor Process.
        # The command queue is joinable because the Controller needs to wait for a response in
        # the response queue.

        self.command_queue = multiprocessing.Queue()
        self.response_queue = multiprocessing.Queue()
        self.priority_queue = multiprocessing.Queue()

        # Start a separate Process to handle FEE communication

        self.processor = DPUProcessor(
            transport, self.priority_queue, self.command_queue, self.response_queue)
        self.processor.name = "dpu.processor"
        self.processor.start()

        self.controller = DPUController(
            self.priority_queue, self.command_queue, self.response_queue)

        self.load_commands(COMMAND_SETTINGS.Commands, DPUCommand, DPUController)

        self.build_device_method_lookup_table(self.controller)

    def get_bind_address(self):
        return bind_address(
            self.control_server.get_communication_protocol(),
            self.control_server.get_commanding_port(),
        )

    def get_status(self) -> dict:
        status = super().get_status()
        status["DPU Processor"] = "alive" if self.processor.is_alive() else "--"
        return status

    def get_housekeeping(self) -> dict:
        return {
            "timestamp": format_datetime(),
        }

    def quit(self):
        self.processor.quit()

        def not_alive():
            return not self.processor.is_alive()

        if wait_until(not_alive, timeout=6.5) is False:
            self.processor.join()
            return

        LOGGER.warning("Terminating DPU Processor")
        self.processor.terminate()

        # Wait at least 6.25s which is the 'normal' readout cycle time

        if wait_until(not_alive, timeout=6.5) is False:
            self.processor.join()
            return

        LOGGER.warning("Killing DPU Processor")
        self.processor.kill()
        self.processor.join()

    def is_alive(self) -> bool:
        is_alive = self.processor.is_alive()

        if not is_alive:
            LOGGER.warning(
                f"Process '{self.processor.name}' died for some reason, check for "
                f"an exception in the logging output."
            )

        return is_alive


DPU_PROCESSOR_SETTINGS = Settings.load("DPU Processor")


class DPUMonitoring:
    """
    The DPUMonitoring class allows you to execute a function synchronised to the reception of a
    timecode or a housekeeping packet from the N-FEE.

    Args:
        timeout: time to wait for a message before a timeout [default=30s]
    """
    def __init__(self, timeout: float = 30):
        self._context = zmq.Context.instance()
        self._endpoint = connect_address('tcp', DPU_PROCESSOR_SETTINGS.HOSTNAME, DPU_PROCESSOR_SETTINGS.MONITORING_PORT)
        self._multipart = True
        self._timeout = timeout  # seconds
        self._retries = 3
        self._socket = None
        self._subscriptions = set()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._socket.closed:
            self.disconnect()

    def connect(self):
        self._socket = self._context.socket(zmq.SUB)
        self._socket.connect(self._endpoint)

        # subscribe_string = b''
        # self._socket.subscribe(subscribe_string)
        # self._subscriptions.add(subscribe_string)

    def disconnect(self):
        self._socket.close(linger=0)
        self._subscriptions.clear()

    def unsubscribe_all(self):
        for sub in self._subscriptions:
            self._socket.unsubscribe(sub)
        self._subscriptions.clear()

    def unsubscribe(self, sync_id: int):
        subscribe_string = sync_id.to_bytes(1, byteorder='big') if sync_id else b''
        try:
            self._subscriptions.remove(subscribe_string)
            self._socket.unsubscribe(subscribe_string)
        except KeyError:
            LOGGER.warning(
                f"Trying to unsubscribe a key that was not previously subscribed: {subscribe_string}"
            )

    def subscribe(self, sync_id: int = None):
        subscribe_string = sync_id.to_bytes(1, byteorder='big') if sync_id else b''

        if subscribe_string in self._subscriptions:
            return

        self._socket.subscribe(subscribe_string)
        self._subscriptions.add(subscribe_string)

    def wait_for_timecode(self) -> Tuple[int, str]:
        """
        Connects to the monitoring socket of the DPU Processor and returns when a TIMECODE
        synchronisation message is received.

        Returns:
            A tuple of the timecode (int) and the corresponding timestamp (str).
        """
        self.unsubscribe_all()
        self.subscribe(MessageIdentifier.SYNC_TIMECODE)

        retries = self._retries

        while True:
            rlist, _, _ = zmq.select([self._socket], [], [], timeout=self._timeout)
            if self._socket in rlist:
                if self._multipart:
                    sync_id, pickle_string = self._socket.recv_multipart()
                    sync_id = int.from_bytes(sync_id, byteorder='big')
                else:
                    sync_id = MessageIdentifier.ALL
                    pickle_string = self._socket.recv()
                timecode, timestamp = pickle.loads(pickle_string)

                LOGGER.debug(f"{MessageIdentifier(sync_id).name}, {timecode}, {timestamp}")

                return timecode, timestamp
            else:
                retries -= 1
                LOGGER.warning(f"Monitoring timeout, {retries} retries to go")
                if retries <= 0:
                    raise TimeoutError(f"DPUMonitoring timed out after {self._retries * self._timeout} seconds.")

    def wait_for_hdf5_filename(self, retries: int = None, timeout: float = None) -> List[Path]:
        """
        Connects to the monitoring socket of the DPU Processor and returns a list of path names that
        were part of the current registration in the Storage, right before a new registration was
        initiated.

        This method is mainly intended to be used by processes that need to work with the generated
        HDF5 files after they have been closed by the DPU Processor. One of these processes is the
        FITS generation.

        Notes:
            The path names that are returned are absolute filenames that are specific for the
            egse-server on which the DPU Processor is running. These files might not be accessible
            from the machine you are running this monitoring request.

        Returns:
            A list of path names.
        Raises:
            A TimeoutError when no sync data was received from the monitoring socket after 30s.
        """
        self.unsubscribe_all()
        self.subscribe(MessageIdentifier.HDF5_FILENAMES)

        retries = retries if retries is not None else self._retries
        timeout = timeout or self._timeout

        while True:
            rlist, _, _ = zmq.select([self._socket], [], [], timeout=timeout)
            if self._socket in rlist:
                if self._multipart:
                    sync_id, pickle_string = self._socket.recv_multipart()
                    sync_id = int.from_bytes(sync_id, byteorder='big')
                else:
                    sync_id = MessageIdentifier.ALL
                    pickle_string = self._socket.recv()
                filenames = pickle.loads(pickle_string)

                LOGGER.debug(f"{MessageIdentifier(sync_id).name}, {filenames}")

                return filenames
            else:
                retries -= 1
                # LOGGER.warning(f"Monitoring timeout, {retries} retries to go")
                if retries <= 0:
                    raise TimeoutError(f"DPUMonitoring timed out after {self._retries * self._timeout} seconds.")

    def wait_number_of_pulses(self, num_pulses: int) -> None:
        """
        Wait for a number of pulses (long and short), then return.

        When the number of pulses has been received, the function returns right after the timecode synchronisation
        message. Any command that is sent to the N-FEE immediately after this function returns will be processes within
        that same readout frame, i.e. before the next sync pulse.

        Args:
            num_pulses: the number of sync pulses to wait before returning.

        Raises:
            A TimeoutError when no sync data was received from the monitoring socket after 30s.
        """
        self.unsubscribe_all()
        self.subscribe(MessageIdentifier.SYNC_TIMECODE)

        retries = self._retries

        LOGGER.debug(f"Waiting for {num_pulses} pulses...")

        while True:
            rlist, _, _ = zmq.select([self._socket], [], [], timeout=self._timeout)
            if self._socket in rlist:
                if self._multipart:
                    sync_id, pickle_string = self._socket.recv_multipart()
                    sync_id = int.from_bytes(sync_id, byteorder='big')
                else:
                    sync_id = MessageIdentifier.ALL
                    pickle_string = self._socket.recv()
                timecode, timestamp = pickle.loads(pickle_string)

                num_pulses -= 1
                LOGGER.debug(f"{MessageIdentifier(sync_id).name}, {timecode=}, {timestamp=}, {num_pulses=}")
                if num_pulses <= 0:
                    return

                retries = self._retries  # reset the number of retries
            else:
                retries -= 1
                LOGGER.warning(f"Monitoring timeout, {retries} retries to go")
                if retries <= 0:
                    raise TimeoutError(f"DPUMonitoring timed out after {self._retries * self._timeout} seconds.")

    def wait_num_cycles(self, num_cycles: int, return_on_frame: int = 3) -> int:
        """
        Wait for a number of long pulses (cycles), then return.

        This method will wait for full cycles, i.e. 4 readouts in external sync mode, 1 readout in internal sync mode,
        and will return immediately after receiving the HK sync pulse for the last frame in the requested cycle, i.e.
        frame number == 3 for external sync and frame number == 0 for internal sync. If an RMAP command is then sent
        when the function returns, it will still be executed within that frame and the changed register settings will
        become active on the next pulse, which is a long pulse, the start of the next cycle.
        That way we do not lose a cycle.

        Args:
            num_cycles: the number of full cycles to wait before returning
            return_on_frame: choose the readout frame on which to return [default = 3]

        Returns:
            Zero (0) when no cycles were waited because num_cycles <= 0, otherwise return value > 0.

        Raises:
            A TimeoutError when no sync data was received from the monitoring socket after 30s.
        """
        self.unsubscribe_all()
        self.subscribe(MessageIdentifier.SYNC_HK_PACKET)

        retries = self._retries
        count = 0

        if num_cycles <= 0:
            LOGGER.debug(f"{num_cycles=}, no cycles waited, returned immediately")
            return count

        LOGGER.debug(f"Waiting for {num_cycles} cycles...")

        with Timer("Loop cycles") as timer, DPUProxy() as dpu_proxy:

            # When we are in external sync mode, we need to skip the current cycle,
            # because the requested changes in the register -> FPGA will ony occur on
            # the next long pulse. No need for this when in internal sync mode.

            sync_mode = dpu_proxy.n_fee_get_sync_mode()
            if sync_mode == 0:
                num_cycles += 1

            while True:
                count += 1
                rlist, _, _ = zmq.select([self._socket], [], [], timeout=self._timeout)
                if self._socket in rlist:
                    if self._multipart:
                        sync_id, pickle_string = self._socket.recv_multipart()
                        sync_id = int.from_bytes(sync_id, byteorder='big')
                    else:
                        sync_id = MessageIdentifier.ALL
                        pickle_string = self._socket.recv()
                    status = pickle.loads(pickle_string)

                    LOGGER.debug(f"{MessageIdentifier(sync_id).name}, {to_string(status[0])}")

                    sync_mode = dpu_proxy.n_fee_get_sync_mode()

                    if (sync_mode == 1) or (packet := status[0]) and packet.frame_number == return_on_frame:
                        num_cycles -= 1

                    LOGGER.debug(f"NUM_CYCLES={num_cycles}, {sync_mode=}")

                    if num_cycles <= 0:
                        return count

                    retries = self._retries  # reset the number of retries
                else:
                    retries -= 1
                    LOGGER.warning(f"Monitoring timeout, {retries} retries to go")
                    if retries <= 0:
                        raise TimeoutError(f"DPUMonitoring timed out after {self._retries * self._timeout} seconds.")

                timer.log_elapsed()

    def monitor_all(self):
        self.subscribe()

        retries = self._retries

        while True:
            rlist, _, _ = zmq.select([self._socket], [], [], timeout=self._timeout)
            if self._socket in rlist:
                if self._multipart:
                    sync_id, pickle_string = self._socket.recv_multipart()
                    sync_id = int.from_bytes(sync_id, byteorder='big')
                else:
                    sync_id = MessageIdentifier.ALL
                    pickle_string = self._socket.recv()

                msg = pickle.loads(pickle_string)
                if sync_id == MessageIdentifier.SYNC_TIMECODE:
                    msg = f"timestamp={msg[1]}, timecode={msg[0]}"
                    LOGGER.info(f"{MessageIdentifier(sync_id).name}, {msg}")
                elif sync_id == MessageIdentifier.SYNC_HK_PACKET:
                    msg = f"timestamp={msg[1]}, packet type={to_string(msg[0])}"
                    LOGGER.info(f"{MessageIdentifier(sync_id).name}, {msg}")
                elif sync_id == MessageIdentifier.NUM_CYCLES:
                    LOGGER.info(f"{MessageIdentifier(sync_id).name}, num_cycles={msg}")

                retries = self._retries  # reset the number of retries
            else:
                retries -= 1
                LOGGER.warning(f"Monitoring timeout, {retries} retries to go")
                if retries <= 0:
                    raise TimeoutError(f"DPUMonitoring timed out after {self._retries * self._timeout} seconds.")

    def wait_until_synced_num_cycles_is_zero(self):
        """
        Wait until the synced num_cycles turns zero, then return. The synced num_cycles is
        the num_cycles that is maintained by the DPU Processor and which is distributed by the
        DPU Processor on every 400ms pulse.

        Raises:
            A TimeoutError when no sync data was received from the monitoring socket after 30s.
        """
        self.unsubscribe_all()
        self.subscribe(MessageIdentifier.NUM_CYCLES)

        retries = self._retries

        while True:
            rlist, _, _ = zmq.select([self._socket], [], [], timeout=self._timeout)
            if self._socket in rlist:
                if self._multipart:
                    sync_id, pickle_string = self._socket.recv_multipart()
                    sync_id = int.from_bytes(sync_id, byteorder='big')
                else:
                    sync_id = MessageIdentifier.ALL
                    pickle_string = self._socket.recv()

                synced_num_cycles = pickle.loads(pickle_string)

                LOGGER.info(f"{MessageIdentifier(sync_id).name} = {synced_num_cycles}")

                if synced_num_cycles <= 0:
                    return

                retries = self._retries  # reset the number of retries
            else:
                retries -= 1
                LOGGER.warning(f"Monitoring timeout, {retries} retries to go")
                if retries <= 0:
                    raise TimeoutError(f"DPUMonitoring timed out after {self._retries * self._timeout} seconds.")

    def do(self, func: Callable, *args, **kwargs):
        return func(*args, **kwargs)

    def on_long_pulse_do(self, func: Callable, *args, **kwargs):
        """
        Connects to the monitoring socket of the DPU Processor and executes the given function
        when the frame_number == 0, i.e. right after a long pulse.

        Args:
            func (Callable): the function to synchronise
            *args: any arguments to pass to the function
            **kwargs: any keyword arguments to pass to the function

        Returns:
            The return value of the called function.

        Raises:
            A TimeoutError when no sync data was received from the monitoring socket after 30s.
        """
        return self.on_frame_number_do(0, func, *args, **kwargs)

    def on_frame_number_do(self, frame_number: int, func: Callable, *args, **kwargs):
        """
        Connects to the monitoring socket of the DPU Processor and executes the given function
        when the given frame_number is reached. This allows to send N-FEE commands right before the long pulse.

        Args:
            frame_number: the frame number on which to execute the function
            func (Callable): the function to synchronise
            *args: any arguments to pass to the function
            **kwargs: any keyword arguments to pass to the function

        Returns:
            The return value of the called function.

        Raises:
            A TimeoutError when no sync data was received from the monitoring socket after 30s.
        """
        self.unsubscribe_all()
        self.subscribe(MessageIdentifier.SYNC_HK_PACKET)

        retries = self._retries

        while True:
            rlist, _, _ = zmq.select([self._socket], [], [], timeout=self._timeout)
            if self._socket in rlist:
                if self._multipart:
                    sync_id, pickle_string = self._socket.recv_multipart()
                    sync_id = int.from_bytes(sync_id, byteorder='big')
                else:
                    sync_id = MessageIdentifier.ALL
                    pickle_string = self._socket.recv()
                status = pickle.loads(pickle_string)

                LOGGER.debug(f"{MessageIdentifier(sync_id).name}, {status[0]}")

                packet: DataPacketType = status[0]
                if packet and packet.frame_number == frame_number:
                    return func(*args, **kwargs)
            else:
                retries -= 1
                LOGGER.warning(f"Monitoring timeout, {retries} retries to go")
                if retries <= 0:
                    raise TimeoutError(f"DPUMonitoring timed out after {self._retries * self._timeout} seconds.")


@dataclass
class DPUInternals:

    # The number of readout cycles requested by the user. A cycle is the period between two long
    # pulses (400ms). When num_cycle == 0, the N-FEE will be instructed to go to dump mode, when
    # num_cycle < 0 nothing will be done.
    num_cycles: int

    # The expected last packet flags tell you if for a certain ccd side and packet a last packet
    # flag is expected. This is similar to saying if such a packet is to be expected from the N-FEE.
    expected_last_packet_flags: List[int]

    # DUMP mode is not a real N-FEE mode, but is defined in the DPU Processor to make sure the CCDs
    # will not saturate when we are not reading out image data. The conditions for a dump mode are
    # the register map flags 'digitise_en' being False and 'DG_high' being True.
    dump_mode: bool = False

    # The internal sync flag is set to True whenever the register map parameter 'sync_sel' is True.
    internal_sync: bool = False

    # This flag is set to True when the N-FEE shall be put into dump mode internal sync after
    # num_cycles becomes zero.
    dump_mode_int: bool = False

    # The current frame number. This value needs to be updated as soon as the housekeeping packet
    # is received.
    frame_number: int = -1

    # Enumeration with the information about E and F, based on the setup (camera-dependent)
    ccd_sides_enum: Enum = None

    # Enumeration with the sensor_sel
    sensor_sel_enum: Enum = None

    # Mapping of the CCD identifier to the binary representation (loaded from the Setup)
    ccd_id_to_bin: List[int] = None

    # The clear_error_flags shall be executed on every readout, i.e. every 200ms and 400ms pulse.
    clear_error_flags = False

    # The number of cycles that will be used for slicing the FITS files. This parameter is
    # saved in the HDF5 file upon reception.
    slicing_num_cycles = 0

    # When in internal sync the ccd_readout_order is not used like in external sync mode.
    # Each readout is done on the same CCD, i.e. the first CCD number in the ccd_readout_order list.
    # Therefore, we will rotate this list on each readout in internal sync dump mode to guarantee
    # each CCD is cleared out.

    # Initialise cycling of CCDs in internal sync dump mode to the default CCD numbering.
    current_ccd_readout_order = CCD_NUMBERS

    # The cycle_count goes from [0 -> 3] to make sure that, during internal sync dump mode, we have cleared out
    # all four CCDs. A clear-out cycle can only be interrupted when cycle_count == 0, at that time all commands
    # on the queue will be executed.
    cycle_count = 0

    def reset_int_sync_dump_mode(self, ccd_numbers: list = None):
        """
        Resets the cycle_count to zero (0) and the current ccd_readout_order to the given ccd_numbers.
        When ccd_numbers is None the default CCD readout order will be used, i.e. CCD_NUMBERS, [1,2,3,4].

        Args:
            ccd_numbers: a list of four CCD numbers going from 1 to 4.

        """
        self.current_ccd_readout_order = ccd_numbers or CCD_NUMBERS
        self.cycle_count = 0

    def int_sync_cycle_dump_mode(self):
        """Returns True if we are in internal sync dump mode."""
        return self.internal_sync and self.dump_mode and self.num_cycles < 0

    def is_start_of_cycle(self):
        """
        Returns True if in the first readout in this cycle, i.e. frame number is 0.
        """

        return self.frame_number == 0

    def is_end_of_cycle(self):
        """
        Returns True if in the last readout in this cycle.
        Note that, when in internal sync mode, this method always returns True.
        """
        return True if self.internal_sync else self.frame_number == 3

    def is_400ms_pulse(self):
        return self.frame_number == 0

    def is_200ms_pulse(self):
        return self.frame_number in [1, 2, 3]

    def update(self, n_fee_state: NFEEState.StateTuple):
        self.dump_mode = n_fee_state.ccd_mode_config == n_fee_mode.FULL_IMAGE_MODE and not bool(n_fee_state.digitise_en)
        self.internal_sync = bool(n_fee_state.sync_sel)
        self.expected_last_packet_flags = create_expected_last_packet_flags(n_fee_state, self.sensor_sel_enum)


class DPUProcessor(multiprocessing.Process):
    """
    The DPU Processor handles all interactions with the FEE. It reads the packets from the FEE
    within the readout time frame, and sends commands to the FEE through the RMAP protocol.

    The commands are read from a commanding queue which is shared between the DPU Processor and
    the DPU Controller. Any response from the FEE is put on the response queue which is also
    shared between the processor and the controller.

    The transport mechanism that is used to read and write SpaceWire packets is abstracted into a
    SpaceWireInterface. That allows us to interact with the FEE through different hardware
    channels, e.g. a SpaceWire interface (DSI) or a ZeroMQ DEALER-DEALER protocol for
    communication with the FEE Simulator.
    """

    def __init__(
        self,
        transport: SpaceWireInterface,
        priority_queue: multiprocessing.Queue,
        command_queue: multiprocessing.Queue,
        response_queue: multiprocessing.Queue,
    ):

        super().__init__()

        self._transport = transport
        self._priority_q = priority_queue
        self._command_q = command_queue
        self._response_q = response_queue
        self.register_map = RegisterMap("N-FEE")
        self._quit_event = multiprocessing.Event()

        # These will be properly initialized when the register map is read from the N-FEE

        self._n_fee_state = NFEEState()


    def run(self):

        setup = GlobalState.setup

        self._dpu_internals = DPUInternals(
            num_cycles=-1,
            expected_last_packet_flags=[False, False, False, False],
            dump_mode=False,
            internal_sync=False,
            frame_number=-1,
            ccd_sides_enum=setup.camera.fee.ccd_sides.enum,
            sensor_sel_enum=setup.camera.fee.sensor_sel.enum,
            ccd_id_to_bin=setup.camera.fee.ccd_numbering.CCD_ID_TO_BIN,
        )

        # The DPU Processor runs in a different process and since ZeroMQ Sockets are not
        # thread/process safe, we have to recreate the ZeroMQHandler attached to the egse.logger
        # in this process.
        import egse.logger
        egse.logger.replace_zmq_handler()

        LOGGER.info("DPU Processor started.")

        self._killer = SignalCatcher()

        # Setup a SpaceWire connection with the FEE (Simulator) and
        # open a Storage proxy to save all the data packets.

        origin_spw_data = N_FEE_SETTINGS.ORIGIN_SPW_DATA
        origin_spw_data_type = DATA_TYPE[N_FEE_SETTINGS.ORIGIN_SPW_DATA_TYPE]

        ctx: zmq.Context = zmq.Context().instance()

        # Setup monitoring socket

        mon_sock: zmq.Socket = ctx.socket(zmq.PUB)
        endpoint = bind_address("tcp", DPU_PROCESSOR_SETTINGS.MONITORING_PORT)
        mon_sock.bind(endpoint)
        LOGGER.info(f"DPU Processor sending monitoring sync signals to {endpoint}.")

        # Setup data distribution socket

        dist_sock: zmq.Socket = ctx.socket(zmq.PUB)
        endpoint = bind_address("tcp", DPU_PROCESSOR_SETTINGS.DATA_DISTRIBUTION_PORT)
        dist_sock.setsockopt(zmq.SNDHWM, 0)  # never block on sending msg
        dist_sock.bind(endpoint)

        LOGGER.info(f"DPU Processor sending SpW data to {endpoint}.")

        with self._transport, StorageProxy() as storage, ConfigurationManagerProxy() as cm:
            LOGGER.info("SpaceWire Transport has been connected.")
            self._transport.configure()
            LOGGER.info("SpaceWire Transport has been configured.")

            LOGGER.info(f"Register {origin_spw_data} to Storage")
            register_to_storage_manager(storage, origin_spw_data)

            # Before going into the wile-loop, read the full register from the N-FEE and initialise
            # the register map.

            try:
                self.initialise_register_map()
                save_register_map(self.register_map, storage, origin_spw_data, dist_sock)
                save_format_version(storage, origin_spw_data)
                save_obsid(storage, origin_spw_data, cm.get_obsid().return_code)
            except Abort:
                LOGGER.warning("The DPU Processor is aborting....")
                unregister_from_storage_manager(storage, origin_spw_data)
                LOGGER.info(f"The DPU Processor unregistered {origin_spw_data} from the Storage.")
                return
            except Exception as exc:
                LOGGER.error(exc, exc_info=exc)

            # Initialise the N-FEE state from the register map

            self._n_fee_state.update_at_400ms(self.register_map)

            # Initialise the DPU internals from the N-FEE State

            self._dpu_internals.update(self._n_fee_state.get_state())

            LOGGER.debug(f"{self._dpu_internals.dump_mode=}")
            LOGGER.debug(f"{self._dpu_internals.internal_sync=}")
            LOGGER.debug(f"{self._dpu_internals.expected_last_packet_flags=}")

            # Initialise the data attributes, they will be added as attributes to the data group
            # in the HDF5 file.

            data_attr = self._n_fee_state.get_state()._asdict()

            # Initialise the start_time. This is needed, because when a NoTimeCodeError occurs
            # the variable will not be initialised resulting in a critical error.

            start_time = time.perf_counter()

            try:
                LOGGER.info("Going into the while True loop...")
                while True:

                    try:
                        # First two packets are a Timecode and a HK packet  ------------------------

                        tc_packet, timestamp, start_time = read_timecode(self._transport)

                        hk_packet, timestamp = read_hk_packet(self._transport)

                        self._dpu_internals.frame_number = hk_packet.type.frame_number
                        self._dpu_internals.clear_error_flags = True

                        # Create a new HDF5 file for each readout cycle ----------------------------

                        if self._dpu_internals.is_start_of_cycle():
                            with Timer("Creating a new data file"):
                                new_spw_data_file(storage, self.register_map, origin_spw_data,
                                                  origin_spw_data_type, mon_sock, dist_sock)
                                save_obsid(storage, origin_spw_data, cm.get_obsid().return_code)
                                save_num_cycles(storage, origin_spw_data, self._dpu_internals.num_cycles)

                        # Update the N-FEE state (FPGA) --------------------------------------------

                        if self._dpu_internals.is_400ms_pulse():
                            self._n_fee_state.update_at_400ms(self.register_map)
                        elif self._dpu_internals.is_200ms_pulse():
                            self._n_fee_state.update_at_200ms(self.register_map)
                        else:
                            pass  # we are entering the loop for the first time

                        # Update the DPU internals from the N-FEE state

                        self._dpu_internals.update(self._n_fee_state.get_state())

                        # Process and save the timecode and HK packet ------------------------------

                        process_timecode(tc_packet, timestamp, storage, origin_spw_data,
                                         self._dpu_internals.frame_number, mon_sock, dist_sock)

                        process_hk_packet(hk_packet, timestamp, storage, origin_spw_data,
                                          self._dpu_internals.frame_number, mon_sock, dist_sock)

                        process_high_priority_commands(self._priority_q, self._response_q,
                                                       self._n_fee_state.get_state(),
                                                       self._dpu_internals, self.register_map)

                        # On any new readout cycle (400ms pulse), update the state and the internals

                        # FIXME: Why is this test done here and not at the end of the while loop
                        #        when all data has been read?

                        if self._dpu_internals.is_400ms_pulse():

                            pickle_string = pickle.dumps(self._dpu_internals.num_cycles)
                            msg_id = MessageIdentifier.NUM_CYCLES.to_bytes(1, 'big')
                            num_cycles_msg = [msg_id, pickle_string]
                            dist_sock.send_multipart(num_cycles_msg)
                            mon_sock.send_multipart(num_cycles_msg)

                            # decrement num_cycles, this can go negative which is interpreted as
                            # not doing anything...

                            self._dpu_internals.num_cycles -= 1  # check issue #917 before changing this line

                            LOGGER.debug(
                                f"HK: frame number={hk_packet.type.frame_number}, dump mode={self._dpu_internals.dump_mode}, num_cycles={self._dpu_internals.num_cycles}"
                            )

                            LOGGER.debug(
                                f"FEE mode in register map: {n_fee_mode(self.register_map['ccd_mode_config']).name}"
                            )

                            save_slicing_parameter(storage, origin_spw_data, self._dpu_internals.slicing_num_cycles)

                        if self._dpu_internals.is_end_of_cycle():

                            # When we are at the end of our requested num_cycles, go to DUMP mode

                            # FIXME: review if this is the right place and if the dump command will
                            #        be executed at the right moment, e.g. are there no commands on
                            #        the queue anymore?

                            if self._dpu_internals.num_cycles == 0:
                                if self._dpu_internals.dump_mode_int:
                                    self._dpu_internals.reset_int_sync_dump_mode()
                                    dump_mode_command = command_set_dump_mode_int_sync
                                else:
                                    dump_mode_command = command_set_dump_mode
                                self._command_q.put((dump_mode_command, [], {'response': False}))

                        # Then we might get data packets depending on the FEE mode -----------------

                        mode = hk_packet.type.mode
                        LOGGER.debug(f"FEE mode in HK packet: {n_fee_mode(mode).name}")

                        data_attr = update_data_attributes(data_attr, self._n_fee_state.get_state())

                        with Timer("Read and process data packets"):
                            read_and_process_data_packets(
                                self._transport, storage, origin_spw_data, start_time, mode,
                                self.register_map, data_attr, self._dpu_internals, dist_sock)

                        # Read HK packet from N-FEE memory map
                        # see #2478 [https://github.com/IvS-KULeuven/plato-common-egse/issues/2478]

                        time.sleep(0.012)  # add 12ms to make sure HK data has been updated on the N-FEE

                        with Timer("Read and process updated HK data"):
                            hk_data, timestamp = read_updated_hk_data(self._transport)
                            process_updated_hk_data(hk_data, timestamp, storage, origin_spw_data,
                                                    self._dpu_internals.frame_number, mon_sock, dist_sock)

                        if self._dpu_internals.int_sync_cycle_dump_mode():
                            LOGGER.warning("Cycling CCD readout in internal sync")

                            # When we are in internal sync and dump mode, we need to cycle through the four CCDs, and
                            # we need an atomic block of four clear outs.

                            internals = self._dpu_internals
                            internals.current_ccd_readout_order = rotate_list(internals.current_ccd_readout_order, 1)
                            internals.cycle_count += 1
                            ccd_readout_order = _get_ccd_readout_order(
                                internals.current_ccd_readout_order, internals.ccd_id_to_bin
                            )
                            # LOGGER.info(f"{internals.current_ccd_readout_order = }, {ccd_readout_order = }, "
                            #              f"{internals.cycle_count = }")
                            _ = command_set_readout_order(self._transport, self.register_map, ccd_readout_order)

                            # We agreed to have atomic blocks of 4 clear-outs such that all four CCDs would always
                            # be dumped. So, whenever we are within one such atomic block, don't execute any DPU
                            # commands.

                            if internals.cycle_count < 4:
                                LOGGER.debug(
                                    f"[1] {internals.current_ccd_readout_order = }, {ccd_readout_order = }, "
                                    f"{internals.cycle_count = }")
                            else:
                                internals.cycle_count = 0
                                LOGGER.debug(
                                    f"[2] {internals.current_ccd_readout_order = }, {ccd_readout_order = }, "
                                    f"{internals.cycle_count = }")

                    except NoBytesReceivedError as exc:
                        # LOGGER.debug(f"No bytes received: {exc}")
                        pass
                    except NoTimeCodeError as exc:
                        LOGGER.warning("Reading the next timecode packet failed.")
                        LOGGER.debug("Traceback for NoTimecodeError:", exc_info=exc)
                    except NoHousekeepingPacketError as exc:
                        LOGGER.warning("Reading the next housekeeping packet failed.")
                        LOGGER.debug("Traceback for NoHousekeepingPacketError:", exc_info=exc)
                    except NoDataPacketError as exc:
                        LOGGER.warning("Reading the next data packet failed.")
                        LOGGER.debug("Traceback for NoDataPacketError:", exc_info=exc)
                    except TimecodeTimeoutError as exc:
                        # LOGGER.debug("Waiting for the next timecode.")
                        pass
                    except TimeExceededError as exc:
                        LOGGER.warning(
                            "Time to retrieve data packets in this readout cycle exceeded "
                            "4.0 seconds."
                        )
                        LOGGER.debug("Traceback for TimeExceededError:", exc_info=exc)
                    # FIXME:
                    #   same here as above, make sure the DPU Processor doesn't crash. This last
                    #   catching also means that Commands on the Queue will still be executed if
                    #   there is an error. What needs to be checked here is that the Command should
                    #   probably be send in the 'save zone' between 4.0s and 6.25s.
                    except Exception as exc:
                        LOGGER.error(exc, exc_info=True)
                        traceback.print_exc()

                    # LOGGER.info(
                    #     f"Time past after reading all packets from FEE:"
                    #     f" {time.perf_counter() - start_time:.3f}s"
                    # )

                    # Process high priority commands

                    process_high_priority_commands(
                        self._priority_q, self._response_q,
                        self._n_fee_state.get_state(), self._dpu_internals, self.register_map)

                    # When we are in internal sync dump mode, we need atomic blocks of 4 readouts such that all four
                    # CCDs will be cleared out. The cycle count goes from [0 -> 3] so, we only send commands when
                    # cycle count == 0.
                    # LOGGER.debug(f"{self._dpu_internals.cycle_count = }")
                    if self._dpu_internals.int_sync_cycle_dump_mode() and self._dpu_internals.cycle_count != 0:
                        continue

                    # Then, we might want to send some RMAP commands -------------------------------

                    # When we are in the 2s RMAP window, send the commands.
                    # Waiting till 4s have passed is apparently not needed, commands can be sent as
                    # soon as no packets will be received anymore, even if the time elapsed is
                    # less than 4s.
                    # But the following two lines might be uncommented for testing purposes.

                    # while time.perf_counter() < start_time + 4.0:
                    #     time.sleep(0.1)

                    try:
                        send_commands_to_n_fee(
                            self._transport, storage, origin_spw_data,
                            self.register_map, self._command_q, self._response_q,
                            self._dpu_internals
                        )
                    except NFEECommandError as exc:
                        # Error is already logged in the send_commands_to_n_fee() function
                        pass

                    # LOGGER.debug(
                    #     f"Time past after sending commands to FEE:"
                    #     f" {time.perf_counter() - start_time:.3f}s"
                    # )

                    # Terminate the DPU Processor when the quit event flag has been set by the
                    # commanding protocol.

                    if self._quit_event.is_set() or self._killer.term_signal_received:
                        LOGGER.info("Quit event is set, terminating..")
                        break

            except (Exception,) as exc:
                LOGGER.critical(
                    "A fatal error occurred in the DPU Processor, needs to be restarted!",
                    exc_info=exc
                )
                # re-raise the exception such that it will bubble up at a higher level.
                raise
            finally:
                LOGGER.debug("Unregistering from Storage Manager.")
                unregister_from_storage_manager(storage, origin_spw_data)

        mon_sock.close(linger=0)
        dist_sock.close(linger=0)
        # ctx.destroy()

    def quit(self):
        LOGGER.warning("Sending a Quit event to the DPU Processor.")
        self._quit_event.set()

    def initialise_register_map(self):

        # FIXME:
        #   The DPU Processor shall not crash, therefore we shall catch all Exceptions thrown.
        #   Log the exceptions as an error and continue here. It must be tested what the exact
        #   harm is when doing this and if we need some further action before proceeding.

        # The DPU Processor is only initialised properly after reading the full register from
        # the N-FEE. This can only be done within the time window we have for sending RMAP
        # commands. Therefore we need to make sure we are in a safe time window for sending
        # RMAP commands.

        LOGGER.info('Initialise Register Map from N-FEE')

        # First wait until a timecode is received

        while True:
            terminator, packet = self._transport.read_packet(timeout=200)
            if self._killer.term_signal_received:
                raise Abort("A SIGTERM signal was received for this process")
            if packet is None or len(packet) in (0, 1):
                continue
            if is_timecode(packet):
                break

        start_time = time.perf_counter()

        LOGGER.debug(f"Timecode received {packet=}")

        while time.perf_counter() < start_time + 4.2:
            terminator, packet = self._transport.read_packet(timeout=200)
            if packet is None:
                msg = f"time passed {time.perf_counter() - start_time:0.3f}"
            else:
                msg = packet[:10]
            LOGGER.debug(f"Discarding packet: {msg}")

        LOGGER.info(f"Time passed since last timecode {time.perf_counter() - start_time:0.3f}s")
        LOGGER.info(
            'In safe time window for sending RMAP command, getting full register..'
        )

        command_sync_register_map(self._transport, self.register_map)

        LOGGER.debug(self.register_map)


def save_register_map(
        reg_map: RegisterMap, storage: StorageProxy, origin: str, dist_socket: zmq.Socket):

    reg_memory_map = reg_map.get_memory_map_as_ndarray()

    LOGGER.debug("Saving register map")

    response = storage.save(
        {
            "origin": origin,
            "data": {
                "/register/": reg_memory_map
            }
        }
    )

    LOGGER.debug(f"Response from saving Register Map: {response}")

    pickle_string = pickle.dumps(reg_memory_map)
    msg_id = MessageIdentifier.N_FEE_REGISTER_MAP.to_bytes(1, 'big')
    dist_socket.send_multipart([msg_id, pickle_string])


def register_to_storage_manager(proxy: StorageProxy, origin: str):
    rc = proxy.new_registration(
        item={
            "origin": origin,
            "persistence_class": HDF5,
            "prep": {
                "mode": "w-",
            },
        },
        use_counter=True
    )
    LOGGER.info(f"{rc=!s}")
    if rc and not rc.successful:
        LOGGER.warning(f"Couldn't register to the Storage manager: {rc}")


def unregister_from_storage_manager(proxy: StorageProxy, origin: str):

    try:
        rc = proxy.unregister({"origin": origin})
        if not rc.successful:
            LOGGER.warning(f"Couldn't unregister from the Storage manager: {rc}")

    except ConnectionError as exc:
        LOGGER.warning(f"Couldn't connect to the Storage manager for de-registration: {exc}")


def new_spw_data_file(
        proxy: StorageProxy, reg_map: RegisterMap, origin: str, data_type: Type[PersistenceLayer],
        mon_socket: zmq.Socket, dist_socket: zmq.Socket
):
    """
    Open a new data file to store CCD data.

    Args:
        - proxy: Storage manager.
        - origin: the origin for which to create a new file
        - reg_map: Register map.
    """

    LOGGER.debug(f"Create a new data file for {origin} in the Storage")

    # prep = {
    #     "expected_last_packet_flags": get_expected_last_packet_flags(reg_map),
    # }
    #
    # for name in CRUCIAL_REGISTER_PARAMETERS:
    #     prep[name] = reg_map[name]

    item = {
        "origin": origin,
        "persistence_class": data_type,
        "prep": {},
    }

    # Retrieve the current filenames that will be available for processing as soon as the new
    # HDF5 file is registered and created by the storage manager. This should be done, of course,
    # before the new-registration call!

    hdf5_filenames = proxy.get_filenames(item={"origin": origin})

    response = proxy.new_registration(item=item, use_counter=True)

    LOGGER.debug(f"Response from new_registration: {response}")

    save_format_version(proxy, origin)

    # Save the Register Map that is used for the current readout cycle

    save_register_map(reg_map, proxy, origin, dist_socket)

    LOGGER.info(f"HDF5 files ready for processing: {hdf5_filenames=}")

    pickle_string = pickle.dumps(hdf5_filenames)
    msg_id = MessageIdentifier.HDF5_FILENAMES.to_bytes(1, 'big')
    mon_socket.send_multipart([msg_id, pickle_string])


def save_format_version(proxy: StorageProxy, origin: str):

    # 2.0 - introduced the format_version
    # 2.1 - Added obsid as a dataset to the HDF5 file
    # 2.2 - Multiple commands can now be saved under the same frame number
    # 2.3 - introduced /dpu/num_cycles attribute
    # 2.4 - introduced /dpu/slicing_num_cycles attribute
    # 2.5 - introduced /{frame number}/hk_data dataset

    major_version = 2
    minor_version = 5

    item_data = {
        "/versions/format_version/": "format version of HDF5 file",
        "/versions/format_version:ATTRS": [
            ("major_version", major_version),
            ("minor_version", minor_version)
        ]
    }
    item = {
        "origin": origin,
        "data": item_data,
    }
    response = proxy.save(item)
    LOGGER.debug(f"Response from saving format_version: {response}")


def save_obsid(proxy: StorageProxy, origin: str, obsid: ObservationIdentifier):

    item_data = {
        "/obsid": str(obsid),
    }
    item = {
        "origin": origin,
        "data": item_data,
    }
    response = proxy.save(item)
    LOGGER.debug(f"Response from saving OBSID: {response}")


def save_num_cycles(proxy: StorageProxy, origin: str, num_cycles: int):
    """Save the number of cycles to the storage. This will only save if num_cycles >= 0."""

    # Only save num_cycles >= 0, the DPU Processor understands when num_cycles is negative,
    # but for the HDF5 file we want to keep it clean and always have num_cycles >= 0.

    num_cycles = max(num_cycles, 0)

    item_data = {
        "/dpu/": "DPU specific parameters",
        "/dpu/:ATTRS": [
            ("num_cycles", num_cycles),
        ]
    }
    item = {
        "origin": origin,
        "data": item_data,
    }
    response = proxy.save(item)
    LOGGER.debug(f"Response from saving NUM_CYCLES: {response}")


def save_slicing_parameter(proxy: StorageProxy, origin: str, slicing_num_cycles: int):
    """Save the number of cycles to use for slicing to the storage."""

    item_data = {
        "/dpu/:ATTRS": [
            ("slicing_num_cycles", slicing_num_cycles),
        ]
    }
    item = {
        "origin": origin,
        "data": item_data,
    }
    response = proxy.save(item)
    LOGGER.debug(f"Response from saving SLICING_NUM_CYCLES: {response}")


def update_data_attributes(attr: dict, n_fee_state: NFEEState.StateTuple) -> Dict[str, Any]:
    """
    Collect parameter/value pairs that will be added to the data group as attributes.

    Args:
        attr (dict): the current attributes that need to be updated
        n_fee_state: the current state of the N-FEE

    Returns:
        Updated data attributes.
    """

    attr.update(n_fee_state._asdict())
    return attr


def read_timecode(transport: SpaceWireInterface) -> (TimecodePacket, str, float):
    """
    Reads the next Timecode packet from the N-FEE.

    Args:
        transport: the SpaceWire interfaces that is used for communication to the N-FEE

    Returns:
        The timecode and associated timestamp, and the approximate start time for this readout cycle.
    Raises:
        NoTimecodeError when the timecode could not be read.
    """
    terminator, packet = transport.read_packet(timeout=100)
    timestamp = format_datetime()

    if terminator is None and packet is None:
        raise TimecodeTimeoutError()

    # Start time taken as closely as possible to timecode reception, this start_time is
    # returned to be used in further functions called in the outer loop.

    start_time = time.perf_counter()
    # LOGGER.debug(f"Time set: {start_time}")

    bytes_received = len(packet)

    # The following check is to cope with loss of connection when either the
    # FEE simulator crashes or the connection dropped for some other reason.
    # We will receive one packet with 0 or 1 bytes.

    if bytes_received in {0, 1}:
        raise NoBytesReceivedError(f"{bytes_received} bytes received, lost connection to FEE?")

    if not is_timecode(packet):
        packet = SpaceWirePacket.create_packet(packet)
        raise NoTimeCodeError(f"Expected Timecode Packet, but got {packet.__class__.__name__}")

    tc_packet: TimecodePacket = SpaceWirePacket.create_packet(packet)

    LOGGER.info(f"Timecode received: {tc_packet.timecode}")

    return tc_packet, timestamp, start_time


def process_timecode(tc_packet: TimecodePacket, timestamp: str,
                     storage: StorageProxy, origin_spw_data: str, frame_number: int,
                     mon_socket: zmq.Socket, dist_socket: zmq.Socket):
    """
    Saves the timecode and associated timestamp for this frame. The timecode and timestamp
    are also published on the monitoring and data distribution message queue.

    Args:
        tc_packet: the timecode packet
        timestamp: a timestamp associated with the reception of the timecode
        frame_number: the current frame number
        storage: the proxy that is used to communicate with the Storage manager
        origin_spw_data: the registration identifier for the Storage manager, for the SpW data
        mon_socket: the ZeroMQ socket to which monitoring sync signals are sent
        dist_socket: the ZeroMQ socket to which SpW data is sent (for real-time view)

    Returns:
        Nothing.
    """
    LOGGER.debug(f"Saving timecode packet: {tc_packet.timecode=}, {frame_number=}")

    response = storage.save(
        {
            "origin": origin_spw_data,
            "data":
                {
                    f"/{frame_number}/timecode": tc_packet,
                    f"/{frame_number}/timecode:ATTRS": [("timestamp", timestamp)],
                }
        }
    )

    LOGGER.debug(f"Response from saving Timecode: {response}")

    pickle_string = pickle.dumps((tc_packet.timecode, timestamp))
    mon_socket.send_multipart([MessageIdentifier.SYNC_TIMECODE.to_bytes(1, "big"), pickle_string])
    dist_socket.send_multipart([MessageIdentifier.SYNC_TIMECODE.to_bytes(1, "big"), pickle_string])


def read_updated_hk_data(transport: SpaceWireInterface) -> (HousekeepingData, str):
    """
    Reads the memory map that contains the housekeeping information from the N-FEE.
    The memory map is returned as a HousekeepingData object.

    This is not the same as a housekeeping packet that is read from the N-FEE. For
    that refer to the function `read_hk_packet()`.

    Args:
        transport: the SpaceWire interfaces that is used for communication to the N-FEE

    Returns:
        The HK data packet and its associated timestamp as a string.
    """
    timestamp = format_datetime()

    data = command_get_hk_information(transport, None, 0x000_0700, 0x90)
    hk_data = HousekeepingData(data)

    msg = f"Updated housekeeping retrieved... {hk_data.frame_counter = }, {hk_data.timecode = }"
    if hk_data.error_flags:
        msg += f", error_flags = 0b{hk_data.error_flags:032b}"
        LOGGER.warning(msg)
    else:
        LOGGER.info(msg)

    return hk_data, timestamp

def process_updated_hk_data(hk_data: HousekeepingData, timestamp: str, storage: StorageProxy,
                            origin: str, frame_number: int,
                            mon_socket: zmq.Socket, dist_socket: zmq.Socket):
    """
    Saves the housekeeping data and associated timestamp for this frame. The data and timestamp
    are also published on the monitoring message queue.

    Args:
        hk_data: the HousekeepingData object
        timestamp: the timestamp associated with the reception of this data
        frame_number: the current frame number
        storage: the proxy that is used to communicate with the Storage manager
        origin: the registration identifier for the Storage manager
        mon_socket: the ZeroMQ socket to which monitoring sync signals are sent
        dist_socket: the ZeroMQ socket to which SpW data is sent (for real-time view)

    Returns:
        Nothing.
    """
    LOGGER.debug(f"Saving updated Housekeeping data: {hk_data.frame_counter = }, {hk_data.timecode = }, {hk_data.frame_number = }")

    response = storage.save(
        {
            "origin": origin,
            "data":
                {
                    f"/{frame_number}/hk_data": hk_data,
                    f"/{frame_number}/hk_data:ATTRS": [("timestamp", timestamp)],
                }
        }
    )

    LOGGER.debug(f"Response from saving updated Housekeeping data: {response}")

    pickle_string = pickle.dumps((hk_data.error_flags, hk_data.frame_counter, timestamp))
    mon_socket.send_multipart([MessageIdentifier.SYNC_ERROR_FLAGS.to_bytes(1, "big"), pickle_string])

    msg_id = MessageIdentifier.SYNC_HK_DATA.to_bytes(1, 'big')

    pickle_string = pickle.dumps((hk_data, timestamp))
    dist_socket.send_multipart([msg_id, pickle_string])


def read_hk_packet(transport: SpaceWireInterface) -> (HousekeepingPacket, str):
    """
    Read the next Housekeeping Packet from the N-FEE.

    Args:
        transport: the SpaceWire interfaces that is used for communication to the N-FEE
    Raises:
        NoHousekeepingPacketError when the next packet is not a `HousekeepingPacket`.
    Returns:
        the received housekeeping packet and the timestamp.
    """
    terminator, packet = transport.read_packet()
    timestamp = format_datetime()

    if not is_hk_data_packet(packet):
        packet = SpaceWirePacket.create_packet(packet)
        raise NoHousekeepingPacketError(
            f"Expected a Housekeeping packet, but got {packet.__class__.__name__}")

    hk_packet: HousekeepingPacket = SpaceWirePacket.create_packet(packet)

    LOGGER.info(f"Housekeeping Packet received: {hk_packet.type!s}")

    return hk_packet, timestamp


def process_hk_packet(hk_packet: HousekeepingPacket, timestamp: str,
                      storage: StorageProxy, origin: str, frame_number: int,
                      mon_socket: zmq.Socket, dist_socket: zmq.Socket):
    """
    Saves the housekeeping packet and associated timestamp for this frame. The data and timestamp
    are also published on the monitoring and data distribution message queue.

    Args:
        hk_packet: the HousekeepingPacket
        timestamp: the timestamp associated with the reception of this packet
        frame_number: the current frame number
        storage: the proxy that is used to communicate with the Storage manager
        origin: the registration identifier for the Storage manager
        mon_socket: the ZeroMQ socket to which monitoring sync signals are sent
        dist_socket: the ZeroMQ socket to which SpW data is sent (for real-time view)

    Returns:
        Nothing.
    """

    LOGGER.debug(f"Saving Housekeeping packet: {hk_packet.type!s}, "
                f"frame counter={hk_packet.frame_counter}, "
                f"sequence counter={hk_packet.sequence_counter}")

    response = storage.save(
        {
            "origin": origin,
            "data":
                {
                    f"/{frame_number}/hk": hk_packet,
                }
        }
    )

    LOGGER.debug(f"Response from saving HK Packet: {response}")

    msg_id = MessageIdentifier.SYNC_HK_PACKET.to_bytes(1, 'big')

    pickle_string = pickle.dumps((hk_packet.type, timestamp))
    mon_socket.send_multipart([msg_id, pickle_string])

    pickle_string = pickle.dumps((hk_packet, timestamp))
    dist_socket.send_multipart([msg_id, pickle_string])


def read_and_process_data_packets(
        transport: SpaceWireInterface, storage: StorageProxy, origin_spw_data: str,
        start_time: float, mode: int, register_map: RegisterMap, data_attr: dict,
        internals: DPUInternals, dist_socket: zmq.Socket
):
    """
    Read the data packets when they are available depending on the mode.

    Args:
        transport: the SpaceWire interfaces that is used for communication to the N-FEE
        storage: the proxy that is used to communicate with the Storage manager
        origin_spw_data: the registration identifier for the Storage manager
        start_time: the approximate time that the readout cycle started
        mode: FPGA mode
        register_map: the DPU Processor's copy of the N-FEE register map
        data_attr: register values to be saved with the data
        internals: use for expected_last_packet_flags (these will be updated within this function)
        dist_socket: the ZeroMQ socket to which SpW data is sent (for real-time view)

    Raises:
        NoDataPacketError when the expected packet is not a data packet.
    """

    if internals.dump_mode or mode not in (
            n_fee_mode.FULL_IMAGE_PATTERN_MODE,
            n_fee_mode.WINDOWING_PATTERN_MODE,
            n_fee_mode.FULL_IMAGE_MODE,
    ):
        return

    timestamp = format_datetime()
    msg_id = MessageIdentifier.SYNC_DATA_PACKET.to_bytes(1, 'big')

    data_count = 0

    # Initialise the flags that determine if the last packet has arrived for
    # all expected data packets.

    actual_last_packet_flags = [False, False, False, False]

    # Read the data, until all the expected last packet bits are set.
    # This should be within next 4 seconds.

    LOGGER.info("Reading data packets....")

    terminator, packet = transport.read_packet()

    data_packet: DataPacket = SpaceWirePacket.create_packet(packet)

    if (not isinstance(data_packet, DataDataPacket) and
            not isinstance(data_packet, OverscanDataPacket)):
        LOGGER.critical(f"DataPacket expected, got {data_packet}")
        raise NoDataPacketError(f"Expected a data packet, but got {data_packet.__class__.__name__}")

    # LOGGER.debug(f"Got data packet of length {len(packet)}")

    LOGGER.debug(f"Saving data packets: {data_packet.type!s}")

    item_data = {f"/{internals.frame_number}/data/{data_count}": data_packet}

    attrs = [(k, v) for k, v in data_attr.items()]
    item_data.update({f"/{internals.frame_number}/data:ATTRS": attrs})

    response = storage.save(
        {
            "origin": origin_spw_data,
            "data": item_data
        }
    )

    if isinstance(response, Exception):
        LOGGER.warning(f"Response from saving data packet: {response}")

    pickle_string = pickle.dumps((data_packet, timestamp))
    dist_socket.send_multipart([msg_id, pickle_string])

    data_count += 1

    # Update the expected flags with the possibly new register values, but only
    # after we had the 400ms pulse which updates the settings from the
    # register map. The test is needed because the register here on the DPU
    # processing side can be updated also on 200ms sync pulses, but the changes
    # only take effect on the 400ms pulse in the N-FEE.

    if data_packet.type.frame_number == 0:
        internals.expected_last_packet_flags = get_expected_last_packet_flags(register_map, internals.sensor_sel_enum)
        LOGGER.debug(f"{internals.expected_last_packet_flags=}")

    idx = get_index_for_last_packet_flags(data_packet.type.packet_type, data_packet.type.ccd_side,
                                          internals.ccd_sides_enum)
    # LOGGER.debug(f"{idx=}, {data_packet.type.packet_type=}, {data_packet.type.ccd_side=}")
    actual_last_packet_flags[idx] = data_packet.type.last_packet

    while not got_all_last_packets(
            actual_last_packet_flags, internals.expected_last_packet_flags):

        terminator, packet = transport.read_packet()
        data_packet: DataPacket = SpaceWirePacket.create_packet(packet)

        if (not isinstance(data_packet, DataDataPacket) and
                not isinstance(data_packet, OverscanDataPacket)):
            LOGGER.critical(f"DataPacket expected, got {data_packet}")
            raise NoDataPacketError(
                f"Expected a data packet, but got {data_packet.__class__.__name__}")

        # LOGGER.debug(f"Saving data packet: {data_packet.type!s}")

        response = storage.save(
            {
                "origin": origin_spw_data,
                "data":
                    {
                        f"/{internals.frame_number}/data/{data_count}": data_packet,
                    }
            }
        )

        if isinstance(response, Exception):
            LOGGER.warning(f"Response from saving data packet: {response}")

        pickle_string = pickle.dumps((data_packet, timestamp))
        dist_socket.send_multipart([msg_id, pickle_string])

        data_count += 1

        #LOGGER.debug(f"Got data packet of length {len(packet)}")
        #LOGGER.debug(f"DataPacketHeader: {data_packet.header.type_as_object}")

        idx = get_index_for_last_packet_flags(data_packet.type.packet_type, data_packet.type.ccd_side,
                                              internals.ccd_sides_enum)
        actual_last_packet_flags[idx] = data_packet.type.last_packet

        # Sending data packets shall not take more than 4 seconds, and if we
        # wait longer than 6.25 seconds, all RMAP commands that we send will be
        # discarded.

        if time.perf_counter() > start_time + 5.25:
            raise TimeExceededError(
                "Retrieving data packets exceeded the allowed 4.0 seconds, "
                "breaking out of the data loop."
            )


def send_commands_to_n_fee(
        transport: SpaceWireInterface, storage: StorageProxy, origin: str,
        register_map: RegisterMap,
        command_q: multiprocessing.Queue,
        response_q: multiprocessing.Queue,
        internals: DPUInternals
):
    """
    Send RMAP commands to the N-FEE. The commands are read from the command queue that is shared
    with the DPU Controller. The response from the N-FEE is put on the response queue, also shared
    with the DPU Controller.

    !!! note
        The current implementation allows only one command from the command queue per sync cycle.

    Args:
        transport: the SpaceWire interfaces that is used for communication to the N-FEE
        storage: the proxy that is used to communicate with the Storage manager
        origin: the registration identifier for the Storage manager
        register_map: the DPU Processor's copy of the N-FEE register map
        command_q: the command queue
        response_q: the response queue
        internals: for some commands we need access to DPUInternals, e.g. num_cycles, dump_mode_int

    Raises:
        Exceptions are caught and put on the response queue.
    """

    if internals.clear_error_flags:
        LOGGER.debug("Set the clear-error-flags register parameter.")
        try:
            _ = command_set_clear_error_flags(transport, register_map)
        except ValueError as exc:
            LOGGER.error("The clear-error-flags register parameter could not be set due to a ValueError.", exc_info=exc)

        internals.clear_error_flags = False

    command = response = None
    kwargs = {}
    try:
        (command, args, kwargs) = command_q.get_nowait()

        # When num_cycles is not specified, don't even set it to 0, the N-FEE will stay in the
        # current configuration until commanded otherwise.

        if num_cycles := kwargs.get("num_cycles"):
            LOGGER.debug(f"Set internals.num_cycle to {num_cycles}.")
            internals.num_cycles = num_cycles

        # Some commanding requires to go back into internal sync dump mode

        dump_mode_int = kwargs.get("dump_mode_int", False)
        LOGGER.debug(f"Set internals.dump_mode_int to {dump_mode_int}.")
        internals.dump_mode_int = dump_mode_int

        LOGGER.debug(f"Executing Command: {command.__name__}, {args=}")
        response = command(transport, register_map, *args)
        LOGGER.debug(f"Command executed: {command.__name__}, {args=}, {response=}")

        LOGGER.debug(f"Saving command: {command.__name__}, {args=}")

        response_save = storage.save({
            "origin": origin,
            "data": {
                f"/{internals.frame_number}/command/": f"{command.__name__}, {args=}, {kwargs=}",
            }
        })

        LOGGER.debug(f"Response from saving Command: {response_save}")

    except queue.Empty:
        pass
    except (Exception,) as exc:
        LOGGER.error(
            f"Exception during command execution in DPU Processor: "
            f"{command}", exc_info=exc
        )
        raise NFEECommandError(
            f"An exception occurred sending the command {command} "
            f"to the N-FEE.") from exc
    finally:
        if command is not None and kwargs.get('response', True):
            response_q.put((command, response))


def process_high_priority_commands(
        priority_q: multiprocessing.Queue,
        response_q: multiprocessing.Queue,
        n_fee_state: tuple, dpu_internals: DPUInternals, reg_map: RegisterMap):
    """
    Execute high priority commands from the DPU Control Server /  Controller. The `n_fee_state` and
    the `dpu_internals` tuples are passed to the high priority commands before any other arguments
    that were passed on the command queue.

    Args:
        priority_q: the command queue with priority
        response_q: the response queue
        n_fee_state: a namedtuple containing the current state of the N-FEE
        dpu_internals: the internal settings of the DPU might be requested or set
            by a high priority command
        reg_map: the current register map from the DPU Processor
    """

    command = response = None
    try:
        (command, args) = priority_q.get_nowait()
        response = command(n_fee_state, dpu_internals, reg_map, *args)
        LOGGER.debug(f"Command executed: {command.__name__}, {args=}, {response=}")
    except queue.Empty:
        pass
    except (Exception,) as exc:
        LOGGER.error(
            f"Exception during command execution in DPU Processor: "
            f"{command}", exc_info=exc
        )
        raise NFEECommandError(
            f"An exception occurred sending the command {command} "
            f"to the N-FEE.") from exc
    finally:
        if command is not None:
            response_q.put((command, response))


def get_index_for_last_packet_flags(packet_type: int, ccd_side: int, ccd_sides_enum):
    """
    Returns the index into the last packet flags list.

    The last packet flags list is organised as follows:

        * index 0: data packet, E-side
        * index 1: data packet, F-side
        * index 2: overscan data packet, E-side
        * index:3: overscan data packet, F-side

    Args:
        packet_type: the packet type as read from the packet header [datapacket=0, overscan=1,
            housekeeping=2]
        ccd_side: the ccd side as read from the packet header
        ccd_sides_enum: Enumeration with information on E and F

    Returns:
        The index for the last packet flags list.
    """
    if ccd_side == ccd_sides_enum.E_SIDE.value:
        return packet_type * 2
    else:
        return packet_type * 2 + 1


def get_expected_last_packet_flags(register_map: Mapping, sensor_sel_enum: Enum) -> List[bool]:
    """
    Build and returns a list of flags that define if a last packet is expected.

    A last packet flag is expected for normal data packets and overscan data
    packets. For both these data packets we can expect E-side and F-side packets
    with a last packet flag. That brings the total expected flags to four. This
    function examines the register values `v_start`, `v_end`, and `sensor_sel`.

    The flags are ordered as follows:

    1. data packet and E-side
    2. data packet and F-side
    3. overscan data packet and E-side
    4. overscan data packet and F-side

    Housekeeping packets are not considered here.

    For comparing the flags with the actual data,
    use the function `got_all_last_packets(actual, expected)`.

    Args:
        register_map: the current Register map for the N-FEE
        sensor_sel_enum:
    Returns:
        a list of flags.
    """
    sensor_sel_from_register = register_map["sensor_sel"]

    e_side = bool(sensor_sel_from_register & sensor_sel_enum.E_SIDE)
    f_side = bool(sensor_sel_from_register & sensor_sel_enum.F_SIDE)
    v_start = register_map["v_start"]
    v_end = register_map["v_end"]
    data_packet = v_start < 4510
    overscan_packet = v_end > 4509

    return [
        data_packet and e_side,
        data_packet and f_side,
        overscan_packet and e_side,
        overscan_packet and f_side
    ]

def create_expected_last_packet_flags(n_fee_state: NFEEState.StateTuple, sensor_sel_enum: Enum):
    """
    Build and returns a list of flags that define if a last packet is expected.

    A last packet flag is expected for normal data packets and overscan data
    packets. For both these data packets we can expect E-side and F-side packets
    with a last packet flag. That brings the total expected flags to four. This
    function examines the register values `v_start`, `v_end`, and `sensor_sel`.

    The flags are ordered as follows:

    1. data packet and E-side
    2. data packet and F-side
    3. overscan data packet and E-side
    4. overscan data packet and F-side

    Housekeeping packets are not considered here.

    For comparing the flags with the actual data,
    use the function `got_all_last_packets(actual, expected)`.

    Args:
        n_fee_state: a namedtuple containing the current N-FEE State
        sensor_sel_enum: Enumeration with the sensor_sel
    Returns:
        a list of flags.
    """
    sensor_sel_from_nfee_state = n_fee_state.sensor_sel

    v_start = n_fee_state.v_start
    v_end = n_fee_state.v_end

    e_side = bool(sensor_sel_from_nfee_state & sensor_sel_enum.E_SIDE)
    f_side = bool(sensor_sel_from_nfee_state & sensor_sel_enum.F_SIDE)
    data_packet = v_start < 4510
    overscan_packet = v_end > 4509

    return [
        data_packet and e_side,
        data_packet and f_side,
        overscan_packet and e_side,
        overscan_packet and f_side
    ]


def got_all_last_packets(actual, expected):
    """
    Returns True if all the expected last packet flags have been seen.

    Args:
        actual: the flags that have been seen so far
        expected: the expected flags

    Returns:
        True if 'actual' matches 'expected', False otherwise.
    """
    rc = all([x == y for (x, y) in zip(actual, expected)])
    # LOGGER.info(f"{expected=}, {actual=}, {rc=}")
    return rc


if __name__ == "__main__":

    def do_something(idx):
        LOGGER.info(f"Hello! {idx=}")

    moni = DPUMonitoring()
    moni.connect()

    for idx in range(3):
        # moni.on_long_pulse_do(do_something, idx)

        # timecode, timestamp = moni.wait_for_timecode()
        # LOGGER.info(f"{timecode=}, {timestamp=}")

        filenames = moni.wait_for_hdf5_filename()
        LOGGER.info(f"{filenames=}")

    moni.disconnect()
