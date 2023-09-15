"""
This module provides a simple simulator for the TCS EGSE equipment.

The difference between this simulator and the TCSSimulator class is that this module is a
standalone process that will accept the command set as accepted by the TCS device, while the
TCSSimulator class replaces the TCSController and never communicates with a device.

This simulator is a very simple implementation. It responds to a number of known commands with
little to no intelligence behind it.

Known commands are:

Usage:

   $ tcs_sim start

"""
import logging
import multiprocessing.process
import re
import socket
from dataclasses import dataclass
from enum import Enum

import click

multiprocessing.current_process().name = "tcs_sim"

logging.basicConfig(level=logging.DEBUG)

LOGGER = logging.getLogger("egse.tcs.sim")
HOST = "localhost"
PORT = 6666


def write(conn, response: str):

    response = f"{response}\n".encode()
    LOGGER.debug(f"{response=}")
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
        LOGGER.warning(f"Socket timeout error from {e_timeout}")
        return ""

    LOGGER.debug(f"Total number of bytes received is {n_total}, idx={idx}")
    LOGGER.debug(f"{command_string=}")

    return command_string.decode().rstrip()


class OnOff(str, Enum):

    ON = "ON"
    OFF = "OFF"


@dataclass
class TCSState:

    remote_control_mode = False


def remote_operation_on():
    tcs_state.remote_control_mode = True


def remote_operation_off():
    tcs_state.remote_control_mode = False


def set_some_parameter(*args, **kwargs):
    LOGGER.info(f"set_some_parameter({args}, {kwargs})")


tcs_state = TCSState()
error_msg = ""

COMMAND_ACTIONS_RESPONSES = {
    "request_remote_operation": (remote_operation_on, "acknowledge_remote_operation"),
    "quit_remote_operation": (remote_operation_off, None),
}

COMMAND_PATTERNS_ACTIONS_RESPONSES = {
    # matches 'level 2 3'
    r"level (\d+) (\d+)": (set_some_parameter, "OK"),
    # matches 'level #25'
    r"level #(\d+)": (set_some_parameter, "OK"),
    # matches int or float: 1e-10
    r"level (\d+(?:\.\d+)?[eE][-+]?\d+)": (set_some_parameter, "OK"),
    # matches int or float: 1, 37, 1.0, 0.45, .3
    r"level (\d+(?:\.\d+)?)": (set_some_parameter, "OK"),
}


def process_command(command_string: str) -> str:

    LOGGER.debug(f"{command_string=}")

    try:
        action, response = COMMAND_ACTIONS_RESPONSES[command_string]
        action and action()
        if error_msg:
            return error_msg
        else:
            return response if isinstance(response, str) or response is None else response()
    except KeyError:
        # try to match with a value
        for key, value in COMMAND_PATTERNS_ACTIONS_RESPONSES.items():
            if match := re.match(key, command_string):
                LOGGER.debug(f"{match=}, {match.groups()}")
                action, response = value
                LOGGER.debug(f"{action=}, {response=}")
                action and action(*match.groups())
                return error_msg or (response if isinstance(response, str) else response())
        return f"ERROR: unknown command string: {command_string}"


@click.group()
def cli():
    pass


@cli.command()
def start():  # sourcery skip: hoist-statement-from-loop
    global error_msg

    LOGGER.info("Starting the TCS EGSE Simulator")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print('Accepted connection from', addr)
            try:
                while True:
                    error_msg = ""
                    data = read(conn)
                    print(f"Received command: {data!r}")
                    response = process_command(data)
                    if response is not None:
                        write(conn, response)
                    if not data:
                        break
            except KeyboardInterrupt:
                print("Keyboard interrupt, closing.")
            except ConnectionResetError as exc:
                print(f"ConnectionResetError: {exc}", flush=True)

    print(flush=True)


if __name__ == "__main__":
    cli()
