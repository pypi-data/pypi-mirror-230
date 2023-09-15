import time
import datetime
import pytest
import logging

from egse.tempcontrol.lakeshore.lsci336_devif import LakeShore336EthernetInterface
from egse.tempcontrol.lakeshore.lsci336_devif import LakeShoreError

logger = logging.getLogger(__name__)

IDENTIFICATION_QUERY = "*IDN?\n"


def is_lakeshore_available():
    try:
        ls = LakeShore336EthernetInterface()
        ls.connect()
    except LakeShoreError as e_ls:
        logger.info(f"LakeShore not connected ({e_ls})")
        return False
    finally:
        ls.disconnect()

    return True


lakeshore_available = True if is_lakeshore_available() else False


@pytest.mark.skipif(not lakeshore_available, reason="requires LakeShore to be connected")
def test_constructor():
    ls = LakeShore336EthernetInterface()

    assert not ls.is_connected()


@pytest.mark.skipif(not lakeshore_available, reason="requires LakeShore to be connected")
def test_connect():
    ls = LakeShore336EthernetInterface()
    ls.connect()

    assert ls.is_connected()


@pytest.mark.skipif(not lakeshore_available, reason="requires LakeShore to be connected")
def test_disconnect():
    ls = LakeShore336EthernetInterface()
    ls.connect()

    assert ls.is_connected()

    ls.disconnect()

    assert not ls.is_connected()


@pytest.mark.skipif(not lakeshore_available, reason="requires LakeShore to be connected")
def test_get_response():
    ls = LakeShore336EthernetInterface()
    ls.connect()

    out = ls.get_response(IDENTIFICATION_QUERY)

    assert type(out) == str
    assert out.startswith("LSCI")

    ls.disconnect()


@pytest.mark.skipif(not lakeshore_available, reason="requires LakeShore to be connected")
def test_get_temperature():
    ls = LakeShore336EthernetInterface()
    ls.connect()

    out = []

    sample_time = datetime.timedelta(seconds=10)
    until = datetime.datetime.now() + sample_time
    while datetime.datetime.now() < until:
        # Celsius Reading Query
        # response = ls.get_response('CRDG? A\n')

        # Kelvin Reading Query
        response = ls.get_response("KRDG? A\n")

        out.append(response.strip())
        time.sleep(1.0)

    assert 9 <= len(out) < 12

    ls.disconnect()
