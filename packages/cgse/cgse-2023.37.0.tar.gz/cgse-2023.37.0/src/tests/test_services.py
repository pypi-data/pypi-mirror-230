import logging
import sys
import time
from pathlib import Path

import pytest
from pytest import approx

from egse.dummy import DummyProxy
from egse.dummy import ctrl_settings
from egse.dummy import is_dummy_cs_active
from egse.process import SubProcess
from egse.process import is_process_running
from egse.services import ServiceProxy
from egse.storage import StorageProxy
from egse.system import Timer
from egse.system import str_to_datetime
from egse.system import waiting_for

LOGGER = logging.getLogger(__name__)

@pytest.fixture(scope="module")
def dummy_cs():

    # The setup part <----------

    dummy_cs = SubProcess("dummy_cs", [sys.executable, "-m", "egse.dummy", "control-server", "start"])
    dummy_cs.execute()

    with Timer("Starting dummy_cs"):
        waiting_for(is_dummy_cs_active, interval=1.0, timeout=10.0)

    LOGGER.info(f"DUMMY CS: is_running = {dummy_cs.is_running()}")
    LOGGER.info(f"DUMMY CS: is_active = {is_dummy_cs_active()}")

    time.sleep(10.0)  # give the dummy_cs some time to build up the duration of the get_housekeeping()

    yield dummy_cs

    # The teardown part <----------

    dummy_cs_stop = SubProcess("dummy_cs_stop", [sys.executable, "-m", "egse.dummy", "control-server", "stop"])
    dummy_cs_stop.execute()

    try:
        waiting_for(is_process_running, ["egse.dummy", "start"], interval=1.0, timeout=5.0)
        LOGGER.info("DUMMY CS stopped")
    except TimeoutError:
        LOGGER.warning("Couldn't stop the DPU Control Server within the given time of 5s. Quiting...")
        dummy_cs.quit()

    time.sleep(1.0)


def test_services_directly(dummy_cs):  # sourcery skip: extract-method
    """Test Services by creating a service proxy and connecting it to the control server using the settings.

    The following commands are tested:

        * set_monitoring_frequency
        * set_hk_frequency
        * get_process_status
        * get_storage_mnemonic
        * get_average_execution_times
        * get_cs_module

    The housekeeping frequency is set to 10 Hz, which means every 100ms. Since this is smaller than the safety of 200ms
    that is build in the control server, the delay will become 200ms + the duration of the get_housekeeping()
    function (which is this dummy_cs is very small).
    """
    hk_frequency = 10
    hk_entries = 5

    service = ServiceProxy(ctrl_settings)

    cmd_list = service.get_commands()
    for cmd in ["set_monitoring_frequency", "set_hk_frequency", "get_average_execution_times", "quit_server"]:
        assert cmd in cmd_list

    assert service.ping()
    assert service.set_monitoring_frequency(2.0) == approx(500)

    hk_delay = service.set_hk_frequency(hk_frequency)
    exec_times = service.get_average_execution_times()

    assert_hk_delay(hk_frequency, hk_delay, exec_times['get_housekeeping'])

    status = service.get_process_status()
    assert status["PID"] == dummy_cs.pid

    origin = service.get_storage_mnemonic()
    assert origin == 'DUMMY-HK'

    cs_module = service.get_cs_module()
    assert cs_module == "egse.dummy"

    with DummyProxy() as dummy, StorageProxy() as storage:

        filenames = storage.get_filenames({'origin': origin})

        assert len(filenames) == 1

        # The first filename is always the CSV file in the daily, should be...

        filename = filenames[0]
        assert 'daily' in str(filename)

        assert dummy.ping()

        cmd_list = dummy.get_commands()
        for cmd in ["info", "response"]:
            assert cmd in cmd_list

        assert "info()" in dummy.info()
        assert dummy.response(one=1, two=2, fake=True) == "response((), {'one': 1, 'two': 2, 'fake': True})"

        # Sleep for a few seconds to allow the control server to save enough HK entries in the CSV file

        time.sleep((hk_entries + 1) * hk_delay / 1000)

    service.disconnect_cs()

    assert_diff_times_csv_file(filename, hk_entries, hk_delay / 1000)


def test_services_through_get_service(dummy_cs):

    hk_frequency = 2.0

    with DummyProxy() as dummy:
        service: ServiceProxy = dummy.get_service_proxy()
        hk_delay = service.set_hk_frequency(hk_frequency)
        exec_times = service.get_average_execution_times()

        assert_hk_delay(hk_frequency, hk_delay, exec_times['get_housekeeping'])

        # TBW

        time.sleep(3.0)


def assert_hk_delay(hk_frequency: float, hk_delay: float, exec_time: float):
    """Check the hk_delay that is returned by the set_hk_frequency()."""

    if 1 / hk_frequency * 1000 > exec_time * 1000 + 200:
        # test against the requested frequency
        assert hk_delay == approx(1 / hk_frequency * 1000, rel=0.1)
    else:
        # safety margin from the control server
        assert hk_delay == approx(200 + exec_time * 1000, rel=0.1)


def assert_diff_times_csv_file(filename: Path, nr_lines: int, diff_time: float):
    """
    Reads the last nr_lines from the CSV file and compares the difference between each successive timestamp
    with the given `diff_time` argument.
    """

    print(f"{diff_time = }")

    with filename.open('r') as csv:
        lines = csv.readlines()

    # Only keep the timestamp for comparison

    lines = [line.strip().split(',')[0] for line in lines[-nr_lines:]]

    # Now check the time difference between all successive lines

    ts_prev = str_to_datetime(lines[0]).timestamp()

    for line in lines[1:]:
        ts_curr = str_to_datetime(line).timestamp()
        print(f"{ts_curr - ts_prev}")
        assert (ts_curr - ts_prev) == approx(diff_time, abs=0.5)
        ts_prev = ts_curr
