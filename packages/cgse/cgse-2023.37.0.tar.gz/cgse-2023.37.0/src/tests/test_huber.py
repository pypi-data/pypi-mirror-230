"""
This module will test the HUBER SMC9300 interfaces. There are several fixtures defined, one for each type of interface.

Please note that not all the interfaces can be used at any time. It depends on your setup which tests are run.

A global variable DONT_MOVE is defined to allow you to run the test without any movements.
"""

import contextlib
import logging
import re
import sys
import time
from collections import namedtuple
from rich import print
import pytest
from pytest import approx

from egse.device import DeviceConnectionError
from egse.process import SubProcess
from egse.stages.huber.smc9300 import HuberSMC9300Controller
from egse.stages.huber.smc9300 import HuberSMC9300Interface
from egse.stages.huber.smc9300 import HuberSMC9300Proxy
from egse.stages.huber.smc9300 import untangle_status
from egse.stages.huber.smc9300_devif import HuberSMC9300EthernetInterface

LOGGER = logging.getLogger("egse.tests.stages.huber")

device = namedtuple("device", ["name", "is_running", "interface"])

DONT_MOVE = True


@pytest.fixture
def smc9300_sim():
    """
    Starts the HUBER SMC9300 Simulator and connects using the Ethernet interface.
    """
    # The setup part <----------

    smc9300_sim = start_smc9300_sim()

    huber = HuberSMC9300EthernetInterface()
    with contextlib.suppress(DeviceConnectionError):
        huber.connect()

    if not huber.is_connected():
        pytest.skip("start_smc9300_sim: could not connect to smc9300_sim, test skipped.")

    yield device("sim", huber.is_connected(), huber)

    # The teardown part <----------

    huber.disconnect()
    smc9300_sim.quit()
    time.sleep(1.0)


@pytest.fixture
def smc9300_dev():
    """
    Connects directly to the device controller using the Ethernet interface.
    """
    huber = HuberSMC9300EthernetInterface()
    with contextlib.suppress(DeviceConnectionError):
        huber.connect()
    if not huber.is_connected():
        pytest.skip("start_smc9300_dev: could not connect to device, test skipped.")

    yield device("dev", huber.is_connected(), huber)

    huber.disconnect()


@pytest.fixture
def smc9300_proxy():
    """
    Starts the HUBER SMC9300 control server and connects using a Proxy.
    """
    smc9300_cs = start_smc9300_cs()
    huber = HuberSMC9300Proxy()
    huber.connect()

    if not huber.is_cs_connected():
        pytest.skip("smc9300_proxy: could not connect to smc9300_cs, test skipped.")

    yield device("proxy", huber.is_cs_connected(), huber)

    huber.disconnect_cs()
    smc9300_cs.quit()


@pytest.fixture(params=["direct", "sim"])
def smc9300_controller(request):
    """
    The Controller needs to be tested against both the device Controller and the
    SMC9300 Simulator.
    """
    smc9300_sim = start_smc9300_sim() if request.param == "sim" else None

    huber = HuberSMC9300Controller()
    with contextlib.suppress(DeviceConnectionError):
        huber.connect()

    if not huber.is_connected():
        pytest.skip("start_smc9300_controller: could not connect to device, test skipped.")

    yield device("controller", huber.is_connected(), huber)

    huber.disconnect()
    if smc9300_sim:
        time.sleep(2.0)  # give disconnect time to clear the errors on all axes
        smc9300_sim.quit()


def start_smc9300_sim():
    """
    Starts the HUBER SMC9300 Simulator.

    Returns:
        An reference to the SubProcess.
    """
    smc9300_sim = SubProcess("smc9300_sim", [sys.executable, "-m", "egse.stages.huber.smc9300_sim", "start"])
    smc9300_sim.execute()
    time.sleep(1.0)  # allow the smc9300_sim process to start

    if not smc9300_sim.is_running():
        pytest.skip("start_smc9300_sim: simulator could not be started, test skipped.")

    return smc9300_sim


def start_smc9300_cs():
    """
    Starts the HUBER SMC9300 Control Server.

    Returns:
        An reference to the SubProcess.
    """
    smc9300_cs = SubProcess("smc9300_cs", [sys.executable, "-m", "egse.stages.huber.smc9300_cs", "start"])
    smc9300_cs.execute()
    time.sleep(1.0)  # allow the smc9300_cs process to start

    if not smc9300_cs.is_running():
        pytest.skip("start_smc9300_cs: smc9300 control server could not be started, test skipped.")

    return smc9300_cs


def test_device_interface(smc9300_dev: device):

    assert smc9300_dev.name == "dev"

    huber = smc9300_dev.interface

    xtest_using_device_interface(huber)


def test_simulator_interface(smc9300_sim: device):

    assert smc9300_sim.name == "sim"

    huber = smc9300_sim.interface

    xtest_using_device_interface(huber)


def test_proxy_interface(smc9300_proxy: device):

    assert smc9300_proxy.name == "proxy"

    huber = smc9300_proxy.interface

    xtest_query_methods(huber)
    # xtest_goto_full(huber)
    # xtest_goto_around_0(huber)
    # xtest_goto_around_180(huber)
    # xtest_goto_360(huber)
    xtest_limits(huber)


def test_controller_interface(smc9300_controller: device):

    assert smc9300_controller.name == "controller"

    huber = smc9300_controller.interface

    xtest_query_methods(huber)


def xtest_using_device_interface(dev: HuberSMC9300EthernetInterface):

    response = dev.trans("?p1\r\n").decode()
    match = re.match(r"1:(-?\d+(?:\.\d+)?);\r\n", response)
    assert match
    float(match[1])

    assert dev.query("?v\r\n") == b'smc 1.2.1093\r\n'

    dev.write("?v\r\n")
    assert dev.read() == b'smc 1.2.1093\r\n'


def xtest_limits(dev: HuberSMC9300Interface):

    # This test is specific for translation stage: 5101.30-943

    alias = dev.get_parameter(axis=3, name="alias")
    if "03~lin (5101.30-943)" not in alias:
        pytest.skip(f"Limits check only valid for axis=3 [5101.30-943], not for [{alias[2]}]")

    dev.goto(axis=3, position=0.0)
    dev.goto(axis=3, position=-73)
    status = dev.get_status(axis=3)
    status = untangle_status(status)
    assert status["err_no"] == 1500
    assert status["err_msg"] == "limit switch error"
    dev.clear_error(3)
    assert dev.get_current_position(3) < -72.5

    dev.goto(axis=3, position=0.0)


def xtest_goto_360(dev: HuberSMC9300Interface):

    # Bring the axis=1 to position 0.0, wait until the axis is in position, and clear errors.
    # Then all tests should be identical for the hardware device and the simulator.

    axis = 1

    dev.goto_direct(axis=axis, position=0.0)
    dev.clear_error(axis=axis)
    dev.wait_until_axis_ready(axis=axis)

    for pos in [0, 360, 0]:
        dev.goto_direct(axis=axis, position=pos)
        dev.wait_until_axis_ready(axis=axis)
        time.sleep(10)


def xtest_goto_full(dev: HuberSMC9300Interface):

    # Bring the axis=1 to position 0.0, wait until the axis is in position, and clear errors.
    # Then all tests should be identical for the hardware device and the simulator.

    axis = 1

    dev.goto_direct(axis=axis, position=0.0)
    dev.clear_error(axis=axis)
    dev.wait_until_axis_ready(axis=axis)

    for pos in [0, 90, 180, 270, 360, 0, -90, -180, -270, -360, 0]:
        dev.goto_direct(axis=axis, position=pos)
        dev.wait_until_axis_ready(axis=axis)
        time.sleep(10)


def xtest_goto_around_0(dev: HuberSMC9300Interface):

    # Bring the axis=1 to position 0.0, wait until the axis is in position, and clear errors.
    # Then all tests should be identical for the hardware device and the simulator.

    axis = 1

    dev.goto_direct(axis=axis, position=0.0)
    dev.clear_error(axis=axis)
    dev.wait_until_axis_ready(axis=axis)

    for pos in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, -9, -8, -7, -6, -5, -4, -3, -2, -1, 0]:
        dev.goto_direct(axis=axis, position=pos)
        dev.wait_until_axis_ready(axis=axis)
        time.sleep(10)


def xtest_goto_around_180(dev: HuberSMC9300Interface):

    # Bring the axis=1 to position 0.0, wait until the axis is in position, and clear errors.
    # Then all tests should be identical for the hardware device and the simulator.

    axis = 1

    dev.goto_direct(axis=axis, position=0.0)
    dev.clear_error(axis=axis)
    dev.wait_until_axis_ready(axis=axis)

    for pos in [170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186,187, 188, 190]:
        dev.goto_direct(axis=axis, position=pos)
        dev.wait_until_axis_ready(axis=axis)
        time.sleep(10)

    for pos in [
        -170, -171, -172, -173, -174, -175, -176, -177, -178, -179,
        -180, -181, -182, -183, -184, -185, -186, -187, -188, -190
    ]:
        dev.goto_direct(axis=axis, position=pos)
        dev.wait_until_axis_ready(axis=axis)
        time.sleep(10)


def xtest_query_methods(dev: HuberSMC9300Interface):

    # Bring the axis=1 to position 0.0, wait until the axis is in position, and clear errors.
    # Then all tests should be identical for the hardware device and the simulator.

    dev.goto_direct(axis=1, position=0.0)
    dev.clear_error(axis=1)
    dev.wait_until_axis_ready(axis=1)

    assert "os image: wes7" in dev.info()
    assert dev.get_version() == "smc 1.2.1093"
    assert dev.get_error(axis=1) == ('0', 'no error')
    assert dev.get_state(axis=1) == 129
    status = dev.get_status(axis=1)
    assert isinstance(status, str)
    status = untangle_status(status)
    print(f"{status = }")
    assert status["prog"] == 0
    assert status["axis"] == 1
    assert status["ctrl"] == 1
    assert status["err_no"] == 0
    assert status["err_msg"] == ""
    conf = dev.get_configuration(axis=1)
    assert "alias" in conf
    assert conf["alias"] == "01~rot (420-20913)"
    assert dev.get_configuration(axis=2)
    assert dev.get_configuration(axis=3)
    assert dev.get_conf_value(axis=1, name='gnum') == '10000'
    assert dev.get_slew_speed(axis=1) == int(dev.get_parameter(axis=1, name='ffast')[-1])
    assert dev.is_in_position(axis=1)
    assert dev.get_current_position(axis=1) == status['pos']
    assert dev.get_current_encoder_position(axis=1) == approx(status["epos"], abs=0.0001)
    assert dev.get_current_encoder_counter_value(axis=1) == approx(4287250032, abs=10000)

    assert dev.get_parameter(axis=1, name='ffast')[-1] == dev.get_conf_value(axis=1, name="ffast")
    assert dev.get_parameter(axis=1, name='frun')[-1] == dev.get_conf_value(axis=1, name="frun")
    # assert dev.get_parameter(axis=1, name='rofs')[-1] == dev.get_conf_value(axis=1, name="rofs")

    dev.clear_error(axis=1)
