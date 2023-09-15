import pytest

from egse.logger import egse_logger
from egse.system import wait_until
from egse.tcs.tcs import TCSProxy
from egse.tcs.tcs import is_tcs_cs_active
from egse.tcs.tcs import print_all_housekeeping
from egse.tcs.tcs import print_configuration


def request_remote_operation():

    with TCSProxy() as tcs:
        tcs.request_remote_operation()

        if wait_until(tcs.is_remote_operation_active, timeout=5.0):
            raise "TCS EGSE shall be in remote operation mode."


@pytest.mark.skipif(not is_tcs_cs_active(),
                    reason="requires TCS Control Server to be running")
def test_module_functions(capsys):

    request_remote_operation()

    print_configuration()

    captured = capsys.readouterr()

    # These tests show us that we have a parameter and also the table that is printed with rich

    assert "Configuration" in captured.out
    assert "fee_rtd_1_cal" in captured.out
    assert "━━━━╇━━━━" in captured.out

    print_all_housekeeping()

    captured = capsys.readouterr()

    # These tests show us that we have a parameter and also the table that is printed with rich

    assert "All Telemetry" in captured.out
    assert "━━━━╇━━━━" in captured.out
    assert "UTC" in captured.out
    assert "fee_rtd_1" in captured.out
    assert "spare_rtd_1" in captured.out


@pytest.mark.skipif(not is_tcs_cs_active(),
                    reason="requires TCS Control Server to be running")
def test_tcs_interface():

    request_remote_operation()

    with TCSProxy() as tcs:
        assert not tcs.is_simulator()

        conf = tcs.get_configuration()

        assert isinstance(conf, dict)

        assert "ch1_closedloop_mode" in conf

        all_hk = tcs.get_all_housekeeping()

        for x in all_hk:
            assert len(x) == 3


@pytest.mark.skipif(not is_tcs_cs_active(),
                    reason="requires TCS Control Server to be running")
def test_tasks():

    request_remote_operation()

    with TCSProxy() as tcs:

        if not tcs.is_task_running():
            tcs.run_task()

        assert tcs.is_task_running()

        tcs.stop_task()

        assert not tcs.is_task_running()


@pytest.mark.skipif(not is_tcs_cs_active(),
                    reason="requires TCS Control Server to be running")
def test_remote_operation():

    with TCSProxy() as tcs:

        if not tcs.is_remote_operation_active():
            tcs.request_remote_operation()

        assert tcs.is_remote_operation_active()

        tcs.quit_remote_operation()

        assert not tcs.is_remote_operation_active()


@pytest.mark.skipif(not is_tcs_cs_active(),
                    reason="requires TCS Control Server to be running")
def test_set_operating_mode():

    request_remote_operation()

    with TCSProxy() as tcs:

        tcs.stop_task()
        tcs.set_operating_mode(6)
        tcs.commit()
        tcs.run_task()

        assert tcs.get_housekeeping_value("op_mode").value == "6"
        assert tcs.get_housekeeping_value("op_mode_verbose").value == "Extended Range"

        tcs.stop_task()
        tcs.set_operating_mode(0)
        tcs.commit()
        tcs.run_task()

        assert tcs.get_housekeeping_value("op_mode").value == "0"
        assert tcs.get_housekeeping_value("op_mode_verbose").value == "Normal"


if __name__ == "__main__":

    LOGGER = egse_logger

    tcs = TCSProxy()

    rc = tcs.request_remote_operation()
    LOGGER.info(f"{rc=}")

    # use this command if there appears a big red box with an error message on the MMI

    tcs.clear_popup()

    tcs.stop_task()

    # Set normal operation mode

    tcs.set_operating_mode("normal")  # strings are not allowed anymore, but it is reported as such
    tcs.commit()
    tcs.get_housekeeping_value("op_mode")  # only updated when task is running
    tcs.get_housekeeping_value("op_mode_verbose")
    tcs.run_task()
    tcs.get_housekeeping_value("op_mode")  # only updated when task is running
    tcs.get_housekeeping_value("op_mode_verbose")

    # Set Extended operating mode

    tcs.set_operating_mode(6)
    tcs.commit()
    tcs.get_housekeeping_value("op_mode")  # only updated when task is running
    tcs.get_housekeeping_value("op_mode_verbose")
    tcs.run_task()
    tcs.get_housekeeping_value("op_mode")  # only updated when task is running
    tcs.get_housekeeping_value("op_mode_verbose")

    # Set an erroneous parameter

    tcs.set_parameter("psu_source", 5)  # Returns: b'parsing_error(s):\r\npsu_source 5, invalid value\x03'

    tcs.run_task()
    tcs.commit()  # returns 'not_acknowledge_commit_unavailable_while_is_running'
    tcs.get_configuration()
    tcs.get_all_housekeeping()
    tcs.get_housekeeping_value("op_mode")  # only updated when task is running
    tcs.get_housekeeping_value("op_mode_verbose")
    tcs.get_housekeeping_value("task_is_running")  # not as expected, this is only updated when task is running, so it's always 1 ??
    tcs.get_housekeeping_value("tou_rtd_1")
    tcs.get_housekeeping_value("crio_free_mem_percent")
    tcs.get_error()
    tcs.get_housekeeping_value("")

    tcs.set_parameters(
        operation_mode=6,
        ch1_loadcontrol=1,
        ch1_closedloop_mode=2,
        ch1_tset=-40,
        cH2_loadcontrol=1,
        ch2_closedloop_mode=2,
        ch2_tset=-45,
    )
    tcs.commit()

    tcs.set_parameter('ch1_tset', -202.0)  # b'parsing_error(s):\r\nch1_tset -202.0, outside of range or resolution\x03'
    tcs.set_parameter('ch2_tset', +151.0)  # no error reported
    tcs.commit()

    tcs.run_task()
    tcs.is_task_running()

    tcs.stop_task()
    tcs.is_task_running()

    tcs.quit_remote_operation()  # Have to execute a reconnect() after this
