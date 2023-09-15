import logging

from egse.tempcontrol.lakeshore.lsci336 import LakeShore336Simulator

MODULE_LOGGER = logging.getLogger(__name__)


def test_constructor():
    ls = LakeShore336Simulator()

    assert ls.is_connected()


def test_disconnect():
    ls = LakeShore336Simulator()

    assert ls.is_connected()

    ls.disconnect()

    assert not ls.is_connected()


def test_get_response():
    ls = LakeShore336Simulator()

    out = ls.info()

    assert type(out) == str
    assert out.startswith('LSCI')

    ls.disconnect()


def test_get_temperature():

    with LakeShore336Simulator() as sim:
        assert -100.0 < sim.get_temperature('A') < 25.0
