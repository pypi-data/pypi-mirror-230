"""
This module provides a simple simulator for the OGSE equipment.

The difference between this simulator and the OGSESimulator class is that this module is a
standalone process that will accept the command set as accepted by the OGSE device, while the
OGSESimulator class replaces the OGSEController and never communicates with a device.

This simulator is a very simple implementation. It responds to a number of known commands with
little to no intelligence behind it.

Known commands are:

* ldls status – returns "OK"
* ldls power on|off - returns "OK"
* ldls operate on|off - returns "OK"
* get lamp - return "lamp: ON|OFF"
* get laser - return "laser: ON|OFF"
* att status - returns "attenuator: ready"
* version - returns a version string

Usage:

   $ ogse_sim start

"""
import multiprocessing.process

from egse.collimator.fcul.ogse import get_attenuation_index
from egse.settings import Settings
from egse.system import SignalCatcher

multiprocessing.current_process().name = "ogse_sim"

import logging
import random
import re
import socket
import time
from enum import Enum

import click

from egse.collimator.fcul.ogse import ATT_LEVELS_BY_FACTOR
from egse.collimator.fcul.ogse import ATT_LEVELS_BY_WHEEL


logging.basicConfig(level=logging.DEBUG)

LOGGER = logging.getLogger("egse.ogse.sim")
HOST = "localhost"
OGSE_SETTINGS = Settings.load("OGSE Controller")


def write(conn, response: str):

    response = f"{response}\n".encode()
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
        for idx in range(100):
            data = conn.recv(buf_size)
            n = len(data)
            n_total += n
            command_string += data
            # if data.endswith(b'\n'):
            if n < buf_size:
                break
    except socket.timeout as e_timeout:
        # LOGGER.warning(f"Socket timeout error from {e_timeout}")
        # This timeout is catch at the caller, where the timeout is set.
        raise

    # LOGGER.debug(f"Total number of bytes received is {n_total}, idx={idx}")
    # LOGGER.debug(f"{command_string=}")

    return command_string.decode().rstrip()


class OnOff(str, Enum):

    ON = "ON"
    OFF = "OFF"


class OGSEState:

    def __init__(self):

        self.ldls_power = OnOff.OFF
        self.ldls_lamp = OnOff.OFF
        self.ldls_laser = OnOff.OFF
        self.att_level = 0.0
        self.att_level_index = 0  # [0:46]
        self.att_is_moving = False
        self.psu = OnOff.OFF
        self.operate = OnOff.OFF
        self.interlock = OnOff.ON  # OPEN by default


ogse_state = OGSEState()
error_msg = ""
fw_moving_until = time.time()


def get_pm_status():
    return "pm1: OK, pm2: ERROR"


def toggle_interlock():
    ogse_state.interlock = OnOff.ON if ogse_state.interlock == OnOff.OFF else OnOff.OFF


def ldls_power_on():
    ogse_state.ldls_power = OnOff.ON


def ldls_power_off():
    ogse_state.ldls_power = OnOff.OFF


def ldls_operate_on():

    ogse_state.ldls_laser = OnOff.ON
    ogse_state.ldls_lamp = OnOff.ON

    ogse_state.operate = OnOff.ON


def ldls_operate_off():

    ogse_state.ldls_laser = OnOff.OFF
    ogse_state.ldls_lamp = OnOff.OFF

    ogse_state.operate = OnOff.OFF


def get_interlock():
    return f'interlock: {"OPEN" if ogse_state.interlock == OnOff.ON else "CLOSE"}'


def get_lamp():
    return f"lamp: {ogse_state.ldls_lamp.name}"


def get_power():
    return f"power: {ogse_state.ldls_power.name}"


def get_laser():
    return f"laser: {ogse_state.ldls_laser.name}"


def get_att_status():
    return 'att: OK'


def get_att_level():

    levels = list(ATT_LEVELS_BY_FACTOR.values())

    # Find the value from the levels list which is closest to the att_level

    value = min(levels, key=lambda x: abs(x - ogse_state.att_level))

    att_index = levels.index(value)

    return f"att-level: {'*' if is_fw_moving() else ''}     {ogse_state.att_level:.1E} #{att_index}"


def att_level_up():

    levels = list(ATT_LEVELS_BY_FACTOR.values())
    index = min(levels.index(ogse_state.att_level) + 1, 46)

    # if factor >= 46:
    #     return "ERROR: usage: attenuator level #index  -- index goes from 0 to 46"

    ogse_state.att_level = ATT_LEVELS_BY_FACTOR[index]


def att_level_down():

    levels = list(ATT_LEVELS_BY_FACTOR.values())
    index = max(levels.index(ogse_state.att_level) - 1, 0)

    # if factor <= 0:
    #     return "ERROR: usage: attenuator level #index  -- index goes from 0 to 46"

    ogse_state.att_level = ATT_LEVELS_BY_FACTOR[index]


def set_att_level_index(index: int):
    """

    Args:
        index:an integer between 0 and 46 (including)
    """

    global error_msg
    global fw_moving_until

    index = int(index)

    if 0 <= index <= 46:

        ogse_state.att_level = att_level = ATT_LEVELS_BY_FACTOR[index]
        ogse_state.att_level_index = index
        LOGGER.debug(f"att level #{index} -> {att_level}")

    else:

        error_msg = "ERROR: usage: attenuator level #index  -- index goes from 0 to 46"

    fw_moving_until = time.time() + random.random() * 3 + 6  # wait between 6.0 and 9.0 seconds


def set_att_level_position(pos1, pos2):
    global error_msg
    global fw_moving_until

    wheel1, wheel2 = int(pos1), int(pos2)
    if (not 0 < wheel1 <= 8) and (not 0 < wheel2 <= 8):
        error_msg = (
            "ERROR: usage: attenuator level <wheel_1> <wheel_2>  "
            "-- wheel positions must be integer = 1..8"
        )
        return
    ogse_state.att_level = att_level = ATT_LEVELS_BY_WHEEL[(wheel1, wheel2)]
    ogse_state.att_level_index = get_attenuation_index(att_level)
    LOGGER.debug(f"att level {wheel1} {wheel2} -> {ogse_state.att_level_index} -> {att_level}")

    fw_moving_until = time.time() + random.random() * 3 + 6  # wait between 6.0 and 9.0 seconds


def set_att_level_factor(level):

    global error_msg
    global fw_moving_until

    level = float(level)

    if not 0.0 <= level <= 1.0:
        error_msg = 'ERROR: usage: attenuator level <value>  -- value must be in [0,1]'
        return

    ogse_state.att_level = att_level = level
    LOGGER.debug(f"att level {level} -> {att_level}")

    fw_moving_until = time.time() + random.random() * 3 + 6  # wait between 6.0 and 9.0 seconds


def pm_get_power_and_temperature():
    return 'pm1: +2.231652e-10 W +22.5 \xc2\xbaC, pm2: +nan W +nan \xc2\xbaC'


def get_lamp_fault():
    # use signal USR1 instead
    [error] = random.choices(["ERROR", "NO-ERROR"], weights=[1, 5])
    error = "NO-ERROR"
    return f"lamp-fault: {error}"


def get_controller_fault():
    # use signal USR2 instead
    [error] = random.choices(["ERROR", "NO-ERROR"], weights=[1, 5])
    error = "NO-ERROR"
    return f"controller-fault: {error}"


def get_psu():
    return f"psu: {ogse_state.psu.name}"


def get_operate():
    return f"operate: {ogse_state.operate.name}"


def get_status():
    return (
        f'power: {ogse_state.ldls_power.name}, '
        f'lamp: {ogse_state.ldls_lamp.name}, '
        f'interlock: {ogse_state.interlock.name}, '
        f'psu: {ogse_state.psu.name}, '
        f'att: {"* " if is_fw_moving() else ""}{ogse_state.att_level} #{ogse_state.att_level_index}, '
        f'power-ch1: +3.185751e-11 W, power-ch2: +2.092843e-07 W, '
        f'temp-ch1: +22.2 \xc2\xbaC, temp-ch2: +22.4 \xc2\xbaC\n'
    )

def is_fw_moving():
    return time.time() < fw_moving_until

def nothing():
    return None


COMMAND_ACTIONS_RESPONSES = {
    "version": (None, "PLATO-RT-OGSE (v2.1.sim)"),
    "get flags": (None, "flags: 0x00  0000 0000"),
    "ldls status": (None, "ldls: OK"),
    "pm status": (None, get_pm_status),
    "att status": (None, get_att_status),
    "power on": (ldls_power_on, "OK"),
    "power off": (ldls_power_off, "OK"),
    "operate on": (ldls_operate_on, "OK"),
    "operate off": (ldls_operate_off, "OK"),
    "level": (None, get_att_level),
    "level up": (att_level_up, "OK"),
    "level down": (att_level_down, "OK"),
    "get interlock": (None, get_interlock),
    "read": (None, pm_get_power_and_temperature),
    "get power": (None, get_power),
    "get lamp": (None, get_lamp),
    "get laser": (None, get_laser),
    "get lamp-fault": (None, get_lamp_fault),
    "get controller-fault": (None, get_controller_fault),
    "get psu": (None, get_psu),
    "get operate": (None, get_operate),
    "toggle interlock": (toggle_interlock, nothing),
    "status": (None, get_status),
}

COMMAND_PATTERNS_ACTIONS_RESPONSES = {
    # matches 'level 2 3'
    r"level (\d+) (\d+)": (set_att_level_position, "OK"),
    # matches 'level #25'
    r"level #(\d+)": (set_att_level_index, "OK"),
    # matches int or float: 1e-10
    r"level (\d+(?:\.\d+)?[eE][-+]?\d+)": (set_att_level_factor, "OK"),
    # matches int or float: 1, 37, 1.0, 0.45, .3
    r"level (\d+(?:\.\d+)?)": (set_att_level_factor, "OK"),
}


def process_command(command_string: str) -> str:

    # LOGGER.debug(f"{command_string=}")

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
                # LOGGER.debug(f"{match=}, {match.groups()}")
                action, response = value
                # LOGGER.debug(f"{action=}, {response=}")
                action and action(*match.groups())
                return error_msg or (response if isinstance(response, str) else response())
        return f"ERROR: unknown command string: {command_string}"


@click.group()
def cli():
    pass


@cli.command()
def start():  # sourcery skip: hoist-statement-from-loop
    global error_msg

    LOGGER.info("Starting the OGSE Simulator")

    killer = SignalCatcher()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, OGSE_SETTINGS.PORT))
        s.listen()
        s.settimeout(2.0)
        while True:
            while True:
                try:
                    conn, addr = s.accept()
                    break
                except socket.timeout:
                    pass
                if killer.term_signal_received:
                    return
            with conn:
                LOGGER.info(f'Accepted connection from {addr}')
                write(conn, 'This is PLATO RT-OGSE 2.1.sim')
                conn.settimeout(2.0)
                try:
                    while True:
                        error_msg = ""
                        try:
                            data = read(conn)
                            response = process_command(data)
                            write(conn, response)
                            if not data:
                                LOGGER.info("Client closed connection, accepting new connection...")
                                break
                        except socket.timeout:
                            pass
                        if killer.term_signal_received:
                            LOGGER.info("Terminating...")
                            return
                        if killer.user_signal_received:
                            if killer.signal_name == "SIGUSR1":
                                LOGGER.info("Sending toggle interlock command to OGSE simulator")
                                process_command("toggle interlock")
                            killer.clear()

                except KeyboardInterrupt:
                    LOGGER.info("Keyboard interrupt, closing.")
                except ConnectionResetError as exc:
                    LOGGER.info(f"ConnectionResetError: {exc}")
                except Exception as exc:
                    LOGGER.info(f"{exc.__class__.__name__} caught: {exc.args}")


if __name__ == "__main__":
    cli()
