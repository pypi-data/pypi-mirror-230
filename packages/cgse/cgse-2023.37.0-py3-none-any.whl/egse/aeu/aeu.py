import logging
import re
from enum import Enum
from enum import IntEnum
from typing import Union

import numpy as np
from math import fabs

from egse.aeu import aeu_metrics
from egse.aeu.aeu_devif import AEUError
from egse.aeu.aeu_devif import AEUEthernetInterface
from egse.control import is_control_server_active
from egse.device import DeviceConnectionInterface
from egse.device import DeviceConnectionObserver
from egse.device import DeviceConnectionState
from egse.device import DeviceInterface
from egse.device import DeviceTransport
from egse.mixin import DynamicCommandMixin
from egse.mixin import add_cr_lf
from egse.mixin import add_lf
from egse.mixin import dynamic_command
from egse.proxy import Proxy
from egse.resource import get_resource
from egse.settings import Settings
from egse.state import GlobalState
from egse.system import find_class, SignalCatcher
from egse.zmq_ser import connect_address

logger = logging.getLogger(__name__)

CRIO_COMMAND_SETTINGS = Settings.load(filename="aeu_crio.yaml")
PSU_COMMAND_SETTINGS = Settings.load(filename="aeu_psu.yaml")
AWG_COMMAND_SETTINGS = Settings.load(filename="aeu_awg.yaml")

AEU_SETTINGS = Settings.load("AEU Controller")
CTRL_SETTINGS = Settings.load("AEU Control Server")
DEVICE_SETTINGS = CRIO_COMMAND_SETTINGS


def is_aeu_cs_active(name: str, timeout: float = 0.5):
    """ Check if the AEU Control Server is running.

    Args:
        - timeout (float): Timeout when waiting for a reply [s, default=0.5].

    Returns: True if the AEU Control Server is running and replied with the expected answer, False otherwise.
    """

    endpoint = connect_address(CTRL_SETTINGS.PROTOCOL, CTRL_SETTINGS.HOSTNAME, CTRL_SETTINGS[name]["COMMANDING_PORT"])

    return is_control_server_active(endpoint, timeout)

##########################
# Parsing of the responses
##########################


class Version(float):
    """ Version float of XX.xx format."""

    def __str__(self):

        return '{0:05.2f}'.format(float(self))


def unpack_response(response: bytes) -> Union[None, list]:
    """ Unpack the comma-separated strings from the given bytestring.

    The unpacking consists of the following steps:

        - Decode the bytestring to a string;
        - Remove the terminator(s);
        - Split the coma-separated strings into a list of strings.

    Args:
        - response: Bytestring representing the response from an AEU device.

    Returns: List of strings, returned by an AEU device.
    """

    if len(response) == 0:

        return None

    else:

        return response.decode(encoding="latin1", errors="ignore").replace("\r", "").replace("\n", "").split(", ")
        # return response.decode().replace("\r\n", "").split(", ")


def parse_strings(response: bytes) -> Union[tuple, str]:
    """ Parse the given AEU device response to a list of floats.

    Args:
        - response: Bytestring representing the response from an AEU device.

    Returns: List of floats.
    """

    response = unpack_response(response)

    if len(response) == 1:

        return response[0]

    else:

        return tuple(response)


def parse_floats(response: bytes) -> Union[tuple, float]:
    """ Parse the given AEU device response to a list of floats.

    Args:
        - response: Bytestring representing the response from an AEU device.

    Returns: List of floats.
    """

    response = unpack_response(response)

    for index, item in enumerate(response):

        response[index] = float(item)

    if len(response) == 1:

        return response[0]

    else:

        return tuple(response)


def parse_ints(response: bytes) -> Union[tuple, int]:
    """ Parse the given AEU device response to a list of integers.

    Args:
        - response: Bytestring representing the response from an AEU device.

    Returns: List of integers.
    """

    response = unpack_response(response)

    for index, item in enumerate(response):

        response[index] = int(item)

    if len(response) == 1:

        return response[0]

    else:

        return tuple(response)


def parse_crio_instrument_id(response: bytes) -> (str, str, str, float):
    """ Parse the given AEU device response to a cRIO status.

    Args:
        - response: Bytestring representing the response from an AEU device.

    Returns: Three strings and a float (in XX.XX format).
    """

    response = unpack_response(response)

    response[3] = Version(response[3])

    return tuple(response)


def parse_led_status(response: bytes) -> dict:
    """ Parse the given AEU device response to a dictionary.

    The keys in the dictionary are the following:

        - "Standby": Stand-by mode;
        - "Selftest": Self-test mode;
        - "FC_TVAC": Functional-check and TVAD operating mode;
        - "Alignment": Alignment operating mode;
        - "N-CAM": Selected N-CAM;
        - "F-CAM": Selected F-CAM;
        - "V_CCD": Secondary power line V_CCD;
        - "V_CLK": Secondary power line V_CLK;
        - "V_AN1": Secondary power line V_AN1;
        - "V_AN2": Secondary power line V_AN2;
        - "V_AN3": Secondary power line V_AN3;
        - "V_DIG": Secondary power line V_DIG;
        - "S_voltage_oor": Secondary voltage generation out-of-range;
        - "S_current_oor": Secondary current generation out-of-range;
        - "Sync_gf": Synchronisation generator failure;
        - "Clk_50MHz": Clk_50MHz clock;
        - "Clk_ccdread": Clk_ccdread clock;
        - "Clk_heater": Clk_heater clock;
        - "Clk_F_FEE_N": Nominal clock for F-CAM;
        - "Clk_F_FEE_R": Redundant clock for F-CAM;
        - "TestPort": Test port active.

    Args:
        - response: Bytestring representing the response from an AEU device.

    Returns: Dictionary with the cRIO led status
    """

    response = unpack_response(response)

    keys = ["Standby", "Selftest", "FC_TVAC", "Alignment", "N-CAM", "F-CAM", "V_CCD", "V_CLK", "V_AN1", "V_AN2",
            "V_AN3", "V_DIG", "S_voltage_oor", "S_current_oor", "Sync_gf", "Clk_50MHz", "Clk_ccdread", "Clk_heater",
            "Clk_F_FEE_N", "Clk_F_FEE_R", "TestPort"]

    for index in range(len(keys)):

        response[index] = (response[index] == "1")

    return dict(zip(keys, response))


def parse_crio_data(response: bytes) -> dict:
    """ Parse the given AEU device response to a dictionary.

    The keys in the dictionary are the following:

        - "I_N_V_CCD": current for V_CCD for the N-CAM;
        - "I_N_V_CLK": current for V_CLK for the N-CAM;
        - "I_N_V_AN1": current for V_AN1 for the N-CAM;
        - "I_N_V_AN2": current for V_AN2 for the N-CAM;
        - "I_N_V_AN3": current for V_AN3 for the N-CAM;
        - "I_N_V_DIG": current for V_DIG for the N-CAM;
        - "I_F_V_CCD": current for V_CCD for the F-CAM;
        - "I_F_V_CLK": current for V_CLK for the F-CAM;
        - "I_F_V_AN1": current for V_AN1 for the F-CAM;
        - "I_F_V_AN2": current for V_AN2 for the F-CAM;
        - "I_F_V_AN3": current for V_AN3 for the F-CAM;
        - "I_F_V_DIG": current for V_DIG for the F-CAM;
        - "V_N_V_CCD": voltage for V_CCD for the N-CAM;
        - "V_N_V_CLK": voltage for V_CLK for the N-CAM;
        - "V_N_V_AN1": voltage for V_AN1 for the N-CAM;
        - "V_N_V_AN2": voltage for V_AN2 for the N-CAM;
        - "V_N_V_AN3": voltage for V_AN3 for the N-CAM;
        - "V_N_V_DIG": voltage for V_DIG for the N-CAM;
        - "V_F_V_CCD": voltage for V_CCD for the F-CAM;
        - "V_F_V_CLK": voltage for V_CLK for the F-CAM;
        - "V_F_V_AN1": voltage for V_AN1 for the F-CAM;
        - "V_F_V_AN2": voltage for V_AN2 for the F-CAM;
        - "V_F_V_AN3": voltage for V_AN3 for the F-CAM;
        - "V_F_V_DIG": voltage for V_DIG for the F-CAM;
        - "Standby": Stand-by mode (led status);
        - "Selftest": Self-test mode (led status);
        - "FC_TVAC": Functional-check and TVAD operating mode (led status);
        - "Alignment": Alignment operating mode (led status);
        - "N-CAM": Selected N-CAM (led status);
        - "F-CAM": Selected F-CAM (led status);
        - "V_CCD": Secondary power line V_CCD (led status);
        - "V_CLK": Secondary power line V_CLK (led status);
        - "V_AN1": Secondary power line V_AN1 (led status);
        - "V_AN2": Secondary power line V_AN2 (led status);
        - "V_AN3": Secondary power line V_AN3 (led status);
        - "V_DIG": Secondary power line V_DIG (led status);
        - "S_voltage_oor": Secondary voltage generation out-of-range (led status);
        - "S_current_oor": Secondary current generation out-of-range (led status);
        - "Sync_gf": Synchronisation generator failure (led status);
        - "Clk_50MHz": Clk_50MHz clock (led status);
        - "Clk_ccdread": Clk_ccdread clock (led status);
        - "Clk_heater": Clk_heater clock (led status);
        - "Clk_F_FEE_N": Nominal clock for F-CAM (led status);
        - "Clk_F_FEE_R": Redundant clock for F-CAM (led status);
        - "TestPort": Test port active (led status).

    Args:
        - response: Bytestring representing the response from an AEU device.

    Returns: Dictionary with the cRIO led status
    """

    response = unpack_response(response)

    num_numerical_values = 24

    for index in range(num_numerical_values):

        response[index] = float(response[index])

    for index in range(num_numerical_values, len(response)):

        response[index] = (response[index] == "1")

    keys = ["I_N_CCD", "I_N_CLK", "I_N_AN1", "I_N_AN2", "I_N_AN3", "I_N_DIG", "I_F_CCD", "I_F_CLK", "I_F_AN1",
            "I_F_AN2", "I_F_AN3", "I_F_DIG", "V_N_CCD", "V_N_CLK", "V_N_AN1", "V_N_AN2", "V_N_AN3", "V_N_DIG",
            "V_F_CCD", "V_F_CLK", "V_F_AN1", "V_F_AN2", "V_F_AN3", "V_F_DIG", "Standby", "Selftest", "FC_TVAC",
            "Alignment", "N-CAM", "F-CAM", "V_CCD", "V_CLK", "V_AN1", "V_AN2", "V_AN3", "V_DIG", "S_voltage_oor",
            "S_current_oor", "Sync_gf", "Clk_50MHz", "Clk_ccdread", "Clk_heater", "Clk_F_FEE_N", "Clk_F_FEE_R",
            "TestPort"]

    return dict(zip(keys, response))


def parse_psu_instrument_id(response: bytes) -> (str, str, str, str):
    """ Parse the given AEU device response to PSU instrument identification.

    Args:
        - response: Bytestring representing the response from an AEU device.

    Returns:
        - Manufacturer.
        - Model.
        - Serial number.
        - IFC version and build number.
        - IOC version and build number
    """

    response = unpack_response(response)[0].split(",")

    logger.info(response)

    return tuple(response[:3]) + tuple(response[3].split(" "))


def parse_psu_error_info(response: bytes) -> (int, str):
    """ Parse the given AEU device response to PSU error info.

    Args:
        - response: Bytestring representing the response from an AEU device.

    Returns:
        - Identifier of the oldest error in the error queue.
        - Description of the oldest error in the error queue.
    """

    # response = unpack_response(response)

    if len(response) == 0:
        return None

    else:
        return tuple(response.decode(encoding="latin1", errors="ignore").replace("\r", "").replace("\n", "").split(","))

    # # response[0] = int(response[0])
    # return tuple(response)


def parse_arb_data_response(response: bytes) -> str:
    """ Parse the given AEU device response to ARB data.

    Args:
        - response: Bytestring representing the response from an AEU device.

    Returns: String representing the ARB data.
    """

    # TODO For some reason, the result is still returned as a bytestring, in despite of the decoding.  Not sure what
    # the problem is here.

    arb_data = ArbData()
    arb_data.init_from_bytestring(response)
    arb_data = arb_data.string

    return arb_data.decode(encoding="latin1", errors="ignore")


def parse_arb_def(response: bytes) -> (str, str, int):
    """ Parse the given AEU device response to PSU error info.

    Args:
        - response: Bytestring representing the response from an AEU device.

    Returns:
        - Waveform name.
        - Waveform point interpolation state.
        - Waveform length.
    """

    if len(response) == 0:

        return None

    else:

        response = response.decode(encoding="latin1", errors="ignore").replace(" ", "").replace("\r", "")\
            .replace("\n", "").split(",")

        return response[0], response[1], int(response[2])


def parse_awg_instrument_id(response: bytes) -> (str, str, str, float, float, float):
    """ Parse the given AEU device response to AWG instrument identification.

    Args:
        - response: Bytestring representing the response from an AEU device.

    Returns:
        - Manufacturer.
        - Model.
        - Serial number.
        - Revision of the main firmware (XX.xx).
        - Revision of the remote interface firmware (YY.yy).
        - Revision of the USB flash drive firmware (ZZ.zz).
    """

    response = unpack_response(response)

    versions = response[3].split("-")

    versions[0] = Version(versions[0])
    versions[1] = Version(versions[1])
    versions[2] = Version(versions[2])

    return (response[0], response[1]) + tuple(versions)


#####################
# Command terminators
#####################


def parse_arb_data(cmd_string: str):
    """ Parse the data from the given file into a string that can be used as ARB data.

    The command string is of the format: ARB[1:4] filename.  The file with the given name must be read and the content
    must be converted to a string that can be sent to the AWG with the ARB[1:4] command.

    Args:
        - cmd_string: Command string of the format: ARB[1:4] filename.
    """

    cmd, filename = cmd_string.split(" ")

    arb_data = ArbData()
    arb_data.init_from_file(filename)
    # arb_data = arb_data.string

    logger.info(f"{cmd} {arb_data.string}")

    return f"{cmd} {arb_data.string}"


def add_crio_terminator(cmd_string: str):
    """ Append the terminators to the given command string for the cRIO.

    All cRIO commands must be terminated using a valid terminator code 0x0D (Carriage Return, CR), followed by a 0x0A
    (Line Feed, LF).  See PTO-EVO-SYS-UCD-0188-2B (PLATO-AEU CAM TEST EGSE TMTC ICD).

    Args:
        - cmd_string: Command string.

    Returns: Command string for the cRIO, ending with the appropriate terminators.
    """

    return add_cr_lf(cmd_string)


def add_psu_terminator(cmd_string: str):
    """ Append the terminator to the given command string for the PSU.

    All commands must be terminated using a valid terminator code 0x0A (Line Feed, LF).  See
    PTO-EVO-SYS-UCD-0188-2B (PLATO-AEU CAM TEST EGSE TMTC ICD).

    Args:
        - cmd_string: Command string.

    Returns: Command string for the PSU, ending with the appropriate terminator.
    """

    return add_lf(cmd_string)


def add_awg_terminator(cmd_string: str):
    """ Append the terminator to the given command string for the AWG.

    All commands must be terminated with the command terminator code 0x0A (Line Feed, LF), except for ARB1, ARB2, ARB3,
    ARB4, ARB1?, ARB2?, ARB3?, and ARB4? commands.  See PTO-EVO-SYS-UCD-0188-2B (PLATO-AEU CAM TEST EGSE TMTC ICD).

    Args:
        - cmd_string: Command string.

    Returns: Command string for the AWG, ending with the appropriate terminator.
    """

    return add_lf(cmd_string)


#########
# Metrics
#########


def set_ncam_ovp_metrics(v_ccd: float, v_clk: float, v_an1: float, v_an2: float, v_an3: float, v_dig: float):
    """ Set the Over-Voltage Protection (OVP) metrics for the cRIO for the N-CAM.

    Args:
        - Over-Voltage Protection (OVP) value for V_CCD [V].
        - Over-Voltage Protection (OVP) value for V_CLK [V].
        - Over-Voltage Protection (OVP) value for V_AN1 [V].
        - Over-Voltage Protection (OVP) value for V_AN2 [V].
        - Over-Voltage Protection (OVP) value for V_AN3 [V].
        - Over-Voltage Protection (OVP) value for V_DIG [V].
    """

    aeu_metrics.GAEU_OVP_CCD_NFEE.set(v_ccd)
    aeu_metrics.GAEU_OVP_CLK_NFEE.set(v_clk)
    aeu_metrics.GAEU_OVP_AN1_NFEE.set(v_an1)
    aeu_metrics.GAEU_OVP_AN2_NFEE.set(v_an2)
    aeu_metrics.GAEU_OVP_AN3_NFEE.set(v_an3)
    aeu_metrics.GAEU_OVP_DIG_NFEE.set(v_dig)


def set_fcam_ovp_metrics(v_ccd: float, v_clk: float, v_an1: float, v_an2: float, v_an3: float, v_dig: float):
    """ Set the Over-Voltage Protection (OVP) metrics for the cRIO for the F-CAM.

    Args:
        - Over-Voltage Protection (OVP) value for V_CCD [V].
        - Over-Voltage Protection (OVP) value for V_CLK [V].
        - Over-Voltage Protection (OVP) value for V_AN1 [V].
        - Over-Voltage Protection (OVP) value for V_AN2 [V].
        - Over-Voltage Protection (OVP) value for V_AN3 [V].
        - Over-Voltage Protection (OVP) value for V_DIG [V].
    """

    aeu_metrics.GAEU_OVP_CCD_FFEE.set(v_ccd)
    aeu_metrics.GAEU_OVP_CLK_FFEE.set(v_clk)
    aeu_metrics.GAEU_OVP_AN1_FFEE.set(v_an1)
    aeu_metrics.GAEU_OVP_AN2_FFEE.set(v_an2)
    aeu_metrics.GAEU_OVP_AN3_FFEE.set(v_an3)
    aeu_metrics.GAEU_OVP_DIG_FFEE.set(v_dig)


def set_ncam_uvp_metrics(v_ccd: float, v_clk: float, v_an1: float, v_an2: float, v_an3: float, v_dig: float):
    """ Set the Under-Voltage Protection (UVP) metrics for the cRIO for the N-CAM.

    Args:
        - Under-Voltage Protection (UVP) value for V_CCD [V].
        - Under-Voltage Protection (UVP) value for V_CLK [V].
        - Under-Voltage Protection (UVP) value for V_AN1 [V].
        - Under-Voltage Protection (UVP) value for V_AN2 [V].
        - Under-Voltage Protection (UVP) value for V_AN3 [V].
        - Under-Voltage Protection (UVP) value for V_DIG [V].
    """

    aeu_metrics.GAEU_UVP_CCD_NFEE.set(v_ccd)
    aeu_metrics.GAEU_UVP_CLK_NFEE.set(v_clk)
    aeu_metrics.GAEU_UVP_AN1_NFEE.set(v_an1)
    aeu_metrics.GAEU_UVP_AN2_NFEE.set(v_an2)
    aeu_metrics.GAEU_UVP_AN3_NFEE.set(v_an3)
    aeu_metrics.GAEU_UVP_DIG_NFEE.set(v_dig)


def set_fcam_uvp_metrics(v_ccd: float, v_clk: float, v_an1: float, v_an2: float, v_an3: float, v_dig: float):
    """ Set the Under-Voltage Protection (UVP) metrics for the cRIO for the F-CAM.

    Args:
        - Under-Voltage Protection (UVP) value for V_CCD [V].
        - Under-Voltage Protection (UVP) value for V_CLK [V].
        - Under-Voltage Protection (UVP) value for V_AN1 [V].
        - Under-Voltage Protection (UVP) value for V_AN2 [V].
        - Under-Voltage Protection (UVP) value for V_AN3 [V].
        - Under-Voltage Protection (UVP) value for V_DIG [V].
    """

    aeu_metrics.GAEU_UVP_CCD_FFEE.set(v_ccd)
    aeu_metrics.GAEU_UVP_CLK_FFEE.set(v_clk)
    aeu_metrics.GAEU_UVP_AN1_FFEE.set(v_an1)
    aeu_metrics.GAEU_UVP_AN2_FFEE.set(v_an2)
    aeu_metrics.GAEU_UVP_AN3_FFEE.set(v_an3)
    aeu_metrics.GAEU_UVP_DIG_FFEE.set(v_dig)


def set_ncam_ocp_metrics(v_ccd: float, v_clk: float, v_an1: float, v_an2: float, v_an3: float, v_dig: float):
    """ Set the Over-Current Protection (OCP) metrics for the cRIO for the N-CAM.

    Args:
        - Over-Current Protection (OCP) value for V_CCD [A].
        - Over-Current Protection (OCP) value for V_CLK [A].
        - Over-Current Protection (OCP) value for V_AN1 [A].
        - Over-Current Protection (OCP) value for V_AN2 [A].
        - Over-Current Protection (OCP) value for V_AN3 [A].
        - Over-Current Protection (OCP) value for V_DIG [A].
    """

    aeu_metrics.GAEU_OCP_CCD_NFEE.set(v_ccd)
    aeu_metrics.GAEU_OCP_CLK_NFEE.set(v_clk)
    aeu_metrics.GAEU_OCP_AN1_NFEE.set(v_an1)
    aeu_metrics.GAEU_OCP_AN2_NFEE.set(v_an2)
    aeu_metrics.GAEU_OCP_AN3_NFEE.set(v_an3)
    aeu_metrics.GAEU_OCP_DIG_NFEE.set(v_dig)


def set_fcam_ocp_metrics(v_ccd: float, v_clk: float, v_an1: float, v_an2: float, v_an3: float, v_dig: float):
    """ Set the Over-Current Protection (OCP) metrics for the cRIO for the F-CAM.

    Args:
        - Over-Current Protection (OCP) value for V_CCD [A].
        - Over-Current Protection (OCP) value for V_CLK [A].
        - Over-Current Protection (OCP) value for V_AN1 [A].
        - Over-Current Protection (OCP) value for V_AN2 [A].
        - Over-Current Protection (OCP) value for V_AN3 [A].
        - Over-Current Protection (OCP) value for V_DIG [A].
    """

    aeu_metrics.GAEU_OCP_CCD_FFEE.set(v_ccd)
    aeu_metrics.GAEU_OCP_CLK_FFEE.set(v_clk)
    aeu_metrics.GAEU_OCP_AN1_FFEE.set(v_an1)
    aeu_metrics.GAEU_OCP_AN2_FFEE.set(v_an2)
    aeu_metrics.GAEU_OCP_AN3_FFEE.set(v_an3)
    aeu_metrics.GAEU_OCP_DIG_FFEE.set(v_dig)


def set_psu_current_setpoint_metrics(current: float):
    """ Set the current setpoint for the PSU with the given index.

    Args:
        - psu_index: Index of the PSU (should be 1..6).
        - current: Current setpoint [A].
    """

    aeu_metrics.GAEU_PSU_I_SETPOINT.set(current)


def set_psu_ocp_metrics(ocp: float):
    """ Set the Over-Current Protection (OCP) for the PSU with the given index.

    Args:
        - psu_index: Index of the PSU (should be 1..6).
        - ocp: Over-Current Protection (OCP) value [A].
    """

    aeu_metrics.GAEU_PSU_OCP.set(ocp)


def set_psu_voltage_setpoint_metrics(voltage: float):
    """ Set the voltage setpoint for the PSU with the given index.

    Args:
        - psu_index: Index of the PSU (should be 1..6).
        - voltage: Voltage setpoint [V].
    """

    aeu_metrics.GAEU_PSU_V_SETPOINT.set(voltage)


def set_psu_ovp_metrics(ovp: float):
    """ Set the Over-Voltage Protection (OVP) for the PSU with the given index.

    Args:
        - psu_index: Index of the PSU (should be 1..6).
        - ovp: Over-Voltage Protection (OVP) value [A].
    """

    aeu_metrics.GAEU_PSU_OVP.set(ovp)


##############
# Enumerations
##############


class LoopBack(IntEnum):
    """ Enumeration of the loopback options for self-testing.

    Possible values are:

        - NO_LOOPBACK: No loopback;
        - F_CAM_NOM: Loopback F-CAM nominal;
        - F_CAM_RED: Loopback F-CAM redundant;
        - N_CAM: Loopback N-CAM;
        - SVM_NOM: Loopback SVM CAM TCS nominal;
        - SVM_RED: Loopback SVM CAM TCS redundant.
    """

    NO_LOOPBACK = 0     # No loopback
    F_CAM_NOM = 1       # Loopback F-CAM nominal
    F_CAM_RED = 2       # Loopback F-CAM redundant
    N_CAM = 3           # Loopback N-CAM
    SVM_NOM = 4         # Loopback SVM CAM TCS nominal
    SVM_RED = 5         # Loopback SVM CAM TCS redundant


class OperatingMode(IntEnum):
    """ Enumeration of the operating modes.

    Possible values are:

        - STANDBY: Stand-by mode;
        - SELFTEST: Self-test mode;
        - ALIGNMENT: Alignment operating mode;
        - FC_TVAC: Functional check & TVAC operating mode.
    """

    STANDBY = 0         # Stand-by mode
    SELFTEST = 1        # Self-test mode
    ALIGNMENT = 2       # Alignment operating mode
    FC_TVAC = 3         # Functional check & TVAC operating mode


class Waveform(str, Enum):
    """ Enumeration of the waveform types.

    Possible values are:

        - ARB: Arbitrary waveform;
        - SQUARE: Square waveform.
    """

    ARB = "ARB"         # Arbitrary waveform
    SQUARE = "SQUARE"   # Square waveform


class ARB(str, Enum):
    """ Enumeration of the arbitrary waveforms.

    Possible values are:

        - ARB1;
        - ARB2;
        - ARB3;
        - ARB4.
    """

    ARB1 = "ARB1"
    ARB2 = "ARB2"
    ARB3 = "ARB3"
    ARB4 = "ARB4"


class CounterSource(str, Enum):
    """ Enumeration of the input counter source.

    Possible values are:

        - AC: AC-coupled (Alternating Current);
        - DC: DC-coupled (Direct Current).
    """

    AC = "AC"       # AC-coupled (Alternating Current)
    DC = "DC"       # DC-coupled (Direct Current)


class CounterType(str, Enum):
    """ Enumeration of the counter type.

    Possible values are:

        - FREQUENCY: Measure the frequency of the signal;
        - PERIOD: Measure the period of the signal;
        - WIDTH: Measure the positive width of the signal;
        - NWIDTH: Measure the negative width of the signal;
        - DUTY: Measure the duty cycle of the signal.
    """

    FREQUENCY = "FREQUENCY"     # Measure the frequency of the signal
    PERIOD = "PERIOD"           # Measure the period of the signal
    WIDTH = "WIDTH"             # Measure the positive width of the signal
    NWIDTH = "NWIDTH"           # Measure the negative width of the signal
    DUTY = "DUTY"               # Measure the duty cycle of the signal


class Switch(str, Enum):
    """ Enumeration of statuses:

    Possible values are:

        - ON;
        - OFF.
    """

    ON = "ON"
    OFF = "OFF"


class IntSwitch(IntEnum):
    """ Enumeration of statuses"""

    ON = 1
    OFF = 0


class Memory(str, Enum):
    """ Enumeration of the PSU memory.

    Possible values are:

        - A: memory A;
        - B: memory B;
        - C: memory C.
    """


class PriorityMode(str, Enum):
    """ Enumeration for the PSU operation mode to be prioritised.

    Possible values are:

        - CONSTANT_CURRENT: Constant current is prioritised;
        - CONSTANT_VOLTAGE: Constant voltage is prioritised.
    """

    CONSTANT_CURRENT = "CC"     # Constant current is prioritised
    CONSTANT_VOLTAGE = "CV"     # Constant voltage is prioritised


class ArbDataFile(str, Enum):
    """ Enumeration for the files with the ARB data (for the AWG).

    The files are located in the /arbdata folder.
    """

    # Original Evoleo files to configure Clk_ccdread with short pulses of 200 ms

    N_CCD_READ_25 = "ccdRead25.arb",          # CCD readout for N-CAM (image cycle time: 25s)
    N_CCD_READ_31_25 = "ccdRead31_25.arb",    # CCD readout for N-CAM (image cycle time: 31.25s)
    N_CCD_READ_37_50 = "ccdRead37_50.arb",    # CCD readout for N-CAM (image cycle time: 37.50s)
    N_CCD_READ_43_75 = "ccdRead43_75.arb",    # CCD readout for N-CAM (image cycle time: 43.75s)
    N_CCD_READ_50 = "ccdRead50.arb",          # CCD readout for N-CAM (image cycle time: 50s)

    F_CCD_READ = "FccdRead.arb",                        # CCD readout for F-CAM (fixed image cycle time)
    F_CCD_READ_MIN_POINTS = "FccdRead_min_points.arb"   # Taken from PTO-EST-SC-TN-1563 (v1.0)

    # Files modified by KUL to configure Clk_ccdread with short pulses of 150ms

    N_CCD_READ_25_150MS = "ccdRead25_150ms.arb",          # CCD readout for N-CAM (image cycle time: 25s)
    N_CCD_READ_31_25_150MS = "ccdRead31_25_150ms.arb",    # CCD readout for N-CAM (image cycle time: 31.25s)
    N_CCD_READ_37_50_150MS = "ccdRead37_50_150ms.arb",    # CCD readout for N-CAM (image cycle time: 37.50s)
    N_CCD_READ_43_75_150MS = "ccdRead43_75_150ms.arb",    # CCD readout for N-CAM (image cycle time: 43.75s)
    N_CCD_READ_50_150MS = "ccdRead50_150ms.arb",          # CCD readout for N-CAM (image cycle time: 50s)

    # Original Evoleo files to configure Clk_heater

    SVM_SYNC_CCD_READ_25 = "HeaterSync_ccdRead25.arb",           # SVM/TCS sync signal (image cycle time: 25s)
    SVM_SYNC_CCD_READ_31_25 = "HeaterSync_ccdRead31_25.arb",     # SVM/TCS sync signal (image cycle time: 31.25s)
    SVM_SYNC_CCD_READ_37_50 = "HeaterSync_ccdRead37_50.arb",     # SVM/TCS sync signal (image cycle time: 37.50s)
    SVM_SYNC_CCD_READ_43_75 = "HeaterSync_ccdRead43_75.arb",     # SVM/TCS sync signal (image cycle time: 43.75s)
    SVM_SYNC_CCD_READ_50 = "HeaterSync_ccdRead50.arb"            # SVM/TCS sync signal (image cycle time: 50s)

    SVM_SYNC_F_CAM = "HeaterSync_FccdRead.arb"                   # SVM/TCS sync signal (fixed image cycle time)
    SVM_SYNC_F_CAM_MIN_POINTS = "Heater_FccdRead_min_points.arb" # Taken from PTO-EST-SC-TN-1563 (v1.0)


class ArbData:
    """ This code is based on the code of ARB_DATA.py, developed by EVOLEO."""

    def __init__(self):
        """ Initialisation of ARB data that can be sent to or be received from the AWG."""

        self.array = []
        self.filename = None

    def init_from_file(self, filename: ArbDataFile):
        """ Read the ARB data from the given file.

        This consists of the following steps:

            - Look for the file with the given name in the /arbdata folder;
            - Read the data from this file;
            - Convert the data to an array.

        Args:
            - filename: Filename as in the /arbdata folder.
        """

        self.filename = get_resource(f":/aeudata/{filename}")

        self.parse_from_file()

    def init_from_bytestring(self, bytestring: bytes):
        """ Read the ARB data from the given bytestring.

        Args:
            - bytestring: Bytestring.
        """

        bytestring = bytestring.decode(encoding="latin1", errors="ignore")

        len_num_bytes = int(bytestring[1])
        data = bytestring[2 + len_num_bytes:]

        self.array_from_bytes(data)

    def parse_from_file(self):
        """ Construct an array from the content of the file.

        The first line of the file indicates what the format is (currently, all files start with "HEX").
        """

        with open(self.filename, "r") as arb_data_file:

            # Check what the data format is

            header = arb_data_file.readline()
            args = header.strip().split("\t")
            data_format = args[0]

            # Data itself (which should be turned into an array)

            data = arb_data_file.read()

            if data_format == "HEX":

                self.array_from_hex_string(data)

            else:

                raise AEUError("The first line in the ARB data file should be: HEX")

    def array_from_hex_string(self, hex_string):
        """ Build an array from the given hex string.

        Examples:
            - hex_string: "0001 0002 0003" -> array: [1, 2, 3]
            - hex_string: "7FFF FFFF 0000 0001 8001" -> array: [32767, -1, 0, 1, -32767]
            - hex_string: "000100020003" -> array: [1, 2, 3]

        Args:
            - hex_string: Hex string to create an array from.
        """

        self.array = []

        # Strip off the blanks

        hex_string = hex_string.replace(" ", "").strip()

        # Each number is represented by 4 characters

        num_hex_numbers = len(hex_string) // 4

        # Loop over all hex numbers in the input string

        for index in range(num_hex_numbers):

            index *= 4
            hex_number = hex_string[index:index + 4]

            # print(f"Hex number: {hex_number} -> {int(np.int16(int(hex_number, 16)))}")

            # Folding
            # E.g. FFFF is folded to -1 (int returns 65535)

            self.array.append(int(np.int16(int(hex_number, 16))))

    @property
    def string(self):
        """ Convert the content of the file to the ARB data as it should be sent to the AWG.

        The returned string is a concatenation of:

            - The #-symbol;
            - The number of ASCII characters that will define the length of the binary data [bytes];
            - The length of the binary data [bytes];
            - The binary data itself.

        Returns: Content of the file as the ARB data as it should be sent to the AWG.
        """

        # Convert the array to a byte string ("latin1": https://stackoverflow.com/questions/42795042)

        byte_array = self.array_as_bytes().decode(encoding="latin1", errors="ignore")

        # Number of ASCII characters that define the length of the binary data [bytes]

        num_bytes = len(byte_array)

        # Length of the binary data [bytes]

        str_num_bytes = str(num_bytes)

        # Binary data itself

        len_num_bytes = len(str_num_bytes)

        header = f"#{len_num_bytes:1d}{str_num_bytes}"

        # return header.encode() + byte_array
        return rf"#{len_num_bytes:1d}{str_num_bytes}{byte_array}"


        # return rf"#{len_num_bytes:1d}{str_num_bytes}{byte_array.hex()}"

    def array_as_bytes(self):
        """ Return the current array as a byte array.

        Returns: Current array as a byte array
        """

        byte_string = bytes()

        for number in self.array:

            byte_string += number.to_bytes(length=2, byteorder="big", signed=True)

        return byte_string

    def array_from_bytes(self, data: str):
        """ Parse array value from the given string.

        Args:
            - data: Data string.
        """

        num_array = []

        if isinstance(data, str):

            bytestring = data.encode(encoding="latin1")

        num_numbers = len(bytestring) // 2

        for index in range(num_numbers):

            index *= 2
            number = bytestring[index: index+2]

            num_array.append(int.from_bytes(number, byteorder='big', signed=True))

        self.array = num_array


class SyncData:

    def __init__(self, sync_data_string: str):
        """ Create an object that holds the information to to configure AWG2, from the given string.

        An example of such a string:

        SyncData//(A | 25.00 | ArbDataFile//(N_CCD_READ_25) | ArbDataFile//(SVM_SYNC_CCD_READ_25) | 0.006667)

        Returns: SyncData object containing the following information:

                    - identifier (A/B/C/D/E/"");
                    - image cycle time [s];
                    - filename for the calibration data for Clk_ccdread;
                    - filename for the calibration data for Clk_heater;
                    - frequency [Hz].
        """

        match = re.match(r"SyncData//\((.*)\)$", sync_data_string)

        image_cycle_time_id, image_cycle_time, ccdread_arb_data, heater_arb_data, frequency = match[1].split(" | ")

        self.id = image_cycle_time_id
        self.image_cycle_time = float(image_cycle_time)

        self.ccdread_arb_data = create_arb_data_file(ccdread_arb_data)
        self.heater_arb_data = create_arb_data_file(heater_arb_data)

        self.frequency = float(frequency)

# SYNC_DATA = {
#     "25.00": SyncData("A", ArbDataFile.N_CCD_READ_25, ArbDataFile.SVM_SYNC_CCD_READ_25, 0.006667),
#     "31.25": SyncData("B", ArbDataFile.N_CCD_READ_31_25, ArbDataFile.SVM_SYNC_CCD_READ_31_25, 0.016),
#     "37.50": SyncData("C", ArbDataFile.N_CCD_READ_37_50, ArbDataFile.SVM_SYNC_CCD_READ_37_50, 0.006667),
#     "43.75": SyncData("D", ArbDataFile.N_CCD_READ_43_75, ArbDataFile.SVM_SYNC_CCD_READ_43_75, 0.0114286),
#     "50.00": SyncData("E", ArbDataFile.N_CCD_READ_50, ArbDataFile.SVM_SYNC_CCD_READ_50, 0.006667)
# }


def create_arb_data_file(arb_data_file_string: str) -> ArbDataFile:
    """ Create an ArbDataFile object from the given string.

    An example of such a string:

        ArbDataFile//N_CCD_READ_25

    Returns: ArbDataFile object.
    """

    match = re.match("ArbDataFile//\((.*)\)$", arb_data_file_string)[1]

    return find_class("egse.aeu.aeu.ArbDataFile")[match]


################
# Look-up tables
################


# To interpret the results from the get_loopback_option command on the cRIO

LOOPBACK = {
    LoopBack.NO_LOOPBACK: "No loopback",
    LoopBack.F_CAM_NOM: "Loopback F-CAM nominal",
    LoopBack.F_CAM_RED: "Loopback F-CAM redundant",
    LoopBack.N_CAM: "Loopback N-CAM",
    LoopBack.SVM_NOM: "Loopback SVM CAM TCS nominal",
    LoopBack.SVM_RED: "Loopback SVM CAM TCS reducant"
}

# To interpret the results from the get_n_cam_voltage_quality and get_f_cam_voltage_quality command on the cRIO.

VOLTAGE_QUALITY = {
    0: "Inside of range",
    1: "Over-Voltage protection (OVP) detected",
    2: "Under-Voltage protection (UVP) detected"
}

# To interpret the results from the get_n_cam_current_quality and get_f_cam_current_quality command on the cRIO.

CURRENT_QUALITY = {
    0: "Inside of range",
    1: "Over-Current Protection (OCP) detected"
}

# To interpret the results from the get_error_info command on the cRIO.

CRIO_ERRORS = {
    0: "No error detected",
    1: "Command error",
    2: "Invalid character",
    3: "Syntax error",
    4: "Unexpected number of parameters",
    5: "Data out of range",
    6: "Invalid mode"
}

# To interpret the results from the get_error_info command on the PSU.

PSU_ERRORS = {

    -100: "Command error.  This is the generic syntax error.",
    -101: "Invalid character.  A syntactic element contains a character that is invalid for that type.",
    -102: "Syntax error.  An unrecognised command or data type was encountered.",
    -103: "Invalid separator.  The parser was expecting a separator and encountered an illegal character.",
    -104: "Data type error.  The parser recognised a data element different than one allowed",
    -105: "GET not allowed.  A Group Execute Trigger was received within a programme message",
    -108: "Parameter not allowed.  More parameters were received than expected for the header.",
    -109: "Missing parameter.  Fewer parameters were received than required for the header",
    -110: "Command header error.  An error was detected in the header.",
    -112: "Programme mnemonic too long.  The header contains more than 12 characters.",
    -113: "Undefined header.  The header is undefined for this device.",
    -114: "Header suffix out-of-range.  The value of a numeric suffix attached to a programme mnemonic.",
    -115: "Unexpected number of parameters.  The number of parameters received does not correspond to the number of "
          "parameters expected.",
    -120: "Numeric data error.  This error is generated when parsing a data element that appears to be numeric, incl. "
          "the non-decimal numeric types.",
    -128: "Numeric data not allowed.  A legal numeric data element was received, but the device does not accept one in "
          "this position for the header.",
    -130: "Suffix error.  This error is generated when parsing a suffix.",
    -131: "Invalid suffix.  The suffix does not follow the syntax of the suffix is inappropriate for this device.",
    -134: "Suffix too long.  The suffix contained more than 12 characters.",
    -138: "Suffix not allowed.  A suffix was encountered after a numeric element which does not allow suffixes.",
    -140: "Charater data error.  This error is generated when parsing a character data element.",
    -141: "Invalid character data.  Either the character data element contains an invalid character or the particular "
          "element received is not valid for the header.",
    -144: "Character data too long.  The character data element contains more than 12 characters.",
    -148: "Character data not allowed.  A legal character data element was encountered where prohibited by the device.",
    -150: "String data error.  This error is generated when parsing a string data element.",
    -151: "Invalid string data.  A string data element was expected, but was invalid for some reason.",
    -158: "String data not allowed.  A string data element was encountered but was noto allowed by the device at this "
          "point in parsing.",
    -160: "Block dat error.  This error is generated when parsing a block data element.",
    -170: "Expression error.  This error is generated when parsing an expression data element.",
    -180: "Macro error.  This error is generated when defining a macro or executing a macro.",
    -200: "Execution error (generic).  This is the generric syntax error for devices that cannot detect more specific "
          "errors.",
    -201: "Invalid while in local.  Indicates that a command is not executable while the device is in local due to a "
          "hard local control.",
    -203: "Command protected.  Indicates that a legal password-protected programme command or query could not be "
          "executed because the command was disabled.",
    -210: "Trigger error.",
    -211: "Trigger ignored. Indicates that a GET, *TRG, or triggering signal was received and recognised by the device "
          "but was ignored because of device timing considerations.",
    -213: "Init ignored.  Indicates that a request for a measurment initiation was ignoredas another measurement was "
          "already in progress.",
    -214: "Trigger deadlock.  Indicates that the trigger source for the initiation of a measurement is set to GET and "
          "a subsequent measurement query was received.",
    -220: "Parameter error.  Indicates that a programme data element related error occurred.",
    -221: "Settings conflict.  Indicates that a legal programme data element was parsed but could not be executed due "
          "to the current device state.",
    -222: "Data out-of-range.  Indicates that a legal programme element was parsed but could not be executed because "
          "the interpreted value was outside the legal range as defined by the device.",
    -223: "Too much data. Indicates that a legal programme data element of block, expression, or string type was"
          " received that contained more data than the device could handle due to memory or related device-specific "
          "requirements.",
    -224: "Illegal parameter value.  Used where an exact value, from a list of possible values, was expected.",
    -230: "Data corrupt or stale.  Possibly invalid data; new reading started but not completed since last access.",
    -241: "Hardware missing.  Indicates that a legal programme command or query could not be executed because of "
          "missing device hardware.",
    -310: "System error.  Indicates that some error, termed 'system error' by the device, has occurred.",
    -311: "Memory errors. Indicates some physical fault in the device's memory, such as parity error.",
    -313: "Calibration memory lost.  Indicates that non-volatile calibration data used by the *CAL? command has been "
          "lost.",
    -314: "Save/recall memory lost.  Indicates that non-volatile data saved by the *SAV? command has been lost.",
    -315: "Configuration memory lost.  Indicates that non-volatile configuration data saved by the device has been "
          "lost.",
    -330: "Self-test failed.",
    -350: "Queue overflow.  A specific code entered into the queue in lieu of the code that caused the error.  This "
          "code indicates that there is no room in the queue and an error occurred but was not recorded.",
    -360: "Communication error when the flow control is turned off.  This error applies when the RS232C interface is "
          "used.",
    -362: "Framing error in programme message.  Framing error.  This error applies when the RS232C interface is used.",
    -363: "Input buffer overrun.  Buffer overrun error.  This error applies when the RS232C interface is used.",
    -365: "Time-out error.  This error applies when the RS232C interface is used.",
    -400: "Query error (generic).  This is the generic query error for devices that cannot detect more specific errors.",
    -410: "Query INTERRUPTED.  Received a new command before the response was read.",
    -420: "Query UNTERMINATED.  The controller attempted to read the response after the device received an unsupported "
          "query or has not received a query.  The -100 'COMMAND ERROR' error and this error are stored in the error "
          "queue.  The controller will time out.",
    -430: "Query DEADLOCKED.  The error queue, input buffer, and output buffer are full when sending large binary data "
          "as a response, and the transmission timing is off.",
    -440: "Query UNTERMINATED after indefinite response.  Received a separate query in semicolon-delimited format "
          "after a query that returns a response in an indefinite form.  (Example: A command such as the following: "
          "*IDN?;SYST:ERR?)",
    -800: "Operation complete.  The instrument has completed all selected pending operations in accordance with the "
          "IEEE 488.2, 12.5.2 synchronisation protocol.",
    +101: "Conflicts with PROTection state.  Configuration is not possible because a protection function is activated.",
    +102: "Conflicts with OUTPut state.  Configuration is not possible because the output is on.",
    +103: "Conflicts with the TRACk state.  Configuration is not possibnle because the tracking function is enabled.",
    +155: "Operation denied during ALARM condition.  The operation was denied because an alarm is occurring on the PMX.",
    +156: "Operation denied during OUTPut ON.  The operation was denied because the output is on.",
    +157: "Operation denied during EXTernal control.  The operation was denied because the output is being controlled "
          "through extenal control.",
    +161: "Operation denied during AUTO CALibration running.  The operation was denied because auto calibration is "
          "being performed.",
    +201: "Conflicts with OUTPut:DELay state.  Configuration is not possible because of the output delay setting.",
    +202: "Conflicts with OUTPut: EXTernal state.  Configuration is not possible because of the setting of the output "
          "on/off control using an external contact.",
    +203: "Conflicts with DTFormation state.  Configuration is not possible because of the parallel or series "
          "operation setting.",
    +301: "Channel disabled.  The channel setting is invalid.",
    +302: "Conflicts with TRANsient in progress.  Configuration is not possible because a TRANsient sub-system is "
          "running.",
    +303: "Conflicts with OUTP:DELay in progress.  Configuration is not possible because an output delay is in effect.",
    +304: "Conflicts with DTFormation in progress.  Configuration is not possible because parallel of series operation "
          "is in progress.",
    +801: "Conflicts with CALibration in progress.  Memory contents cannot be recalled because of the VOLT:PROT "
          "setting.",
    +802: "Conflicts with the CALibration:AUTO in progress.  Memory contents cannot be recalled becaused of the "
          "VOLT:LIM:LOW setting.",
    +901: "EEPROM content error for CRITICAL data.  An error has occurred in a critical area.  Contact your Kikusui "
          "agent or distributor.",
    +902: "EEPROM CAL info lost.  Calibration information was lost.",
    +903: "EEPROM content error for CONFIG data.  An error has occurred in the configuration area.  The PMX will be "
          "reset to its factory default settings.  This error occurring multiple times indicates that the memory is "
          "damaged.  Contact your Kikusui agent or distributor.",
    +910: "IOC No response.  There is no response from the IOC (firmware for controlling the instrument's internal "
          "hardware).",
    +911: "IOC Bad sync or Cmd/Resp code mismatch.  Failed to synchronised the IOC.  Or, the command code does not "
          "match the response code."
}

# To interpret the results from the execution_error_register command on the AWG.

AWG_ERRORS = {
    -1: "Firmware Update / Battery Fail. Initialised to factory default state.",
    -2: "Frequency / Period invalid. Frequency lower limit 1mHz. Period upper limit 1000s.",
    -3: "Frequency / Period invalid. Frequency upper limit [VALUE] Period lower limit [VALUE].",
    -4: "Pulse width invalid. Limited by pulse period.",
    -5: "Pulse width invalid. Lower limit [VALUE].",
    -6: "Pulse edge time invalid. Limited by pulse width. OR Pulse rise time invalid. Limited by pulse width.",
    -7: "Pulse edge time invalid. Lower limit [VALUE]. OR Pulse rise time invalid. Lower limits [VALUE].",
    -8: "Invalid entry. Width cannot be less than (0.625 * Rise + 0.625 * Fall + [VALUE]).",
    -9: "Invalid entry. Period cannot be less than (Delay + Width + 0.625 * Rise + 0.625 * Fall + [VALUE]).",
    -10: "Pulse width deviation invalid for current pulse parameter settings.",
    -11: "Square width invalid. Lower limit [VALUE].",
    -12: "Bitrate invalid. Lower limit 1ubps.",
    -13: "Bitrate invalid. Upper limit [VALUE].",
    -14: "Frequency / Period invalid. Frequency lower limit 1uHz. Period upper limit 1000000s.",
    -15: "Frequency / Period invalid for Sine. Frequency upper limit [VALUE]. Period lower limit [VALUE]. "
         "OR Frequency / Period invalid for Square. Frequency upper limit [VALUE]. Period lower limit [VALUE]. "
         "OR Frequency / Period invalid for Ramp. Frequency upper limit [VALUE]. Period lower limit [VALUE]. "
         "OR Frequency / Period invalid for Arb. Frequency upper limit [VALUE]. Period lower limit [VALUE].",
    -16: "Ramp symmetry invalid. Upper limit 100%.",
    -17: "Ramp symmetry invalid. Lower limit 0%.",
    -18: "Square duty cycle invalid. Upper limit 99.999%.",
    -19: "Square duty cycle invalid. Lower limit 0.001%.",
    -20: "Frequency deviation invalid for current waveform / parameter settings.",
    -21: "Hop frequency invalid for current waveform / parameter settings.",
    -22: "Sweep frequency invalid for current waveform / parameter settings.",
    -23: "Amplitude value invalid. Upper limit +32767.",
    -24: "Amplitude value invalid. Lower limit -32767.",
    -25: "Point number invalid. Last defined point [VALUE].",
    -26: "Point number invalid. First defined point 1.",
    -27: "Number of points invalid. Upper limit 8192.",
    -28: "Number of points invalid. Lower limit 1.",
    -29: "Please specify a filename in Short File Name (SFN) format.",
    -30: "AM frequency invalid. Upper limit 10MHz.",
    -31: "AM frequency invalid. Lower limit 1uHz.",
    -32: "Amplitude depth invalid. Upper limit 100%.",
    -33: "Amplitude depth invalid. Lower limit 0%.",
    -34: "FM frequency invalid. Upper limit 10MHz.",
    -35: "FM frequency invalid. Lower limit 1uHz.",
    -36: "Frequency deviation invalid. Current upper limit [VALUE] "
         "OR Frequency deviation invalid. Cannot exceed carrier frequency. "
         "Frequency plus deviation limited to [VALUE].",
    -37: "Frequency deviation invalid. Lower limit 0Hz.",
    -38: "PM frequency invalid. Upper limit 10MHz.",
    -39: "PM frequency invalid. Lower limit 1uHz.",
    -40: "Phase deviation invalid. Upper limit +360 degrees.",
    -41: "Phase deviation invalid. Lower limit -360 degrees.",
    -42: "FSK rate invalid. Upper limit 10MHz.",
    -43: "FSK rate invalid. Lower limit 2mHz.",
    -44: "Hop frequency invalid. Current upper limit [VALUE].",
    -45: "Hop frequency invalid. Lower limit 1uHz.",
    -46: "BPSK rate invalid. Upper limit 10MHz.",
    -47: "BPSK rate invalid. Lower limit 2mHz.",
    -48: "Hop phase invalid. Upper limit +360 degrees.",
    -49: "Hop phase invalid. Lower limit -360 degrees.",
    -50: "SUM frequency invalid. Upper limit 10MHz.",
    -51: "SUM frequency invalid. Lower limit 1uHz.",
    -52: "SUM modulation level invalid. Upper limit 100%.",
    -53: "SUM modulation level invalid. Lower limit 0%.",
    -54: "PWM frequency invalid. Upper limit 10MHz.",
    -55: "PWM frequency invalid. Lower limit 1uHz.",
    -56: "PWM deviation invalid. Maximum deviation limited by carrier width setting.",
    -57: "PWM deviation invalid. Lower limit 0ns.",
    -58: "Arb DC cannot be selected when modulation is enabled and vice versa.",
    -59: "FM invalid for Noise / PRBS.",
    -60: "PM invalid for Noise / PRBS.",
    -61: "FSK invalid for Noise / PRBS.",
    -62: "BPSK invalid for Noise / PRBS.",
    -63: "PWM invalid for Noise / PRBS.",
    -64: "PWM is only valid for Pulse.",
    -65: "Start frequency invalid. Lower limit 1uHz.",
    -66: "Start frequency invalid. Cannot be greater than stop frequency.",
    -67: "Stop frequency invalid. Cannot be less than start frequency.",
    -68: "Stop frequency invalid. Current upper limit [VALUE].",
    -69: "Sweep time invalid. Lower limit 1us.",
    -70: "Sweep time invalid. Upper limit 500s.",
    -71: "Trigger period invalid. Lower limit [VALUE].",
    -72: "Trigger period invalid. Upper limit 500s.",
    -73: "Arb DC cannot be selected when frequency sweep is enabled and vice versa.",
    -74: "Sweep invalid for Noise.",
    -75: "Burst count invalid. Upper limit 2147483647.",
    -76: "Burst count invalid. Lower limit 1.",
    -77: "Trigger period invalid. Upper limit 500s.",
    -78: "Trigger period invalid. Lower limit [VALUE].",
    -79: "Arb DC cannot be selected when burst is enabled and vice versa.",
    -80: "OUTPUT VOLTAGE OVERLOAD. Output turned off for safety.",
    -81: "Invalid entry. High level upper limit [VALUE].",
    -82: "Invalid entry. Low level lower limit [VALUE].",
    -83: "Invalid entry. Amplitude upper limit [VALUE].",
    -84: "Invalid entry. Amplitude lower limit [VALUE].",
    -85: "Invalid entry. Offset upper limit [VALUE].",
    -86: "Invalid entry. Offset lower limit [VALUE].",
    -87: "Phase invalid. Upper limit +360 degrees.",
    -88: "Phase invalid. Lower limit -360 degrees.",
    -89: "Output load invalid. Upper limit 10000 ohms.",
    -90: "Output load invalid. Lower limit 1 ohms.",
    -91: "Frequency coupling cannot be turned on when modulation is enabled.",
    -92: "Frequency coupling cannot be turned on when frequency sweep is enabled.",
    -93: "Frequency coupling cannot be turned on. Pulse waveform can only be coupled with Pulse waveform.",
    -94: "Frequency coupling cannot be turned on when Noise is set as main output.",
    -95: "Frequency coupling cannot be turned on when DC is set as main output.",
    -96: "Outputs cannot be coupled when Tracking is selected.",
    -97: "Amplitudes cannot be coupled when Tracking is selected.",
    -98: "Frequencies cannot be coupled when Tracking is selected.",
    -99: "Tracking cannot be selected when outputs are coupled.",
    -100: "Tracking cannot be selected when amplitudes are coupled.",
    -101: "Tracking cannot be selected when frequencies are coupled.",
    -102: "Channel 2 parameters not available when Tracking is selected.",
    -103: "Invalid entry. Upper limit 99%.",
    -104: "Invalid entry. Lower limit 1%.",
    -105: "GPIB address invalid. Upper limit 30.",
    -106: "GPIB address invalid. Lower limit 0.",
    -107: "Incorrect password. Please try again.",
    -108: "Password did not match. Please try again.",
    -109: "Unsupported USB device. Device current limited to 500mA.",
    -110: "Unsupported USB device. Please insert USB-Flash disk only.",
    -111: "Unsupported remote command.",
    -112: "Unsupported remote command parameter.",
    -113: "USB HOST hardware not found.",
    -114: "Please insert USB-Flash disk and try again.",
    -115: "USB-Flash disk files limited to 1260.",
    -116: "Please edit different file name as the current file already exist.",
    -117: "FATAL ERROR: Invalid waveform location.",
    -118: "FATAL ERROR: Invalid setup location.",
    -119: "Unsupported waveform file or the file may be corrupted, please wait.",
    -120: "Unsupported setup file or the file may be corrupted, please wait.",
    -121: "Unsupported command on the Webpage.",
    -122: "Unable to Recall instrument setup. The specified location is empty.",
    -123: "Test FAILED at address [VALUE]. Data written [VALUE]. Data read back [VALUE].",
    -124: "PM invalid for Pulse.",
    -125: "BPSK invalid for Pulse.",
    -126: "FM invalid for Pulse.",
    -127: "FSK invalid for Pulse.",
    -128: "Sweep invalid for Pulse.",
    -129: "Finite Burst invalid for frequencies above [VALUE].",
    -130: "Channel 2 parameters not available when channel 2 is set to output channel 1 sync waveform.",
    -131: "Gated Burst invalid for frequencies above [VALUE].",
    -132: "Frequency coupling cannot be turned on when burst is enabled.",
    -133: "Frequency and amplitude coupling cannot be turned on when channel 2 is set to output channel 1 sync.",
    -134: "Tracking cannot be turned on when channel 2 is set to output channel 1 sync waveform.",
    -135: "Channel 2 cannot be set to output channel 1 sync when frequencies or amplitudes are coupled.",
    -136: "Channel 2 cannot be set to output channel 1 sync when channels are in tracking mode.",
    -137: "Channel 2 parameters not available when Tracking is selected.",
    -138: "Invalid entry. Order upper limit 50.",
    -139: "Invalid entry. Order lower limit 1.",
    -140: "Invalid entry. Amplitude. percent upper limit 100.0%.",
    -141: "Invalid entry. Amplitude. percent lower limit 0.0%.",
    -142: "Invalid entry. Phase upper limit 360.0 degrees.",
    -143: "Invalid entry. Phase lower limit -360.0 degrees.",
    -144: "Amplitude coupling cannot be turned on when ASK modulation is enabled.",
    -145: "Amplitude coupling cannot be turned on when DC is set as main output.",
    -146: "Amplitude invalid. Carrier amplitude cannot be less than hop amplitude.",
    -147: "Hop amplitude invalid. Cannot be less than 0 Vpp.",
    -148: "ASK rate invalid. Upper limit 10MHz.",
    -149: "ASK rate invalid. Lower limit 2mHz.",
    -150: "Amplitude modulation invalid for carrier frequencies above [VALUE].",
    -151: "Amplitude shift keying invalid for carrier frequencies above [VALUE].",
    -152: "SUM modulation invalid for carrier frequencies above [VALUE].",
    -153: "Feature not available in this model.",
    -154: "Pulse delay invalid. Limited by pulse period.",
    -155: "Pulse delay time invalid. Lower limit 0ns.",
    -156: "Pulse fall time invalid. Limited by pulse width.",
    -157: "Pulse fall time invalid. Lower limit [VALUE].",
    -158: "External clock invalid. Switching back to internal reference clock. Please wait."
}

# To interpret the results from the get_operating_mode command on the cRIO.

OPERATING_MODE = {
    OperatingMode.STANDBY: "Stand-by mode",
    OperatingMode.SELFTEST: "Self-test mode",
    OperatingMode.ALIGNMENT: "Alignment operating mode",
    OperatingMode.FC_TVAC: "Functional check & TVAC operating mode"
}

# To interpret the results from the get_selftest_result command on the cRIO.

SELFTEST_RESULT = {
    0: "No result",
    1: "Doing loopback test",
    2: "Doing normal test",
    3: "Loopback test pass",
    4: "Normal test pass",

    7: "Can't update the frequency value in channel 1 of AWG1",
    8: "Frequency not within limits for channel 1 of AWG1",
    11: "Can't update the frequency value in channel 1 of AWG2",
    12: "Frequency not within limits for channel 1 of AWG2",
    15: "Can't update the frequency value in channel 2 of AWG2",
    16: "Frequency not within limits for channel 2 of AWG2",
    19: "Can't update the frequency value in channel 2 of AWG2",
    20: "Frequency not within limits for channel 3 of AWG2",
    21: "Can't update the automatic test result for PSU1",

    22: "Result of automatic test on PSU1 if fail",
    23: "Can't update the automatic test result for PSU1",
    24: "Result of automatic test on PSU2 if fail",
    25: "Can't update the automatic test result for PSU3",
    26: "Result of automatic test on PSU3 if fail",
    27: "Can't update the automatic test result for PSU4",
    28: "Result of automatic test on PSU4 if fail",
    29: "Can't update the automatic test result for PSU5",
    30: "Result of automatic test on PSU5 if fail",
    31: "Can't update the automatic test result for PSU5",
    32: "Result of automatic test on PSU6 if fail",

    33: "Connected load was detected in N-CAM (V_CCD)",
    34: "Connected load was detected in N-CAM (V_CCLK)",
    35: "Connected load was detected in N-CAM (V_AN1)",
    36: "Connected load was detected in N-CAM (V_AN2)",
    37: "Connected load was detected in N-CAM (V_AN3)",
    38: "Connected load was detected in N-CAM (V_DIG)",
    39: "Connected load was detected in F-CAM (V_CCD)",
    40: "Connected load was detected in F-CAM (V_CLK)",
    41: "Connected load was detected in F-CAM (V_AN1)",
    42: "Connected load was detected in F-CAM (V_AN2)",
    43: "Connected load was detected in F-CAM (V_AN3)",
    44: "Connected load was detected in F-CAM (V_DIG)",

    45: "Voltage value outside the limits in N-CAM (V_CCD)",
    46: "Voltage value outside the limits in N-CAM (V_CLK)",
    47: "Voltage value outside the limits in N-CAM (V_AN1)",
    48: "Voltage value outside the limits in N-CAM (V_AN2)",
    49: "Voltage value outside the limits in N-CAM (V_AN3)",
    50: "Voltage value outside the limits in N-CAM (V_DIG)",
    51: "Voltage value outside the limits in F-CAM (V_CCD)",
    52: "Voltage value outside the limits in F-CAM (V_CLK)",
    53: "Voltage value outside the limits in F-CAM (V_AN1)",
    54: "Voltage value outside the limits in F-CAM (V_AN2)",
    55: "Voltage value outside the limits in F-CAM (V_AN3)",
    56: "Voltage value outside the limits in F-CAM (V_DIG)"
}


###################
# Device interfaces
###################


class CRIOInterface(DeviceInterface):
    """ AEU device interface for the cRIO."""

    def __init__(self):
        """ Initialisation of a cRIO device interface."""

        super().__init__()

        self.device_name = "CRIO"

    def get_status(self):

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="*IDN?",
                     process_cmd_string=add_crio_terminator,
                     process_response=parse_crio_instrument_id)
    def get_id(self) -> (str, str, str, float):
        """ Return the instrument identification of the cRIO.

        Returns:
            - Manufacturer of the cRIO.
            - Model of the cRIO.
            - Serial number of the cRIO.
            - Build version of the cRIO.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="*RST",
                     process_cmd_string=add_crio_terminator)
    def reset(self) -> None:
        """ Reset the cRIO settings.

        This command will configure:
            - self-test with no loopback;
            - quality of frequency intervals to "value inside of range";
            - set to stand-by mode;
            - protection software values (OCP/OVP/UVP for N-/F-CAM).
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="*CLS",
                     process_cmd_string=add_crio_terminator)
    def clear_error_queue(self) -> None:
        """ Clear the cRIO error queue."""

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="MEAS:N:CURR?",
                     process_cmd_string=add_crio_terminator,
                     process_response=parse_floats)
    def get_n_cam_current(self) -> (float, float, float, float, float, float):
        """ Return the measured current values for the N-CAM [A].

        Returns:
            - Measured current value for V_CCD [A] (coming from PSU1).
            - Measured current value for V_CLK [A] (coming from PSU2).
            - Measured current value for V_AN1 [A] (coming from PSU3).
            - Measured current value for V_AN2 [A] (coming from PSU4).
            - Measured current value for V_AN3 [A] (coming from PSU5).
            - Measured current value for V_DIG [A] (coming from PSU).
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="MEAS:F:CURR?",
                     process_cmd_string=add_crio_terminator,
                     process_response=parse_floats)
    def get_f_cam_current(self) -> (float, float, float, float, float, float):
        """ Return the measured current values for the F-CAM [A].

        Returns:
            - Measured current value for V_CCD [A] (coming from PSU1).
            - Measured current value for V_CLK [A] (coming from PSU2).
            - Measured current value for V_AN1 [A] (coming from PSU3).
            - Measured current value for V_AN2 [A] (coming from PSU4).
            - Measured current value for V_AN3 [A] (coming from PSU5).
            - Measured current value for V_DIG [A] (coming from PSU).
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="MEAS:N:VOLT?",
                     process_cmd_string=add_crio_terminator,
                     process_response=parse_floats)
    def get_n_cam_voltage(self) -> (float, float, float, float, float, float):
        """ Return the measured voltage values for the N-CAM [V].

        Returns:
            - Measured voltage value for V_CCD [V] (coming from PSU1).
            - Measured voltage value for V_CLK [V] (coming from PSU2).
            - Measured voltage value for V_AN1 [V] (coming from PSU3).
            - Measured voltage value for V_AN2 [V] (coming from PSU4).
            - Measured voltage value for V_AN3 [V] (coming from PSU5).
            - Measured voltage value for V_DIG [V] (coming from PSU).
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="MEAS:F:VOLT?",
                     process_cmd_string=add_crio_terminator,
                     process_response=parse_floats)
    def get_f_cam_voltage(self) -> (float, float, float, float, float, float):
        """ Return the measured voltage values for the F-CAM [V].

        Returns:
            - Measured voltage value for V_CCD [V] (coming from PSU1).
            - Measured voltage value for V_CLK [V] (coming from PSU2).
            - Measured voltage value for V_AN1 [V] (coming from PSU3).
            - Measured voltage value for V_AN2 [V] (coming from PSU4).
            - Measured voltage value for V_AN3 [V] (coming from PSU5).
            - Measured voltage value for V_DIG [V] (coming from PSU).
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="CNTRL:LOOPBACK ${loopback_option}",
                     process_cmd_string=add_crio_terminator)
    def set_loopback_option(self, loopback_option: LoopBack) -> None:
        """ Control the self-test operation.

        Set the loopback option for the self-test.  Possible values are:

            - 0 (LoopBack.NO_LOOPBACK): no loopback;
            - 1 (LoopBack.F_CAM_NOM): loopback F-CAM nominal;
            - 2 (LoopBack.F_CAM_RED): loopback F-CAM redundant;
            - 3 (LoopBack.N_CAM): loopback N-CAM;
            - 4 (LoopBack.SVM_NOM): loopback SVM CAM TCS nominal;
            - 5 (LoopBack.SVM_RED): loopback SVN CAM TCS redundant.

        Args:
           - opt: Option for loopback during self-test.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="CNTRL:LOOPBACK?",
                     process_cmd_string=add_crio_terminator,
                     process_response=parse_ints)
    def get_loopback_option(self) -> int:
        """ Return the loopback option selected to self-test.

        To understand the meaning of the returned value, check:

            LOOPBACK[returned_value]

        Returns: Option selected to self-test.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="CNTRL:N:OUTP ${output_status}",
                     process_cmd_string=add_crio_terminator)
    def set_n_cam_secondary_power_status(self, output_status: IntSwitch) -> None:
        """ Configure the secondary power lines of the N-CAM to ON/OFF.

        Args:
            - out: 1 if the output of the secondary power lines must be enabled for the N-CAM, 0 otherwise.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="CNTRL:N:OUTP?",
                     process_cmd_string=add_crio_terminator,
                     process_response=parse_ints)
    def get_n_cam_secondary_power_status(self) -> IntSwitch:
        """ Return the status of the secondary power lines for the N-CAM.

        Returns: 1 if the output of the secondary power lines has been enabled for the N-CAM, 0 otherwise.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="CNTRL:F:OUTP ${output_status}",
                     process_cmd_string=add_crio_terminator)
    def set_f_cam_secondary_power_status(self, output_status: IntSwitch) -> None:
        """ Configure the secondary power lines of the F-CAM to ON/OFF.

        Args:
            - out: 1 if the output of the secondary power lines must be enabled for the F-CAM, 0 otherwise.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="CNTRL:F:OUTP?",
                     process_cmd_string=add_crio_terminator,
                     process_response=parse_ints)
    def get_f_cam_secondary_power_status(self) -> IntSwitch:
        """ Return the status of the secondary power lines for the F-CAM.

        Returns: 1 if the output of the secondary power lines has been enabled for the F-CAM, 0 otherwise.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="CNTRL:N:CURR:PROT ${v_ccd}, ${v_clk}, ${v_an1}, ${v_an2}, ${v_an3}, ${v_dig}",
                     process_cmd_string=add_crio_terminator)
    def set_n_cam_ocp(self, v_ccd: float, v_clk: float, v_an1: float, v_an2: float, v_an3: float, v_dig: float) -> None:
        """ Set the Over-Current Protection (OCP) values for the N-CAM [A].

        Args:
            - v_ccd: OCP in V_CCD [A] for the N-CAM.
            - v_clk: OCP in V_CLK [A] for the N-CAM.
            - v_an1: OCP in V_AN1 [A] for the N-CAM.
            - v_an2: OCP in V_AN2 [A] for the N-CAM.
            - v_an3: OCP in V_AN3 [A] for the N-CAM.
            - v_dig: OCP in V_DIG [A] for the N-CAM.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="CNTRL:N:CURR:PROT?",
                     process_cmd_string=add_crio_terminator,
                     process_response=parse_floats)
    def get_n_cam_ocp(self) -> (float, float, float, float, float, float):
        """ Return the Over-Current Protection (OCP) values for the N-CAM [A].

        Returns:
            - OCP in V_CCD [A] for the N-CAM.
            - OCP in V_CLK [A] for the N-CAM.
            - OCP in V_AN1 [A] for the N-CAM.
            - OCP in V_AN2 [A] for the N-CAM.
            - OCP in V_AN3 [A] for the N-CAM.
            - OCP in V_DIG [A] for the N-CAM.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="CNTRL:F:CURR:PROT ${v_ccd}, ${v_clk}, ${v_an1}, ${v_an2}, ${v_an3}, ${v_dig}",
                     process_cmd_string=add_crio_terminator)
    def set_f_cam_ocp(self, v_ccd: float, v_clk: float, v_an1: float, v_an2: float, v_an3: float, v_dig: float) \
            -> None:
        """ Set the Over-Current Protection (OCP) values for the F-CAM [A].

        Args:
            - v_ccd: OCP in V_CCD [A] for the F-CAM.
            - v_clk: OCP in V_CLK [A] for the F-CAM.
            - v_an1: OCP in V_AN1 [A] for the F-CAM.
            - v_an2: OCP in V_AN2 [A] for the F-CAM.
            - v_an3: OCP in V_AN3 [A] for the F-CAM.
            - v_dig: OCP in V_DIG [A] for the F-CAM.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="CNTRL:F:CURR:PROT?",
                     process_cmd_string=add_crio_terminator,
                     process_response=parse_floats)
    def get_f_cam_ocp(self) -> (float, float, float, float, float, float):
        """ Return the Over-Current Protection (OCP) values for the F-CAM [A].

        Returns:
            - OCP in V_CCD [A] for the F-CAM.
            - OCP in V_CLK [A] for the F-CAM.
            - OCP in V_AN1 [A] for the F-CAM.
            - OCP in V_AN2 [A] for the F-CAM.
            - OCP in V_AN3 [A] for the F-CAM.
            - OCP in V_DIG [A] for the F-CAM.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="CNTRL:N:VOLT:PROT:OV ${v_ccd}, ${v_clk}, ${v_an1}, ${v_an2}, ${v_an3}, ${v_dig}",
                     process_cmd_string=add_crio_terminator)
    def set_n_cam_ovp(self, v_ccd: float, v_clk: float, v_an1: float, v_an2: float, v_an3: float, v_dig: float) \
            -> None:
        """ Set the Over-Voltage Protection (OVP) values for the N-CAM [V].

        Args:
            - v_ccd: OVP in V_CCD [V] for the N-CAM.
            - v_clk: OVP in V_CLK [V] for the N-CAM.
            - v_an1: OVP in V_AN1 [V] for the N-CAM.
            - v_an2: OVP in V_AN2 [V] for the N-CAM.
            - v_an3: OVP in V_AN3 [V] for the N-CAM.
            - v_dig: OVP in V_DIG [V] for the N-CAM.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="CNTRL:N:VOLT:PROT:OV?",
                     process_cmd_string=add_crio_terminator,
                     process_response=parse_floats)
    def get_n_cam_ovp(self) -> (float, float, float, float, float, float):
        """ Return the Over-Voltage Protection (OVP) values for the N-CAM [V].

        Returns:
            - OVP in V_CCD [V] for the N-CAM.
            - OVP in V_CLK [V] for the N-CAM.
            - OVP in V_AN1 [V] for the N-CAM.
            - OVP in V_AN2 [V] for the N-CAM.
            - OVP in V_AN3 [V] for the N-CAM.
            - OVP in V_DIG [V] for the N-CAM.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="CNTRL:F:VOLT:PROT:OV ${v_ccd}, ${v_clk}, ${v_an1}, ${v_an2}, ${v_an3}, ${v_dig}",
                     process_cmd_string=add_crio_terminator)
    def set_f_cam_ovp(self, v_ccd: float, v_clk: float, v_an1: float, v_an2: float, v_an3: float, v_dig: float) \
            -> None:
        """ Set the Over-Voltage Protection (OVP) values for the F-CAM [V].

        Args:
            - v_ccd: OVP in V_CCD [V] for the F-CAM.
            - v_clk: OVP in V_CLK [v] for the F-CAM.
            - v_an1: OVP in V_AN1 [V] for the F-CAM.
            - v_an2: OVP in V_AN2 [V] for the F-CAM.
            - v_an3: OVP in V_AN3 [V] for the F-CAM.
            - v_dig: OVP in V_DIG [V] for the F-CAM.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="CNTRL:F:VOLT:PROT:OV?",
                     process_cmd_string=add_crio_terminator,
                     process_response=parse_floats)
    def get_f_cam_ovp(self) -> (float, float, float, float, float, float):
        """ Return the Over-Voltage Protection (OVP) values for the F-CAM [V].

        Returns:
            - OVP in V_CCD [V] for the F-CAM.
            - OVP in V_CLK [V] for the F-CAM.
            - OVP in V_AN1 [V] for the F-CAM.
            - OVP in V_AN2 [V] for the F-CAM.
            - OVP in V_AN3 [V] for the F-CAM.
            - OVP in V_DIG [V] for the F-CAM.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="CNTRL:N:VOLT:PROT:UV ${v_ccd}, ${v_clk}, ${v_an1}, ${v_an2}, ${v_an3}, ${v_dig}",
                     process_cmd_string=add_crio_terminator)
    def set_n_cam_uvp(self, v_ccd: float, v_clk: float, v_an1: float, v_an2: float, v_an3: float, v_dig: float) \
            -> None:
        """ Set the Under-Voltage Protection (UVP) values for the N-CAM [V].

        Args:
            - v_ccd: UVP in V_CCD [V] for the N-CAM.
            - v_clk: UVP in V_CLK [V] for the N-CAM.
            - v_an1: UVP in V_AN1 [V] for the N-CAM.
            - v_an2: UVP in V_AN2 [V] for the N-CAM.
            - v_an3: UVP in V_AN3 [V] for the N-CAM.
            - v_dig: UVP in V_DIG [V] for the N-CAM.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="CNTRL:N:VOLT:PROT:UV?",
                     process_cmd_string=add_crio_terminator,
                     process_response=parse_floats)
    def get_n_cam_uvp(self) -> (float, float, float, float, float, float):
        """ Return the Under-Voltage Protection (OVP) values for the N-CAM [V].

        Returns:
            - UVP in V_CCD [V] for the N-CAM.
            - UVP in V_CLK [V] for the N-CAM.
            - UVP in V_AN1 [V] for the N-CAM.
            - UVP in V_AN2 [V] for the N-CAM.
            - UVP in V_AN3 [V] for the N-CAM.
            - UVP in V_DIG [V] for the N-CAM.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="CNTRL:F:VOLT:PROT:UV ${v_ccd}, ${v_clk}, ${v_an1}, ${v_an2}, ${v_an3}, ${v_dig}",
                     process_cmd_string=add_crio_terminator)
    def set_f_cam_uvp(self, v_ccd: float, v_clk: float, v_an1: float, v_an2: float, v_an3: float, v_dig: float) -> None:
        """ Set the Under-Voltage Protection (UVP) values for the F-CAM [V].

        Args:
            - v_ccd: UVP in V_CCD [V] for the F-CAM.
            - v_clk: UVP in V_CLK [V] for the F-CAM.
            - v_an1: UVP in V_AN1 [V] for the F-CAM.
            - v_an2: UVP in V_AN2 [V] for the F-CAM.
            - v_an3: UVP in V_AN3 [V] for the F-CAM.
            - v_dig: UVP in V_DIG [V] for the F-CAM.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="CNTRL:F:VOLT:PROT:UV?",
                     process_cmd_string=add_crio_terminator,
                     process_response=parse_floats)
    def get_f_cam_uvp(self) -> (float, float, float, float, float, float):
        """ Return the Under-Voltage Protection (UVP) values for the F-CAM [V].

        Returns:
            - UVP in V_CCD [V] for the F-CAM.
            - UVP in V_CLK [V] for the F-CAM.
            - UVP in V_AN1 [V] for the F-CAM.
            - UVP in V_AN2 [V] for the F-CAM.
            - UVP in V_AN3 [V] for the F-CAM.
            - UVP in V_DIG [V] for the F-CAM.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="MEAS:N:VOLT:QUAL?",
                     process_cmd_string=add_crio_terminator,
                     process_response=parse_ints)
    def get_n_cam_voltage_quality(self) -> (int, int, int, int, int, int):
        """ Return the secondary power line voltage information out-of-range for the N-CAM.

        To understand the meaning of the returned values for the voltages V_CCD, V_CLK, V_AN1, V_AN2, V_AN3, and V_DIG,
        check:

            VOLTAGE_QUALITY[returned_value]

        Returns: Status of the secondary power voltages V_CCD, V_CLK, V_AN1, V_AN2, V_AN3, and V_DIG for the N-CAM.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="MEAS:F:VOLT:QUAL?",
                     process_cmd_string=add_crio_terminator,
                     process_response=parse_ints)
    def get_f_cam_voltage_quality(self) -> (int, int, int, int, int, int):
        """ Return the secondary power line voltage information out-of-range for the F-CAM.

        To understand the meaning of the returned values for the voltages V_CCD, V_CLK, V_AN1, V_AN2, V_AN3, and V_DIG,
        check:

            VOLTAGE_QUALITY[returned_value]

        Returns: Status of the secondary power voltages V_CCD, V_CLK, V_AN1, V_AN2, V_AN3, and V_DIG for the F-CAM.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="MEAS:N:CURR:QUAL?",
                     process_cmd_string=add_crio_terminator,
                     process_response=parse_ints)
    def get_n_cam_current_quality(self) -> (int, int, int, int, int, int):
        """ Return the secondary power line current information out-of-range for the N-CAM.

        To understand the meaning of the returned values for the currents V_CCD, V_CLK, V_AN1, V_AN2, V_AN3, and V_DIG,
        check:

            CURRENT_QUALITY[returned_value]

        Returns: The quality of the signal of the secondary power lines V_CCD, V_CLK, V_AN1, V_AN2, V_AN3, and V_DIG for
                 the N-CAM.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="MEAS:F:CURR:QUAL?",
                     process_cmd_string=add_crio_terminator,
                     process_response=parse_ints)
    def get_f_cam_current_quality(self) -> (int, int, int, int, int, int):
        """ Return the secondary power line current information out-of-range for the F-CAM.

        To understand the meaning of the returned values for the currents V_CCD, V_CLK, V_AN1, V_AN2, V_AN3, and V_DIG,
        check:

            CURRENT_QUALITY[returned_value]

        Returns: Quality of the signal of the secondary power lines V_CCD, V_CLK, V_AN1, V_AN2, V_AN3, and V_DIG for the
                 F-CAM.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="CNTRL:N:CLOCK ${clk_50mhz}, ${clk_ccdread}",
                     process_cmd_string=add_crio_terminator)
    def set_n_cam_clock_status(self, clk_50mhz: IntSwitch, clk_ccdread: IntSwitch) -> None:
        """ Enable/disable the clocks for the N-CAM.

        For the N-CAM, the clocks are Clk_50MHz and Clk_ccdread.

        Args:
            - clk_50mhz: Boolean indicating whether or not the Clk_50MHz clock should be enabled for the N-CAM.
            - clk_ccdread: Boolean indicating whether or not the Clk_ccdread clock should be enabled for the N-CAM.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="CNTRL:N:CLOCK?",
                     process_cmd_string=add_crio_terminator,
                     process_response=parse_ints)
    def get_n_cam_clock_status(self) -> (IntSwitch, IntSwitch):
        """ Return whether or not the clocks are enabled or not for the N-CAM.

        For the N-CAM, the clocks are Clk_50MHz and Clk_ccdread.

        Returns:
            - Boolean indicating whether or not the Clk_50MHz has been enabled for the N-CAM.
            - Boolean indicating whether or not eh Clk_ccdread has been enabled for the N-CAM.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="MEAS:N:CLOCK:QUAL?",
                     process_cmd_string=add_crio_terminator,
                     process_response=parse_ints)
    def get_n_cam_clock_quality(self) -> (IntSwitch, IntSwitch):
        """ Return the status for the synchronisation generator for the N-CAM.

        For the Clk_50MHz and Clk_ccdread clocks for the N-CAM a boolean is returned with the following meaning:

            - 1: Synchronisation failure detected;
            - 0: No synchronisation failure detected.

        Returns:
            - Boolean indicating the status of the synchronisation generator for the Clk_50MHz clock for the N-CAM.
            - Boolean indicating the status of the synchronisation generator for the Clk_ccdread clock for the N-CAM.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="CNTRL:F:CLOCK ${clk_50mhz_nom}, ${clk_50mhz_red}, ${clk_ccdread_nom}, "
                                "${clk_ccdread_red}",
                     process_cmd_string=add_crio_terminator)
    def set_f_cam_clock_status(self, clk_50mhz_nom: IntSwitch, clk_50mhz_red: IntSwitch, clk_ccdread_nom: IntSwitch,
                               clk_ccdread_red: IntSwitch) -> None:
        """ Enable/disable the clocks for the F-CAM.

        For the F-CAM, the clocks are Clk_50MHz and Clk_ccdread, both nominal and redundant.

        Args:
            - clk_50mhz_nom: Boolean indicating whether or not the Clk_50MHz_nom clock should be enabled for the F-CAM.
            - clk_50mhz_red: Boolean indicating whether or not the Clk_50MHz_red clock should be enabled for the F-CAM.
            - clk_ccdread_nom: Boolean indicating whether or not the Clk_ccdread_nom clock should be enabled for the
                               F-CAM.
            - clk_ccdread_red: Boolean indicating whether or not the Clk_ccdread_red clock should be enabled for the
                               F-CAM.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="CNTRL:F:CLOCK?",
                     process_cmd_string=add_crio_terminator,
                     process_response=parse_ints)
    def get_f_cam_clock_status(self) -> (IntSwitch, IntSwitch, IntSwitch, IntSwitch):
        """ Return whether or not the clocks are enabled or not for the F-CAM.

        For the F-CAM, the clocks are Clk_50MHz and Clk_ccdread, both nominal and redundant.

        Returns:
            - Boolean indicating whether or not the Clk-50MHz_nom has been enabled for the F-CAM.
            - Boolean indicating whether or not the Clk-50MHz_red has been enabled for the F-CAM.
            - Boolean indicating whether or not the Clk_ccdread_nom has been enabled for the F-CAM.
            - Boolean indicating whether or not the Clk_ccdread_red has been enabled for the F-CAM.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="MEAS:F:CLOCK:QUAL?",
                     process_cmd_string=add_crio_terminator,
                     process_response=parse_ints)
    def get_f_cam_clock_quality(self) -> (IntSwitch, IntSwitch, IntSwitch, IntSwitch):
        """ Return the status for the synchronisation generator for the F-CAM.

        For the Clk_50MHz and Clk_ccdread clocks (both nominal and redundant) for the F-CAM a boolean is returned with
        the following meaning:

            - 1: Synchronisation failure detected;
            - 0: No synchronisation failure detected.

        Returns:
            - Boolean indicating the status of the synchronisation generator for the Clk_50MHz_nom clock for the F-CAM.
            - Boolean indicating the status of the synchronisation generator for the Clk_50MHz_red clock for the F-CAM.
            - Boolean indicating the status of the synchronisation generator for the Clk_ccdread_nom clock for the
              F-CAM.
            - Boolean indicating the status of the synchronisation generator for the Clk_ccdread_red clock for the
              F-CAM.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="CNTRL:SVM:CLOCK ${clk_50mhz_nom}, ${clk_50mhz_red}, ${clk_heater_nom}, "
                                "${clk_heater_red}",
                     process_cmd_string=add_crio_terminator)
    def set_svm_clock_status(self, clk_50mhz_nom: IntSwitch, clk_50mhz_red: IntSwitch, clk_heater_nom: IntSwitch,
                             clk_heater_red: IntSwitch) -> None:
        """ Enable/disable the clocks for the SVM CAM TCS.

        For the SVM CAM TCS, the clocks are Clk_50MHz and Clk_heater, both nominal and redundant.

        Args:
            - clk_50mhz_nom: Boolean indicating whether or not the Clk_50MHz_nom clock should be enabled for the SVM CAM
                             TCS.
            - clk_50mhz_red: Boolean indicating whether or not the Clk_50MHz_red clock should be enabled for the SVM CAM
                             TCS.
            - clk_heater_nom: Boolean indicating whether or not the Clk_heater_nom clock should be enabled for the SVM
                              CAM TCS.
            - clk_heater_red: Boolean indicating whether or not the Clk_heater_red clock should be enabled for the SVM
                              CAM TCS.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="CNTRL:SVM:CLOCK?",
                     process_cmd_string=add_crio_terminator,
                     process_response=parse_ints)
    def get_svm_clock_status(self) -> (IntSwitch, IntSwitch, IntSwitch, IntSwitch):
        """ Return whether or not the clocks are enabled or not for the SVM.

        For the SVM CAM TCS, the clocks are Clk_50MHz and Clk_heater, both nominal and redundant.

        Returns:
            - Boolean indicating whether or not the Clk_50MHz_nom has been enabled for the SVM CAM TCS.
            - Boolean indicating whether or not the Clk_50MHz_red has been enabled for the SVM CAM TCS.
            - Boolean indicating whether or not the Clk_heater_nom has been enabled for the SVM CAM TCS.
            - Boolean indicating whether or not the Clk_heater_red has been enabled for the SVM CAM TCS.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="MEAS:SVM:CLOCK:QUAL?",
                     process_cmd_string=add_crio_terminator,
                     process_response=parse_ints)
    def get_svm_clock_quality(self) -> (IntSwitch, IntSwitch, IntSwitch, IntSwitch):
        """ Return the status for the synchronisation generator for the SVM.

        For the Clk_50MHz and Clk_heater clocks (both nominal and redundant) for the SVM a boolean is returned with
        the following meaning:

            - True: Synchronisation failure detected;
            - False: No synchronisation failure detected.

        Returns:
            - Boolean indicating the status of the synchronisation generator for the Clk_50MHz_nom clock for the SVM.
            - Boolean indicating the status of the synchronisation generator for the Clk_50MHz_red clock for the SVM.
            - Boolean indicating the status of the synchronisation generator for the Clk_heater_nom clock for the SVM.
            - Boolean indicating the status of the synchronisation generator for the Clk_heater_red clock for the SVM.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="MEAS:LED?",
                     process_cmd_string=add_crio_terminator,
                     process_response=parse_led_status)
    def get_led_status(self) -> dict:
        """ Returns the led status.

        Returns: Led status of (True: led on, False: led off):

            - "Standby": Stand-by mode;
            - "Selftest": Self-test mode;
            - "FC_TVAC": Functional-check and TVAD operating mode;
            - "Alignment": Alignment operating mode;
            - "N-CAM": Selected N-CAM;
            - "F-CAM": Selected F-CAM;
            - "V_CCD": Secondary power line V_CCD;
            - "V_CLK": Secondary power line V_CLK;
            - "V_AN1": Secondary power line V_AN1;
            - "V_AN2": Secondary power line V_AN2;
            - "V_AN3": Secondary power line V_AN3;
            - "V_DIG": Secondary power line V_DIG;
            - "S_voltage_oor": Secondary voltage generation out-of-range;
            - "S_current_oor": Secondary current generation out-of-range;
            - "Sync_gf": Synchronisation generator failure;
            - "Clk_50MHz": Clk_50MHz clock;
            - "Clk_ccdread": Clk_ccdread clock;
            - "Clk_heater": Clk_heater clock;
            - "Clk_F_FEE_N": Nominal clock for F-CAM;
            - "Clk_F_FEE_R": Redundant clock for F-CAM;
            - "TestPort": Test port active.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="CNTRL:MODE ${operating_mode}",
                     process_cmd_string=add_crio_terminator)
    def set_operating_mode(self, operating_mode: OperatingMode) -> None:
        """ Change the operating mode.

        Possible values are:

            - 0 (OperatingMode.STANDBY): stand-by mode;
            - 1 (OperatingMode.SELFTEST): self-test mode;
            - 2 (OperatingMode.ALIGNMENT): alignment operating mode;
            - 3 (OperatingMode.FC_TVAC): functional-check and TVAC mode.

        Args:
            - operating_mode: Operating mode to change to.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="CNTRL:MODE?",
                     process_cmd_string=add_crio_terminator,
                     process_response=parse_ints)
    def get_operating_mode(self) -> int:
        """ Return the actual operating mode.

        To understand the meaning of the returned value,check:

            OPERATING_MODE[returned_value]

        Returns: Actual operating mode.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="MEAS:ALL:ANALOG?",
                     process_cmd_string=add_crio_terminator,
                     process_response=parse_crio_data)
    def get_data(self) -> dict:
        """ Return all relevant data.

        Returns: Dictionary with all relevant data:
            - "I_N_V_CCD": current for V_CCD for the N-CAM;
            - "I_N_V_CLK": current for V_CLK for the N-CAM;
            - "I_N_V_AN1": current for V_AN1 for the N-CAM;
            - "I_N_V_AN2": current for V_AN2 for the N-CAM;
            - "I_N_V_AN3": current for V_AN3 for the N-CAM;
            - "I_N_V_DIG": current for V_DIG for the N-CAM;
            - "I_F_V_CCD": current for V_CCD for the F-CAM;
            - "I_F_V_CLK": current for V_CLK for the F-CAM;
            - "I_F_V_AN1": current for V_AN1 for the F-CAM;
            - "I_F_V_AN2": current for V_AN2 for the F-CAM;
            - "I_F_V_AN3": current for V_AN3 for the F-CAM;
            - "I_F_V_DIG": current for V_DIG for the F-CAM;
            - "V_N_V_CCD": voltage for V_CCD for the N-CAM;
            - "V_N_V_CLK": voltage for V_CLK for the N-CAM;
            - "V_N_V_AN1": voltage for V_AN1 for the N-CAM;
            - "V_N_V_AN2": voltage for V_AN2 for the N-CAM;
            - "V_N_V_AN3": voltage for V_AN3 for the N-CAM;
            - "V_N_V_DIG": voltage for V_DIG for the N-CAM;
            - "V_F_V_CCD": voltage for V_CCD for the F-CAM;
            - "V_F_V_CLK": voltage for V_CLK for the F-CAM;
            - "V_F_V_AN1": voltage for V_AN1 for the F-CAM;
            - "V_F_V_AN2": voltage for V_AN2 for the F-CAM;
            - "V_F_V_AN3": voltage for V_AN3 for the F-CAM;
            - "V_F_V_DIG": voltage for V_DIG for the F-CAM;
            - "Standby": Stand-by mode (led status);
            - "Selftest": Self-test mode (led status);
            - "FC_TVAC": Functional-check and TVAD operating mode (led status);
            - "Alignment": Alignment operating mode (led status);
            - "N-CAM": Selected N-CAM (led status);
            - "F-CAM": Selected F-CAM (led status);
            - "V_CCD": Secondary power line V_CCD (led status);
            - "V_CLK": Secondary power line V_CLK (led status);
            - "V_AN1": Secondary power line V_AN1 (led status);
            - "V_AN2": Secondary power line V_AN2 (led status);
            - "V_AN3": Secondary power line V_AN3 (led status);
            - "V_DIG": Secondary power line V_DIG (led status);
            - "S_voltage_oor": Secondary voltage generation out-of-range (led status);
            - "S_current_oor": Secondary current generation out-of-range (led status);
            - "Sync_gf": Synchronisation generator failure (led status);
            - "Clk_50MHz": Clk_50MHz clock (led status);
            - "Clk_ccdread": Clk_ccdread clock (led status);
            - "Clk_heater": Clk_heater clock (led status);
            - "Clk_F_FEE_N": Nominal clock for F-CAM (led status);
            - "Clk_F_FEE_R": Redundant clock for F-CAM (led status);
            - "TestPort": Test port active (led status).
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="SYST:ERR?",
                     process_cmd_string=add_crio_terminator,
                     process_response=parse_ints)
    def get_error_info(self) -> int:
        """ Read the oldest error information the error queue.

        Return the number/identifier of the oldest error information in the error queue.  To understand the meaning of
        the returned value, check:

            CRIO_ERRORS[returned_value]

        The error queue can store up to 16 errors.  To clear the error queue, use the clear_error_queue command.

        Returns: Number/identifier of the oldest error in the error queue.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="SYST:ERR:QUANT?",
                     process_cmd_string=add_crio_terminator,
                     process_response=parse_ints)
    def get_num_errors(self) -> int:
        """ Return the number of errors/events in the error queue.

        The error queue can store up to 16 errors.  To clear the error queue, use the clear_error_queue command.

        Returns: Number of errors/events in the error queue.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="SYST:TEST:RESULT?",
                     process_cmd_string=add_crio_terminator,
                     process_response=parse_ints)
    def get_selftest_result(self) -> int:
        """ Return the status/result of a self-test.

        To understand the meaning of the returned value,check:

            SELFTEST_RESULT[returned_value]

        Returns: Status/result of a self-test.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="SYST:PROT?",
                     process_cmd_string=add_crio_terminator,
                     process_response=parse_ints)
    def get_protection_status(self) -> (IntSwitch, IntSwitch, IntSwitch, IntSwitch):
        """ Return the status of protections.

        The protections are the status of the emergency button, Over-Voltage Protection (OVP) for PSU nominal and for
        PSU redundant, Over-Voltage Protection for PDU.

        Returns:
            - Boolean indicating whether or not the emergency button has been pressed.
            - Boolean indicating whether or not an OVP has been detected for PSU nominal.
            - Boolean indicating whether or not an OVP has been detected for PSU redundant.
            - Boolean indicating whether or not an OVP has been detected for PDU.
        """
        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="SYST:TIME:PROT ${trip_time_ovp_n_cam_v_ccd}, ${trip_time_ovp_n_cam_v_clk}, "
                                "${trip_time_ovp_n_cam_v_an1}, ${trip_time_ovp_n_cam_v_an2}, "
                                "${trip_time_ovp_n_cam_v_an3}, ${trip_time_ovp_n_cam_v_dig}, "
                                "${trip_time_ovp_f_cam_v_ccd}, ${trip_time_ovp_f_cam_v_clk}, "
                                "${trip_time_ovp_f_cam_v_an1}, ${trip_time_ovp_f_cam_v_an2}, "
                                "${trip_time_ovp_f_cam_v_an3}, ${trip_time_ovp_f_cam_v_dig}, "
                                "${trip_time_uvp_n_cam_v_ccd}, ${trip_time_uvp_n_cam_v_clk}, "
                                "${trip_time_uvp_n_cam_v_an1}, ${trip_time_uvp_n_cam_v_an2}, "
                                "${trip_time_uvp_n_cam_v_an3}, ${trip_time_uvp_n_cam_v_dig}, "
                                "${trip_time_uvp_f_cam_v_ccd}, ${trip_time_uvp_f_cam_v_clk}, "
                                "${trip_time_uvp_f_cam_v_an1}, ${trip_time_uvp_f_cam_v_an2}, "
                                "${trip_time_uvp_f_cam_v_an3}, ${trip_time_uvp_f_cam_v_dig}, "
                                "${trip_time_ocp_n_cam_v_ccd}, ${trip_time_ocp_n_cam_v_clk}, "
                                "${trip_time_ocp_n_cam_v_an1}, ${trip_time_ocp_n_cam_v_an2}, "
                                "${trip_time_ocp_n_cam_v_an3}, ${trip_time_ocp_n_cam_v_dig}, "
                                "${trip_time_ocp_f_cam_v_ccd}, ${trip_time_ocp_f_cam_v_clk}, "
                                "${trip_time_ocp_f_cam_v_an1}, ${trip_time_ocp_f_cam_v_an2}, "
                                "${trip_time_ocp_f_cam_v_an3}, ${trip_time_ocp_f_cam_v_dig}, "
                                "${startup_time_ovp_n_cam_v_ccd}, ${startup_time_ovp_n_cam_v_clk}, "
                                "${startup_time_ovp_n_cam_v_an1}, ${startup_time_ovp_n_cam_v_an2}, "
                                "${startup_time_ovp_n_cam_v_an3}, ${startup_time_ovp_n_cam_v_dig}, "
                                "${startup_time_ovp_f_cam_v_ccd}, ${startup_time_ovp_f_cam_v_clk}, "
                                "${startup_time_ovp_f_cam_v_an1}, ${startup_time_ovp_f_cam_v_an2}, "
                                "${startup_time_ovp_f_cam_v_an3}, ${startup_time_ovp_f_cam_v_dig}, "
                                "${startup_time_uvp_n_cam_v_ccd}, ${startup_time_uvp_n_cam_v_clk}, "
                                "${startup_time_uvp_n_cam_v_an1}, ${startup_time_uvp_n_cam_v_an2}, "
                                "${startup_time_uvp_n_cam_v_an3}, ${startup_time_uvp_n_cam_v_dig}, "
                                "${startup_time_uvp_f_cam_v_ccd}, ${startup_time_uvp_f_cam_v_clk}, "
                                "${startup_time_uvp_f_cam_v_an1}, ${startup_time_uvp_f_cam_v_an2}, "
                                "${startup_time_uvp_f_cam_v_an3}, ${startup_time_uvp_f_cam_v_dig}, "
                                "${startup_time_ocp_n_cam_v_ccd}, ${startup_time_ocp_n_cam_v_clk}, "
                                "${startup_time_ocp_n_cam_v_an1}, ${startup_time_ocp_n_cam_v_an2},"
                                "${startup_time_ocp_n_cam_v_an3}, ${startup_time_ocp_n_cam_v_dig}, "
                                "${startup_time_ocp_f_cam_v_ccd}, ${startup_time_ocp_f_cam_v_clk}, "
                                "${startup_time_ocp_f_cam_v_an1}, ${startup_time_ocp_f_cam_v_an2}, "
                                "${startup_time_ocp_f_cam_v_an3}, ${startup_time_ocp_f_cam_v_dig}",
                     process_cmd_string=add_crio_terminator)
    def set_time(self, trip_time_ovp_n_cam_v_ccd: float, trip_time_ovp_n_cam_v_clk: float, trip_time_ovp_n_cam_v_an1:
                 float, trip_time_ovp_n_cam_v_an2: float, trip_time_ovp_n_cam_v_an3: float, trip_time_ovp_n_cam_v_dig:
                 float, trip_time_ovp_f_cam_v_ccd: float, trip_time_ovp_f_cam_v_clk: float, trip_time_ovp_f_cam_v_an1:
                 float, trip_time_ovp_f_cam_v_an2: float, trip_time_ovp_f_cam_v_an3: float, trip_time_ovp_f_cam_v_dig:
                 float, trip_time_uvp_n_cam_v_ccd: float, trip_time_uvp_n_cam_v_clk: float, trip_time_uvp_n_cam_v_an1:
                 float, trip_time_uvp_n_cam_v_an2: float, trip_time_uvp_n_cam_v_an3: float, trip_time_uvp_n_cam_v_dig:
                 float, trip_time_uvp_f_cam_v_ccd: float, trip_time_uvp_f_cam_v_clk: float, trip_time_uvp_f_cam_v_an1:
                 float, trip_time_uvp_f_cam_v_an2: float, trip_time_uvp_f_cam_v_an3: float, trip_time_uvp_f_cam_v_dig:
                 float, trip_time_ocp_n_cam_v_ccd: float, trip_time_ocp_n_cam_v_clk: float, trip_time_ocp_n_cam_v_an1:
                 float, trip_time_ocp_n_cam_v_an2: float, trip_time_ocp_n_cam_v_an3: float, trip_time_ocp_n_cam_v_dig:
                 float, trip_time_ocp_f_cam_v_ccd: float, trip_time_ocp_f_cam_v_clk: float, trip_time_ocp_f_cam_v_an1:
                 float, trip_time_ocp_f_cam_v_an2: float, trip_time_ocp_f_cam_v_an3: float, trip_time_ocp_f_cam_v_dig:
                 float, startup_time_ovp_n_cam_v_ccd: float, startup_time_ovp_n_cam_v_clk: float,
                 startup_time_ovp_n_cam_v_an1: float, startup_time_ovp_n_cam_v_an2: float, startup_time_ovp_n_cam_v_an3:
                 float, startup_time_ovp_n_cam_v_dig: float, startup_time_ovp_f_cam_v_ccd: float,
                 startup_time_ovp_f_cam_v_clk: float, startup_time_ovp_f_cam_v_an1: float, startup_time_ovp_f_cam_v_an2:
                 float, startup_time_ovp_f_cam_v_an3: float, startup_time_ovp_f_cam_v_dig: float,
                 startup_time_uvp_n_cam_v_ccd: float, startup_time_uvp_n_cam_v_clk: float, startup_time_uvp_n_cam_v_an1:
                 float, startup_time_uvp_n_cam_v_an2: float, startup_time_uvp_n_cam_v_an3: float,
                 startup_time_uvp_n_cam_v_dig: float, startup_time_uvp_f_cam_v_ccd: float, startup_time_uvp_f_cam_v_clk:
                 float, startup_time_uvp_f_cam_v_an1: float, startup_time_uvp_f_cam_v_an2: float,
                 startup_time_uvp_f_cam_v_an3: float, startup_time_uvp_f_cam_v_dig: float, startup_time_ocp_n_cam_v_ccd:
                 float, startup_time_ocp_n_cam_v_clk: float, startup_time_ocp_n_cam_v_an1: float,
                 startup_time_ocp_n_cam_v_an2: float, startup_time_ocp_n_cam_v_an3: float, startup_time_ocp_n_cam_v_dig:
                 float, startup_time_ocp_f_cam_v_ccd: float, startup_time_ocp_f_cam_v_clk: float,
                 startup_time_ocp_f_cam_v_an1: float, startup_time_ocp_f_cam_v_an2: float, startup_time_ocp_f_cam_v_an3:
                 float, startup_time_ocp_f_cam_v_dig: float) -> None:
        """ Configure start-up and detection time [s].

        The start-up time is the period of time during which protections are being ignored, upon start-up.

        The trip time is the period of time over which:

            - the voltage must exceed the configured OVP limit, in order for an OVP detection to be triggered;
            - the voltage must be below the configured OVP limit, in order for an UVP detection to be triggered;
            - the current must exceeed the configured OCP limit, in order for an OCP detection to be triggered.

        Args:
            - trip_time_ovp_n_cam_v_ccd: Trip time for the N-CAM Over-Voltage Protection (OVP) for V_CCD [ms].
            - trip_time_ovp_n_cam_v_clk: Trip time for the N-CAM Over-Voltage Protection (OVP) for V_CLK [ms].
            - trip_time_ovp_n_cam_v_an1: Trip time for the N-CAM Over-Voltage Protection (OVP) for V_AN1 [ms].
            - trip_time_ovp_n_cam_v_an2: Trip time for the N-CAM Over-Voltage Protection (OVP) for V_AN2 [ms].
            - trip_time_ovp_n_cam_v_an3: Trip time for the N-CAM Over-Voltage Protection (OVP) for V_AN3 [ms].
            - trip_time_ovp_n_cam_v_dig: Trip time for the N-CAM Over-Voltage Protection (OVP) for V_DIG [ms].
            - trip_time_ovp_f_cam_v_ccd: Trip time for the F-CAM Over-Voltage Protection (OVP) for V_CCD [ms].
            - trip_time_ovp_f_cam_v_clk: Trip time for the F-CAM Over-Voltage Protection (OVP) for V_CLK [ms].
            - trip_time_ovp_f_cam_v_an1: Trip time for the F-CAM Over-Voltage Protection (OVP) for V_AN1 [ms].
            - trip_time_ovp_f_cam_v_an2: Trip time for the F-CAM Over-Voltage Protection (OVP) for V_AN2 [ms].
            - trip_time_ovp_f_cam_v_an3: Trip time for the F-CAM Over-Voltage Protection (OVP) for V_AN3 [ms].
            - trip_time_ovp_f_cam_v_dig: Trip time for the F-CAM Over-Voltage Protection (OVP) for V_DIG [ms].
            - trip_time_uvp_n_cam_v_ccd: Trip time for the N-CAM Under-Voltage Protection (UVP) for V_CCD [ms].
            - trip_time_uvp_n_cam_v_clk: Trip time for the N-CAM Under-Voltage Protection (UVP) for V_CLK [ms].
            - trip_time_uvp_n_cam_v_an1: Trip time for the N-CAM Under-Voltage Protection (UVP) for V_AN1 [ms].
            - trip_time_uvp_n_cam_v_an2: Trip time for the N-CAM Under-Voltage Protection (UVP) for V_AN2 [ms].
            - trip_time_uvp_n_cam_v_an3: Trip time for the N-CAM Under-Voltage Protection (UVP) for V_AN3 [ms].
            - trip_time_uvp_n_cam_v_dig: Trip time for the N-CAM Under-Voltage Protection (UVP) for V_DIG [ms].
            - trip_time_uvp_f_cam_v_ccd: Trip time for the F-CAM Under-Voltage Protection (UVP) for V_CCD [ms].
            - trip_time_uvp_f_cam_v_clk: Trip time for the F-CAM Under-Voltage Protection (UVP) for V_CLK [ms].
            - trip_time_uvp_f_cam_v_an1: Trip time for the F-CAM Under-Voltage Protection (UVP) for V_AN1 [ms].
            - trip_time_uvp_f_cam_v_an2: Trip time for the F-CAM Under-Voltage Protection (UVP) for V_AN2 [ms].
            - trip_time_uvp_f_cam_v_an3: Trip time for the F-CAM Under-Voltage Protection (UVP) for V_AN3 [ms].
            - trip_time_uvp_f_cam_v_dig: Trip time for the F-CAM Under-Voltage Protection (UVP) for V_DIG [ms].
            - trip_time_ocp_n_cam_v_ccd: Trip time for the N-CAM Over-Current Protection (OCP) for V_CCD [ms].
            - trip_time_ocp_n_cam_v_clk: Trip time for the N-CAM Over-Current Protection (OCP) for V_CLK [ms].
            - trip_time_ocp_n_cam_v_an1: Trip time for the N-CAM Over-Current Protection (OCP) for V_AN1 [ms].
            - trip_time_ocp_n_cam_v_an2: Trip time for the N-CAM Over-Current Protection (OCP) for V_AN2 [ms].
            - trip_time_ocp_n_cam_v_an3: Trip time for the N-CAM Over-Current Protection (OCP) for V_AN3 [ms].
            - trip_time_ocp_n_cam_v_dig: Trip time for the N-CAM Over-Current Protection (OCP) for V_DIG [ms].
            - trip_time_ocp_f_cam_v_ccd: Trip time for the F-CAM Over-Current Protection (OCP) for V_CCD [ms].
            - trip_time_ocp_f_cam_v_clk: Trip time for the F-CAM Over-Current Protection (OCP) for V_CLK [ms].
            - trip_time_ocp_f_cam_v_an1: Trip time for the F-CAM Over-Current Protection (OCP) for V_AN1 [ms].
            - trip_time_ocp_f_cam_v_an2: Trip time for the F-CAM Over-Current Protection (OCP) for V_AN2 [ms].
            - trip_time_ocp_f_cam_v_an3: Trip time for the F-CAM Over-Current Protection (OCP) for V_AN3 [ms].
            - trip_time_ocp_f_cam_v_dig: Trip time for the F-CAM Over-Current Protection (OCP) for V_DIG [ms].
            - startup_time_ovp_n_cam_v_ccd: Start-up time for the N-CAM Over-Voltage Protection (OVP) for V_CCD [ms].
            - startup_time_ovp_n_cam_v_clk: Start-up time for the N-CAM Over-Voltage Protection (OVP) for V_CLK [ms].
            - startup_time_ovp_n_cam_v_an1: Start-up time for the N-CAM Over-Voltage Protection (OVP) for V_AN1 [ms].
            - startup_time_ovp_n_cam_v_an2: Start-up time for the N-CAM Over-Voltage Protection (OVP) for V_AN2 [ms].
            - startup_time_ovp_n_cam_v_an3: Start-up time for the N-CAM Over-Voltage Protection (OVP) for V_AN3 [ms].
            - startup_time_ovp_n_cam_v_dig: Start-up time for the N-CAM Over-Voltage Protection (OVP) for V_DIG [ms].
            - startup_time_ovp_f_cam_v_ccd: Start-up time for the F-CAM Over-Voltage Protection (OVP) for V_CCD [ms].
            - startup_time_ovp_f_cam_v_clk: Start-up time for the F-CAM Over-Voltage Protection (OVP) for V_CLK [ms].
            - startup_time_ovp_f_cam_v_an1: Start-up time for the F-CAM Over-Voltage Protection (OVP) for V_AN1 [ms].
            - startup_time_ovp_f_cam_v_an2: Start-up time for the F-CAM Over-Voltage Protection (OVP) for V_AN2 [ms].
            - startup_time_ovp_f_cam_v_an3: Start-up time for the F-CAM Over-Voltage Protection (OVP) for V_AN3 [ms].
            - startup_time_ovp_f_cam_v_dig: Start-up time for the F-CAM Over-Voltage Protection (OVP) for V_DIG [ms].
            - startup_time_uvp_n_cam_v_ccd: Start-up time for the N-CAM Under-Voltage Protection (UVP) for V_CCD [ms].
            - startup_time_uvp_n_cam_v_clk: Start-up time for the N-CAM Under-Voltage Protection (UVP) for V_CLK [ms].
            - startup_time_uvp_n_cam_v_an1: Start-up time for the N-CAM Under-Voltage Protection (UVP) for V_AN1 [ms].
            - startup_time_uvp_n_cam_v_an2: Start-up time for the N-CAM Under-Voltage Protection (UVP) for V_AN2 [ms].
            - startup_time_uvp_n_cam_v_an3: Start-up time for the N-CAM Under-Voltage Protection (UVP) for V_AN3 [ms].
            - startup_time_uvp_n_cam_v_dig: Start-up time for the N-CAM Under-Voltage Protection (UVP) for V_DIG [ms].
            - startup_time_uvp_f_cam_v_ccd: Start-up time for the F-CAM Under-Voltage Protection (UVP) for V_CCD [ms].
            - startup_time_uvp_f_cam_v_clk: Start-up time for the F-CAM Under-Voltage Protection (UVP) for V_CLK [ms].
            - startup_time_uvp_f_cam_v_an1: Start-up time for the F-CAM Under-Voltage Protection (UVP) for V_AN1 [ms].
            - startup_time_uvp_f_cam_v_an2: Start-up time for the F-CAM Under-Voltage Protection (UVP) for V_AN2 [ms].
            - startup_time_uvp_f_cam_v_an3: Start-up time for the F-CAM Under-Voltage Protection (UVP) for V_AN3 [ms].
            - startup_time_uvp_f_cam_v_dig: Start-up time for the F-CAM Under-Voltage Protection (UVP) for V_DIG [ms].
            - startup_time_ocp_n_cam_v_ccd: Start-up time for the N-CAM Over-Current Protection (OCP) for V_CCD [ms].
            - startup_time_ocp_n_cam_v_clk: Start-up time for the N-CAM Over-Current Protection (OCP) for V_CLK [ms].
            - startup_time_ocp_n_cam_v_an1: Start-up time for the N-CAM Over-Current Protection (OCP) for V_AN1 [ms].
            - startup_time_ocp_n_cam_v_an2: Start-up time for the N-CAM Over-Current Protection (OCP) for V_AN2 [ms].
            - startup_time_ocp_n_cam_v_an3: Start-up time for the N-CAM Over-Current Protection (OCP) for V_AN3 [ms].
            - startup_time_ocp_n_cam_v_dig: Start-up time for the N-CAM Over-Current Protection (OCP) for V_DIG [ms].
            - startup_time_ocp_f_cam_v_ccd: Start-up time for the F-CAM Over-Current Protection (OCP) for V_CCD [ms].
            - startup_time_ocp_f_cam_v_clk: Start-up time for the F-CAM Over-Current Protection (OCP) for V_CLK [ms].
            - startup_time_ocp_f_cam_v_an1: Start-up time for the F-CAM Over-Current Protection (OCP) for V_AN1 [ms].
            - startup_time_ocp_f_cam_v_an2: Start-up time for the F-CAM Over-Current Protection (OCP) for V_AN2 [ms].
            - startup_time_ocp_f_cam_v_an3: Start-up time for the F-CAM Over-Current Protection (OCP) for V_AN3 [ms].
            - startup_time_ocp_f_cam_v_dig: Start-up time for the F-CAM Over-Current Protection (OCP) for V_DIG [ms].
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="SYST:TIME:PROT?",
                     process_cmd_string=add_crio_terminator,
                     process_response=parse_floats)
    def get_time(self) -> (float, float):
        """ Return the start-up and detection time [ms].

        The start-up time is the period of time during which protections are being ignored, upon start-up.

        The detection time is the period of time over which:

            - the voltage must exceed the configured OVP limit, in order for an OVP detection to be triggered;
            - the voltage must be below the configured OVP limit, in order for an UVP detection to be triggered;
            - the current must exceeed the configured OCP limit, in order for an OCP detection to be triggered.

        Returns:
            - Start-up time [ms].
            - Detection time [ms].
        """

        raise NotImplementedError


class PSUInterface(DeviceInterface):
    """ AEU device interface for the PSU."""

    def __init__(self, psu_index: int):
        """ Initialisation of a PSU device interface with the given index.

        Args:
            - psu_index: Index of the PSU (should be 1..6).
        """

        super().__init__()

        self.device_name = "PSU" + str(psu_index)
        self.psu_index = psu_index

    @dynamic_command(cmd_type="query",
                     cmd_string="*IDN?",
                     process_cmd_string=add_psu_terminator,
                     process_response=parse_psu_instrument_id)
    def get_id(self) -> (str, str, str, str, str):
        """ Return the instrument identification of the PSU.

        Returns:
            - Manufacturer of the PSU
            - Model of the PSU
            - Serial number of the PSU
            - IFC version and build number
            - IOC version and build number
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="*RST",
                     process_cmd_string=add_psu_terminator)
    def reset(self) -> None:
        """ Reset the PSU settings.

        Reset the panel settings, clear alarms, abort the trigger sub-system operation, clear the OPC bit (bit0) of
        the status event register.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="*TST",
                     process_cmd_string=add_psu_terminator,
                     process_response=parse_ints)
    def test(self) -> int:
        """ Execute a self-test.

        Returns: Result of the self-test.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="SYST:ERR?",
                     process_cmd_string=add_psu_terminator,
                     process_response=parse_psu_error_info)
    def get_error_info(self) -> (int, str):
        """ Read the oldest error information the error queue.

        The error queue can store up to 16 errors. Use the clear_psu command to clear the error queue.

        Returns:
            - Identifier of the oldest error in the error queue.
            - Description of the oldest error in the error queue.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="*CLS",
                     process_cmd_string=add_psu_terminator)
    def clear(self) -> None:
        """ Clear all event registers, including the status byte, event status, and error queue."""

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="INST ${channel}",
                     process_cmd_string=add_psu_terminator)
    def set_channel(self, channel: int) -> None:
        """ Specify the channel to configure

        Args:
            - channel: Channel to configure.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="INST?",
                     process_cmd_string=add_psu_terminator,
                     process_response=parse_ints)
    def get_channel(self) -> int:
        """ Return the channel to configure.

        Returns: Channel to configure.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="INST:CAT?",
                     process_cmd_string=add_psu_terminator,
                     process_response=parse_ints)
    def get_channel_list(self) -> int:
        """ Return the list of channels that can be configured with the set_channel command.

        Returns:  List of channels that can be configured with the set_channel command.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="INST:INFO?",
                     process_cmd_string=add_psu_terminator,
                     process_response=parse_floats)
    def get_channel_info(self) -> (float, float):
        """
        Return the information of the channel currently being controlled.

        Returns:
            - Maximum voltage of the channel [V].
            - Maximum current of the channel [A].
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="MEAS:CURR?",
                     process_cmd_string=add_psu_terminator,
                     process_response=parse_floats)
    def get_current(self) -> float:
        """ Return the measured value of the current [A].

        Returns:  Measured value of the current [A].
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="MEAS:VOLT?",
                     process_cmd_string=add_psu_terminator,
                     process_response=parse_floats)
    def get_voltage(self) -> float:
        """ Return the measured value of the voltage [V].

        Returns: Measured value of the voltage [V].
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="MEM:REC ${memory}",
                     process_cmd_string=add_psu_terminator)
    def recall_memory(self, memory: Memory) -> None:
        """ Recall the settings stored in the given pre-set memory.

        Recall the settings (current, voltage, OCP (Over-Current Protection), and OVP (Over-Voltage Protection)) stored
        in the pre-set memory (1 for memory A, 2 for memory B, 3 for memory C).  When recalling a pre-set memory when
        the output is turned on, the setting stored in the memory will be applied immediately.

        Args:
            - memory: Pre-set memory identifier (1 or Memory.A for memory A, 2 or Memory.B for memory B, 3 or Memory.C
                      for memory C).
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="MEM:REC:CONF ${conf}",
                     process_cmd_string=add_psu_terminator)
    def conf_settings(self, conf: IntSwitch) -> None:
        """ Confirm (or not) the settings.

        Set whether or not to check the content saved in the pre-set memory (current, voltage, OCP (Over-Current
        Protection), and OVP (Over-Voltage Protection)), when recalling it from the control panel (1 to confirm the
        settings, 0 to reject the settings).  When recalling the memory with the recall_psu_memory command, the settings
        stored in the pre-set memory will be recalled immediately.

        Args:
            - conf: Indicates whether or not to check the content saved in the pre-set memory (current, voltage, OCP
                    (Over-Current Protection), and OVP (Over-Voltage Protection)), when recalling it from the control
                    panel.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="MEM:REC:CONF?",
                     process_cmd_string=add_psu_terminator,
                     process_response=parse_ints)
    def get_memory_config(self) -> IntSwitch:
        """ Query whether to check the content saved in the pre-set memory when recalling them from the control panel.

        Query whether or not to check the content (current, voltage, OCP (Over-Current Protection), and OVP
        (Over-Voltage Protection)) saved in the pre-set memory when recalling them from the control panel.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="MEM:REC:PREV? ${memory}",
                     process_cmd_string=add_psu_terminator,
                     process_response=parse_floats)
    def get_memory_setting(self, memory: Memory) -> (float, float, float, float):
        """ Return the settings stored in the given pre-set memory.

        Args:
            - memory: Pre-set memory identifier (1 for memory A, 2 for memory B, 3 for memory C).

        Returns:
            - Current [A] as stored in memory.
            - Voltage [V] as stored in memory.
            - Over-Current Protection (OCP) [A] as stored in memory.
            - Over-Voltage Protection (OCP) [V] as stored in memory.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="MEM:SAVE ${memory}",
                     process_cmd_string=add_psu_terminator)
    def save_memory(self, memory: Memory) -> None:
        """ Save to the pre-set memory.

        The current, voltage, OCP (Over-Current Protection), and OVP (Over-Voltage Protection) are saved in the pre-set
        memory.

        Args:
            - memory: Pre-set memory identifier (1 or Memory.A for memory A, 2 or Memory.B for memory B, 3 or Memory.C
                      for memory C).
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write", cmd_string="OUTP ${output_status}", process_cmd_string=add_psu_terminator)
    def set_output_status(self, output_status: IntSwitch) -> None:
        """ Set the output status and type (0/1).

        Set the output status and type (0/1).  This command is invalid when a protection function is activated.  The
        settings are reset to default with the reset_psu command.

        Args:
            - out: Indicates whether or not the output should be switched on.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="OUTP?",
                     process_cmd_string=add_psu_terminator,
                     process_response=parse_ints)
    def get_output_status(self) -> IntSwitch:
        """ Return the output status.

        Returns: 1 of the output is enabled, 0 otherwise.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="CURR ${current}",
                     process_cmd_string=add_psu_terminator)
    def set_current(self, current: float) -> None:
        """ Set the current to the given value [A].

        This is invalid when the PMX is configured such that constant current is controlled externally.  The settings
        are set to the default values with the reset command.

        Args:
            - current: Current to configure [A].
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="CURR?",
                     process_cmd_string=add_psu_terminator,
                     process_response=parse_floats)
    def get_current_config(self) -> float:
        """ Return the actual current configuration [A].

        Returns: Actual current configuration [A].
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="CURR:PROT ${ocp}",
                     process_cmd_string=add_psu_terminator)
    def set_ocp(self, ocp: float) -> None:
        """ Set the Over-Current Protection (OCP) value [A].

        Args:
            - ocp: Over-Current Protection (OCP) [A] to configure.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="CURR:PROT?",
                     process_cmd_string=add_psu_terminator,
                     process_response=parse_floats)
    def get_ocp(self) -> float:
        """ Return the Over-Current Protection (OCP) value [A].

        Returns: Actual Over-Current Protection configuration [A].
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="VOLT ${voltage}",
                     process_cmd_string=add_psu_terminator)
    def set_voltage(self, voltage: float) -> None:
        """ Set the voltage to the given value [V].

        This is invalid when the PMX is configured such that constant voltage is controlled externally.  The settings
        are set to the default values with the reset command.

        Args:
            - voltage: Voltage to configure [V].
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="VOLT?",
                     process_cmd_string=add_psu_terminator,
                     process_response=parse_floats)
    def get_voltage_config(self) -> float:
        """ Return the actual voltage configuration [V].

        Returns: Actual voltage configuration [V].
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="VOLT:PROT ${ovp}",
                     process_cmd_string=add_psu_terminator)
    def set_ovp(self, ovp: float) -> None:
        """ Set the Over-Voltage Protection (OVP) value [V].

        Args:
            - ocp: Over-Voltage Protection (OVP) [V] to configure.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="VOLT:PROT?",
                     process_cmd_string=add_psu_terminator,
                     process_response=parse_floats)
    def get_ovp(self) -> float:
        """ Return the Over-Voltage Protection (OVP) value [V].

        Returns: Actual Over-Voltage Protection configuration [V].
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="SYST:CONF:STAR:PRI ${priority_mode}",
                     process_cmd_string=add_psu_terminator)
    def set_priority_mode(self, priority_mode: PriorityMode) -> None:
        """ Set the operation mode to be prioritised when the output is turned on.

        Args:
            - priority_mode: Priority mode to configure.  Should be CC or PriorityMode.CONSTANT_CURRENT for Constant
                             Current, CV or PriorityMode.CONSTANT_VOLTAGE for Constant Voltage.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="SYST:CONF:STAR:PRI?",
                     process_cmd_string=add_psu_terminator,
                     process_response=parse_strings)
    def get_priority_mode(self) -> PriorityMode:
        """ Return the operation mode to be prioritised when the output is turned on.

        Possible values are:

            - "CC" (PriorityMode.CONSTANT_CURRENT): to prioritise constant current;
            - "CV" (PriorityMode.CONSTANT_VOLTAGE): to prioritise constant voltage.

        Returns: Configured priority mode.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="OUTP:PROT:CLE",
                     process_cmd_string=add_psu_terminator)
    def clear_alarms(self) -> None:
        """ Clear all alarms."""

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="STAT:QUES:COND?",
                     process_cmd_string=add_psu_terminator,
                     process_response=parse_ints)
    def questionable_status_register(self) -> int:
        """ Query the status of the questionable status register.

        A query does not clear the content of the register.  This command is useful to get the events and status during
        PMX operation (e.g. when the PSU detects and OVP or OCP).

        Returns: Questionable events and status register.  The questionable status register is a 16-bit register that
                 stores information related to the questionable events and status:
                    - bit 0: Over-Voltage Protection (OVP) has been activated;
                    - bit 1: Over-Current Protection (OCP) has been activated;
                    - bit 2: AC power failure or power interruption;
                    - bit 3: Not used;
                    - bit 4: Over-Temperature Protection has been activated:
                    - bit 5..15: Not used.
        """

        raise NotImplementedError


class AWGInterface(DeviceInterface):
    """ AEU device interface for the AWG."""

    def __init__(self, awg_index: int):
        """ Initialisation of an AWG device interface with the given index.

        Args:
             - awg_index: Index of the AWG (should be 1 or 2).
        """

        super().__init__()

        self.device_name = "AWG" + str(awg_index)
        self.awg_index = awg_index

    @dynamic_command(cmd_type="write",
                     cmd_string="*RST",
                     process_cmd_string=add_awg_terminator)
    def reset(self) -> None:
        """ Reset the instrument to the remote operation default settings."""

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="CHN ${channel}",
                     process_cmd_string=add_awg_terminator)
    def set_channel(self, channel: int) -> None:
        """ Select the given channel as the destination for sub-sequent commands.

        Args:
            - channel: Destination channel (should be 1 or 2).
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="CHN?",
                     process_cmd_string=add_awg_terminator,
                     process_response=parse_ints)
    def get_channel(self) -> int:
        """ Return the currently selected channel number.

        Returns: Currently selected channel number (1 or 2).
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="WAVE ${waveform_type}",
                     process_cmd_string=add_awg_terminator)
    def set_waveform_type(self, waveform_type: Waveform) -> None:
        """ Set the output waveform type.

        Possible values are:

            - Waveform.ARB or "ARB" for arbitrary;
            - Waveform.SQUARE or "SQUARE" for square.

        Other values van be set, but for the current system only these two should be used.

        Args:
            - waveform_type: Waveform (Waveform.ARB or "ARB" for arbitrary, Waveform.SQUARE or "SQUARE" for square).
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="WAVE?",
                     process_cmd_string=add_awg_terminator,
                     process_response=parse_ints)
    def get_waveform_type(self) -> Waveform:
        """ Return the output waveform type.

        Returns: Waveform type (Waveform.ARB or "ARB" for arbitrary, Waveform.SQUARE or "SQUARE" for square).
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="ZLOAD ${load}",
                     process_cmd_string=add_awg_terminator)
    def set_output_load(self, load: float) -> None:
        """ Set the output load [Ohm], which the generator is to assume for amplitude and DC offset entries.

        For the current system only 50 Ohm should be used.

        Args:
            - load: Output load [Ohm].
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="ZLOAD?",
                     process_cmd_string=add_awg_terminator,
                     process_response=parse_floats)
    def get_output_load(self) -> float:
        """ Return the output load.

        Returns: Output load [Ohm].
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="AMPL ${amplitude}",
                     process_cmd_string=add_awg_terminator)
    def set_amplitude(self, amplitude: float) -> None:
        """ Set the amplitude to the given value.

        Args:
            - amplitude: Amplitude [Vpp].
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="AMPL?",
                     process_cmd_string=add_awg_terminator,
                     process_response=parse_floats)
    def get_amplitude(self) -> float:
        """ Return the amplitude.

        Returns: Amplitude [Vpp].
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="DCOFFS ${offset}",
                     process_cmd_string=add_awg_terminator)
    def set_dc_offset(self, offset: float) -> None:
        """ Set the DC offset to the given value.

        Args:
            - offset: DC offset [V].
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="DCOFFS?",
                     process_cmd_string=add_awg_terminator,
                     process_response=parse_floats)
    def get_dc_offset(self) -> float:
        """ Return the DC offset.

        Returns: DC offset [V].
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="SQRSYMM ${duty_cycle}",
                     process_cmd_string=add_awg_terminator)
    def set_duty_cycle(self, duty_cycle: float):
        """ Set the square waveform symmetry.

        Args:
            - duty: Duty cycle [%] used to square waveforms.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="SQRSYMM?",
                     process_cmd_string=add_awg_terminator,
                     process_response=parse_floats)
    def get_duty_cycle(self) -> float:
        """ Return the square waveform symmetry.

        Returns: Square waveform symmetry, as duty cycle [%].
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="FREQ ${frequency}",
                     process_cmd_string=add_awg_terminator)
    def set_frequency(self, frequency: float):
        """ Set the waveform frequency.

        Args:
            - frequency: Waveform frequency [Hz].
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="FREQ?",
                     process_cmd_string=add_awg_terminator,
                     process_response=parse_floats)
    def get_frequency(self) -> float:
        """ Return the waveform frequency.

        Returns: Waveform frequency [Hz].
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="OUTPUT ${output_status}",
                     process_cmd_string=add_awg_terminator)
    def set_output_status(self, output_status: Switch) -> None:
        """ Set the output status and type (ON/OFF).

        Other values van be set, but for the current system only these should be used.

        Args:
            - out: ON/OFF.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="OUTPUT?",
                     process_cmd_string=add_awg_terminator,
                     process_response=parse_ints)
    def get_output_status(self) -> Switch:
        """ Return the output status and type.

        Returns: Whether or not the output has been enabled (Switch.ON or Switch.OFF).
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="ARBLOAD ${arb}",
                     process_cmd_string=add_awg_terminator)
    def set_arb_waveform(self, arb: ARB):
        """ Set the given arbitrary waveform type.

        Possible values are:

            - ARB.ARB1;
            - ARB.ARB2;
            - ARB.ARB3;
            - ARB.ARB4.

        Other values van be set, but for the current system only these should be used.

        Args:
            - arb: Arbitrary waveform type (ARB1/ARB2/ARB3/ARB4).
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="ARBLOAD?",
                     process_cmd_string=add_awg_terminator)
    def get_arb_waveform(self) -> ARB:
        """ Return the arbitrary waveform type (ARB1/ARB2/ARB3/ARB4).

        Returns: Arbitrary waveform type (ARB1/ARB2/ARB3/ARB4).
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="ARBDEF ${arb}, ${name}, ${interpolation}",
                     process_cmd_string=add_awg_terminator)
    def define_arb_waveform(self, arb: ARB, name: str, interpolation: Switch):
        """ Definition of an arbitrary waveform.

        Define an arbitrary waveform (ARB1/ARB2/ARB3/ARB5) with the given name and waveform point interpolation state
        (ON/OFF).

        Args:
            - arb: Arbitrary waveform type (ARB1/ARB2/ARB3/ARB4).
            - name: Name (capitalised, no numbers).
            - interpolation: Indicates whether or not to use waveform point interpolation.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="ARB1 ${binary}",
                     process_cmd_string=parse_arb_data)
    def load_arb1_data(self, binary: ArbDataFile) -> None:
        """ Load data to an existing arbitrary waveform memory location ARB1.

        This command does not need the command terminator code 0x0A (Line Feed).

        The waveform memory size is 8192 points, with a vertical resolution of 16 bits.

        Args:
            - binary: Data consisting of two bytes per point with no characters between bytes or points. The point data
                      is sent high byte first. The data block has a header which consists of the # character followed by
                      several ascii coded numeric characters. The first of these defines the number of ascii characters
                      to follow and these following characters define the length of the binary data in bytes. The
                      instrument will wait for data indefinitely If less data is sent. If more data is sent the extra is
                      processed by the command parser which results in a command error.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="ARB2 ${binary}",
                     process_cmd_string=parse_arb_data)
    def load_arb2_data(self, binary: ArbDataFile) -> None:
        """ Load data to an existing arbitrary waveform memory location ARB2.

        This command does not need the command terminator code 0x0A (Line Feed).

        The waveform memory size is 8192 points, with a vertical resolution of 16 bits.

        Args:
            - binary: Data consisting of two bytes per point with no characters between bytes or points. The point data
                      is sent high byte first. The data block has a header which consists of the # character followed by
                      several ascii coded numeric characters. The first of these defines the number of ascii characters
                      to follow and these following characters define the length of the binary data in bytes. The
                      instrument will wait for data indefinitely If less data is sent. If more data is sent the extra is
                      processed by the command parser which results in a command error.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="ARB3 ${binary}",
                     process_cmd_string=parse_arb_data)
    def load_arb3_data(self, binary: ArbDataFile) -> None:
        """ Load data to an existing arbitrary waveform memory location ARB3.

        This command does not need the command terminator code 0x0A (Line Feed).

        The waveform memory size is 8192 points, with a vertical resolution of 16 bits.

        Args:
            - binary: Data consisting of two bytes per point with no characters between bytes or points. The point data
                      is sent high byte first. The data block has a header which consists of the # character followed by
                      several ascii coded numeric characters. The first of these defines the number of ascii characters
                      to follow and these following characters define the length of the binary data in bytes. The
                      instrument will wait for data indefinitely If less data is sent. If more data is sent the extra is
                      processed by the command parser which results in a command error.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="ARB4 ${binary}",
                     process_cmd_string=parse_arb_data)
    def load_arb4_data(self, binary: ArbDataFile) -> None:
        """ Load data to an existing arbitrary waveform memory location ARB4.

        This command does not need the command terminator code 0x0A (Line Feed).

        The waveform memory size is 8192 points, with a vertical resolution of 16 bits.

        Args:
            - binary: Data consisting of two bytes per point with no characters between bytes or points. The point data
                      is sent high byte first. The data block has a header which consists of the # character followed by
                      several ascii coded numeric characters. The first of these defines the number of ascii characters
                      to follow and these following characters define the length of the binary data in bytes. The
                      instrument will wait for data indefinitely If less data is sent. If more data is sent the extra is
                      processed by the command parser which results in a command error.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="ARB1 ${binary}")
    def load_arb1_ascii(self, binary: str) -> None:

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="ARB2 ${binary}")
    def load_arb2_ascii(self, binary: str) -> None:

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="ARB3 ${binary}")
    def load_arb3_ascii(self, binary: str) -> None:

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="ARB4 ${binary}")
    def load_arb4_ascii(self, binary: str) -> None:

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="ARB1DEF?",
                     process_cmd_string=add_awg_terminator,
                     process_response=parse_arb_def)
    def get_arb1_def(self) -> (str, Switch, int):
        """ Return the user-specified waveform name, waveform point interpolation state, and waveform length of ARB1.

        Returns:
            - Waveform name for ARB1.
            - Waveform point interpolation state for ARB1.
            - Waveform length of ARB1.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="ARB2DEF?",
                     process_cmd_string=add_awg_terminator,
                     process_response=parse_arb_def)
    def get_arb2_def(self) -> (str, Switch, int):
        """ Return the user-specified waveform name, waveform point interpolation state, and waveform length of ARB2.

        Returns:
            - Waveform name for ARB2.
            - Waveform point interpolation state for ARB2.
            - Waveform length of ARB2.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="ARB3DEF?",
                     process_cmd_string=add_awg_terminator,
                     process_response=parse_arb_def)
    def get_arb3_def(self) -> (str, Switch, int):
        """ Return the user-specified waveform name, waveform point interpolation state, and waveform length of ARB3.

        Returns:
            - Waveform name for ARB3.
            - Waveform point interpolation state for ARB3.
            - Waveform length of ARB3.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="ARB4DEF?",
                     process_cmd_string=add_awg_terminator,
                     process_response=parse_arb_def)
    def get_arb4_def(self) -> (str, Switch, int):
        """ Return the user-specified waveform name, waveform point interpolation state, and waveform length of ARB4.

        Returns:
            - Waveform name for ARB4.
            - Waveform point interpolation state for ARB4.
            - Waveform length of ARB4.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="ARB1?",
                     process_cmd_string=add_awg_terminator,
                     process_response=parse_arb_data_response)
    def get_arb1(self) -> str:
        """ Return the data from the existing arbitrary waveform location ARB1.

        This command does not need the command terminator code 0x0A (Line Feed).

        The waveform memory size is 8192 points, with a vertical resolution of 16 bits.

        Returns: Data consisting of two bytes per point with no characters between bytes or points. The point data is
                 sent high byte first. The data block has a header which consists of the # character followed by
                 several ascii coded numeric characters. The first of these defines the number of ascii characters to
                 follow and these following characters define the length of the binary data in bytes. The instrument
                 will wait for data indefinitely If less data is sent. If more data is sent the extra is
                 processed by the command parser which results in a command error.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="ARB2?",
                     process_cmd_string=add_awg_terminator,
                     process_response=parse_arb_data_response)
    def get_arb2(self) -> str:
        """ Return the data from the existing arbitrary waveform location ARB2.

        This command does not need the command terminator code 0x0A (Line Feed).

        The waveform memory size is 8192 points, with a vertical resolution of 16 bits.

        Returns: Data consisting of two bytes per point with no characters between bytes or points. The point data is
                 sent high byte first. The data block has a header which consists of the # character followed by
                 several ascii coded numeric characters. The first of these defines the number of ascii characters to
                 follow and these following characters define the length of the binary data in bytes. The instrument
                 will wait for data indefinitely If less data is sent. If more data is sent the extra is
                 processed by the command parser which results in a command error.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="ARB3?",
                     process_cmd_string=add_awg_terminator,
                     process_response=parse_arb_data_response)
    def get_arb3(self) -> str:
        """ Return the data from the existing arbitrary waveform location ARB3.

        This command does not need the command terminator code 0x0A (Line Feed).

        The waveform memory size is 8192 points, with a vertical resolution of 16 bits.

        Returns: Data consisting of two bytes per point with no characters between bytes or points. The point data is
                 sent high byte first. The data block has a header which consists of the # character followed by
                 several ascii coded numeric characters. The first of these defines the number of ascii characters to
                 follow and these following characters define the length of the binary data in bytes. The instrument
                 will wait for data indefinitely If less data is sent. If more data is sent the extra is
                 processed by the command parser which results in a command error.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="ARB4?",
                     process_cmd_string=add_awg_terminator,
                     process_response=parse_arb_data_response)
    def get_arb4(self) -> str:
        """ Return the data from the existing arbitrary waveform location ARB4.

        This command does not need the command terminator code 0x0A (Line Feed).

        The waveform memory size is 8192 points, with a vertical resolution of 16 bits.

        Returns: Data consisting of two bytes per point with no characters between bytes or points. The point data is
                 sent high byte first. The data block has a header which consists of the # character followed by
                 several ascii coded numeric characters. The first of these defines the number of ascii characters to
                 follow and these following characters define the length of the binary data in bytes. The instrument
                 will wait for data indefinitely If less data is sent. If more data is sent the extra is
                 processed by the command parser which results in a command error.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="*CLS",
                     process_cmd_string=add_awg_terminator)
    def clear_status(self) -> None:
        """ Clear the status structure.

        This indirectly clears the status byte register.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="EER?",
                     process_cmd_string=add_awg_terminator,
                     process_response=parse_ints)
    def execution_error_register(self) -> int:
        """ Query and clear the execution error register.

        This register contains a number representing the last error encountered over the current interface.

        Returns: Execution error register.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="QER?",
                     process_cmd_string=add_awg_terminator,
                     process_response=parse_ints)
    def query_error_register(self) -> int:
        """ Query and clear the query error register.

        Returns: Query error register.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="*IDN?",
                     process_cmd_string=add_awg_terminator,
                     process_response=parse_awg_instrument_id)
    def get_id(self) -> (str, str, str, float, float, float):
        """ Return the instrument identification.

        Returns:
            - Manufacturer.
            - Model.
            - Serial number.
            - Revision of the main firmware (XX.xx).
            - Revision of the remote interface firmware (YY.yy).
            - Revision of the USB flash drive firmware (ZZ.zz).
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="CNTRSWT ${counter_status}",
                     process_cmd_string=add_awg_terminator)
    def set_counter_status(self, counter_status: Switch) -> None:
        """ Set the external counter to ON or OFF.

        Args:
            - status: ON/OFF.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="CNTRSWT?",
                     process_cmd_string=add_awg_terminator,
                     process_response=parse_strings)
    def get_counter_status(self) -> Switch:
        """ Return the external counter status (ON/OFF).

        Returns:
             - External counter status (ON/OFF).
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="CNTRCPLNG ${counter_source}",
                     process_cmd_string=add_awg_terminator)
    def set_counter_source(self, counter_source: CounterSource):
        """ Set the counter source to AC (Alternating Current) or DC (Direct Current) coupled input.

        Args:
            - counter_source: "AC" or CounterSource.AC for Alternating Current, "DC" or CounterSource.DC for Direct
                              Current coupled input.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="CNTRCPLNG?",
                     process_cmd_string=add_awg_terminator,
                     process_response=parse_strings)
    def get_counter_source(self) -> CounterSource:
        """ Return the counter source coupled input (AC for Alternating Current, DC for Direct Current).

        Returns: CounterSource.AC or "AC" for Alternating Current, CounterSource.DC or "DC" for Direct Current coupled
                 input.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="CNTRTYPE ${counter_type}",
                     process_cmd_string=add_awg_terminator)
    def set_counter_type(self, counter_type: CounterType) -> None:
        """ Set the counter type.

        Possible values are:

            - "FREQUENCY" (CounterType.FREQUENCY): measure the frequency of the signal;
            - "PERIOD" (CounterType.PERIOD): measure the period of the signal;
            - "WIDTH" (CounterType.WIDTH): measure the positive width of the signal;
            - "NWIDTH" (CounterType.NWIDTH): measure the negative width of the signal;
            - "DUTY" (CounterType.DUTY): measure the duty cycle of the signal.

        Args:
            - Counter type (FREQUENCY/PERIOD/WIDTH/NWIDTH/DUTY).
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="CNTRTYPE?",
                     process_cmd_string=add_awg_terminator,
                     process_response=parse_strings)
    def get_counter_type(self) -> CounterType:
        """ Return the counter type.

        Possible values are:

            - "FREQUENCY" (CounterType.FREQUENCY): measure the frequency of the signal;
            - "PERIOD" (CounterType.PERIOD): measure the period of the signal;
            - "WIDTH" (CounterType.WIDTH): measure the positive width of the signal;
            - "NWIDTH" (CounterType.NWIDTH): measure the negative width of the signal;
            - "DUTY" (CounterType.DUTY): measure the duty cycle of the signal.

        Returns:
            - Counter type (FREQUENCY/PERIOD/WIDTH/NWIDTH/DUTY).
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="query",
                     cmd_string="CNTRVAL?",
                     process_cmd_string=add_awg_terminator,
                     process_response=parse_floats)
    def get_counter_value(self) -> float:
        """ Return the currently measured count value.

        If the counter type is FREQUENCY, the returned value is expressed in Hz.  If the counter type is DUTY (duty
        cycle), the returned value is expressed in %.  Else the returned value is expressed in s.

        Returns: Currently measure count value.  If the counter type is FREQUENCY, the returned value is expressed in
                 Hz.  If the couter type is DUTY (duty cycle), the returned value is expressed in %.  Else the returned
                 value is expressed in s.
        """

        raise NotImplementedError

    @dynamic_command(cmd_type="write",
                     cmd_string="ALIGN",
                     process_cmd_string=add_awg_terminator)
    def align(self) -> None:
        """ Send signal to align the zero phase reference of both channels.

        This shall be used to synchronise Clk_ccdread with Clk_heater. To synchronise both channels, the frequency
        should be the same.
        """

        raise NotImplementedError


#############
# Controllers
#############


class AEUDeviceController(DeviceConnectionInterface, DeviceTransport):

    def write(self, command: str):
        self.aeu.write(command)

    def read(self) -> bytes:
        return self.aeu.read()

    def trans(self, command: str):
        return self.aeu.trans(command)

    def __init__(self, name, hostname, port):
        """
        Args:
            hostname (str): the IP address or fully qualified hostname of the OGSE hardware
                controller. The default is defined in the ``settings.yaml`` configuration file.

            port (int): the IP port number to connect to, by default set in the `settings.yaml`
                configuration file.
        """

        super().__init__()

        logger.debug(f"Initializing AEUDeviceController with hostname={hostname} on port={port}")

        self.aeu = AEUEthernetInterface(name, hostname, port)

    def connect(self):
        """ Connect to the device controller hardware or simulator."""

        self.aeu.connect()
        self.notify_observers(DeviceConnectionState.DEVICE_CONNECTED)

    def disconnect(self):
        """ Disconnect from the device controller hardware or simulator."""

        self.aeu.disconnect()
        self.notify_observers(DeviceConnectionState.DEVICE_NOT_CONNECTED)

    def reconnect(self):
        """ Reconnect to the device controller hardware or simulator.

        In case a connection had already been established, disconnect first.
        """

        if self.is_connected():

            self.disconnect()

        self.connect()

    def is_connected(self) -> bool:
        """ Check if a connection to the device controller hardware or simulator has been established.

        Returns:
            - True if a connected to the device controller hardware or simulator has already been established, False
              otherwise.
        """

        return self.aeu.is_connected()

    def is_simulator(self) -> bool:
        """ Checks if a simulator is used rather than device controller hardware.

        Returns:
            - True if a simulator is used rather than device controller hardware, False otherwise.
        """

        return False


class CRIOController(CRIOInterface, DynamicCommandMixin):
    """ AEU cRIO device controller interface."""

    def __init__(self):
        """ Initialisation of a cRIO device controller."""

        super().__init__()
        # TODO
        self.transport = AEUDeviceController("CRIO", AEU_SETTINGS.HOSTNAME, AEU_SETTINGS.CRIO_PORT)

    def add_observer(self, observer: DeviceConnectionObserver):
        # forward the observer to the generic AEUDeviceController class, i.e. self.transport
        # notification of state changes will be done by this transport class.
        self.transport.add_observer(observer)

    def connect(self):
        """ Connect to the AEU Ethernet Interface."""

        self.transport.connect()

    def disconnect(self):
        """ Disconnect from the AEU Ethernet Interface."""

        self.transport.disconnect()

    def reconnect(self):
        """ Reconnect to the AEU Ethernet Interface."""

        self.transport.reconnect()

    def is_connected(self) -> bool:
        """ Check whether a connection to the AEU Ethernet Interface has been established.

        Returns: True if a connection to the AEU Ethernet Interface has been established; False otherwise.
        """

        return self.transport.is_connected()

    def is_simulator(self) -> bool:
        """ Check whether you are running the AEU device interface in simulator mode.

        Returns: False.
        """

        return self.transport.is_simulator()

    def set_n_cam_ocp(self, v_ccd: float, v_clk: float, v_an1: float, v_an2: float, v_an3: float, v_dig: float) -> None:
        """ Set the Over-Current Protection (OCP) values for the N-CAM [A] and corresponding metrics.

        Args:
            - v_ccd: OCP in V_CCD [A] for the N-CAM.
            - v_clk: OCP in V_CLK [A] for the N-CAM.
            - v_an1: OCP in V_AN1 [A] for the N-CAM.
            - v_an2: OCP in V_AN2 [A] for the N-CAM.
            - v_an3: OCP in V_AN3 [A] for the N-CAM.
            - v_dig: OCP in V_DIG [A] for the N-CAM.
        """

        set_ncam_ocp_metrics(v_ccd, v_clk, v_an1, v_an2, v_an3, v_dig)

        return DynamicCommandMixin.handle_dynamic_command(self, super().set_n_cam_ocp)(v_ccd, v_clk, v_an1, v_an2, v_an3, v_dig)

    def set_f_cam_ocp(self, v_ccd: float, v_clk: float, v_an1: float, v_an2: float, v_an3: float, v_dig: float) -> None:
        """ Set the Over-Current Protection (OCP) values for the F-CAM [A] and corresponding metrics.

        Args:
            - v_ccd: OCP in V_CCD [A] for the F-CAM.
            - v_clk: OCP in V_CLK [A] for the F-CAM.
            - v_an1: OCP in V_AN1 [A] for the F-CAM.
            - v_an2: OCP in V_AN2 [A] for the F-CAM.
            - v_an3: OCP in V_AN3 [A] for the F-CAM.
            - v_dig: OCP in V_DIG [A] for the F-CAM.
        """

        set_fcam_ocp_metrics(v_ccd, v_clk, v_an1, v_an2, v_an3, v_dig)

        return DynamicCommandMixin.handle_dynamic_command(self, super().set_f_cam_ocp)(v_ccd, v_clk, v_an1, v_an2, v_an3, v_dig)

    def set_n_cam_ovp(self, v_ccd: float, v_clk: float, v_an1: float, v_an2: float, v_an3: float, v_dig: float) -> None:
        """ Set the Over-Voltage Protection (OVP) values for the N-CAM [V] and corresponding metrics.

        Args:
            - v_ccd: OVP in V_CCD [V] for the N-CAM.
            - v_clk: OVP in V_CLK [V] for the N-CAM.
            - v_an1: OVP in V_AN1 [V] for the N-CAM.
            - v_an2: OVP in V_AN2 [V] for the N-CAM.
            - v_an3: OVP in V_AN3 [V] for the N-CAM.
            - v_dig: OVP in V_DIG [V] for the N-CAM.
        """

        set_ncam_ovp_metrics(v_ccd, v_clk, v_an1, v_an2, v_an3, v_dig)

        return DynamicCommandMixin.handle_dynamic_command(self, super().set_n_cam_ovp)(v_ccd, v_clk, v_an1, v_an2, v_an3, v_dig)

    def set_f_cam_ovp(self, v_ccd: float, v_clk: float, v_an1: float, v_an2: float, v_an3: float, v_dig: float) -> None:
        """ Set the Over-Voltage Protection (OVP) values for the F-CAM [V] and corresponding metrics.

        Args:
            - v_ccd: OVP in V_CCD [V] for the F-CAM.
            - v_clk: OVP in V_CLK [v] for the F-CAM.
            - v_an1: OVP in V_AN1 [V] for the F-CAM.
            - v_an2: OVP in V_AN2 [V] for the F-CAM.
            - v_an3: OVP in V_AN3 [V] for the F-CAM.
            - v_dig: OVP in V_DIG [V] for the F-CAM.
        """

        set_fcam_ovp_metrics(v_ccd, v_clk, v_an1, v_an2, v_an3, v_dig)

        return DynamicCommandMixin.handle_dynamic_command(self, super().set_f_cam_ovp)(v_ccd, v_clk, v_an1, v_an2, v_an3, v_dig)

    def set_n_cam_uvp(self, v_ccd: float, v_clk: float, v_an1: float, v_an2: float, v_an3: float, v_dig: float) -> None:
        """ Set the Under-Voltage Protection (UVP) values for the N-CAM [V] and corresponding metrics.

        Args:
            - v_ccd: UVP in V_CCD [V] for the N-CAM.
            - v_clk: UVP in V_CLK [V] for the N-CAM.
            - v_an1: UVP in V_AN1 [V] for the N-CAM.
            - v_an2: UVP in V_AN2 [V] for the N-CAM.
            - v_an3: UVP in V_AN3 [V] for the N-CAM.
            - v_dig: UVP in V_DIG [V] for the N-CAM.
        """

        set_ncam_uvp_metrics(v_ccd, v_clk, v_an1, v_an2, v_an3, v_dig)

        return DynamicCommandMixin.handle_dynamic_command(self, super().set_n_cam_uvp)(v_ccd, v_clk, v_an1, v_an2, v_an3, v_dig)

    def set_f_cam_uvp(self, v_ccd: float, v_clk: float, v_an1: float, v_an2: float, v_an3: float, v_dig: float) -> None:
        """ Set the Under-Voltage Protection (UVP) values for the F-CAM [V] and corresponding metrics.

        Args:
            - v_ccd: UVP in V_CCD [V] for the F-CAM.
            - v_clk: UVP in V_CLK [V] for the F-CAM.
            - v_an1: UVP in V_AN1 [V] for the F-CAM.
            - v_an2: UVP in V_AN2 [V] for the F-CAM.
            - v_an3: UVP in V_AN3 [V] for the F-CAM.
            - v_dig: UVP in V_DIG [V] for the F-CAM.
        """

        set_fcam_uvp_metrics(v_ccd, v_clk, v_an1, v_an2, v_an3, v_dig)

        return DynamicCommandMixin.handle_dynamic_command(self, super().set_f_cam_uvp)(v_ccd, v_clk, v_an1, v_an2, v_an3, v_dig)


class PSUController(PSUInterface, DynamicCommandMixin):
    """ PSU device controller interface."""

    def __init__(self, psu_index: int):
        """ Initialisation of a PSU device controller interface.

        Args:
            - psu_index: Index of the PSU (should be 1..6).
        """

        super().__init__(psu_index)
        self.transport = AEUDeviceController(self.device_name, AEU_SETTINGS.HOSTNAME,
                                             AEU_SETTINGS[self.device_name + "_PORT"])

    def add_observer(self, observer: DeviceConnectionObserver):
        # forward the observer to the generic AEUDeviceController class, i.e. self.transport
        # notification of state changes will be done by this transport class.
        self.transport.add_observer(observer)

    def connect(self):
        """ Connect to the AEU Ethernet Interface."""

        self.transport.connect()

    def disconnect(self):
        """ Disconnect from the AEU Ethernet Interface."""

        self.transport.disconnect()

    def reconnect(self):
        """ Reconnect to the AEU Ethernet Interface."""

        self.transport.reconnect()

    def is_connected(self) -> bool:
        """ Check whether a connection to the AEU Ethernet Interface has been established.

        Returns: True if a connection to the AEU Ethernet Interface has been established; False otherwise.
        """

        return self.transport.is_connected()

    def is_simulator(self) -> bool:
        """ Check whether you are running the AEU device interface in simulator mode.

        Returns: False.
        """

        return self.transport.is_simulator()

    def set_voltage(self, voltage: float) -> None:
        """ Set the voltage setpoint and corresponding metrics.

        Args:
            - voltage: Voltage setpoint [V] to configure.
        """

        set_psu_voltage_setpoint_metrics(voltage)

        return DynamicCommandMixin.handle_dynamic_command(self, super().set_voltage)(voltage)

    def set_current(self, current: float) -> None:
        """ Set the current setpoint and corresponding metrics.

        Args:
            - current: Current setpoint [A] to configure.
        """

        set_psu_current_setpoint_metrics(current)

        return DynamicCommandMixin.handle_dynamic_command(self, super().set_current)(current)


    def set_ocp(self, ocp: float) -> None:
        """ Set the Over-Current Protection (OCP) value [A] and corresponding metrics.

        Args:
            - ocp: Over-Current Protection (OCP) [A] to configure.
        """

        set_psu_ocp_metrics(ocp)

        return DynamicCommandMixin.handle_dynamic_command(self, super().set_ocp)(ocp)

    def set_ovp(self, ovp: float) -> None:
        """ Set the Over-Voltage Protection (OVP) value [V] and corresponding metrics.

        Args:
            - ocp: Over-Voltage Protection (OVP) [V] to configure.
        """

        set_psu_ovp_metrics(ovp)

        return DynamicCommandMixin.handle_dynamic_command(self, super().set_ovp)(ovp)


class AWGController(AWGInterface, DynamicCommandMixin):
    """ AWG device controller interface."""

    def __init__(self, awg_index: int):
        """ Initialisation of an AWG device controller interface.

        Args:
            - awg_index: Index of the AWG (should be 1 or 2).
        """

        # name = "AWG" + str(awg_index)
        super().__init__(awg_index)
        self.transport = AEUDeviceController(self.device_name, AEU_SETTINGS.HOSTNAME,
                                             AEU_SETTINGS[self.device_name + "_PORT"])
        self.killer = SignalCatcher()

    def add_observer(self, observer: DeviceConnectionObserver):
        # forward the observer to the generic AEUDeviceController class, i.e. self.transport
        # notification of state changes will be done by this transport class.
        self.transport.add_observer(observer)

    def connect(self):
        """ Connect to the AEU Ethernet Interface."""

        self.transport.connect()

    def disconnect(self):
        """ Disconnect from the AEU Ethernet Interface."""

        self.transport.disconnect()

    def reconnect(self):
        """ Reconnect to the AEU Ethernet Interface."""

        self.transport.reconnect()

    def is_connected(self) -> bool:
        """ Check whether a connection to the AEU Ethernet Interface has been established.

        Returns: True if a connection to the AEU Ethernet Interface has been established; False otherwise.
        """

        return self.transport.is_connected()

    def is_simulator(self) -> bool:
        """ Check whether you are running the AEU device interface in simulator mode.

        Returns: False.
        """

        return self.transport.is_simulator()


#########
# Proxies
#########


class CRIOProxy(Proxy, CRIOInterface):
    """ AEU cRIO Proxy."""

    def __init__(self):
        """ Initialisation of a cRIO Proxy."""

        self.name = "CRIO"

        super().__init__(connect_address(CTRL_SETTINGS.PROTOCOL,
                                         CTRL_SETTINGS.HOSTNAME,
                                         CTRL_SETTINGS.CRIO["COMMANDING_PORT"]))


class PSUProxy(Proxy, PSUInterface):
    """ PSU Proxy."""

    def __init__(self, psu_index: int):
        """ Initialisation of a PSU Proxy.

        Args:
            - psu_index: Index of the PSU (should be 1..6).
        """

        self.name = "PSU" + str(psu_index)

        super().__init__(connect_address(CTRL_SETTINGS.PROTOCOL,
                                         CTRL_SETTINGS.HOSTNAME,
                                         CTRL_SETTINGS[self.name]["COMMANDING_PORT"]))


class AWGProxy(Proxy, AWGInterface):
    """ AWG Proxy."""

    def __init__(self, index: int):
        """ Initialisation of an AWG Proxy.

        Args:
            - psu_index: Index of the AWG (should be 1 or 2).
        """

        self.name = "AWG" + str(index)

        super().__init__(connect_address(CTRL_SETTINGS.PROTOCOL,
                                         CTRL_SETTINGS.HOSTNAME,
                                         CTRL_SETTINGS[self.name]["COMMANDING_PORT"]))


############
# Simulators
############


def get_voltage_quality(voltage, uvp, ovp):
    """ Return the quality of the given voltage w.r.t. the given protections.

    Possible values are:

        - 0 (VoltageQuality.INSIDE_RANGE): voltage inside range;
        - 1 (VoltageQuality.OVP_DETECTED): OVP detection;
        - 2: (VoltageQuality.UVP_DETECTED): UVP detection.

    Args:
        - voltage: Voltage.
        - uvp: Under-Voltage Protection (UVP).
        - ovp: Over-Voltage Protection (OVP).

    Returns: Quality of the given voltage w.r.t. the given protections.
    """

    if fabs(voltage) < fabs(uvp):

        return 2

    elif fabs(voltage) > fabs(ovp):

        return 1

    return 0


def get_current_quality(current, ocp):
    """ Returns the quality of the given current w.r.t. the given protection.

    Possible values are:

        - 0 (CurrentQuality.INSIDE_RANGE): current inside range;
        - 1 (CurrentQuality.OCP_DETECTED): OCP detection.

    Args:
        - current: Current.
        - ocp: Over-Current Protection (OCP).

    Returns: Quality of the given current w.r.t. the given protection.
    """

    if current > ocp:

        return 1

    return 0


class CRIOSimulator(CRIOInterface):

    def __init__(self):

        print("CRIO Simulator")

        super().__init__()

        self.n_cam_selected = IntSwitch.ON
        self.f_cam_selected = IntSwitch.OFF

        self._is_connected = True

        self.clk_50mhz_n_cam = IntSwitch.OFF
        self.clk_50mhz_f_cam_nom = IntSwitch.OFF
        self.clk_50mhz_f_cam_red = IntSwitch.OFF
        self.clk_50mhz_svm_nom = IntSwitch.OFF
        self.clk_50mhz_svm_red = IntSwitch.OFF

        self.clk_ccdread_n_cam = IntSwitch.OFF
        self.clk_ccdread_f_cam_nom = IntSwitch.OFF
        self.clk_ccdread_f_cam_red = IntSwitch.OFF

        self.clk_heater_nom = IntSwitch.OFF
        self.clk_heater_red = IntSwitch.OFF

        self.mode = OperatingMode.STANDBY

        # self.times = None
        self.trip_time_ovp_n_cam_v_ccd = None
        self.trip_time_ovp_n_cam_v_clk = None
        self.trip_time_ovp_n_cam_v_an1 = None
        self.trip_time_ovp_n_cam_v_an2 = None
        self.trip_time_ovp_n_cam_v_an3 = None
        self.trip_time_ovp_n_cam_v_dig = None
        self.trip_time_ovp_f_cam_v_ccd = None
        self.trip_time_ovp_f_cam_v_clk = None
        self.trip_time_ovp_f_cam_v_an1 = None
        self.trip_time_ovp_f_cam_v_an2 = None
        self.trip_time_ovp_f_cam_v_an3 = None
        self.trip_time_ovp_f_cam_v_dig = None
        self.trip_time_uvp_n_cam_v_ccd = None
        self.trip_time_uvp_n_cam_v_clk = None
        self.trip_time_uvp_n_cam_v_an1 = None
        self.trip_time_uvp_n_cam_v_an2 = None
        self.trip_time_uvp_n_cam_v_an3 = None
        self.trip_time_uvp_n_cam_v_dig = None
        self.trip_time_uvp_f_cam_v_ccd = None
        self.trip_time_uvp_f_cam_v_clk = None
        self.trip_time_uvp_f_cam_v_an1 = None
        self.trip_time_uvp_f_cam_v_an2 = None
        self.trip_time_uvp_f_cam_v_an3 = None
        self.trip_time_uvp_f_cam_v_dig = None
        self.trip_time_ocp_n_cam_v_ccd = None
        self.trip_time_ocp_n_cam_v_clk = None
        self.trip_time_ocp_n_cam_v_an1 = None
        self.trip_time_ocp_n_cam_v_an2 = None
        self.trip_time_ocp_n_cam_v_an3 = None
        self.trip_time_ocp_n_cam_v_dig = None
        self.trip_time_ocp_f_cam_v_ccd = None
        self.trip_time_ocp_f_cam_v_clk = None
        self.trip_time_ocp_f_cam_v_an1 = None
        self.trip_time_ocp_f_cam_v_an2 = None
        self.trip_time_ocp_f_cam_v_an3 = None
        self.trip_time_ocp_f_cam_v_dig = None
        self.startup_time_ovp_n_cam_v_ccd = None
        self.startup_time_ovp_n_cam_v_clk = None
        self.startup_time_ovp_n_cam_v_an1 = None
        self.startup_time_ovp_n_cam_v_an2 = None
        self.startup_time_ovp_n_cam_v_an3 = None
        self.startup_time_ovp_n_cam_v_dig = None
        self.startup_time_ovp_f_cam_v_ccd = None
        self.startup_time_ovp_f_cam_v_clk = None
        self.startup_time_ovp_f_cam_v_an1 = None
        self.startup_time_ovp_f_cam_v_an2 = None
        self.startup_time_ovp_f_cam_v_an3 = None
        self.startup_time_ovp_f_cam_v_dig = None
        self.startup_time_uvp_n_cam_v_ccd = None
        self.startup_time_uvp_n_cam_v_clk = None
        self.startup_time_uvp_n_cam_v_an1 = None
        self.startup_time_uvp_n_cam_v_an2 = None
        self.startup_time_uvp_n_cam_v_an3 = None
        self.startup_time_uvp_n_cam_v_dig = None
        self.startup_time_uvp_f_cam_v_ccd = None
        self.startup_time_uvp_f_cam_v_clk = None
        self.startup_time_uvp_f_cam_v_an1 = None
        self.startup_time_uvp_f_cam_v_an2 = None
        self.startup_time_uvp_f_cam_v_an3 = None
        self.startup_time_uvp_f_cam_v_dig = None
        self.startup_time_ocp_n_cam_v_ccd = None
        self.startup_time_ocp_n_cam_v_clk = None
        self.startup_time_ocp_n_cam_v_an1 = None
        self.startup_time_ocp_n_cam_v_an2 = None
        self.startup_time_ocp_n_cam_v_an3 = None
        self.startup_time_ocp_n_cam_v_dig = None
        self.startup_time_ocp_f_cam_v_ccd = None
        self.startup_time_ocp_f_cam_v_clk = None
        self.startup_time_ocp_f_cam_v_an1 = None
        self.startup_time_ocp_f_cam_v_an2 = None
        self.startup_time_ocp_f_cam_v_an3 = None
        self.startup_time_ocp_f_cam_v_dig = None

        self.loopback_option = LoopBack.NO_LOOPBACK

        self.n_cam_secondary_power_status = IntSwitch.OFF
        self.f_cam_secondary_power_status = IntSwitch.OFF

        self.ocp_n_cam = (0.211, 0.295, 0.380, 0.116, -0.4469, 1.023)
        self.ocp_f_cam = (0.213, 0.920, 0.665, 1.820, -0.222, 3.093)
        self.ovp_n_cam = (39, 18, 7.5, 7.5, -7.5, 5.2)
        self.ovp_f_cam = (38, 21.5, 9, 6.4, -9, 6.5)
        self.uvp_n_cam = (34, 15.7, 6.5, 6.5, -6.5, 4.45)
        self.uvp_f_cam = (30.8, 15.6, 7.3, 5, -7.1, 4.9)

        self.current_n_cam = (0.105, 0.208, 0.190, 0.058, -0.224, 0.553)
        self.current_f_cam = (0.164, 0.708, 0.511, 1.400, -0.171, 2.379)
        self.voltage_n_cam = (34.70, 16.05, 6.65, 6.65, -6.65, 4.55)
        self.voltage_f_cam = (31.6, 16.2, 7.7, 5.4, -7.6, 5.3)

    def get_id(self) -> (str, str, str, float):

        return "National Instruments", "cRIO-9063", "E7CB6B", 01.00

    def reset(self) -> None:

        pass

    def clear_error_queue(self) -> None:

        pass

    def get_n_cam_current(self) -> (float, float, float, float, float, float):

        if self.get_n_cam_secondary_power_status():

            return self.current_n_cam

        else:

            return 0, 0, 0, 0, 0, 0

    def get_f_cam_current(self) -> (float, float, float, float, float, float):

        if self.get_f_cam_secondary_power_status():

            return self.current_f_cam

        else:

            return 0, 0, 0, 0, 0, 0

    def get_n_cam_voltage(self) -> (float, float, float, float, float, float):

        if self.get_n_cam_secondary_power_status():

            return self.voltage_n_cam

        else:

            return 0, 0, 0, 0, 0, 0

    def get_f_cam_voltage(self) -> (float, float, float, float, float, float):

        if self.get_f_cam_secondary_power_status():

            return self.voltage_f_cam

        else:

            return 0, 0, 0, 0, 0, 0

    def set_loopback_option(self, loopback_option: LoopBack) -> None:

        self.loopback_option = loopback_option

    def get_loopback_option(self) -> LoopBack:

        return self.loopback_option

    def set_n_cam_secondary_power_status(self, output_status: IntSwitch) -> None:

        self.n_cam_secondary_power_status = output_status

    def get_n_cam_secondary_power_status(self) -> IntSwitch:

        return self.n_cam_secondary_power_status

    def set_f_cam_secondary_power_status(self, output_status: IntSwitch) -> None:

        self.f_cam_secondary_power_status = output_status

    def get_f_cam_secondary_power_status(self) -> IntSwitch:

        return self.f_cam_secondary_power_status

    def set_n_cam_ocp(self, v_ccd: float, v_clk: float, v_an1: float, v_an2: float, v_an3: float, v_dig: float) -> None:

        self.ocp_n_cam = (v_ccd, v_clk, v_an1, v_an2, v_an3, v_dig)

    def get_n_cam_ocp(self) -> (float, float, float, float, float, float):

        return self.ocp_n_cam

    def set_f_cam_ocp(self, v_ccd: float, v_clk: float, v_an1: float, v_an2: float, v_an3: float, v_dig: float) -> None:

        self.ocp_f_cam = (v_ccd, v_clk, v_an1, v_an2, v_an3, v_dig)

    def get_f_cam_ocp(self) -> (float, float, float, float, float, float):

        return self.ocp_f_cam

    def set_n_cam_ovp(self, v_ccd: float, v_clk: float, v_an1: float, v_an2: float, v_an3: float, v_dig: float) -> None:

        self.ovp_n_cam = (v_ccd, v_clk, v_an1, v_an2, v_an3, v_dig)

    def get_n_cam_ovp(self):

        return self.ovp_n_cam

    def set_f_cam_ovp(self, v_ccd: float, v_clk: float, v_an1: float, v_an2: float, v_an3: float, v_dig: float) -> None:

        self.ovp_f_cam = (v_ccd, v_clk, v_an1, v_an2, v_an3, v_dig)

    def get_f_cam_ovp(self):

        return self.ovp_f_cam

    def set_n_cam_uvp(self, v_ccd: float, v_clk: float, v_an1: float, v_an2: float, v_an3: float, v_dig: float) -> None:

        self.uvp_n_cam = (v_ccd, v_clk, v_an1, v_an2, v_an3, v_dig)

    def get_n_cam_uvp(self):

        return self.uvp_n_cam

    def set_f_cam_uvp(self, v_ccd: float, v_clk: float, v_an1: float, v_an2: float, v_an3: float, v_dig: float) -> None:

        self.uvp_f_cam = (v_ccd, v_clk, v_an1, v_an2, v_an3, v_dig)

    def get_f_cam_uvp(self) -> (float, float, float, float, float, float):

        return self.uvp_f_cam

    def get_n_cam_voltage_quality(self) -> (int, int, int, int, int, int):
        voltage = self.get_n_cam_voltage()
        uvp = self.get_n_cam_uvp()
        ovp = self.get_n_cam_ovp()

        # quality = []

        # for index in range(len(voltages)):
        #     print(index)
        #
        #     quality.append(get_voltage_quality(voltages[index], uvp[index], ovp[index]))
        #
        # return tuple(quality)

        return get_voltage_quality(voltage[0], uvp[0], ovp[0]), get_voltage_quality(voltage[1], uvp[1], ovp[1]), \
            get_voltage_quality(voltage[2], uvp[2], ovp[2]), get_voltage_quality(voltage[3], uvp[3], ovp[3]), \
            get_voltage_quality(voltage[4], uvp[4], ovp[4]), get_voltage_quality(voltage[5], uvp[5], ovp[5])

    def get_f_cam_voltage_quality(self) -> (int, int, int, int, int, int):

        voltage = self.get_f_cam_voltage()
        uvp = self.get_f_cam_uvp()
        ovp = self.get_f_cam_ovp()

        # quality = []
        #
        # for index in range(len(voltage)):
        #
        #     print(index)
        #
        #     quality.append(get_voltage_quality(voltage[index], uvp[index], ovp[index]))
        #
        # return tuple(quality)

        return get_voltage_quality(voltage[0], uvp[0], ovp[0]), get_voltage_quality(voltage[1], uvp[1], ovp[1]), \
            get_voltage_quality(voltage[2], uvp[2], ovp[2]), get_voltage_quality(voltage[3], uvp[3], ovp[3]), \
            get_voltage_quality(voltage[4], uvp[4], ovp[4]), get_voltage_quality(voltage[5], uvp[5], ovp[5])

    def get_n_cam_current_quality(self) -> (int, int, int, int, int, int):

        current = self.get_n_cam_current()
        ocp = self.get_n_cam_ocp()

        # quality = []
        #
        # for index in range(len(current)):
        #
        #     print(index)
        #
        #     quality.append(get_current_quality(current[index], ocp[index]))
        #
        # return tuple(quality)

        return get_current_quality(current[0], ocp[0]), get_current_quality(current[1], ocp[1]), \
            get_current_quality(current[2], ocp[2]), get_current_quality(current[3], ocp[3]), \
            get_current_quality(current[4], ocp[4]), get_current_quality(current[5], ocp[5])

    def get_f_cam_current_quality(self) -> (int, int, int, int, int, int):

        current = self.get_f_cam_current()
        ocp = self.get_f_cam_ocp()

        # quality = []
        #
        # for index in range(len(current)):
        #
        #     print(index)
        #
        #     quality.append(get_current_quality(current[index], ocp[index]))
        #
        # return tuple(quality)

        return get_current_quality(current[0], ocp[0]), get_current_quality(current[1], ocp[1]), \
            get_current_quality(current[2], ocp[2]), get_current_quality(current[3], ocp[3]), \
            get_current_quality(current[4], ocp[4]), get_current_quality(current[5], ocp[5])

    def set_n_cam_clock_status(self, clk_50mhz: IntSwitch, clk_ccdread: IntSwitch) -> None:

        self.clk_50mhz_n_cam = clk_50mhz
        self.clk_ccdread_n_cam = clk_ccdread

    def get_n_cam_clock_status(self) -> (IntSwitch, IntSwitch):

        if self.get_n_cam_secondary_power_status() == IntSwitch.ON:

            return self.clk_50mhz_n_cam, self.clk_ccdread_n_cam

        else:

            return IntSwitch.OFF, IntSwitch.OFF

    def get_n_cam_clock_quality(self) -> (bool, bool):

        # No synchronisation failures detected

        return False, False

    def set_f_cam_clock_status(self, clk_50mhz_nom: IntSwitch, clk_50mhz_red: IntSwitch, clk_ccdread_nom: IntSwitch,
                               clk_ccdread_red: IntSwitch) -> None:

        self.clk_50mhz_f_cam_nom = clk_50mhz_nom
        self.clk_50mhz_f_cam_red = clk_50mhz_red
        self.clk_ccdread_f_cam_nom = clk_ccdread_nom
        self.clk_ccdread_f_cam_red = clk_ccdread_red

    def get_f_cam_clock_status(self) -> (IntSwitch, IntSwitch, IntSwitch, IntSwitch):

        if self.get_f_cam_secondary_power_status() == IntSwitch.ON:

            return self.clk_50mhz_f_cam_nom, self.clk_50mhz_f_cam_red, self.clk_ccdread_f_cam_nom, \
                   self.clk_ccdread_f_cam_red
        else:

            return IntSwitch.OFF, IntSwitch.OFF, IntSwitch.OFF, IntSwitch.OFF

    def get_f_cam_clock_quality(self) -> (bool, bool, bool, bool):

        # No synchronisation failures detected

        return False, False, False, False

    def set_svm_clock_status(self, clk_50mhz_nom: bool, clk_50mhz_red: bool, clk_heater_nom: bool, clk_heater_red:
                             bool) -> None:

        self.clk_50mhz_svm_nom = clk_50mhz_nom
        self.clk_50mhz_svm_red = clk_50mhz_red
        self.clk_heater_nom = clk_heater_nom
        self.clk_heater_red = clk_heater_red

    def get_svm_clock_status(self) -> (bool, bool, bool, bool):

        if self.get_n_cam_secondary_power_status() == IntSwitch.ON or \
                self.get_f_cam_secondary_power_status() == IntSwitch.ON:

            return self.clk_50mhz_svm_nom, self.clk_50mhz_svm_red, self.clk_heater_nom, self.clk_heater_red

        else:

            return IntSwitch.OFF, IntSwitch.OFF, IntSwitch.OFF, IntSwitch.OFF

    def get_svm_clock_quality(self) -> (bool, bool, bool, bool):

        # No synchronisation failures detected

        return False, False, False, False

    def get_led_status(self) -> dict:

        operating_mode = self.get_operating_mode()

        output = IntSwitch.OFF
        if self.get_n_cam_secondary_power_status() == IntSwitch.ON or self.get_f_cam_secondary_power_status() == IntSwitch.ON:
            output = IntSwitch.ON

        clk_50mhz = IntSwitch.OFF
        clk_ccdread = IntSwitch.OFF
        clk_heater = IntSwitch.OFF

        clk_n_50mhz, clk_n_ccdread = self.get_n_cam_clock_status()
        clk_f_50mhz_nom, clk_f_50mhz_red, clk_f_ccdread_nom, clk_f_ccdread_red = self.get_f_cam_clock_status()
        clk_tcs_50mhz_nom, clk_tcs_50mhz_red, clk_heater_nom, clk_heater_red = self.get_svm_clock_status()

        if clk_n_50mhz == IntSwitch.ON or clk_f_50mhz_nom == IntSwitch.ON or clk_f_50mhz_red == IntSwitch.ON or \
                clk_tcs_50mhz_nom == IntSwitch.ON or clk_tcs_50mhz_red == IntSwitch.ON:

            clk_50mhz = IntSwitch.ON

        if clk_n_ccdread == IntSwitch.ON or clk_f_ccdread_nom == IntSwitch.ON or clk_f_ccdread_red == IntSwitch.ON:

            clk_ccdread = IntSwitch.ON

        if clk_heater_nom == IntSwitch.ON or clk_heater_red == IntSwitch.ON:

            clk_heater = IntSwitch.ON

        led_status = {
            "Standby": operating_mode == OperatingMode.STANDBY,
            "Selftest": operating_mode == OperatingMode.SELFTEST,
            "FC_TVAC": operating_mode == OperatingMode.FC_TVAC,
            "Alignment": operating_mode == OperatingMode.ALIGNMENT,
            "N-CAM": self.get_n_cam_secondary_power_status(),
            "F-CAM": self.get_f_cam_secondary_power_status(),
            "V_CCD": output,
            "V_CLK": output,
            "V_AN1": output,
            "V_AN2": output,
            "V_AN3": output,
            "V_DIG": output,
            "S_voltage_oor": IntSwitch.OFF,
            "S_current_oor": IntSwitch.OFF,
            "Sync_gf": IntSwitch.OFF,
            "Clk_50MHz": clk_50mhz,
            "Clk_ccdread": clk_ccdread,
            "Clk_heater": clk_heater,
            "Clk_F_FEE_N": clk_f_ccdread_nom,
            "Clk_F_FEE_R": clk_f_ccdread_red,
            "TestPort": IntSwitch.OFF
        }

        return led_status

    def set_operating_mode(self, operating_mode: OperatingMode) -> None:

        self.mode = operating_mode

    def get_operating_mode(self) -> OperatingMode:

        return self.mode

    def get_data(self) -> dict:

        # Measured current

        current_n_cam = zip(["I_N_CCD", "I_N_CLK", "I_N_AN1", "I_N_AN2", "I_N_AN3", "I_N_DIG"],
                            self.get_n_cam_current())
        current_f_cam = zip(["I_F_CCD", "I_F_CLK", "I_F_AN1", "I_F_AN2", "I_F_AN3", "I_F_DIG"],
                            self.get_f_cam_current())

        # Measured voltages

        voltage_n_cam = zip(["V_N_CCD", "V_N_CLK", "V_N_AN1", "V_N_AN2", "V_N_AN3", "V_N_DIG"],
                            self.get_n_cam_voltage())
        voltage_f_cam = zip(["V_F_CCD", "V_F_CLK", "V_F_AN1", "V_F_AN2", "V_F_AN3", "V_F_DIG"],
                            self.get_f_cam_voltage())

        # Led status

        led_status = self.get_led_status()

        data = {"N-CAM": self.n_cam_selected, "F-CAM": self.f_cam_selected}

        data.update(current_n_cam)
        data.update(current_f_cam)
        data.update(voltage_n_cam)
        data.update(voltage_f_cam)
        data.update(led_status)

        return data

    def get_error_info(self) -> int:

        return 0

    def get_num_errors(self) -> int:

        return 0

    def get_selftest_result(self) -> int:

        return 0

    def get_protection_status(self) -> (bool, bool, bool, bool):

        return False, False, False, False

    def set_time(self, trip_time_ovp_n_cam_v_ccd: float, trip_time_ovp_n_cam_v_clk: float, trip_time_ovp_n_cam_v_an1:
                 float, trip_time_ovp_n_cam_v_an2: float, trip_time_ovp_n_cam_v_an3: float, trip_time_ovp_n_cam_v_dig:
                 float, trip_time_ovp_f_cam_v_ccd: float, trip_time_ovp_f_cam_v_clk: float, trip_time_ovp_f_cam_v_an1:
                 float, trip_time_ovp_f_cam_v_an2: float, trip_time_ovp_f_cam_v_an3: float, trip_time_ovp_f_cam_v_dig:
                 float, trip_time_uvp_n_cam_v_ccd: float, trip_time_uvp_n_cam_v_clk: float, trip_time_uvp_n_cam_v_an1:
                 float, trip_time_uvp_n_cam_v_an2: float, trip_time_uvp_n_cam_v_an3: float, trip_time_uvp_n_cam_v_dig:
                 float, trip_time_uvp_f_cam_v_ccd: float, trip_time_uvp_f_cam_v_clk: float, trip_time_uvp_f_cam_v_an1:
                 float, trip_time_uvp_f_cam_v_an2: float, trip_time_uvp_f_cam_v_an3: float, trip_time_uvp_f_cam_v_dig:
                 float, trip_time_ocp_n_cam_v_ccd: float, trip_time_ocp_n_cam_v_clk: float, trip_time_ocp_n_cam_v_an1:
                 float, trip_time_ocp_n_cam_v_an2: float, trip_time_ocp_n_cam_v_an3: float, trip_time_ocp_n_cam_v_dig:
                 float, trip_time_ocp_f_cam_v_ccd: float, trip_time_ocp_f_cam_v_clk: float, trip_time_ocp_f_cam_v_an1:
                 float, trip_time_ocp_f_cam_v_an2: float, trip_time_ocp_f_cam_v_an3: float, trip_time_ocp_f_cam_v_dig:
                 float, startup_time_ovp_n_cam_v_ccd: float, startup_time_ovp_n_cam_v_clk: float,
                 startup_time_ovp_n_cam_v_an1: float, startup_time_ovp_n_cam_v_an2: float, startup_time_ovp_n_cam_v_an3:
                 float, startup_time_ovp_n_cam_v_dig: float, startup_time_ovp_f_cam_v_ccd: float,
                 startup_time_ovp_f_cam_v_clk: float, startup_time_ovp_f_cam_v_an1: float, startup_time_ovp_f_cam_v_an2:
                 float, startup_time_ovp_f_cam_v_an3: float, startup_time_ovp_f_cam_v_dig: float,
                 startup_time_uvp_n_cam_v_ccd: float, startup_time_uvp_n_cam_v_clk: float, startup_time_uvp_n_cam_v_an1:
                 float, startup_time_uvp_n_cam_v_an2: float, startup_time_uvp_n_cam_v_an3: float,
                 startup_time_uvp_n_cam_v_dig: float, startup_time_uvp_f_cam_v_ccd: float, startup_time_uvp_f_cam_v_clk:
                 float, startup_time_uvp_f_cam_v_an1: float, startup_time_uvp_f_cam_v_an2: float,
                 startup_time_uvp_f_cam_v_an3: float, startup_time_uvp_f_cam_v_dig: float, startup_time_ocp_n_cam_v_ccd:
                 float, startup_time_ocp_n_cam_v_clk: float, startup_time_ocp_n_cam_v_an1: float,
                 startup_time_ocp_n_cam_v_an2: float, startup_time_ocp_n_cam_v_an3: float, startup_time_ocp_n_cam_v_dig:
                 float, startup_time_ocp_f_cam_v_ccd: float, startup_time_ocp_f_cam_v_clk: float,
                 startup_time_ocp_f_cam_v_an1: float, startup_time_ocp_f_cam_v_an2: float, startup_time_ocp_f_cam_v_an3:
                 float, startup_time_ocp_f_cam_v_dig: float) -> None:

        self.trip_time_ovp_n_cam_v_ccd = trip_time_ovp_n_cam_v_ccd
        self.trip_time_ovp_n_cam_v_clk = trip_time_ovp_n_cam_v_clk
        self.trip_time_ovp_n_cam_v_an1 = trip_time_ovp_n_cam_v_an1
        self.trip_time_ovp_n_cam_v_an2 = trip_time_ovp_n_cam_v_an2
        self.trip_time_ovp_n_cam_v_an3 = trip_time_ovp_n_cam_v_an3
        self.trip_time_ovp_n_cam_v_dig = trip_time_ovp_n_cam_v_dig
        self.trip_time_ovp_f_cam_v_ccd = trip_time_ovp_f_cam_v_ccd
        self.trip_time_ovp_f_cam_v_clk = trip_time_ovp_f_cam_v_clk
        self.trip_time_ovp_f_cam_v_an1 = trip_time_ovp_f_cam_v_an1
        self.trip_time_ovp_f_cam_v_an2 = trip_time_ovp_f_cam_v_an2
        self.trip_time_ovp_f_cam_v_an3 = trip_time_ovp_f_cam_v_an3
        self.trip_time_ovp_f_cam_v_dig = trip_time_ovp_f_cam_v_dig
        self.trip_time_uvp_n_cam_v_ccd = trip_time_uvp_n_cam_v_ccd
        self.trip_time_uvp_n_cam_v_clk = trip_time_uvp_n_cam_v_clk
        self.trip_time_uvp_n_cam_v_an1 = trip_time_uvp_n_cam_v_an1
        self.trip_time_uvp_n_cam_v_an2 = trip_time_uvp_n_cam_v_an2
        self.trip_time_uvp_n_cam_v_an3 = trip_time_uvp_n_cam_v_an3
        self.trip_time_uvp_n_cam_v_dig = trip_time_uvp_n_cam_v_dig
        self.trip_time_uvp_f_cam_v_ccd = trip_time_uvp_f_cam_v_ccd
        self.trip_time_uvp_f_cam_v_clk = trip_time_uvp_f_cam_v_clk
        self.trip_time_uvp_f_cam_v_an1 = trip_time_uvp_f_cam_v_an1
        self.trip_time_uvp_f_cam_v_an2 = trip_time_uvp_f_cam_v_an2
        self.trip_time_uvp_f_cam_v_an3 = trip_time_uvp_f_cam_v_an3
        self.trip_time_uvp_f_cam_v_an3 = trip_time_uvp_f_cam_v_an3
        self.trip_time_ocp_n_cam_v_ccd = trip_time_ocp_n_cam_v_ccd
        self.trip_time_ocp_n_cam_v_clk = trip_time_ocp_n_cam_v_clk
        self.trip_time_ocp_n_cam_v_an1 = trip_time_ocp_n_cam_v_an1
        self.trip_time_ocp_n_cam_v_an2 = trip_time_ocp_n_cam_v_an2
        self.trip_time_ocp_n_cam_v_an3 = trip_time_ocp_n_cam_v_an3
        self.trip_time_ocp_n_cam_v_dig = trip_time_ocp_n_cam_v_dig
        self.trip_time_ocp_f_cam_v_ccd = trip_time_ocp_f_cam_v_ccd
        self.trip_time_ocp_f_cam_v_clk = trip_time_ocp_f_cam_v_clk
        self.trip_time_ocp_f_cam_v_an1 = trip_time_ocp_f_cam_v_an2
        self.trip_time_ocp_f_cam_v_an2 = trip_time_ocp_f_cam_v_an2
        self.trip_time_ocp_f_cam_v_an3 = trip_time_ocp_f_cam_v_an3
        self.trip_time_ocp_f_cam_v_dig = trip_time_ocp_f_cam_v_dig
        self.startup_time_ovp_n_cam_v_ccd = startup_time_ovp_n_cam_v_ccd
        self.startup_time_ovp_n_cam_v_clk = startup_time_ovp_n_cam_v_clk
        self.startup_time_ovp_n_cam_v_an1 = startup_time_ovp_n_cam_v_an1
        self.startup_time_ovp_n_cam_v_an2 = startup_time_ovp_n_cam_v_an2
        self.startup_time_ovp_n_cam_v_an3 = startup_time_ovp_n_cam_v_an3
        self.startup_time_ovp_n_cam_v_dig = startup_time_ovp_n_cam_v_dig
        self.startup_time_ovp_f_cam_v_ccd = startup_time_ovp_f_cam_v_ccd
        self.startup_time_ovp_f_cam_v_clk = startup_time_ovp_f_cam_v_clk
        self.startup_time_ovp_f_cam_v_an1 = startup_time_ovp_f_cam_v_an1
        self.startup_time_ovp_f_cam_v_an2 = startup_time_ovp_f_cam_v_an2
        self.startup_time_ovp_f_cam_v_an3 = startup_time_ovp_f_cam_v_an3
        self.startup_time_ovp_f_cam_v_dig = startup_time_ovp_f_cam_v_dig
        self.startup_time_uvp_n_cam_v_ccd = startup_time_uvp_n_cam_v_ccd
        self.startup_time_uvp_n_cam_v_clk = startup_time_uvp_n_cam_v_clk
        self.startup_time_uvp_n_cam_v_an1 = startup_time_uvp_n_cam_v_an1
        self.startup_time_uvp_n_cam_v_an2 = startup_time_uvp_n_cam_v_an2
        self.startup_time_uvp_n_cam_v_an3 = startup_time_uvp_n_cam_v_an3
        self.startup_time_uvp_n_cam_v_dig = startup_time_uvp_n_cam_v_dig
        self.startup_time_uvp_f_cam_v_ccd = startup_time_uvp_f_cam_v_ccd
        self.startup_time_uvp_f_cam_v_clk = startup_time_uvp_f_cam_v_clk
        self.startup_time_uvp_f_cam_v_an1 = startup_time_uvp_f_cam_v_an1
        self.startup_time_uvp_f_cam_v_an2 = startup_time_uvp_f_cam_v_an2
        self.startup_time_uvp_f_cam_v_an3 = startup_time_uvp_f_cam_v_an3
        self.startup_time_uvp_f_cam_v_dig = startup_time_uvp_f_cam_v_dig
        self.startup_time_ocp_n_cam_v_ccd = startup_time_ocp_n_cam_v_ccd
        self.startup_time_ocp_n_cam_v_clk = startup_time_ocp_n_cam_v_clk
        self.startup_time_ocp_n_cam_v_an1 = startup_time_ocp_n_cam_v_an1
        self.startup_time_ocp_n_cam_v_an2 = startup_time_ocp_n_cam_v_an2
        self.startup_time_ocp_n_cam_v_an3 = startup_time_ocp_n_cam_v_an3
        self.startup_time_ocp_n_cam_v_dig = startup_time_ocp_n_cam_v_dig
        self.startup_time_ocp_f_cam_v_ccd = startup_time_ocp_f_cam_v_ccd
        self.startup_time_ocp_f_cam_v_clk = startup_time_ocp_f_cam_v_clk
        self.startup_time_ocp_f_cam_v_an1 = startup_time_ocp_f_cam_v_an1
        self.startup_time_ocp_f_cam_v_an2 = startup_time_ocp_f_cam_v_an2
        self.startup_time_ocp_f_cam_v_an3 = startup_time_ocp_f_cam_v_an3
        self.startup_time_ocp_f_cam_v_dig = startup_time_ocp_f_cam_v_dig

    def get_time(self) -> (float, float):

        return self.trip_time_ovp_n_cam_v_ccd, self.trip_time_ovp_n_cam_v_clk, self.trip_time_ovp_n_cam_v_an1,\
               self.trip_time_ovp_n_cam_v_an2, self.trip_time_ovp_n_cam_v_an3, self.trip_time_ovp_n_cam_v_dig,\
               self.trip_time_ovp_f_cam_v_ccd, self.trip_time_ovp_f_cam_v_clk, self.trip_time_ovp_f_cam_v_an1,\
               self.trip_time_ovp_f_cam_v_an2, self.trip_time_ovp_f_cam_v_an3, self.trip_time_ovp_f_cam_v_dig,\
               self.trip_time_uvp_n_cam_v_ccd, self.trip_time_uvp_n_cam_v_clk, self.trip_time_uvp_n_cam_v_an1,\
               self.trip_time_uvp_n_cam_v_an2, self.trip_time_uvp_n_cam_v_an3, self.trip_time_uvp_n_cam_v_dig,\
               self.trip_time_uvp_f_cam_v_ccd, self.trip_time_uvp_f_cam_v_clk, self.trip_time_uvp_f_cam_v_an1,\
               self.trip_time_uvp_f_cam_v_an2, self.trip_time_uvp_f_cam_v_an3, self.trip_time_uvp_f_cam_v_an3,\
               self.trip_time_ocp_n_cam_v_ccd, self.trip_time_ocp_n_cam_v_clk, self.trip_time_ocp_n_cam_v_an1,\
               self.trip_time_ocp_n_cam_v_an2, self.trip_time_ocp_n_cam_v_an3, self.trip_time_ocp_n_cam_v_dig, \
               self.trip_time_ocp_f_cam_v_ccd, self.trip_time_ocp_f_cam_v_clk, self.trip_time_ocp_f_cam_v_an1, \
               self.trip_time_ocp_f_cam_v_an2, self.trip_time_ocp_f_cam_v_an3, self.trip_time_ocp_f_cam_v_dig,\
               self.startup_time_ovp_n_cam_v_ccd, self.startup_time_ovp_n_cam_v_clk, self.startup_time_ovp_n_cam_v_an1,\
               self.startup_time_ovp_n_cam_v_an2, self.startup_time_ovp_n_cam_v_an3, self.startup_time_ovp_n_cam_v_dig,\
               self.startup_time_ovp_f_cam_v_ccd, self.startup_time_ovp_f_cam_v_clk, self.startup_time_ovp_f_cam_v_an1,\
               self.startup_time_ovp_f_cam_v_an2, self.startup_time_ovp_f_cam_v_an3, self.startup_time_ovp_f_cam_v_dig,\
               self.startup_time_uvp_n_cam_v_ccd, self.startup_time_uvp_n_cam_v_clk, self.startup_time_uvp_n_cam_v_an1,\
               self.startup_time_uvp_n_cam_v_an2, self.startup_time_uvp_n_cam_v_an3, self.startup_time_uvp_n_cam_v_dig,\
               self.startup_time_uvp_f_cam_v_ccd, self.startup_time_uvp_f_cam_v_clk, self.startup_time_uvp_f_cam_v_an1,\
               self.startup_time_uvp_f_cam_v_an2, self.startup_time_uvp_f_cam_v_an3, self.startup_time_uvp_f_cam_v_dig,\
               self.startup_time_ocp_n_cam_v_ccd, self.startup_time_ocp_n_cam_v_clk, self.startup_time_ocp_n_cam_v_an1,\
               self.startup_time_ocp_n_cam_v_an2, self.startup_time_ocp_n_cam_v_an3, self.startup_time_ocp_n_cam_v_dig,\
               self.startup_time_ocp_f_cam_v_ccd, self.startup_time_ocp_f_cam_v_clk, self.startup_time_ocp_f_cam_v_an1,\
               self.startup_time_ocp_f_cam_v_an2, self.startup_time_ocp_f_cam_v_an3, self.startup_time_ocp_f_cam_v_dig

    def connect(self):

        self._is_connected = True

    def disconnect(self):

        self._is_connected = False

    def reconnect(self):

        self._is_connected = True

    def is_connected(self) -> bool:

        return self._is_connected

    def is_simulator(self) -> bool:

        return True


class PSUSimulator(PSUInterface):

    def __init__(self, psu_index: int):

        super().__init__(psu_index)

        self._is_connected = True
        self.channel = -1

        self.current = +2.1000E+00
        self.voltage = +3.2500E+01
        self.output_status = IntSwitch.ON
        self.ocp = 5.0
        self.ovp = 13.0
        self.priority_mode = PriorityMode.CONSTANT_VOLTAGE

    def get_id(self) -> (str, str, str, str, str):

        return "KIKUSUI", "PMX18-5", "AB123456", "IFC01.00.0016", "IOC01.00.0015"

    def reset(self) -> None:

        pass

    def test(self) -> int:

        return 0

    def get_error_info(self) -> (int, str):

        return -221, "Settings conflict"

    def clear(self) -> None:

        pass

    def set_channel(self, channel: int) -> None:

        self.channel = channel

    def get_channel(self) -> int:

        return self.channel

    def get_channel_list(self) -> int:

        return 1

    def get_channel_info(self) -> (float, float):

        return +3.5000E+01, +1.0000E+00

    def get_current(self) -> float:

        if self.get_output_status() == IntSwitch.ON:

            return self.current

        else:

            return 0

    def get_voltage(self) -> float:

        if self.get_output_status() == IntSwitch.ON:

            return self.voltage

        else:

            return 0

    def recall_memory(self, memory: Memory) -> None:

        pass

    def conf_settings(self, conf: bool) -> None:

        pass

    def get_memory_config(self) -> bool:

        return True

    def get_memory_setting(self, memory: Memory) -> (float, float, float, float):

        return +1.0000E+01, +2.0000E+00, +2.0000E+00, +5.0000E-01

    def save_memory(self, memory: Memory) -> None:

        pass

    def set_output_status(self, output_status: bool) -> None:

        self.output_status = output_status

    def get_output_status(self) -> IntSwitch:

        return self.output_status

    def set_current(self, current: float) -> None:

        self.current = current

    def get_current_config(self) -> float:

        return self.current

    def set_ocp(self, ocp: float) -> None:

        self.ocp = ocp

    def get_ocp(self) -> float:

        return self.ocp

    def set_voltage(self, voltage: float) -> None:

        self.voltage = voltage

    def get_voltage_config(self) -> float:

        return self.voltage

    def set_ovp(self, ovp: float) -> None:

        self.ovp = ovp

    def get_ovp(self) -> float:

        return self.ovp

    def set_priority_mode(self, priority_mode: PriorityMode) -> None:

        self.priority_mode = priority_mode

    def get_priority_mode(self) -> PriorityMode:

        return self.priority_mode

    def clear_alarms(self) -> None:

        pass

    def questionable_status_register(self) -> int:

        return 0

    def connect(self):

        self._is_connected = True

    def disconnect(self):

        self._is_connected = False

    def reconnect(self):

        self._is_connected = True

    def is_connected(self) -> bool:

        return self._is_connected

    def is_simulator(self) -> bool:

        return True


class AWGSimulator(AWGInterface):

    def __init__(self, awg_index: int):

        super().__init__(awg_index)

        self._is_connected = True
        self.channel = -1

        self.waveform_type = [None, None]
        self.output_load = [None, None]
        self.amplitude = [None, None]
        self.dc_offset = [None, None]
        self.duty_cycle = [None, None]
        self.frequency = [None, None]
        self.output_status = [Switch.OFF, Switch.OFF]
        self.arb = [None, None]

        self.arbs = {
            ARB.ARB1: ["A", Switch.OFF, 0],
            ARB.ARB2: ["B", Switch.OFF, 0],
            ARB.ARB3: ["C", Switch.OFF, 0],
            ARB.ARB4: ["D", Switch.OFF, 0]
        }

        self.arb1 = None
        self.arb2 = None
        self.arb3 = None
        self.arb4 = None

        self.counter_status = [Switch.OFF, Switch.OFF]
        self.counter_source = [CounterSource.AC, CounterSource.AC]
        self.counter_type = [CounterType.FREQUENCY, CounterType.FREQUENCY]

    def reset(self) -> None:
        pass

    def set_channel(self, channel: int) -> None:

        self.channel = channel

    def get_channel(self) -> int:

        return self.channel

    def set_waveform_type(self, waveform_type: Waveform) -> None:

        self.waveform_type[self.get_channel() - 1] = waveform_type

    def get_waveform_type(self) -> Waveform:

        return self.waveform_type[self.get_channel() - 1]

    def set_output_load(self, load: float) -> None:

        self.output_load = load

    def get_output_load(self) -> float:

        return self.output_load[self.get_channel() - 1]

    def set_amplitude(self, amplitude: float) -> None:

        self.amplitude[self.get_channel() - 1] = amplitude

    def get_amplitude(self) -> float:

        return self.amplitude[self.get_channel() - 1]

    def set_dc_offset(self, offset: float) -> None:

        self.dc_offset[self.get_channel() - 1] = offset

    def get_dc_offset(self) -> float:

        return self.dc_offset[self.get_channel() - 1]

    def set_duty_cycle(self, duty_cycle: float):

        self.duty_cycle[self.get_channel() - 1] = duty_cycle

    def get_duty_cycle(self) -> float:

        return self.duty_cycle[self.get_channel() - 1]

    def set_frequency(self, frequency: float):

        self.frequency[self.get_channel() - 1] = frequency

    def get_frequency(self) -> float:

        return self.frequency[self.get_channel() - 1]

    def set_output_status(self, output_status: Switch) -> None:

        self.output_status[self.get_channel() - 1] = output_status

    def get_output_status(self) -> Switch:

        return self.output_status[self.get_channel() - 1]

    def set_arb_waveform(self, arb: ARB):

        self.arb[self.get_channel() - 1] = arb

    def get_arb_waveform(self) -> ARB:

        return self.arb[self.get_channel() - 1]

    def define_arb_waveform(self, arb: ARB, name: str, interpolation: Switch):

        self.arbs[arb][0] = name
        self.arbs[arb][1] = interpolation

    def load_arb1_data(self, binary: ArbDataFile) -> None:

        arb_data = ArbData()
        arb_data.init_from_file(binary)
        arb_data = arb_data.string

        self.arbs[ARB.ARB1][2] = (len(arb_data) - 2 - int(arb_data[1])) / 2
        self.arb1 = arb_data

    def load_arb2_data(self, binary: ArbDataFile) -> None:

        arb_data = ArbData()
        arb_data.init_from_file(binary)
        arb_data = arb_data.string

        self.arbs[ARB.ARB2][2] = (len(arb_data) - 2 - int(arb_data[1])) / 2
        self.arb2 = arb_data

    def load_arb3_data(self, binary: ArbDataFile) -> None:

        arb_data = ArbData()
        arb_data.init_from_file(binary)
        arb_data = arb_data.string

        self.arbs[ARB.ARB3][2] = (len(arb_data) - 2 - int(arb_data[1])) / 2
        self.arb3 = arb_data

    def load_arb4_data(self, binary: ArbDataFile) -> None:

        arb_data = ArbData()
        arb_data.init_from_file(binary)
        arb_data = arb_data.string

        self.arbs[ARB.ARB4][2] = (len(arb_data) - 2 - int(arb_data[1])) / 2
        self.arb4 = arb_data

    def load_arb1_ascii(self, binary: str) -> None:

        self.arb1 = binary

    def load_arb2_ascii(self, binary: str) -> None:

        self.arb1 = binary

    def load_arb3_ascii(self, binary: str) -> None:

        self.arb1 = binary

    def load_arb4_ascii(self, binary: str) -> None:

        self.arb1 = binary

    def get_arb1_def(self) -> (str, Switch, int):

        return self.arbs[ARB.ARB1][0], self.arbs[ARB.ARB1][1], self.arbs[ARB.ARB1][2]

    def get_arb2_def(self) -> (str, Switch, int):

        return self.arbs[ARB.ARB2][0], self.arbs[ARB.ARB2][1], self.arbs[ARB.ARB2][2]

    def get_arb3_def(self) -> (str, Switch, int):

        return self.arbs[ARB.ARB3][0], self.arbs[ARB.ARB3][1], self.arbs[ARB.ARB3][2]

    def get_arb4_def(self) -> (str, Switch, int):

        return self.arbs[ARB.ARB4][0], self.arbs[ARB.ARB4][1], self.arbs[ARB.ARB4][2]

    def get_arb1(self) -> str:

        return self.arb1

    def get_arb2(self) -> str:

        return self.arb2

    def get_arb3(self) -> str:

        return self.arb3

    def get_arb4(self) -> str:

        return self.arb4

    def clear_status(self) -> None:

        pass

    def execution_error_register(self) -> int:

        return 0

    def query_error_register(self) -> int:

        return 0

    def get_id(self) -> (str, str, str, float, float, float):

        return "THURLY THANDAR", "TGF4162", "527758", 01.00, 02.10, 01.20

    def set_counter_status(self, counter_status: Switch) -> None:

        self.counter_status[self.get_channel() - 1] = counter_status

    def get_counter_status(self) -> Switch:

        return self.counter_status[self.get_channel() - 1]

    def set_counter_source(self, counter_source: CounterSource):

        self.counter_source[self.get_channel() - 1] = counter_source

    def get_counter_source(self) -> CounterSource:

        return self.counter_source[self.get_channel() - 1]

    def set_counter_type(self, counter_type: CounterType) -> None:

        self.counter_type[self.get_channel() - 1] = counter_type

    def get_counter_type(self) -> CounterType:

        return self.counter_type[self.get_channel() - 1]

    def get_counter_value(self) -> float:

        return 1

    def align(self) -> None:

        pass

    def connect(self):

        self._is_connected = True

    def disconnect(self):

        self._is_connected = False

    def reconnect(self):

        self._is_connected = True

    def is_connected(self) -> bool:

        return self._is_connected

    def is_simulator(self) -> bool:

        return True


def get_n_cam_cycle_time():
    """ Return the N-CAM cycle time.

    Returns: N-CAM cycle time [s].
    """

    with AWGProxy(2) as awg2:

        identifier = awg2.get_arb1_def()[0][-1]

        awg2_cal = GlobalState.setup.gse.aeu.awg2.calibration
        sync_data_string = awg2_cal.n_cam_sync_data[identifier]

        return float(SyncData(sync_data_string).image_cycle_time)


def get_f_cam_cycle_time():
    """ Return the F-CAM cycle time.

    Returns: F-CAM cycle time [s].
    """

    awg2_cal = GlobalState.setup.gse.aeu.awg2.calibration
    sync_data_string = awg2_cal.n_cam_sync_data["F"]

    return float(SyncData(sync_data_string).image_cycle_time)
