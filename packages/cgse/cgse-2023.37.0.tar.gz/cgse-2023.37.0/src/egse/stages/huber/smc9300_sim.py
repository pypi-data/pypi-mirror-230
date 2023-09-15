"""
This module provides a simple simulator for the HUBER stages SMC9300.

The difference between this simulator and the HuberSMC9300Simulator class is that this module is a
standalone process that will accept the command set as accepted by the SMC9300 device controller,
while the HuberSMC9300Simulator class replaces the Huber9300Controller and never communicates
with a device.

This simulator is a very simple implementation. It responds to a number of known commands with
little to no intelligence behind it.

Known commands are:

* version - returns a version string

Usage:

   $ smc9300_sim start

"""
from __future__ import annotations

import multiprocessing.process
import textwrap
import time
from typing import Optional

from egse.settings import Settings

multiprocessing.current_process().name = "smc9300_sim"

import logging
import re
import socket
from enum import Enum

import click

logging.basicConfig(level=logging.DEBUG)

LOGGER = logging.getLogger("egse.stages.huber.smc9300_sim")

HOST = "localhost"
STAGES_SETTINGS = Settings.load("Huber Controller")


class InvalidStateError(Exception):
    pass


def write(conn, response: str) -> None:
    """
    Writes a response string on the socket connection.

    Args:
        conn: the socket that is used for communication
        response: the response of the previous command

    Returns:
        None.
    """
    response = f"{response}\r\n".encode()
    # LOGGER.debug(f"{response=}")
    conn.sendall(response)


def read(conn) -> str:
    """
    Reads one command string from the socket, i.e. until a linefeed ('\n') is received.

    Returns:
        The command string with the linefeed stripped off.
    """

    idx, n_total = 0, 0
    buf_size = 1024 * 4
    command_string = bytes()

    try:
        for _ in range(100):
            data = conn.recv(buf_size)
            n = len(data)
            n_total += n
            command_string += data
            # if data.endswith(b'\n'):
            if n < buf_size:
                break
    except socket.timeout as e_timeout:
        LOGGER.warning(f"Socket timeout error from {e_timeout}")
        return ""

    # LOGGER.debug(f"Total number of bytes received is {n_total}, idx={idx}")
    # LOGGER.debug(f"{command_string=}")

    return command_string.decode().rstrip()


class AxisTimer:
    """
    This class controls all the timings of an axis.
    """

    def __init__(self):
        self._start_time = time.time()
        self._running = False

    def is_running(self):
        return self._running

    def start(self):
        """Start the timer."""
        self._start_time = time.time()
        self._running = True

    def stop(self):
        """Stop the timer."""
        self._start_time = time.time()
        self._running = False

    def get_delta_time(self) -> float:
        """
        Returns the delta time since the start() method was called on this
        AxisTimer.

        :returns: delta time in seconds since the start of the timer
        """
        return time.time() - self._start_time if self._running else 0.0


class Axis:
    """
    This class controls the settings and movements of one particular axis
    for the HUBER Stages.

    Do not use this class directly, it is used from within the HuberSimulator.
    """

    def __init__(self, slew_speed, encoder_conversion, alias, type_):
        # Translation Stage: slew_speed = 77_200, encoder_conversion = 20_000
        # Big Rotation: slew_speed = 22_943_316, encoder_conversion = 11_930_500
        self._alias = alias
        self._type = type_
        self._slew_speed = slew_speed  # 1e-4 deg per second -> 15_000 is 1.5 deg/s
        self._encoder_conversion_factor = encoder_conversion  # encoder positions per mm/deg
        self._encoder_counter_offset = 4287251092
        self._encoder_position = 0.0
        self._current_position = 0.0
        self._start_position = 0.0
        self._edev = 0.001
        self._edir = 0
        self._frun = 0
        self._commanded_position = None
        self._moving = False
        self._distance = 0
        self._direction = 0
        self._timer = AxisTimer()
        self._biss_t = 360 if self._type == 0 else 0

        self._unit = "deg" if self._type == 0 else "mm"

    @property
    def alias(self):
        return self._alias

    @property
    def type(self):
        return self._type

    @property
    def unit(self):
        return self._unit

    @property
    def ffast(self):
        return self._slew_speed

    @property
    def frun(self):
        return self._frun

    @property
    def edev(self):
        return self._edev

    @edev.setter
    def edev(self, value: float):
        self._edev = value

    @property
    def edir(self):
        return self._edir

    @edir.setter
    def edir(self, value: int):
        # value can be 0 or 1 only
        self._edir = value

    def get_slew_speed(self) -> int:
        return self._slew_speed

    def set_slew_speed(self, speed: int):
        self._slew_speed = speed

    def get_converted_slew_speed(self) -> float:
        """Returns the slew speed in mm/s or deg/s"""
        return self._slew_speed * 1e-4

    def get_state(self) -> int:
        return 0 if self._moving else 129

    def start(self):
        """
        Start a movement. A movement is defined as the change from the current
        position to the commanded position. Therefore, the start position will
        be set to the current position and all calculations including time will
        be with respect to the starting position.
        """
        if self._commanded_position is None:
            raise InvalidStateError("Can not start a movement if commanded position is not set.")

        self._timer.start()
        self._moving = True
        self._distance = self._current_position - self._commanded_position
        self._direction = 1 if self._commanded_position > self._current_position else -1
        self._start_position = self._current_position

    def stop(self):
        """
        Stop a movement by

        """
        self._moving = False
        self._timer.stop()

    def set_commanded_position(self, position):
        self._commanded_position = position

    def get_current_position(self) -> float:
        self._calc_current_position()
        return self._current_position

    def get_encoder_position(self) -> float:
        return self.get_current_position()  # add some noise here

    def get_encoder_counter_value(self) -> int:
        return self._encoder_counter_offset + int(self.get_encoder_position() * self._encoder_conversion_factor)

    def is_in_position(self) -> bool:
        self._calc_current_position()
        return not self._moving

    def _calc_current_position(self):
        if not self._moving:
            return

        delta_t = self._timer.get_delta_time()
        slew_speed = self.get_converted_slew_speed()
        travel = slew_speed * delta_t

        # LOGGER.info(f"{delta_t=}, {slew_speed=}, {travel=}")

        if travel >= abs(self._distance):
            self._current_position = self._commanded_position
            self._moving = False
            self._distance = 0.0
        else:
            self._current_position = self._start_position + travel * self._direction


class OnOff(str, Enum):

    ON = "ON"
    OFF = "OFF"


class State:
    def __init__(self, axis: int):
        self.axis = axis
        self.errors = []
        self.slew_speed = 20_000
        self.current_position = 270
        self.current_encoder_position = 271
        self.current_encoder_counter = 272_000
        self.controller_ready = True
        self.is_connected = False


# The slew_speed and the encoder_conversion factor is empirically determined from the
# hardware measures between 0 and 100. The timings that result for these stages are
# only approximately correct.

axes = [
    None,
    Axis(22_943_316, 11_930_500, alias="01~rot (420-20913)", type_=0),
    Axis(20_000, 20_000, alias="02~rot (409-10661)", type_=0),
    Axis(77_200, 20_000, alias="03~lin (5101.30-943)", type_=1),
]


states = [None, State(1), State(2), State(3)]

error_msg = ""


def get_configuration(axis: str) -> str:
    axis = int(axis)
    response = (
        f"# configuration settings of axis {axis}\r\n"
        f"alias{axis}:{axes[axis].alias}\r\n"
        f"type{axis}:{axes[axis].type}\r\n"
        f"unit{axis}:{axes[axis].unit}\r\n"
        f"ffast{axis}:{axes[axis].ffast}\r\n"
        f"frun{axis}:{axes[axis].frun}\r\n"
        f"gnum{axis}:10000\r\n"
        f"biss_t{axis}:{axes[axis]._biss_t}"  # last line doesn't have a \r\n, will be added later
    )
    return response


def cancel_movement(axis: Optional[str] = None):

    if axis is None:
        for axis in axes:
            axis and axis.stop()
    else:
        axes[int(axis)].stop()


def clear_error(axis: str) -> None:
    states[int(axis)].errors = []


def get_error(axis: str) -> str:
    return f"{axis}:0"


def get_parameter(par_name: str, axis: str) -> str:
    # LOGGER.info(f"get_parameter({par_name=}, {axis=})")
    if par_name == "edev":
        return f"{par_name}{axis}:{axes[int(axis)].edev}"
    elif par_name == "edir":
        return f"{par_name}{axis}:{axes[int(axis)].edir}"
    elif par_name == "ffast":
        return f"{par_name}{axis}:{axes[int(axis)].ffast}"
    elif par_name == "frun":
        return f"{par_name}{axis}:{axes[int(axis)].frun}"

    return f"{par_name}{axis}:0"


def set_parameter(par_name: str, axis: str, value: int | float):
    # LOGGER.info(f"set_parameter({par_name=}, {axis=}, {value=}")
    if par_name == "edev":
        axes[int(axis)].edev = float(value)
    elif par_name == "edir":
        axes[int(axis)].edir = int(value)


def get_status(axis: str):
    return f"{axis}:0::0:{axes[int(axis)].get_encoder_position()}:0:0:0:1:0:0:0:0:0:0:0:0\r\n"


def get_state(axis: str):
    return f"{axis}:{axes[int(axis)].get_state()};"


def set_slew_speed(axis: str, slew_speed: str):
    axes[int(axis)].set_slew_speed(int(slew_speed))


def get_current_position(axis: str) -> str:
    return f"{axis}:{axes[int(axis)].get_current_position()};"


def get_current_encoder_position(axis: str) -> str:
    # For now, we just return the current position, but this should actually
    # lag a little behind the current position. That's why it is to_be_implemented.
    return f"{axis}:{axes[int(axis)].get_encoder_position()};"


def get_current_encoder_counter_value(axis: str) -> str:
    return f"{axis}:{axes[int(axis)].get_encoder_counter_value()};"


def goto_position(axis, position):

    axis = int(axis)
    position = float(position)

    # For the big rotation stage use the workaround to avoid continuous movement in the same
    # direction, and to avoid the limit switch.

    axes[axis].set_commanded_position(position)
    axes[axis].start()


def move_to_position(axis, distance):

    axis = int(axis)
    distance = float(distance)

    cp = axes[axis].get_current_position()
    axes[axis].set_commanded_position(cp + distance)
    axes[axis].start()


def home_position(axis, direction, pos):
    LOGGER.debug(f"home{axis}:he;{direction}{pos}")
    LOGGER.warning("The home_position() command is not yet implemented.")


def save_configuration():
    print("Request to save the current configuration, not implemented.")


def reset():
    print("Request to reset the device, not implemented.")


def nothing():
    return None


class Pass:
    """
    Used to indicate that the arguments from the pattern match should be passed on to the
    response function.
    """
    def __bool__(self):
        return False


pass_args = Pass()


COMMAND_ACTIONS_RESPONSES = {
    "?v": (None, "smc 1.2.1093"),
    "?": (None, textwrap.dedent("""\
              system date: June 20, 2022 08:44:22
              os image: wes7
              control IC: MCX
              FBWF/UWF: disabled
              available axes: 3
              counter: not installed.
              filter device: not available.
              half screen device: not available.
              simulator: true.
              
              ?:cmdlist returns a command list,
              ?:xyz returns help for command 'xyz'.
              ?<parameter>{:<axis>} returns current setting.
              """)),
    "update": (save_configuration, nothing),
    "reset": (reset, nothing),
    "quit": (cancel_movement, nothing)
}

COMMAND_PATTERNS_ACTIONS_RESPONSES = {
    r"cerr(\d)": (clear_error, nothing),
    r"ffast(\d)\:(\d+)": (set_slew_speed, nothing),
    r"(edev)(\d):(\d+(?:\.\d+)?)": (set_parameter, nothing),
    r"(edir)(\d):(\d)": (set_parameter, nothing),
    r"goto(\d):(-?\d+(?:\.\d+)?)": (goto_position, nothing),
    r"move(\d):(-?\d+(?:\.\d+)?)": (move_to_position, nothing),
    r"home(\d):he;(h[mr])(-?\d+(?:\.\d+)?)": (home_position, nothing),
    r"\?err(\d)": (pass_args, get_error),
    r"\?p(\d)": (pass_args, get_current_position),
    r"\?e(\d)": (pass_args, get_current_encoder_position),
    r"\?ec(\d)": (pass_args, get_current_encoder_counter_value),
    r"\?s(\d)": (pass_args, get_state),
    r"\?status(\d)": (pass_args, get_status),
    r"\?conf(\d)": (pass_args, get_configuration),
    r"\?(\w+)(\d)": (pass_args, get_parameter),
}


def process_command(command_string: str) -> str:

    LOGGER.debug(f"{command_string = }")

    try:
        action, response = COMMAND_ACTIONS_RESPONSES[command_string]
        action and action()
        if error_msg:
            return error_msg
        else:
            return response if isinstance(response, str) else response()
    except KeyError:
        # try to match with a value
        for key, value in COMMAND_PATTERNS_ACTIONS_RESPONSES.items():
            if match := re.match(key, command_string):
                LOGGER.debug(f"{match=}, {match.groups()}")
                action, response = value
                LOGGER.debug(f"{action=}, {response=}")
                # if action is not None and not isinstance(action, Pass):
                action and action(*match.groups())
                if error_msg:
                    return error_msg
                if isinstance(response, str):
                    return response
                elif isinstance(action, Pass):
                    return response(*match.groups())
                else:
                    return response()
        return f"ERROR: unknown command string: {command_string}"


@click.group()
def cli():
    pass


@cli.command()
def start():  # sourcery skip: hoist-statement-from-loop
    global error_msg

    LOGGER.info("Starting the SMC9300 Simulator")

    quit_request = False

    while not quit_request:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, STAGES_SETTINGS.PORT))
            s.listen()
            conn, addr = s.accept()
            with conn:
                LOGGER.info(f"Accepted connection from {addr}")
                write(conn, 'smc 1.2.1093')
                try:
                    while True:
                        error_msg = ""
                        data = read(conn)
                        if (response := process_command(data)) is not None:
                            write(conn, response)
                        LOGGER.debug(f"{data = } -> {response = }")
                        if not data:
                            break  # connection closed by peer
                except KeyboardInterrupt:
                    LOGGER.info("Keyboard interrupt, closing.")
                except ConnectionResetError as exc:
                    LOGGER.info(f"ConnectionResetError: {exc}")
                except Exception as exc:
                    LOGGER.info(f"{exc.__class__.__name__} caught: {exc.args}")


if __name__ == "__main__":
    cli()
