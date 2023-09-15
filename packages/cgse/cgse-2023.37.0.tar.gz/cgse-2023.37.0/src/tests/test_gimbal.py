import time

import numpy as np
import pytest

from pytest import approx

from egse.config import find_file
from egse.gimbal import GimbalError
from egse.gimbal.symetrie.gimbal import GimbalController, GimbalSimulator, GimbalProxy
from egse.process import SubProcess
from egse.services import ServiceProxy
from egse.settings import Settings
from egse.system import wait_until, AttributeDict

# When the 'real' Gimbal controller is connected, the pytest can be run with the
# GimbalController class. However, by default we use the GimbalSimulator class for testing.

Gimbal = GimbalController
Gimbal = GimbalProxy
Gimbal = GimbalSimulator


def test_context_manager():

    with Gimbal() as gimbal:
        print(gimbal.info())


def test_connection():
    gimbal = Gimbal()

    try:
        gimbal.connect()
        gimbal.info()

        # FIXME: The controller might be in a bad state due to previous failures.
        #        We need some way to fix & reset the controller at the beginning of the unit tests.

        gimbal.clear_error()

        if gimbal.is_simulator():
            gimbal.reset(wait=False, verbose=False)  # Wait is not needed
        else:
            gimbal.reset(wait=True, verbose=False)  # Wait is definitely needed

        gimbal.homing()

        if wait_until(gimbal.is_homing_done, interval=0.5, timeout=300):
            assert False
        if wait_until(gimbal.is_in_position, interval=0.5, timeout=300):
            assert False

        assert gimbal.is_homing_done()

    except GimbalError:
        assert False
    finally:
        gimbal.disconnect()


def test_goto_position():

    with Gimbal() as gimbal:

        rc = gimbal.goto_specific_position(2)

        assert rc in [0, -1, -2]  # FIXME: How can we do proper checking here?

        rc = gimbal.goto_specific_position(5)

        assert rc in [0, -1, -2]  # FIXME: How can we do proper checking here?


def test_absolute_movement():

    with Gimbal() as gimbal:

        rx_off = 0
        ry_off = 0

        gimbal.configure_offsets(rx_off, ry_off)
        gimbal.homing()

        if wait_until(gimbal.is_homing_done, interval=0.5, timeout=300):
            assert False
        if wait_until(gimbal.is_in_position, interval=1, timeout=300):
            assert False

        urx_off = -2
        ury_off = -3

        gimbal.configure_offsets(urx_off, ury_off)

        out = gimbal.get_user_positions()
        check_positions(out, (urx_off, ury_off))

        out = gimbal.get_machine_positions()
        check_positions(out, (0.00000, 0.00000))

        m_rx = 10.8732461
        m_ry = 12.1027342

        u_rx, u_ry = m_rx + urx_off, m_ry + ury_off

        rc = gimbal.move_absolute(u_rx, u_ry)
        assert rc == 0

        if wait_until(gimbal.is_in_position, interval=1, timeout=300):
            assert False

        out = gimbal.get_user_positions()
        check_positions(out, (u_rx, u_ry))

        out = gimbal.get_machine_positions()
        check_positions(out, (m_rx, m_ry))

        # Test the move relative object

        d_rx = -9
        d_ry = -15

        gimbal.move_relative(d_rx, d_ry)

        if wait_until(gimbal.is_in_position, interval=1, timeout=300):
            assert False

        out = gimbal.get_user_positions()
        check_positions(out, (u_rx + d_rx, u_ry + d_ry))

        out = gimbal.get_machine_positions()
        check_positions(out, (m_rx + d_rx, m_ry + d_ry))

def test_offsets():

    with Gimbal() as gimbal:
        rx_off, ry_off = 1.23456, 12.34567

        rc = gimbal.configure_offsets(rx_off, ry_off)

        assert rc >= 0

        out = gimbal.get_offsets()
        check_positions(out, (rx_off, ry_off))


def test_temperatures():
    with Gimbal() as gimbal:
        temps = gimbal.get_motor_temperatures()

        assert len(temps) == 2
        assert np.isfinite(temps[0])
        assert np.isfinite(temps[1])

def check_positions(out, expected, rel=0.0001, abs=0.0001):
    assert len(out) == len(expected)

    for idx, element in enumerate(out):
        assert element == approx(expected[idx], rel=rel, abs=abs)


import os

def test_gimbal_proxy():

    # This test needs a Storage Manager running on hostnamE from settings.yaml

    path = find_file('gimbal_cs.py', in_dir='gimbal/symetrie')

    assert path is not None

    path = str(path)

    stub = SubProcess(
        "Dummy Process",
        ["python3", path, 'start', '--sim'])

    stub.execute()

    # Wait for server to start (i.e. to expose the 'quit_server' command)
    # This is necessary to prevent proxy.quit_server() from failing with
    # an AttributeError exception. If this still fails, consider increasing
    # the time spent here:

    time.sleep(.2)

    proxy = ServiceProxy(hostname='localhost', port=6710)
    
    with GimbalProxy(hostname='localhost') as gimbal:
        gimbal.ping()
        assert 'info' in gimbal.get_commands()
        assert 'reference frames' in gimbal.info()

    proxy.quit_server()
    proxy.disconnect_cs()

    time.sleep(0.2)  # give Gimbal control Server the time to quit properly and unregister from Storage

    assert stub.quit() == 0
