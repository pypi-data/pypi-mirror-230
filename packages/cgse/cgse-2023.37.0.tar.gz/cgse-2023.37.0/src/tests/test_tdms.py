import pytest

from egse.system import Timer
from egse.tdms import load_tdms_from_file, load_tdms_from_string
from egse.config import find_file


def test_tdms_load():

    tdms = load_tdms_from_file(find_file('test_04.Dec.2019_17.38.17_UTC_0000.tdms.txt'))

    assert tdms.start_time.year == 2019
    assert tdms.start_time.month == 12
    assert tdms.start_time.day == 4
    assert tdms.start_time.strftime('%m/%d/%Y %H:%M:%S.%f') == '12/04/2019 17:38:27.584141'

    assert tdms.names[0] == 'PSU_Voltage'
    assert tdms.names[15] == 'Downsampled_Clk_50MHz'

    assert len(tdms.values) == len(tdms.names)
    assert tdms.values.shape == (79, 119)
    assert len(tdms.values[0]) == 119
    assert len(tdms.values[-1]) == 119


def test_tdms_load_error():

    with pytest.raises(ValueError):
        tdms = load_tdms_from_file(None)

    with pytest.raises(FileNotFoundError):
        tdms = load_tdms_from_file('non-existing-file')

    with pytest.raises(ValueError):
        tdms = load_tdms_from_file(__file__)


def test_tdms_load_string():

    tdms = load_tdms_from_string(
        "start time:\n"
        "12/04/2019 17:38:27.584141\n\n"
        "dt:\n"
        "0.1\n\n"
        "channel names:\nX\tY\n\n"
        "data:\n"
        "0.0\t1.0\n0.1\t0.9\n0.2\t0.8\n0.3\t0.7\n0.4\t0.6\n0.5\t0.5\n0.6\t0.4\n0.7\t0.3\n0.8\t0.2\n0.9\t0.1\n1.0\t0.0"
    )

    assert tdms.time_interval == 0.1
    assert tdms.names == ['X', 'Y']
    assert (tdms.values[0] == [round(x * tdms.time_interval, 2) for x in range(11)]).all()
    assert (tdms.values[1] == [round(x * tdms.time_interval, 2) for x in range(10, -1, -1)]).all()
