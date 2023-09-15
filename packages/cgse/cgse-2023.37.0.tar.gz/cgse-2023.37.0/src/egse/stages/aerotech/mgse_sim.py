import multiprocessing.process

from sympy import re
multiprocessing.current_process().name = "mgse_sim"

import logging
import random
import re
import socket
import time
from enum import Enum
from egse.settings import Settings

import click

logging.basicConfig(level=logging.DEBUG)

DEVICE_SETTINGS = Settings.load("Aerotech Ensemble Controller")

LOGGER = logging.getLogger("egse.mgse.sim")
HOST = "localhost"
PORT = DEVICE_SETTINGS.PORT

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


class MGSEState:
    def __init__(self):
        self.XcwEOTLimit  = 0
        self.XccwEOTLimit = 0
        self.YcwEOTLimit  = 0
        self.YccwEOTLimit = 0
        self.Xhomed       = 1
        self.Yhomed       = 1
        self.Xenabled     = 1
        self.Yenabled     = 1

mgse_state = MGSEState()
error_msg  = ""
     
def set_limit(axis: str, side: str, state: bool):
    if axis == "Y":
        if side == "cw":
            mgse_state.YcwEOTLimit = state
        elif side == 'ccw':
            mgse_state.YccwEOTLimit = state
    elif axis == "X":
        if side == "cw":
            mgse_state.XcwEOTLimit = state
        elif side == 'ccw':
            mgse_state.XccwEOTLimit = state
            
def set_home(axis: str, state: bool):
    if axis == "Y":
        mgse_state.Yhomed = state
    elif axis == 'X':
        mgse_state.Xhomed = state
        
def set_enable(axis: str, state: bool):
    if axis == "Y":
        mgse_state.Yenabled = state
    elif axis == "X":
        mgse_state.Xenabled = state

def reset():
    set_enable('X', 0)
    set_enable('Y', 0)
    set_home('X', 0)
    set_home('Y', 0)
    set_limit('X', 'cw', 0)
    set_limit('X', 'ccw', 0)
    set_limit('Y', 'cw', 0)
    set_limit('Y', 'ccw', 0)


COMMAND_ACTIONS_RESPONSES = {
    "VERSION" : (None, "%Ensemble"),
    "RESET" : (None, "%"),
    "ABORT" : (None, "%"),
    "ACKNOWLEDGEALL" : (None, "%"),
    "MOVEABS" : (None, "%"),
    "HOME" : (None, "%"),
    "ENABLE" : (None, "%"),
    "AXISSTATUS(X)" : (None, "%11"),
    "AXISSTATUS(Y)" : (None, "%11"),
    "AXISFAULT(X)"  : (None, "%1100"),
    "AXISFAULT(Y)"  : (None, "%1100"),
    "PFBK(X)" : (None, "%10"),
    "PFBK(Y)" : (None, "%10"),
    "CMDPOS(X)" : (None, "%10"),
    "CMDPOS(Y)" : (None, "%10"),
    "PERR(X)" : (None, "%10"),
    "PERR(Y)" : (None, "%10"),
    "IFBK(X)"    : (None, "%0.5"),
    "ICMD(X)"   : (None, "%0.5"),
    "VFBK(X)"   : (None, "%0.01"),
    "VCMD(X)"   : (None, "%0.01"),
    "IFBK(Y)"    : (None, "%0.5"),
    "ICMD(Y)"   : (None, "%0.5"),
    "VFBK(Y)"   : (None, "%0.01"),
    "VCMD(Y)"   : (None, "%0.01")
}





def process_command(command_string: str) -> str:

    LOGGER.debug(f"{command_string=}")

    try:
        action, response = COMMAND_ACTIONS_RESPONSES[command_string]
        action and action()
        if error_msg:
            return error_msg
        else:
            return response if isinstance(response, str) else response()
    except KeyError:
        # try to match with a value
        return f"ERROR: unknown command string: {command_string}"


@click.group()
def cli():
    pass

@cli.command()
def start():
    global error_msg
    
    LOGGER.info("Starting the MGSE Simulator")
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print('Accepted connection from', addr)
            # write(conn, 'This is PLATO RT-OGSE 2.1')
            try:
                while True:
                    error_msg = ""
                    data = read(conn)
                    print(f"Received command: {data!r}")
                    data = data.split(" ")
                    response = process_command(data[0])
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