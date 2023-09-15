import time
from logging import warning

import pytest

from egse.control import Failure
from egse.hexapod.symetrie.puna import PunaProxy
from egse.hexapod.symetrie.punaplus import PunaPlusController
from egse.process import SubProcess
from egse.process import is_process_running
from egse.system import wait_until


@pytest.mark.skip(reason="For the puna_cs to use the Alpha+ controller we need to have proper Setup and Settings.")
def test_proxy():

    from rich import print as rp

    rp()

    puna_cs = SubProcess("PUNA CS Alpha+", ["puna_cs"], ["start"])
    puna_cs.execute()

    # We need the following sleep time for the process to start, initialize and perhaps fail.
    # If we do not wait, the check below, for is_process_running(), might be a false positive.

    time.sleep(5.0)

    if wait_until(is_process_running, ["puna_cs"], interval=1.0, timeout=5.0):
        raise RuntimeError("Couldn't start the PUNA Control Server within the given time of 5s.")

    # Now that the control server started properly, perform some tests with the proxy

    with PunaProxy() as puna_proxy:
        rp(f"{puna_proxy.info() = }")

    # Shut down the control server before finishing the test

    puna_cs_stop = SubProcess("PUNA Control Server", ["puna_cs", "stop"])
    puna_cs_stop.execute()

    if wait_until(is_process_running, ["puna_cs", "start"], interval=1.0, timeout=5.0):
        warning("Couldn't stop the DPU Control Server within the given time of 5s. Quiting...")
        puna_cs.quit()


def test_controller():

    from rich import print as rp

    rp()

    # puna = PunaPlusController(hostname="192.168.56.10", port=23)  # emulator running in VirtualBox
    puna = PunaPlusController(hostname="10.37.129.10", port=23)  # emulator running in Parallels Desktop
    puna.connect()

    rp(puna.info(), flush=True)
    rp(f"Version = {puna.version()}", flush=True)

    response = puna.query_variable("s_hexa")
    print(f"{response = } <- s_hexa")
    assert len(response) == 1

    response = puna.query_variables("s_hexa", 3)
    print(f"{response = } <- s_hexa,3")
    assert len(response) == 3

    response = puna.query_array("c_par", 0)
    print(f"{response = } <- c_par(0)")

    response = puna.query_array_values("c_par", 0, count=3)
    print(f"{response = } <- c_par(0),3")

    response = puna.query_variable("c_par")
    print(f"{response = } <- c_par")
    assert isinstance(response, Failure)
    assert "ILLEGAL CMD" in response.message

    response = puna.stop()
    rp(f"{response = } <- C_STOP")

    response = puna.homing()
    rp(f"{response = } <- C_HOME")

    while not puna.is_in_position():
        time.sleep(0.5)

    # it is possible to activate the control loop on motors even if the home is not complete

    response = puna.activate_control_loop()
    rp(f"{response = } <- C_CONTROLON")
    assert not isinstance(response, Failure)

    response = puna.deactivate_control_loop()
    rp(f"{response = } <- C_CONTROLOFF")

    response = puna.clear_error()
    print(f"{response = } <- C_CLEARERROR")

    rp(f"Version = {puna.version()}")

    response = puna.goto_machine_zero_position()
    print(f"{response = } <- goto_machine_zero_position")

    response = puna.get_machine_positions()
    print(f"{response = } <- get_machine_positions")
    assert len(response) == 6

    response = puna.goto_zero_position()
    print(f"{response = } <- goto_zero_position")

    response = puna.get_user_positions()
    print(f"{response = } <- get_user_positions")
    assert len(response) == 6

    while not puna.is_in_position():
        time.sleep(1.0)

    response = puna.move_ptp(0, 1, 2, 3, 0, 0, 10)
    print(f"{response = } <- move_ptp")

    response = puna.get_general_state()
    print(f"{response = } <- get_general_state")

    response = puna.get_actuator_state()
    print(f"{response = } <- get_actuator_state")

    puna.disconnect()


def test_alpha_plus_telnet_interface():

    from rich import print as rp
    from egse.hexapod.symetrie.dynalpha import AlphaPlusTelnetInterface

    rp()

    # telnet = AlphaPlusTelnetInterface(hostname="192.168.56.10")  # emulator running in VirtualBox
    telnet = AlphaPlusTelnetInterface(hostname="10.37.129.10")  # emulator running in Parallels Desktop
    telnet.connect()

    telnet.write('c_cmd=C_VERSION\r\n')
    response = telnet.read()
    rp(response.decode(), flush=True, end='')

    for _ in range(5):
        telnet.write('c_cmd\r\n')
        response = telnet.read()
        rp(response.decode(), flush=True, end='')
        if response.decode().split('\r\n')[1] == '0':
            break
        time.sleep(1)

    telnet.write('c_par(0),12,1\r\n')
    response = telnet.read()
    response = response.decode().split('\r\n')
    rp(response, flush=True)

    response = telnet.trans('c_cmd=C_VERSION\r\n')
    rp(response.decode(), flush=True, end='')

    for _ in range(10):
        response = telnet.trans('c_cmd\r\n')
        rp(response.decode(), flush=True, end='')
        if response.decode().split('\r\n')[1] == '0':
            break
        time.sleep(0.1)

    response = telnet.trans('c_par(0),12,1\r\n')
    response = response.decode().split('\r\n')
    rp(response, flush=True)

    telnet.disconnect()


def test_telnet_lib():

    from rich import print as rp
    from telnetlib import Telnet

    # telnet = Telnet("192.168.56.10", 23)    # emulator running in VirtualBox
    telnet = Telnet("10.37.129.10", 23)  # emulator running in Parallels Desktop

    rp()

    response = telnet.read_until(b'login: ', timeout=10)
    rp(response.decode(), flush=True, end='')
    telnet.write(b'root\r\n')
    response = telnet.read_until(b'Password: ', timeout=10)
    rp(response.decode(), flush=True, end='')
    telnet.write(b'deltatau\r\n')
    response = telnet.read_until(b'ppmac# ', timeout=10)
    rp(response.decode(), flush=True, end='')
    telnet.write(b'gpascii -2\r\n')
    response = telnet.read_until(b'\x06\r\n', timeout=1)
    rp(response.decode(), flush=True, end='')
    telnet.write(b'echo7\r\n')
    response = telnet.read_until(b'\x06\r\n', timeout=1)
    rp(response.decode(), flush=True, end='')

    telnet.write(b'c_cmd=C_VERSION\r\n')
    response = telnet.read_until(b'\x06\r\n', timeout=1)
    rp(response.decode(), flush=True, end='')

    for _ in range(5):
        telnet.write(b'c_cmd\r\n')
        response = telnet.read_until(b'\x06\r\n', timeout=1)
        rp(response.decode(), flush=True, end='')
        if response.decode().split('\r\n')[1] == '0':
            break
        time.sleep(1)

    telnet.write(b'c_par(0),12,1\r\n')
    response = telnet.read_until(b'\x06\r\n', timeout=1)
    response = response.decode().split('\r\n')
    rp(response, flush=True)

    telnet.close()
