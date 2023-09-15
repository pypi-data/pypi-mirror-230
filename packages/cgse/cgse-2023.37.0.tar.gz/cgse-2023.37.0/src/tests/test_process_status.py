import pytest

from egse.process import ProcessStatus


def test_no_metrics_prefix_given():
    """This test will just fail when ProcessStatus is instantiated incorrectly."""

    process_status = ProcessStatus()

    with pytest.raises(ValueError):
        process_status = ProcessStatus()


def test_duplicate_instantiation():
    """
    Test what happens when the ProcessStatus class is instantiated multiple times within the
    same process. The check here is mainly on the definition of the metrics.

    The exception raised:

        ValueError: Duplicated timeseries in CollectorRegistry: {'test_process_status_psutil_number_of_cpu'}

    """

    process_status = ProcessStatus(metrics_prefix="TEST_1")

    with pytest.raises(ValueError):
        process_status = ProcessStatus(metrics_prefix="TEST_1")

    process_status = ProcessStatus(metrics_prefix="TEST_2")


def test_process_status_as_dict():

    process_status = ProcessStatus(metrics_prefix="TEST_3")

    ps = process_status.as_dict()

    assert "PID" in ps
    assert "CPU%" in ps
    assert "RSS" in ps
    assert "USS" in ps
