import contextlib
import logging
import sys
import time

import pytest
import rich

from egse.collimator.fcul.ogse import OGSEController
from egse.collimator.fcul.ogse import OGSEProxy
from egse.collimator.fcul.ogse import OnOffSwitch
from egse.collimator.fcul.ogse_devif import OGSEEthernetInterface
from egse.command import CommandError
from egse.control import Failure
from egse.hk import HKError
from egse.hk import get_housekeeping
from egse.process import SubProcess
from egse.setup import load_setup
from egse.system import wait_until

LOGGER = logging.getLogger("egse.test_ogse_sim")

@pytest.fixture(scope="session")
def setup():
    """
    The Setup is loaded once for the full session, i.e. all the tests. This assumes however that the configuration
    manager is running and accessible to request the Setup from. The Setup is made available to the tests.
    """
    setup = load_setup()
    print(f"Setup ID = {setup.get_id()}, dictionary = {setup.telemetry.get_raw_value('dictionary')}")
    yield setup

@pytest.fixture(scope="session")
def start_ogse_sim():

    LOGGER.info("Starting OGSE Simulator")

    # The setup part <----------

    ogse_sim = SubProcess("ogse_sim", [sys.executable, "-m", "egse.collimator.fcul.ogse_sim", "start"])
    ogse_sim.execute()

    time.sleep(1.0)  # allow the ogse_sim process to start

    if not ogse_sim.is_running():
        LOGGER.warning("The OGSE Simulator is not running after the expected delay of 1s.")

    yield ogse_sim

    # The teardown part <----------

    ogse_sim.quit()

    time.sleep(1.0)


@pytest.fixture
def start_ogse_cs(start_ogse_sim):

    if not start_ogse_sim.is_running():
        LOGGER.warning("The OGSE Simulator is not running when entering the start_ogse_cs fixture.")

    # The setup part <----------

    ogse_cs = SubProcess("ogse_cs", [sys.executable, "-m", "egse.collimator.fcul.ogse_cs", "start"])
    ogse_cs.execute()

    time.sleep(2.0)  # allow the ogse_cs process to start

    LOGGER.info(f"OGSE CS: is_running = {ogse_cs.is_running()}")

    if not ogse_cs.is_running():
        LOGGER.warning("The OGSE CS is not running after the expected delay of 2s.")

    yield ogse_cs

    # The teardown part <----------

    ogse_cs.quit()

    time.sleep(1.0)


def test_ethernet_interface(start_ogse_sim):

    ogse = OGSEEthernetInterface()
    ogse.connect()

    try:
        assert ogse.query("version\n").decode().startswith("PLATO-RT-OGSE")

        assert ogse.query("ldls status\n").decode() == 'ldls: OK\n'

        assert ogse.query("power on\n").decode() == 'OK\n'
        assert ogse.query("power off\n").decode() == 'OK\n'

        assert ogse.query("operate on\n").decode() == 'OK\n'
        assert ogse.query("get lamp").decode() == "lamp: ON\n"
        assert ogse.query("operate off\n").decode() == 'OK\n'
        assert ogse.query("get lamp").decode() == "lamp: OFF\n"

        assert ogse.query("level 0.3\n").decode() == 'OK\n'
        assert ogse.query("level 5\n").decode().startswith(
            'ERROR: usage: attenuator level <value>  -- value must be in [0,1]')
        assert ogse.query("level\n").decode() == "att-level: *     3.0E-01 #39\n"

        assert ogse.query("level 1 7\n").decode() == "OK\n"
        assert ogse.query("level\n").decode() == "att-level: *     7.5E-03 #19\n"

        assert ogse.query("level up\n").decode() == "OK\n"
        assert ogse.query("level\n").decode() == "att-level: *     8.1E-03 #20\n"

        assert ogse.query("level 4 6\n").decode() == "OK\n"
        assert ogse.query("level\n").decode() == "att-level: *     5.0E-02 #27\n"  # should be 49.5E-03

        assert ogse.query("level down\n").decode() == "OK\n"
        assert ogse.query("level\n").decode() == "att-level: *     3.2E-02 #26\n"  # should be 31.5E-03

        assert ogse.query("read\n").decode().startswith("pm1: ")
    finally:
        ogse.query("level 0")
        ogse.disconnect()


def test_user_manual_commands(start_ogse_sim):

    ogse = OGSEEthernetInterface()
    ogse.connect()

    try:
        assert ogse.query("init\n") == b"ERROR: unknown command string: init\n"
        assert ogse.query("ldls status\n") == b"ldls: OK\n"
        assert b"pm1:" in ogse.query("pm status\n")
        assert b"pm2:" in ogse.query("pm status\n")
        assert ogse.query("att status\n") == b"att: OK\n"
        assert ogse.query("get interlock") == b"interlock: OPEN\n"
        assert ogse.query("get flags") == b"flags: 0x00  0000 0000\n"

    finally:
        ogse.disconnect()


def test_controller_interface(start_ogse_sim):

    ogse = OGSEController(hostname="localhost")
    ogse.connect()

    try:
        print(f"----->{ogse.version()}<-----")
        assert ogse.version().startswith("PLATO-RT-OGSE")

        assert ogse.ldls_status() == "ldls: OK"
        assert ogse.pm_status()['pm1'] == "OK"
        assert ogse.pm_status()['pm2'] == "ERROR"
        assert ogse.att_status() == "att: OK"

        assert ogse.power_on() == 'OK'
        assert ogse.get_interlock() == "interlock: OPEN"
        assert ogse.get_power() == "power: ON"
        assert ogse.get_lamp() == 'lamp: OFF'
        assert ogse.get_laser() == "laser: OFF"
        assert ogse.get_lamp_fault() == 'lamp-fault: NO-ERROR'
        assert ogse.get_controller_fault() == 'controller-fault: NO-ERROR'
        assert ogse.get_psu() == "psu: OFF"
        assert ogse.get_operate() == "operate: OFF"
        assert ogse.get_flags() == "flags: 0x00  0000 0000"

        assert isinstance(ogse.get_power_and_temperature(), dict)

        x = ogse.get_power_and_temperature()
        assert 'power1' in x
        assert 'power2' in x
        assert 'temp1' in x
        assert 'temp2' in x

        assert isinstance(ogse.status(), dict)

        x = ogse.status()
        assert "att_factor" in x
        assert x["att_factor"] == 0.0

        assert ogse.att_set_level_factor(0.3) == "OK"
        assert ogse.status()["att_moving"] is True
        assert ogse.att_get_level()["att_factor"] == 0.3
        assert ogse.att_get_level()["att_index"] == 39
        assert ogse.att_get_level()["att_moving"] is True

        wait_until(lambda: ogse.status()["att_moving"], timeout=10)

        assert ogse.att_set_level_index(25) == "OK"
        assert ogse.att_get_level()["att_factor"] == 0.025
        assert ogse.att_get_level()["att_index"] == 25
        assert ogse.att_get_level()["att_moving"] is True

        wait_until(lambda: ogse.status()["att_moving"], timeout=10)

        with pytest.raises(CommandError):
            ogse.att_set_level_index(47)

        assert ogse.att_set_level_position(1, 7) == "OK"
        assert ogse.att_get_level()["att_factor"] == 0.0075
        assert ogse.att_get_level()["att_index"] == 19
        assert ogse.att_get_level()["att_moving"] is True

        wait_until(lambda: ogse.status()["att_moving"], timeout=10)

        assert ogse.get_flags() == "flags: 0x00  0000 0000"
    finally:
        ogse.att_set_level_index(0)
        ogse.disconnect()


# @pytest.mark.skip
def test_proxy_interface(setup, start_ogse_cs):
    """
    In this test we check the OGSE functionality through the OGSE Proxy. That means an OGSE control server must be
    running, but this is handled by the fixture `start_ogse__cs` that is passed into the test. The OGSE CS connects
    to the OGSE Simulator which is also automatically started when the test runs.

    We will test the following functionality:

    * all basic commands to manipulate the Power supply, LDLS, Lamp, Filter Wheel
    * movement of the filter wheel is checked since the command to set the attenuation level immediately returns.
      There is a movement flag that is saved in the OGSE HK CSV file. To better test this we increase the HK frequency
      to 2Hz at the beginning of the test. The proper monitoring of this flag is tested with the `get_housekeeping()`
      function.
    * we also test if the FW_MOVING metric exist for the CSL2 OGSE. That is done by calling `curl` on the metrics
      port of the OGSE CS and extracting the value of the metric from the output.

    Args:
        setup: the current setup, loaded from the configuration manager
        start_ogse_cs: a handle to the OGSE CS process

    """
    with OGSEProxy(hostname="localhost") as ogse:

        from egse.services import ServiceProxy
        srv: ServiceProxy = ogse.get_service_proxy()
        srv.set_hk_frequency(2)

        print(f"----->{ogse.version()}<-----")
        assert ogse.version().startswith("PLATO-RT-OGSE")

        assert ogse.ldls_status() == 'ldls: OK'

        # The reset command is not implemented by the OGSE SIM
        assert ogse.reset() == 'ERROR: unknown command string: reset'

        assert ogse.power_on()
        assert ogse.get_power() == "power: ON"
        assert ogse.power_off()
        assert ogse.get_power() == "power: OFF"

        assert ogse.att_set_level_factor(0.3) == "OK"
        assert ogse.att_get_level()["att_factor"] == 0.3
        assert ogse.att_get_level()["att_moving"] is True

        wait_until(lambda: ogse.status()["att_moving"] is False, timeout=10)

        assert ogse.att_set_level_index(25) == "OK"
        assert ogse.att_get_level()['att_index'] == 25
        assert ogse.att_get_level()["att_moving"] is True

        wait_until(lambda: ogse.status()["att_moving"] is False, timeout=10)

        assert isinstance(ogse.att_set_level_index(47), Failure)

        assert ogse.att_set_level_position(1, 7) == "OK"
        assert ogse.att_get_level()['att_factor'] == 0.0075
        assert ogse.att_get_level()["att_moving"] is True

        wait_until(lambda: ogse.status()["att_moving"] is False, timeout=10)

        assert ogse.get_flags() == "flags: 0x00  0000 0000"

        ogse.att_set_level_index(0)

        time.sleep(0.5)  # housekeeping sampling is 2Hz, wait for the next sample..

        hk_name = f"G{setup.site_id}_OGSE_FW_MOVING"

        assert get_housekeeping(hk_name)[1] == 'True'
        assert get_metric(hk_name) == "1.0"

        wait_until(lambda: ogse.status()["att_moving"] is False, timeout=10)

        time.sleep(2.0)  # make sure we have some False entries for is_moving in the OGSE HK CSV file

        assert get_housekeeping(hk_name)[1] == 'False'
        assert get_metric(hk_name) == "0.0"

        rich.print("Average connection time: ", srv.get_average_execution_times())


def get_metric(name: str) -> str:

    import subprocess
    response = subprocess.run(["curl", "localhost:4246"], capture_output=True, text=True).stdout

    lines = response.split('\n')

    return next(
        (
            line.split()[1]
            for line in lines
            if name in line and not line.startswith('# ')
        ),
        None,
    )
