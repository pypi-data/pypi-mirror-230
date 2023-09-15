"""
This module defines the device classes to be used to connect to and control the OGSE.
"""
from __future__ import annotations
import logging
import math
import random
import re
import time
from enum import Enum
from typing import Union

import numpy as np

from egse.collimator.fcul.ogse_devif import OGSEEthernetInterface
from egse.command import ClientServerCommand
from egse.command import CommandError
from egse.control import Failure
from egse.control import is_control_server_active
from egse.device import DeviceConnectionState
from egse.device import DeviceInterface
from egse.mixin import DynamicCommandMixin
from egse.mixin import add_lf
from egse.mixin import dynamic_command
from egse.proxy import DynamicProxy
from egse.settings import Settings
from egse.system import format_datetime
from egse.zmq_ser import connect_address

logger = logging.getLogger(__name__)

OGSE_SETTINGS = Settings.load("OGSE Controller")
CTRL_SETTINGS = Settings.load("OGSE Control Server")
DEVICE_SETTINGS = Settings.load(filename="ogse.yaml")


def is_ogse_cs_active(timeout: float = 2.0):
    """
    Checks whether the OGSE Control Server is running.

    Args:
        timeout (float): Timeout when waiting for a reply [seconds, default=2.0]

    Returns:
        True if the OGSE CS is running and replied with the expected answer.
    """

    endpoint = connect_address(
        CTRL_SETTINGS.PROTOCOL, CTRL_SETTINGS.HOSTNAME, CTRL_SETTINGS.COMMANDING_PORT
    )

    return is_control_server_active(endpoint, timeout)


def decode_response(response: bytes) -> str:
    """Decodes the bytes object and strips off the newline."""
    return response.decode().rstrip()


def _convert_to_float(value: str) -> float:
    try:
        return float(value)
    except ValueError:
        return math.nan


def check_cmd_att_index(cmd_string: str):
    """Check if the 'level #<index>' command has a correct index."""

    # index is expected to be in the range [0-46] (inclusive)

    index = int(cmd_string.split()[-1][1:])

    if not (0 <= index <= 46):
        raise CommandError("ERROR: usage: attenuator level #index  -- index goes from 0 to 46")

    return add_lf(cmd_string)


def decode_pm_status_response(response: bytes):
    """ Decode the response from the OGSE 'pm status' command.

    The command will return a bytes object of the following format:

        b'pm1: OK, pm2: OK\n''

    After processing, the function returns a dictionary with the following tpw entries:

    * "pm1": power status of channel 1
    * "pm2": power status of channel 2

    Args:
        response: the unprocessed response from the device.

    Returns:
        A dictionary containing the power status of channel 1 and 2. If the response can not
        be processed,  a Failure object will be returned.
    """

    if not isinstance(response, bytes):

        return Failure(f"The given argument is not a bytes object as expected: {response=}")

    response = response.decode().rstrip()

    try:
        _, pm1, _, pm2 = re.split(', |: ', response)

    except ValueError as exc:

        logger.error(f"ValueError caught: {exc}")
        return Failure(f"Unexpected response from the OGSE read command: {response=}", exc)

    return {
        "pm1": pm1,
        "pm2": pm2
    }


def decode_read_command(response: bytes) -> dict | Failure:
    """
    Decode the response from the OGSE 'read' command.

    The command will return a bytes object of the following format:

        b'pm1: -2.323670e-14 W +21.6 \xc2\xbaC, pm2: +2.143803e-07 W +22.7 \xc2\xbaC\n'

    After processing, the function returns a dictionary with the following four entries:

    * "power1": power measure for power meter 1 in Watt
    * "temp1": temperature of the power meter 1 in degrees Celsius
    * "power2": power measure for power meter 2 in Watt
    * "temp2": temperature of the power meter 2 in degrees Celsius

    Args:
        response: the unprocessed response from the device.

    Returns:
        A dictionary containing the power and temperature values as floats. If the response can not
        be processed,  a Failure object will be returned.
    """

    # This function cannot raise exceptions, but should return a proper Failure method.
    # The reason for this is that the result of this function will be returned to the Proxy object
    # that issued the command.

    if not isinstance(response, bytes):

        return Failure(f"The given argument is not a bytes object as expected: {response=}")

    response = response.decode().rstrip()

    try:
        _, power1, _, temp1, _, _, power2, _, temp2, _ = response.split()
    except ValueError as exc:
        logger.error(f"ValueError caught: {exc}")
        return Failure(f"Unexpected response from the OGSE read command: {response=}", exc)

    power1 = _convert_to_float(power1)
    temp1 = _convert_to_float(temp1)
    power2 = _convert_to_float(power2)
    temp2 = _convert_to_float(temp2)

    return {
        "power1": power1,
        "temp1": temp1,
        "power2": power2,
        "temp2": temp2
    }


def decode_status_command(response: bytes) -> dict | Failure:
    """
    Decode the response from the OGSE 'status' command.

    The command will return a bytes object of the following format:

        b'power: OFF, lamp: OFF, interlock: OFF, psu: OFF, att: 0E-9 #0, power-ch1: +3.185751e-11 W,
         power-ch2: +2.068336e-07 W, temp-ch1: +21.5 \xc2\xbaC, temp-ch2: +22.6 \xc2\xbaC\n'

    In the case the attenuator is still moving, an asterisk '*' will appear after 'att:' as in:

        b'power: OFF, lamp: OFF, interlock: OFF, psu: OFF, att: * 280E-3 #39,
          power-ch1: -6.378473e-11 W, power-ch2: +2.190483e-07 W,
          temp-ch1: +21.5 \xc2\xbaC, temp-ch2: +22.6 \xc2\xbaC\n'

    After processing, the function returns a dictionary with the following eleven (11) values:

    * 'power': The status of the power
    * 'lamp': The status of the lamp
    * 'interlock': The status of the interlock
    * 'psu': The status of the PSU
    * 'att_moving':The status of the attenuator: True=Moving, False=Not Moving
    * 'att_factor': The attenuation factor as a float
    * 'att_index': The attenuation index as an int
    * 'power1': The power measure for power meter 1 in Watt
    * 'temp1': The temperature of the power meter 1 in degrees Celsius
    * 'power2': The power measure for power meter 2 in Watt
    * 'temp2': The temperature of the power meter 2 in degrees Celsius

    Args:
        response: the unprocessed response from the device.

    Returns:
        A dictionary containing the status and measures of most important parameters (see above).
        If the response can not be processed, a Failure object will be returned.

    """

    # This function cannot raise exceptions, but should return a proper Failure method.
    # The reason for this is that the result of this function will be returned to the Proxy object
    # that issued the command.

    if not isinstance(response, bytes):
        return Failure(f"The given argument is not a bytes object as expected: {response=}")

    response = response.decode().rstrip()

    try:
        if '*' in response:
            (_, power_status, _, lamp_status, _, interlock_status, _, psu_status,
             _, att_moving, att_factor, att_index, _, power1, _, _, power2, _,
             _, temp1, _, _, temp2, _) = response.split()
            att_moving = True
        else:
            (_, power_status, _, lamp_status, _, interlock_status, _, psu_status,
             _, att_factor, att_index, _, power1, _, _, power2, _,
             _, temp1, _, _, temp2, _) = response.split()
            att_moving = False
    except ValueError as exc:
        logger.error(f"ValueError caught: {exc}")
        return Failure(f"Unexpected response from the OGSE status command: {response=}", exc)

    # cut off the trailing comma

    power_status, lamp_status, interlock_status, psu_status = [
        x[:-1] for x in (power_status, lamp_status, interlock_status, psu_status)]

    att_factor = _convert_to_float(att_factor)
    att_index = int(att_index[1:-1])  # cut off the leading '#' and the trailing ','
    power1 = _convert_to_float(power1)
    temp1 = _convert_to_float(temp1)
    power2 = _convert_to_float(power2)
    temp2 = _convert_to_float(temp2)

    return {
        "power": power_status,
        "lamp": lamp_status,
        "interlock": interlock_status,
        "psu": psu_status,
        "att_moving": att_moving,
        "att_factor": att_factor,
        "att_index": att_index,
        "power1": power1,
        "temp1": temp1,
        "power2": power2,
        "temp2": temp2
    }


def decode_att_get_level_command(response: bytes) -> dict | Failure:
    """
    Decode the response from the OGSE 'level' command.

    The command will return a bytes object of the following format:

        b'att-level:        1E+0  #46\n'
        b'att-level: *      1E+0  #46\n'

    After processing, the function returns a tuple with the following eleven (11) values:

    * The status of the attenuator: True=Moving, False=Not Moving
    * The attenuation factor as a float
    * The attenuation index as an int

    Args:
        response: the unprocessed response from the device.

    Returns:
        A dictionary containing the moving status of the attenuator, the level (factor)
        and the index. If the response can not be processed, a Failure object will be returned.

    """

    # This function cannot raise exceptions, but should return a proper Failure method.
    # The reason for this is that the result of this function will be returned to the Proxy object
    # that issued the command.

    if not isinstance(response, bytes):
        return Failure(f"The given argument is not a bytes object as expected: {response=}")

    response = response.decode().rstrip()

    try:
        if '*' in response:
            _, att_moving, att_factor, att_index = response.split()
            att_moving = True
        else:
            _, att_factor, att_index = response.split()
            att_moving = False
    except ValueError as exc:
        logger.error(f"ValueError caught: {exc}")
        return Failure(f"Unexpected response from the OGSE level command: {response=}", exc)

    try:
        att_factor = _convert_to_float(att_factor)
        att_index = int(att_index[1:])  # cut off the leading '#'
    except Exception as exc:
        logger.error(f"Exception caught: {exc=}")
        return Failure(f"Exception caught when converting values from "
                       f"the OGSE level command: {response=}", exc)

    return {
        "att_moving": att_moving,
        "att_factor": att_factor,
        "att_index": att_index
    }


class OnOffSwitch(str, Enum):
    on = "on"
    off = "off"


class OGSECommand(ClientServerCommand):
    def get_cmd_string(self, *args, **kwargs) -> str:
        out = super().get_cmd_string(*args, **kwargs)
        return out + "\n"


class OGSEInterface(DeviceInterface):
    """
    Interface definition for the Controller, Simulator and Proxy classes for this device.
    """

    @dynamic_command(cmd_type="query", cmd_string="version", process_cmd_string=add_lf,
                     process_response=decode_response)
    def version(self) -> str:
        """Returns version information about the OGSE hardware controller."""
        raise NotImplementedError

    @dynamic_command(cmd_type="query", cmd_string="quit", process_cmd_string=add_lf,
                     process_response=decode_response)
    def quit(self):
        """Disconnects client from the server."""
        raise NotImplementedError

    @dynamic_command(cmd_type="query", cmd_string="exit", process_cmd_string=add_lf,
                     process_response=decode_response)
    def exit(self):
        """Disconnects client from the server."""
        raise NotImplementedError

    @dynamic_command(cmd_type="query", cmd_string="ldls status", process_cmd_string=add_lf,
                     process_response=decode_response)
    def ldls_status(self) -> str:
        """
        Returns the state of the connection to the LDLS device. The returned value is 'OK'
        when the LDLS device is initialised and ready, 'ERROR' when the device failed to
        initialise.

        Returns:
            'ldls: OK' or 'ldls: ERROR'
        """
        raise NotImplementedError

    @dynamic_command(cmd_type="query", cmd_string="pm status", process_cmd_string=add_lf,
                     process_response=decode_pm_status_response)
    def pm_status(self) -> dict:
        """
        Returns the state of the connection to the power-meter devices. The returned value is 'OK'
        when the power-meter device is initialised and ready, 'ERROR' when the device failed to
        initialise.

        Returns:
            A dictionary with keys: 'pm1', 'pm2' and values 'OK' or 'ERROR'.
        """
        raise NotImplementedError

    @dynamic_command(cmd_type="query", cmd_string="att status", process_cmd_string=add_lf,
                     process_response=decode_response)
    def att_status(self) -> str:
        """
        Returns the state of the connection to attenuator device. The returned value contains 'OK'
        when the attenuator device is initialised and ready, 'ERROR' when the device failed to
        initialise.

        Returns:
            A string containing 'OK' or 'ERROR', i.e. 'att: OK' or 'att: ERROR'.
        """
        raise NotImplementedError

    @dynamic_command(cmd_type="query", cmd_string="get interlock", process_cmd_string=add_lf,
                     process_response=decode_response)
    def get_interlock(self) -> str:
        """Get the state of the interlock.

        Returns:
            A string containg 'OPEN' or 'CLOSE', i.e. 'interlock: OPEN' or 'interlock: CLOSE'.
        """
        raise NotImplementedError

    @dynamic_command(cmd_type="query", cmd_string="get power", process_cmd_string=add_lf,
                     process_response=decode_response)
    def get_power(self) -> str:
        """Get the state of the power supply. Returns 'power: ON' or 'power: OFF'."""
        raise NotImplementedError

    @dynamic_command(cmd_type="query", cmd_string="get lamp", process_cmd_string=add_lf,
                     process_response=decode_response)
    def get_lamp(self) -> str:
        """Get the state of the lamp.  Returns 'lamp: ON' or 'lamp: OFF'."""
        raise NotImplementedError

    @dynamic_command(cmd_type="query", cmd_string="get laser", process_cmd_string=add_lf,
                     process_response=decode_response)
    def get_laser(self) -> str:
        """Get the state of the laser.  Returns 'laser: ON' or 'laser: OFF'."""
        raise NotImplementedError

    @dynamic_command(cmd_type="query", cmd_string="get lamp-fault", process_cmd_string=add_lf,
                     process_response=decode_response)
    def get_lamp_fault(self) -> str:
        """
        Returns if there was an error with the lamp.
        Returned value is 'lamp-fault: ERROR' or 'lamp-fault: NO-ERROR'.
        """
        raise NotImplementedError

    @dynamic_command(cmd_type="query", cmd_string="get controller-fault", process_cmd_string=add_lf,
                     process_response=decode_response)
    def get_controller_fault(self) -> str:
        """
        Returns if there was an error with the controller.
        The returned value is 'controller-fault: ERROR' or 'controller-fault: NO-ERROR'.
        """
        raise NotImplementedError

    @dynamic_command(cmd_type="query", cmd_string="get psu", process_cmd_string=add_lf,
                     process_response=decode_response)
    def get_psu(self) -> str:
        """Get the state of the power supply unit.  Returns 'psu: ON' or 'psu: OFF'."""
        raise NotImplementedError

    @dynamic_command(cmd_type="query", cmd_string="get operate", process_cmd_string=add_lf,
                     process_response=decode_response)
    def get_operate(self) -> str:
        """Get the state of the laser (operate).  Returns 'operate: ON' or 'operate: OFF'."""
        raise NotImplementedError

    @dynamic_command(cmd_type="query", cmd_string="get flags", process_cmd_string=add_lf,
                     process_response=decode_response)
    def get_flags(self) -> str:
        """
        Get the state of all parameters encoded in a single number formatted in hexadecimal
        and binary. The bit order from msb to lsb is:

        * bit 0 - interlock
        * bit 1 - power
        * bit 2 - lamp
        * bit 3 - laser
        * bit 4 - lamp-fault
        * bit 5 - controller-fault
        * bit 6 - psu
        * bit 7 - operate

        Returns:
            flags: 0xhh bbbb bbbb.
        """
        raise NotImplementedError

    @dynamic_command(cmd_type="query", cmd_string="read", process_cmd_string=add_lf,
                     process_response=decode_read_command)
    def get_power_and_temperature(self) -> dict | Failure:
        """
        Gets a power and temperature reading of both power-meters. Units are in Watt and degrees
        Celsius.

        Returns:
            A dictionary containing the power and temperature values as floats. If the response
            can not be processed, a Failure object will be returned.
        """
        raise NotImplementedError

    @dynamic_command(cmd_type="query", cmd_string="status", process_cmd_string=add_lf,
                     process_response=decode_status_command)
    def status(self) -> dict | Failure:
        """
        Gets a global view of various relevant parameters. Returns a comma separated with the
        current value of 9 parameters. Optionally, the attenuation shows an asterisk '*' when
        the wheels are moving.

        Returns:
            power: <flag>, lamp: <flag>, interlock: <flag>, psu: <flag>, att: [*] <level> #index,
            power-ch1: <value> W, power-ch2: <value> W, temp-ch1: <value> ºC, temp-ch2: <value> ºC.
        """
        raise NotImplementedError

    @dynamic_command(cmd_type="query", cmd_string="level", process_cmd_string=add_lf,
                     process_response=decode_att_get_level_command)
    def att_get_level(self) -> dict | Failure:
        """
        Returns a dictionary with the following keys: att_moving [bool], att_factor [float],
        and att_index [int].  In case of an error a Failure object will be returned.
        """
        raise NotImplementedError

    @dynamic_command(cmd_type="transaction", cmd_string="level ${factor}",
                     process_cmd_string=add_lf,
                     process_response=decode_response)
    def att_set_level_factor(self, factor: int | float) -> str:
        """
        Sets attenuator to the level closest to <factor>. There are 47 levels of attenuation
        available, from 0 to 1.
        This command chooses the level closest to the requested value.

        Args:
            factor (float): value between 0.0 and 1.0, where 0.0 is opaque and 1.0 is transparant.

        Returns:
            The string 'OK' or 'ERROR' depending whether the command
            was accepted or the attenuator device is not ready.
        """
        raise NotImplementedError

    @dynamic_command(cmd_type="transaction", cmd_string="level #${index}",
                     process_cmd_string=check_cmd_att_index,
                     process_response=decode_response)
    def att_set_level_index(self, index: int) -> str:
        """
        Sets attenuator to the level closest to <index>. There are 47 levels of attenuation
        available, from 0 to 46. This command chooses the level closest to the requested value.

        Args:
            index (int): value between 0-46 (inclusive).

        Returns:
            The string 'OK' or 'ERROR' depending whether the command
            was accepted or the attenuator device is not ready.
        """
        raise NotImplementedError

    @dynamic_command(cmd_type="transaction", cmd_string="level ${pos1} ${pos2}",
                     process_cmd_string=add_lf,
                     process_response=decode_response)
    def att_set_level_position(self, pos1: int, pos2: int) -> str:
        """
        Sets the two filter wheels to the given values (pos1 and pos2 must be between 1 and 8).

        Args:
            pos1: the requested position for wheel 1
            pos2: the requested position for wheel 2

        Returns:
            The string 'OK' or 'ERROR' depending whether the command
            was accepted or the attenuator device is not ready.

        """
        raise NotImplementedError

    @dynamic_command(cmd_type="transaction", cmd_string="level up", process_cmd_string=add_lf,
                     process_response=decode_response)
    def att_level_up(self) -> str:
        """
        Selects the attenuation one step higher than the current value.
        It has no effect if the current level is already the highest value allowed.

        Returns:
            The string 'OK' or 'ERROR' depending whether the command
            was accepted or the attenuator device is not ready.
        """
        raise NotImplementedError

    @dynamic_command(cmd_type="transaction", cmd_string="level down", process_cmd_string=add_lf,
                     process_response=decode_response)
    def att_level_down(self) -> str:
        """
        Selects the attenuation one step lower than the current value.
        It has no effect if the current level is already the lowest value allowed.

        Returns:
            The string 'OK' or 'ERROR' depending whether the command
            was accepted or the attenuator device is not ready.
        """
        raise NotImplementedError

    @dynamic_command(cmd_type="transaction", cmd_string="power on", process_cmd_string=add_lf,
                     process_response=decode_response)
    def power_on(self) -> str:
        """Turns the power supply on, returns 'OK' or 'ERROR'."""
        raise NotImplementedError

    @dynamic_command(cmd_type="transaction", cmd_string="power off", process_cmd_string=add_lf,
                     process_response=decode_response)
    def power_off(self) -> str:
        """Turns the power supply off, returns 'OK' or 'ERROR'."""
        raise NotImplementedError

    @dynamic_command(cmd_type="transaction", cmd_string="operate on", process_cmd_string=add_lf,
                     process_response=decode_response)
    def operate_on(self) -> str:
        """Turns the laser on, returns 'OK' or 'ERROR'."""
        raise NotImplementedError

    @dynamic_command(cmd_type="transaction", cmd_string="operate off", process_cmd_string=add_lf,
                     process_response=decode_response)
    def operate_off(self) -> str:
        """Turns the laser off, returns 'OK' or 'ERROR'."""
        raise NotImplementedError

    @dynamic_command(cmd_type="transaction", cmd_string="reset", process_cmd_string=add_lf,
                     process_response=decode_response)
    def reset(self) -> str:
        """Performs a ‘reset’ cycle. This is sometimes needed to take LDLS out of a locked state.
        Returns 'OK' or 'ERROR'.
        """
        raise NotImplementedError


class OGSEController(OGSEInterface, DynamicCommandMixin):
    """
    This is the class that talks directly to the OGSE device. It opens a TCP/IP socket
    connection with the OGSE Hardware Controller and sends commands to the device.
    """

    def __init__(self, hostname=OGSE_SETTINGS.HOSTNAME, port=OGSE_SETTINGS.PORT):
        """
        Args:
            hostname (str): the IP address or fully qualified hostname of the OGSE hardware
                controller. The default is defined in the ``settings.yaml`` configuration file.

            port (int): the IP port number to connect to, by default set in the `settings.yaml`
                configuration file.
        """

        super().__init__()

        logger.debug(f"Initializing OGSEController with hostname={hostname} on port={port}")

        self.transport = self.ogse = OGSEEthernetInterface(hostname, port)

    def connect(self):
        self.transport.connect()
        self.notify_observers(DeviceConnectionState.DEVICE_CONNECTED)

    def disconnect(self):
        self.transport.disconnect()
        self.notify_observers(DeviceConnectionState.DEVICE_NOT_CONNECTED)

    def reconnect(self):
        self.transport.reconnect()

    def is_connected(self):
        """Check if the OGSE Controller is connected. """
        return self.transport.is_connected()

    def is_simulator(self):
        return "sim" in self.version()


ATT_LEVELS_BY_WHEEL = {
    (1, 1):      1E+0,
    (1, 2):      0E-9,
    (1, 3):    600E-3,
    (1, 4):    350E-3,
    (1, 5):    250E-3,
    (1, 6):     90E-3,
    (1, 7):    7.5E-3,
    (1, 8):    900E-6,
    (2, 1):      0E-9,
    (2, 2):      0E-9,
    (2, 3):      0E-9,
    (2, 4):      0E-9,
    (2, 5):      0E-9,
    (2, 6):      0E-9,
    (2, 7):      0E-9,
    (2, 8):      0E-9,
    (3, 1):    800E-3,
    (3, 2):      0E-9,
    (3, 3):    480E-3,
    (3, 4):    280E-3,
    (3, 5):    200E-3,
    (3, 6):     72E-3,
    (3, 7):      6E-3,
    (3, 8):    720E-6,
    (4, 1):    550E-3,
    (4, 2):      0E-9,
    (4, 3):    330E-3,
    (4, 4):  192.5E-3,
    (4, 5):  137.5E-3,
    (4, 6):   49.5E-3,
    (4, 7):  4.125E-3,
    (4, 8):    495E-6,
    (5, 1):    260E-3,
    (5, 2):      0E-9,
    (5, 3):    156E-3,
    (5, 4):     91E-3,
    (5, 5):     65E-3,
    (5, 6):   23.4E-3,
    (5, 7):   1.95E-3,
    (5, 8):    234E-6,
    (6, 1):     90E-3,
    (6, 2):      0E-9,
    (6, 3):     54E-3,
    (6, 4):   31.5E-3,
    (6, 5):   22.5E-3,
    (6, 6):    8.1E-3,
    (6, 7):    675E-6,
    (6, 8):     81E-6,
    (7, 1):     25E-3,
    (7, 2):      0E-9,
    (7, 3):     15E-3,
    (7, 4):   8.75E-3,
    (7, 5):   6.25E-3,
    (7, 6):   2.25E-3,
    (7, 7):  187.5E-6,
    (7, 8):   22.5E-6,
    (8, 1):    900E-6,
    (8, 2):      0E-9,
    (8, 3):    540E-6,
    (8, 4):    315E-6,
    (8, 5):    225E-6,
    (8, 6):     81E-6,
    (8, 7):   6.75E-6,
    (8, 8):    810E-9,
}

ATT_LEVELS_BY_FACTOR = {
     0:     0.0,
     1: 8.10E-7,
     2: 6.75E-6,
     3: 2.25E-5,
     4: 8.10E-5,
     5: 1.88E-4,
     6: 2.25E-4,
     7: 2.34E-4,
     8: 3.15E-4,
     9: 4.95E-4,
    10: 5.40E-4,
    11: 6.75E-4,
    12: 7.20E-4,
    13: 9.00E-4,
    14: 1.95E-3,
    15: 2.25E-3,
    16: 4.13E-3,
    17: 6.00E-3,
    18: 6.25E-3,
    19: 7.50E-3,
    20: 8.10E-3,
    21: 8.75E-3,
    22: 1.50E-2,
    23: 2.25E-2,
    24: 2.34E-2,
    25: 2.50E-2,
    26: 3.15E-2,
    27: 4.95E-2,
    28: 5.40E-2,
    29: 6.50E-2,
    30: 7.20E-2,
    31: 9.00E-2,
    32: 9.10E-2,
    33: 1.38E-1,
    34: 1.56E-1,
    35: 1.93E-1,
    36: 2.00E-1,
    37: 2.50E-1,
    38: 2.60E-1,
    39: 2.80E-1,
    40: 3.30E-1,
    41: 3.50E-1,
    42: 4.80E-1,
    43: 5.50E-1,
    44: 6.00E-1,
    45: 8.00E-1,
    46: 1.0,
}


def get_attenuation_index(attenuation_level: float):
    """
    Determine the attenuation index corresponding to the given transmittance.

    Args:
        attenuation level: Transmittance.

    Returns:
        Attenuation index corresponding to the given transmittance.
    """
    attenuation_levels = np.array([level for level in ATT_LEVELS_BY_FACTOR.values()])

    return np.abs(attenuation_levels - attenuation_level).argmin()


class OGSESimulator(OGSEInterface):

    def __init__(self):

        super().__init__()

        self._lamp = False
        self._laser = False
        self._psu = False
        self._interlock = False
        self._operate = False
        self._power = False
        self._att_level = 1.0
        self._att_index = 46
        self._att_position_1 = 1
        self._att_position_2 = 1
        self._connected = False

    def is_simulator(self) -> bool:
        return True

    def connect(self):
        self._connected = True

    def disconnect(self):
        self._connected = False

    def reconnect(self):
        self._connected = True

    def is_connected(self) -> bool:
        return self._connected

    def version(self):
        return "PLATO-RT-OGSE (v2.1)"

    def get_flags(self):

        return "flags: 0x00  0000 0000"

    def get_interlock(self):

        return "interlock: OPEN" if self._interlock else "interlock: CLOSED"

    def get_power(self):

        return "power: ON" if self._power else "power: OFF"

    def get_lamp(self):

        return "lamp: ON" if self._lamp else "lamp: OFF"

    def get_laser(self):

        return "laser: ON" if self._laser else "laser: OFF"

    def quit(self):
        pass

    def exit(self):
        pass

    def ldls_status(self):

        return "ldls: OK"

    def get_lamp_fault(self):

        return "lamp-fault: NO-ERROR"

    def get_controller_fault(self):

        return "controller-fault: NO-ERROR"

    def get_psu(self):

        return "psu: ON" if self._psu else "psu: OFF"

    def get_operate(self):

        return "operate: ON" if self._operate else "operate: OFF"

    def att_status(self):

        return "att: OK"

    def att_get_level(self):

        return {
            "att_moving": False,
            "att_factor": self._att_level,
            "att_index": self._att_index
        }

    def att_set_level_factor(self, factor):

        if 0 <= factor <= 1:

            self._att_level = factor
            self._att_index = get_attenuation_index(factor)

            time.sleep(random.random() * 3 + 6)  # wait between 6.0 and 9.0 seconds

            return "OK"

        else:

            return "ERROR: usage: attenuator level <value>  -- value must be in [0,1]"

    def att_set_level_position(self, level1, level2):

        if 1 <= level1 <= 8 and 1 <= level2 <= 8:

            self._att_position_1 = level1
            self._att_position_2 = level2

            self._att_level = ATT_LEVELS_BY_WHEEL[(level1, level2)]
            self._att_index = get_attenuation_index(self._att_level)

            time.sleep(random.random() * 3 + 6)  # wait between 6.0 and 9.0 seconds

            return "OK"

        else:

            return (
                "ERROR: usage: attenuator level <wheel_1> <wheel_2>  -- " 
                "wheel positions must be integer = 1..8"
            )

    def att_level_up(self):

        self.att_set_level_index(min(self._att_index + 1, len(ATT_LEVELS_BY_FACTOR) - 1))

        return "OK"

    def att_level_down(self):

        self.att_set_level_index(max(self._att_index - 1, 0))

        return "OK"

    def pm_status(self):

        return {
            "pm1": "OK",
            "pm2": "OK"
        }

    def get_power_and_temperature(self):

        return {
            "power1": 6.376149e-11,
            "temp1": 21.3,
            "power2": 1.484441e-07,
            "temp2": 21.3
        }

    def status(self):

        power_and_temp = self.get_power_and_temperature()
        _, att_level, att_index = self.att_get_level()

        # return self.get_power(), self.get_lamp(), self.get_interlock(), self.get_psu(), \
        #     f"att: {att_level} #{att_index}",  f"power-ch1: {power_ch1} W", f"temp-ch1: {temp_ch1} °C", \
        #     f"power-ch2: {power_ch2} W", f"temp-ch2: {temp_ch2} °C",
        #
        status = {
            "power": "ON" if self._power else "OFF",
            "lamp": "ON" if self._lamp else "OFF",
            "interlock": "ON" if self._interlock else "OFF",
            "psu": "ON" if self._psu else "OFF",
            "att_moving": False,
            "att_factor": self._att_level,
            "att_index": self._att_index
        }

        status.update(power_and_temp)

        return status

    def att_set_level_index(self, index: int):

        if 0 <= factor < len(ATT_LEVELS_BY_FACTOR):

            self._att_index = index
            self._att_level = ATT_LEVELS_BY_FACTOR[index][0]

            time.sleep(random.random() * 3 + 6)  # wait between 6.0 and 9.0 seconds

            return "OK"

        else:

            return "ERROR: usage: attenuator level #index  -- index goes from 0 to 47"

    def power_on(self):

        self._power = True

        return "OK"

    def power_off(self):

        self._power = False

        return "OK"

    def operate_on(self):

        self._operate = True

        return "OK"

    def operate_off(self):

        self._operate = True

        return "OK"

    def reset(self):
        pass


REQUEST_TIMEOUT = 10_000  # setting the attenuator can take up to 10 seconds


class OGSEProxy(DynamicProxy, OGSEInterface):
    """
    The OGSEProxy class is used to connect to the OGSE control server and send commands
    to the OGSE Hardware Controller remotely.
    """

    def __init__(
            self,
            protocol=CTRL_SETTINGS.PROTOCOL,
            hostname=CTRL_SETTINGS.HOSTNAME,
            port=CTRL_SETTINGS.COMMANDING_PORT,
            timeout=REQUEST_TIMEOUT
    ):
        """
        Args:
            protocol: the transport protocol
                [default is taken from settings file]
            hostname: location of the control server (IP address)
                [default is taken from settings file]
            port: TCP port on which the control server is listening for commands
                [default is taken from settings file]
            timeout: time out on the response from the control server [milliseconds]
        """
        super().__init__(connect_address(protocol, hostname, port), timeout=timeout)


# commands = load_commands(CommandProtocol, COMMAND_SETTINGS.Commands, OGSECommand, OGSEController)


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=20)

    from egse.collimator.fcul.ogse import OGSEController

    ogse = OGSEController()
    ogse.connect()

    print(ogse.version())
    print(ogse.status())

    print("att level: ", ogse.att_get_level())

    for factor in 1e-10, 1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1e-0:
        print(format_datetime(), end=" ")
        print(f"set att level: {factor:10e}", end=" ")
        print(ogse.att_set_level_factor(factor), end=" ")
        print(ogse.att_get_level())

    for factor in 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0:
        print(format_datetime(), end=" ")
        print(f"set att level: {factor:10e}", end=" ")
        print(ogse.att_set_level_factor(factor), end=" ")
        print(ogse.att_get_level())

    ogse.disconnect()
