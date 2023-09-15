import logging

from egse.powermeter.thorlabs.pm100a import ThorlabsPM100Simulator

MODULE_LOGGER = logging.getLogger(__name__)


def test_constructor():
    tl = ThorlabsPM100Simulator()

    assert tl.is_connected()


def test_disconnect():
    tl = ThorlabsPM100Simulator()

    assert tl.is_connected()

    tl.disconnect()

    assert not tl.is_connected()


def test_get_response():
    tl = ThorlabsPM100Simulator()

    out = tl.info()

    assert type(out) == str
    assert 'PM100' in out

    tl.disconnect()
