"""
This module defines the device classes to be used to connect to and control the HUBER Stages.
"""
from __future__ import annotations

import logging
import textwrap
from typing import Tuple

import rich
import time

from egse.control import Failure
from egse.device import DeviceConnectionError
from egse.device import DeviceConnectionState
from egse.device import DeviceInterface
from egse.mixin import DynamicCommandMixin
from egse.mixin import add_cr_lf
from egse.mixin import dynamic_command
from egse.proxy import DynamicProxy
from egse.settings import Settings
from egse.stages.huber.smc9300_devif import HuberError
from egse.stages.huber.smc9300_devif import HuberSMC9300EthernetInterface
from egse.state import GlobalState
from egse.zmq_ser import connect_address

# Explicitly set the module name instead of __name__. When module is executed instead of imported
# __name__ will result in __main__ and no logging to zmq will be done.

MODULE_LOGGER = logging.getLogger("egse.stages.huber.smc9300")

HC_SETTINGS = Settings.load("Huber Controller")
CTRL_SETTINGS = Settings.load("Huber Control Server")
DEVICE_SETTINGS = Settings.load(filename="smc9300.yaml")


def print_state(state: int) -> None:
    """Prints the state of the axis."""

    rich.print(
        textwrap.dedent(
            f"""\
                axis ready: {bool(state & 1)}
                reference position installed: {bool(state & 2)}
                end/limit switch EL- active: {bool(state & 4)}
                end/limit switch EL+ active: {bool(state & 8)}
                program execution in progress: {bool(state & 64)}
                controller ready: {bool(state & 128)}
                oscillation in progress: {bool(state & 256)}
                oscillation positioning error: {bool(state & 512)}
                encoder reference installed: {bool(state & 1024)}
                axis error: {bool(state & 16384)}
            """
        )
    )


def untangle_status(status: str) -> dict:
    """Returns a dictionary with all the values from the status string."""

    try:

        axis, errn, errm, pos, epos, el, ref, eref, rdy, osc, prog, *_ = status.split(":")

        return {
            "axis": int(axis),  # the axis id
            "err_no": int(errn),  # error number
            "err_msg": errm,  # error message
            "pos": float(pos),  # position
            "epos": float(epos),  # encode position
            "elimit": int(el),  # end/limit status
            "ref": int(ref),  # reference status
            "eref": int(eref),  # encoder reference status
            "ctrl": int(rdy),  # controller ready
            "osc": int(osc),  # oscillation status
            "prog": int(prog),  # program running
        }
    except ValueError as exc:
        raise ValueError(
            textwrap.dedent(
                f"""\
                Could not disentangle the status from SMC9300, response from the device can not be parsed.
                The expected format is "axis:err_no:err_msg:pos:epos:elimit:ref:eref:ctrl:osc:prog", where
                `err_msg` is a string, `pos` and `epos` are floats and the others are of type int.
                {status=}
                """
            )
        ) from exc


def decode_response(response: bytes) -> str:
    """Decodes the bytes object and strips off the newline."""

    # MODULE_LOGGER.debug(f"response -> {response}")

    return response.decode().rstrip()


def decode_info(response: bytes) -> str:
    response = decode_response(response).split("\r\n")

    return "\n".join(response)


def decode_get_state(response: bytes) -> int:
    """Decodes the response from the get state command and strips off the newline."""

    # The response argument has the following format: '<axis>:<state>;'
    # where <axis> is 1, 2, or 3 and we need the <state>, so we to
    # cut e.g. '1:' and ';' if <axis> is 1.

    response = decode_response(response)
    return int(response[2:-1])


def decode_get_parameter(response: bytes) -> Tuple[str, int, str]:
    """
    Decodes the response from a request for a parameter value. The response contains
    the parameter name, the axis, and the value.

    Returns:
        A tuple of (`<parameter name: str>`, `<axis: int>`, `<value: str>`)
    """
    response = decode_response(response)
    name, value = response.split(":")
    axis = name[-1]
    name = name[:-1]
    return name, int(axis), value


def decode_get_error(response: bytes) -> Tuple[str]:
    """Decodes the response from the get error command and strips off the newline."""

    response = decode_response(response)

    # The response string looks like '<axis>:<errno> <errmsg>' where <axis> is the axis number,
    # <errno> is the error number and <errmsg> is the error message.

    response = response[2:]

    error = response.split(maxsplit=1)

    if len(error) == 1 and error[0] == '0':
        error.append("no error")

    return tuple(error)


def decode_axis_float(response: bytes) -> float:
    """Decodes the response of type `<axis>:<float>;` and strips off the newline."""

    response = decode_response(response)

    return float(response[2:-1])


def decode_axis_int(response: bytes) -> int:
    """Decodes the response of type `<axis>:<int>;` and strips off the newline."""

    response = decode_response(response)

    return int(response[2:-1])


def decode_get_configuration(response: bytes) -> dict | Failure:
    """Decodes the response from the controller on the request for the configuration parameters.

    Returns:
        A dictionary with parameter names and their values.
    """
    all_conf = decode_response(response).split("\r\n")

    # Every item in the all_conf list has the format '<var><axis>:<value>' where <var> is the
    # name of the configuration variable, <axis> is the axis number and <value> is the current
    # value for the configuration variable. A comment line starts with a '#' character.

    all_conf = [item.split(":") for item in all_conf if not item.startswith("#")]

    # Turn this list of lists into a dictionary and remove the <axis> from the variable names

    return {key[:-1]: value for key, value in all_conf}


def process_cmd_string(command: str) -> str:
    """Prepares the command string for sending to the controller.
    A carriage return and newline is appended to the command."""

    # MODULE_LOGGER.debug(f"process_command() = {command}")

    return add_cr_lf(command)


class HuberSMC9300Interface(DeviceInterface):
    """
    Interface definition for the Controller, Simulator and Proxy classes for this device.
    """

    @dynamic_command(
        cmd_type="query", cmd_string="?",
        process_cmd_string=process_cmd_string,
        process_response=decode_info)
    def info(self) -> str:
        """
        Retrieve basic information about the Huber Stages and the Controller.
        The returned string contains multiple lines seperated by a newline (`\n`).
        """
        raise NotImplementedError

    @dynamic_command(
        cmd_type="query", cmd_string="?conf${axis}",
        process_cmd_string=process_cmd_string,
        process_response=decode_get_configuration)
    def get_configuration(self, axis) -> dict | Failure:
        """
        Returns the configuration parameters for the given axis.

        Returns:
            A dictionary with configuration parameter names and their values.
        """
        raise NotImplementedError

    def get_conf_value(self, axis, name):
        """
        Returns the value of the requested configuration parameter.

        Returns:
            A string containing the value of the requested parameter. The returned object is
            always a string and needs to be converted to int or float by the caller if needed.
        """
        conf = self.get_configuration(axis)
        return conf[name] if name in conf else None

    @dynamic_command(
        cmd_type="query", cmd_string="?v",
        process_cmd_string=process_cmd_string,
        process_response=decode_response)
    def get_version(self):
        """
        Returns the version information about the current control program on the HUBER controller.
        """
        raise NotImplementedError

    def goto(self, axis: int, position: float, wait: bool = True) -> int:
        """
        Moves the stage to the given absolute position. For the big rotation stage, the movement is done
        relative to the current position and the avoidance range and hard stop from the Setup are taken
        into account.

        A positive angle moves the rotation stage counter clockwise.

        Args:
            axis (int): the integer identifier of one of the axis controlled by the SMC
            position (float): when the given axis is a rotation stage, the position is given
                in degrees [deg], for a translation stage, the position is given
                in millimeter [mm].
            wait (bool): Only return when the device is in position [default=True]

        Returns:
            Zero (0) is returned unless a limit switch was hit, in which case +1 is returned when the LIMIT+ switch
            was hit, and -1 is returned when the LIMIT- switch was hit.
        """

        # For the big rotation stage use the workaround to avoid continuous movement in the same
        # direction, and to avoid the limit switch.

        if axis == HC_SETTINGS.BIG_ROTATION_STAGE:
            current = self.get_current_position(axis)
            movement = calculate_relative_movement(current, position)
            self.move_direct(axis, movement)
        else:
            self.goto_direct(axis, position)

        if wait:
            return self.wait_until_axis_ready(axis)

        return 0

    @dynamic_command(
        cmd_type="write", cmd_string="goto${axis}:${position}",
        process_cmd_string=process_cmd_string)
    def goto_direct(self, axis: int, position: float) -> None:
        """
        Moves the stage to the given absolute position. No position checking nor conversion is done.

        A positive angle moves the rotation stage counter clockwise.

        Args:
            axis (int): the integer identifier of one of the axis controlled by the SMC
            position (float): when the given axis is a rotation stage, the position is given
                in degrees [deg], for a translation stage, the position is given
                in millimeter [mm].
        """
        raise NotImplementedError

    def move(self, axis: int, distance: float, wait: bool = True) -> int:
        """
        Moves the stage relative to the current position in the given distance.

        A positive angle moves the rotation stage counterclockwise.

        Args:
            axis: the integer identifier of one of the axis controlled by the SMC
            distance: when the given axis is a rotation stage, the distance is given
                in degrees [deg], for a translation stage, the distance is given
                in millimeter [mm].
            wait (bool): Only return when the device is in position [default=True]

        Returns:
            Zero (0) is returned unless a limit switch was hit, in which case +1 is returned when the LIMIT+ switch
            was hit, and -1 is returned when the LIMIT- switch was hit.
        """
        self.move_direct(axis, distance)
        if wait:
            return self.wait_until_axis_ready(axis)
        return 0

    @dynamic_command(
        cmd_type="write", cmd_string="move${axis}:${distance}",
        process_cmd_string=process_cmd_string,
    )
    def move_direct(self, axis: int, distance: float) -> None:
        """
        Moves the stage relative to the current position in the given distance.

        A positive angle moves the rotation stage counterclockwise.

        Args:
            axis: the integer identifier of one of the axis controlled by the SMC
            distance: when the given axis is a rotation stage, the distance is given
                in degrees [deg], for a translation stage, the distance is given
                in millimeter [mm].
        """
        raise NotImplementedError

    @dynamic_command(
        cmd_type="write", cmd_string="home${axis}:he;hm${pos}",
        process_cmd_string=process_cmd_string,
    )
    def home_forward_direction(self, axis: int, pos: float = 0):
        """
        Execute a home position search procedure for the given axis. This function will search in
        forward direction for the encoder ECZ (index) signal and set the position to `pos`.

        Args:
            axis: the integer identifier of one of the axis controlled by the SMC, this
                  should be '3' for the translation stage (the other axes have an absolute encoder).
            pos: after the home is found, set the position to `pos`.

        """
        raise NotImplementedError

    @dynamic_command(
        cmd_type="write", cmd_string="home${axis}:he;hr${pos}",
        process_cmd_string=process_cmd_string,
    )
    def home_reverse_direction(self, axis: int, pos: float = 0):
        """
        Execute a home position search procedure for the given axis. This function will search in
        reverse direction for the encoder ECZ (index) signal and set the position to `pos`.

        Args:
            axis: the integer identifier of one of the axis controlled by the SMC, this
                  should be '3' for the translation stage (the other axes have an absolute encoder).
            pos: after the home is found, set the position to `pos`.

        """
        raise NotImplementedError

    @dynamic_command(
        cmd_type="write", cmd_string="ffast${axis}:${speed}",
        process_cmd_string=process_cmd_string)
    def set_slew_speed(self, axis, speed):
        """
        Configures the maximum slew speed used for the execution of manual
        positioning commands. The maximum speed depends on the motor type,
        driver type and positioning hardware properties.

        For axis=1 (big rotation stage) the slew speed is given in 1e-4 deg/s, i.e. a slew_speed of
        15_000 results in an actual speed of 1.5deg/s.

        Manual positioning commands are i.e. ``fast``, ``move``, ``goto``, or
        the use of the direction keys.
        """
        raise NotImplementedError

    def get_slew_speed(self, axis) -> int:
        """
        Returns the maximum slew speed used for the execution of manual
        positioning commands. The maximum speed depends on the motor type,
        driver type and positioning hardware properties.
        """
        return int(self.get_parameter(axis, "ffast")[-1])

    @dynamic_command(
        cmd_type="write", cmd_string="edev${axis}:${value}",
        process_cmd_string=process_cmd_string)
    def set_edev(self, axis, value):
        """
        Configure the maximum allowed deviation between actual position
        and commanded target position for closed-loop positioning. this
        value must not be less than the resolution of the used encoder.

        This command cannot be executed during positioning or program execution.
        """
        raise NotImplementedError

    def get_edev(self, axis) -> float:
        """
        Returns the maximum allowed deviation between actual position
        and commanded target position for closed-loop positioning.
        """
        return float(self.get_parameter(axis, "edev")[-1])

    @dynamic_command(
        cmd_type="write", cmd_string="edir${axis}:${value}",
        process_cmd_string=process_cmd_string)
    def set_edir(self, axis, value):
        """
        Configure the encoder rotation sense. For the case the controller returns the encoder
        position information with the wrong sign, use this command to change it correspondingly.

        This command cannot be executed during positioning or program execution.
        """
        raise NotImplementedError

    def get_edir(self, axis) -> int:
        """
        Returns the encoder rotation sense: 0 is normal, 1 is inverted.
        """
        return int(self.get_parameter(axis, "edir")[-1])

    def is_in_position(self, axis) -> bool:
        """
        Returns True if the mechanism is in position and not moving.
        """

        # The sleep of 0.5s here is empirically determined because tests failed randomly
        # because the position was apparently not completely reached. We also noticed an
        # oscilation when arriving at a certain position. A diagnostic test revealed that
        # the status sometimes changes bit 0 and bit 7 indicating the axis/controller
        # ready before the mechanism actually reached the setpoint. We need about
        # 0.2s before the actual value is reached, 0.5 seconds is a safe wait time.

        time.sleep(0.5)

        state = self.get_state(axis)

        return state & 0b10000001 == 0b10000001

    @dynamic_command(
        cmd_type="query", cmd_string="?p${axis}",
        process_cmd_string=process_cmd_string,
        process_response=decode_axis_float)
    def get_current_position(self, axis) -> float:
        """
        Returns the current position for this axis as a float. The position is
        given in degrees for rotation stages and in mm for translation stages.
        """
        raise NotImplementedError

    @dynamic_command(
        cmd_type="query", cmd_string="?e${axis}",
        process_cmd_string=process_cmd_string,
        process_response=decode_axis_float)
    def get_current_encoder_position(self, axis) -> float:
        """
        Returns the current encoder position for this axis as a float. The position
        is given in degrees for rotation stages and in mm for translation stages.
        """
        raise NotImplementedError

    @dynamic_command(
        cmd_type="query", cmd_string="?ec${axis}",
        process_cmd_string=process_cmd_string,
        process_response=decode_axis_int)
    def get_current_encoder_counter_value(self, axis) -> int:
        """
        Returns the current encoder counter value for this axis as an int.
        """
        raise NotImplementedError

    @dynamic_command(
        cmd_type="query", cmd_string="?err${axis}",
        process_cmd_string=process_cmd_string,
        process_response=decode_get_error)
    def get_error(self, axis) -> Tuple[str]:
        """
        Returns the last occurred error and corresponding error message for the given axis.
        """
        raise NotImplementedError

    @dynamic_command(
        cmd_type="query", cmd_string="?${name}${axis}",
        process_cmd_string=process_cmd_string,
        process_response=decode_get_parameter)
    def get_parameter(self, axis, name) -> Tuple[str, int, str]:
        """
        Queries the device for the current value of the given parameter and the given axis.

        Returns:
            A tuple containing the parameter name (str), axis (int), and the value (str).
        """
        raise NotImplementedError

    @dynamic_command(
        cmd_type="write", cmd_string="cerr${axis}",
        process_cmd_string=process_cmd_string)
    def clear_error(self, axis):
        """
        Reset the last occurred error and clear the error message.
        """
        raise NotImplementedError

    @dynamic_command(
        cmd_type="write", cmd_string="quit",
        process_cmd_string=process_cmd_string)
    def quit(self) -> None:
        """
        Immediately stop any positioning process.

        The controller decelerates with the configured deceleration ramp.
        In contrast to an emergency stop caused by limit switch events,
        the position information remains valid in this case.
        """
        raise NotImplementedError

    @dynamic_command(cmd_type="write", cmd_string="update", process_cmd_string=process_cmd_string)
    def save_configuration(self):
        """Saves the current configuration permanently. The settings will be reloaded automatically
        the next time the controller starts."""
        raise NotImplementedError

    @dynamic_command(cmd_type="write", cmd_string="reset", process_cmd_string=process_cmd_string)
    def reset(self):
        """Resets the controller back to power-on state. When you previously saved the configuration,
        those values will be reloaded automatically, otherwise the default configuration will be loaded."""
        raise NotImplementedError

    @dynamic_command(
        cmd_type="query", cmd_string="?s${axis}",
        process_cmd_string=process_cmd_string,
        process_response=decode_get_state)
    def get_state(self, axis) -> int:
        """Query of the current operating state of the controller."""
        raise NotImplementedError

    @dynamic_command(
        cmd_type="query", cmd_string="?status${axis}",
        process_cmd_string=process_cmd_string,
        process_response=decode_response)
    def get_status(self, axis) -> str:
        """
        Returns the status of the given axis. The status contains the following information:

            * axis: the axis number
            * err_no: the error number
            * err_msg: the error message if there is an error
            * pos: the current position
            * epos: the encoder position
            * elimit: end/limit status
            * ref: reference status
            * eref: encoder reference status
            * ctrl: is controller ready?
            * osc: status oscillation
            * pro: is program running?

        The status response can be untangled as follows:

            >>> dev = HuberSMC9300Proxy()
            >>> untangle_status(dev.get_status(axis=1))

        """
        raise NotImplementedError

    @dynamic_command(
        cmd_type="write", cmd_string="zero${axis}",
        process_cmd_string=process_cmd_string)
    def zero(self, axis) -> None:
        """
        Set the current position of the axis to zero (0.00). If a reference position
        offset value is configured (see the configuration command `rofs`) the current
        position is set to that reference offset value.

        If you want to retain this zero position, you will have to also call the
        'save_configuration()' command. Otherwise the zero position will be lost
        after a reset or a power cycle.
        """
        raise NotImplementedError

    def wait_until_axis_ready(self, axis: int) -> int:
        """
        Send the given axis a state query and wait for the response.

        This function will return only when one of the following states has been reached:

        * The LIMIT- switch was activated
        * The LIMIT+ switch was activated
        * The end position was reached, axis ready (bit 0) & controller ready (bit 7)

        Returns:

            *  0: on success, i.e. position is reached
            * +1: when LIMIT+ switch is reached
            * -1: when LIMIT- switch is reached
        """

        # MODULE_LOGGER.debug(f"Wait until axis {axis} is ready...")

        while True:

            time.sleep(0.5)

            state = self.get_state(axis)

            # MODULE_LOGGER.debug(f"state for axis {axis}: {beautify_binary(state)} ({state})")

            if state & 4 == 4:
                MODULE_LOGGER.warning("LIMIT- active!")
                rv = -1
                break

            if state & 8 == 8:
                MODULE_LOGGER.warning("LIMIT+ active!")
                rv = +1
                break

            if state & 512 == 512:
                MODULE_LOGGER.error("oscillation positioning error (encoder)")

            if state & 129 == 129:
                # exit loop when position is reached,
                # state bit 0 and bit 7 indicate 'axis ready' AND 'controller ready',
                # i.e. all axes stopped
                rv = 0
                break

            if state & 16384:  # 0b100_0000_0000_0000
                response = self.get_error(axis)
                MODULE_LOGGER.error(f"ERROR on axis {axis}: {response}")
                self.clear_error(axis)

        # The sleep of 0.5s here is empirically determined because tests failed randomly
        # because the position was apparently not completely reached. We also noticed an
        # oscillation when arriving at a certain position. A diagnostic test revealed that
        # the state sometimes changes bit 0 and bit 7 indicating the axis/controller
        # ready before the mechanism actually reached the setpoint. We need about
        # 0.2s before the actual value is reached, 0.5 seconds is a safe wait time.

        time.sleep(0.5)

        return rv


class HuberSMC9300Controller(HuberSMC9300Interface, DynamicCommandMixin):
    """
    The HuberSmC9300Controller class is used to directly communicate with the HUBER SMC9300
    Controller through an Ethernet interface.
    """

    def __init__(self, hostname=HC_SETTINGS.HOSTNAME, port=HC_SETTINGS.PORT):
        """
        Opens a TCP/IP socket connection with the HUBER SMC9300 Hardware Controller.

        Args:
            hostname (str): the IP address or fully qualified hostname of the HUBER hardware
                controller. The default is defined in the ``settings.yaml`` configuration file.

            port (int): the IP port number to connect to, by default set in the `settings.yaml`
                configuration file.

        """
        super().__init__()

        MODULE_LOGGER.info(
            f"Initializing Huber SMC9300 Controller with hostname={hostname} on port={port}")

        self.transport = self.huber = HuberSMC9300EthernetInterface(hostname, port)

        self._number_of_axes = HC_SETTINGS.NUMBER_OF_AXES

    def connect(self):
        try:
            self.huber.connect()

            # set the speed of each of the stages to the default speed from the Settings.

            for stage in 1, 2, 3:
                default_speed = HC_SETTINGS.DEFAULT_SPEED[stage - 1]
                self.set_slew_speed(stage, default_speed)

        except HuberError as exc:
            MODULE_LOGGER.warning(f"HuberError caught: Couldn't establish connection ({exc})")
            raise ConnectionError("Couldn't establish a connection with the HUBER Stage.") from exc

        self.notify_observers(DeviceConnectionState.DEVICE_CONNECTED)

    def disconnect(self):
        try:
            # Clear the error for each of the axis before disconnecting
            for axis in range(1, self._number_of_axes + 1):
                self.clear_error(axis)
            self.huber.disconnect()
        except DeviceConnectionError as exc:
            raise ConnectionError("Couldn't disconnect from HUBER Controller.") from exc

        self.notify_observers(DeviceConnectionState.DEVICE_NOT_CONNECTED)

    def reconnect(self):
        if self.is_connected():
            self.disconnect()
        self.connect()

    def is_connected(self):
        """Check if the HUBER Stages Controller is connected. """
        return self.huber.is_connected()

    def is_simulator(self):
        return "simulator: true" in self.info()


class HuberSMC9300Simulator(HuberSMC9300Interface):
    """
    The class simulates the HUBER Stages.
    """

    def __init__(self):
        super().__init__()
        MODULE_LOGGER.critical(
            textwrap.dedent(
                """\
                The HuberSMC9300Simulator class is deprecated in favor of the smc9300_sim process. 
                Start the SMC9300 simulator in a separate terminal with the command:
                
                   smc9300_sim start
                
                then restart the SCM9300 Control Server: 
                
                   smc9300_cs start
                
                Make sure the local_settings.yaml file contains the correct HOSTNAME
                and PORT for accessing the simulator process. 
                """
            )
        )


REQUEST_TIMEOUT = 10_000  # 10 seconds


class HuberSMC9300Proxy(DynamicProxy, HuberSMC9300Interface):
    """
    The HuberProxy class is used to connect to the Huber SMC9300 control server and send commands
    to the HUBER Hardware Controller remotely.
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


def calculate_relative_movement(current, setpoint, hardstop=None, avoidance=None):
    """
    This function calculates the relative movement from the current position to the given setpoint.
    It defines the direction and the size of the movement based on the current position,
    the setpoint, the hardstop position and the avoidance angle.

    The function strives to always return the smallest possible angle in order to minimize the
    duration of the movement.

    The target position (setpoint) can not fall in the range [hardstop - avoidance,
    hardstop + avoidance]. There is no check on the current position, it is assumed not to be in
    the avoidance range.

    If hardstop or avoidance are not given, they are loaded from the setup.

    Args:
        current (float): the current position of the rotation stage
        setpoint (float): the target position of the rotation stage
        hardstop (float): the location of the hardstop
        avoidance (float): angle of avoidance
    Returns:
        The angle to move relative from current position to setpoint.
    Raises:
        A ValueError when the setpoint falls inside the avoidance range, i.e.
        [-180 + avoidance, +180 - avoidance].
    """

    setup = GlobalState.setup

    avoidance = avoidance if avoidance is not None else setup.gse.stages.big_rotation_stage.avoidance
    hardstop = hardstop if hardstop is not None else setup.gse.stages.big_rotation_stage.hardstop

    # MODULE_LOGGER.debug(f"@entry: {current=}, {setpoint=}, {hardstop=}, {avoidance=}")

    # Bring the current and the setpoint between 0 and 360 (non-inclusive)

    current %= 360
    setpoint %= 360

    # MODULE_LOGGER.debug(f"After % 360: {current=}, {setpoint=}")

    # Check if the setpoint falls in the avoidance range

    if hardstop - avoidance < setpoint < hardstop + avoidance:
        raise ValueError(
            f"setpoint argument shall NOT be between {hardstop - avoidance} and "
            f"{hardstop + avoidance}, given value {setpoint = }")

    # Find the smallest angle between the current and the setpoint

    movement = min(abs(current - setpoint), abs(360 + current - setpoint))
    direction = +1 if current + movement == setpoint else -1

    target = current + direction * movement

    # MODULE_LOGGER.debug(
    #     f"Smallest movement: {current=}, {setpoint=}, {target=:.2f}, "
    #     f"{movement=:.2f}, {direction=}"
    # )

    # Check if we will pass over 180º and invert direction if true.

    if (current < target and current < hardstop < target) or \
            (current > target and target < hardstop < current):
        movement = 360 - movement
        direction *= -1

        # target = current + direction * movement
        # MODULE_LOGGER.debug(
        #     f"corrected: {current=}, {setpoint=}, {target=:.2f}, {movement=:.2f}, {direction=}"
        # )

    return direction * movement


if __name__ == "__main__":
    from rich import print

    huber = HuberSMC9300Controller()

    # The .connect() method takes 1.5s because it also configures the slew speed of all the axes

    huber.connect()

    print(f"{huber.info()=}")
    print(f"{huber.get_version()=}")
    print(f"{huber.get_error(axis=1)=}")
    print(f"{huber.get_error(axis=2)=}")
    print(f"{huber.get_error(axis=3)=}")
    print(f"{huber.get_state(axis=1)=}")
    print(f"{huber.get_state(axis=2)=}")
    print(f"{huber.get_state(axis=3)=}")
    print(f"{huber.get_status(axis=1)=}")
    print(f"{huber.get_status(axis=2)=}")
    print(f"{huber.get_status(axis=3)=}")
    print(f"{huber.get_configuration(axis=1)=}")
    print(f"{huber.get_configuration(axis=2)=}")
    print(f"{huber.get_configuration(axis=3)=}")
    print(f"{huber.get_conf_value(axis=1, name='gnum')=}")
    print(f"{huber.get_slew_speed(axis=1)=}")
    print(f"{huber.get_slew_speed(axis=2)=}")
    print(f"{huber.get_slew_speed(axis=3)=}")
    print(f"{huber.is_in_position(axis=1)=}")
    print(f"{huber.is_in_position(axis=2)=}")
    print(f"{huber.is_in_position(axis=3)=}")
    print(f"{huber.get_current_position(axis=1)=}")
    print(f"{huber.get_current_position(axis=2)=}")
    print(f"{huber.get_current_position(axis=3)=}")
    print(f"{huber.get_current_encoder_position(axis=1)=}")
    print(f"{huber.get_current_encoder_position(axis=2)=}")
    print(f"{huber.get_current_encoder_position(axis=3)=}")
    print(f"{huber.get_current_encoder_counter_value(axis=1)=}")
    print(f"{huber.get_current_encoder_counter_value(axis=2)=}")
    print(f"{huber.get_current_encoder_counter_value(axis=3)=}")

    for axis_ in range(1, 4):
        print(f"{huber.get_parameter(axis=axis_, name='ffast')=}")
        print(f"{huber.get_parameter(axis=axis_, name='frun')=}")
        print(f"{huber.get_parameter(axis=axis_, name='rofs')=}")
        print(f"{huber.get_parameter(axis=axis_, name='erofs')=}")

        print(f"{huber.get_parameter(axis=axis_, name='ecl')=}")
        print(f"{huber.get_parameter(axis=axis_, name='edev')=}")
        print(f"{huber.get_parameter(axis=axis_, name='edir')=}")
        print(f"{huber.get_parameter(axis=axis_, name='eres')=}")

        huber.clear_error(axis=axis_)

    huber.disconnect()
