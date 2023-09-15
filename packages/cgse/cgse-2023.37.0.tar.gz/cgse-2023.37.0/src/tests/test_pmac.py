"""
This test suite contains a number of tests that require the PMAC Controller of
Symetrie to be connected. The tests are skipped if it can not connect to the
PMAC (either directly or through an ssh tunnel).

use 'py.test -rs' to check the reasons for skipping a test.

"""

import logging

import pytest
from pytest import approx
from pytest import raises

from egse.hexapod.symetrie.pmac import PMACError
from egse.hexapod.symetrie.pmac import PmacEthernetInterface
from egse.hexapod.symetrie.pmac import extractQ20AndOutput

logger = logging.getLogger(__name__)

HOSTNAME = '10.33.178.145'
PORT = 1025


def is_pmac_connected():

    try:
        pmac = PmacEthernetInterface()

        pmac.setConnectionParameters(HOSTNAME, PORT)
        pmac.connect()

    except PMACError:
        return False
    finally:
        pmac.disconnect()

    return True


@pytest.mark.skipif(not is_pmac_connected(),
                    reason="requires Symetrie PMAC Controller to be connected")
def test_QVars():
    try:
        pmac = PmacEthernetInterface()

        pmac.setConnectionParameters(HOSTNAME, PORT)
        pmac.connect()

        result = pmac.getQVars(0, [20, 36, 29], int)

        logger.info (f"Q20, Q36, Q29 = {result} of type {type(result)}")

        assert result[0] == 0   # assume Q20 is 0

    finally:
        pmac.disconnect()


@pytest.mark.skipif(not is_pmac_connected(),
                    reason="requires Symetrie PMAC Controller to be connected")
def test_IVars():
    try:
        pmac = PmacEthernetInterface()

        pmac.setConnectionParameters(HOSTNAME, PORT)
        pmac.connect()

        result = pmac.getIVars(0, [20, 36, 29])

        logger.info (f"I20, I36, I29 = {result} of type {type(result)}")

        assert result[0] == '$0'   # assume I20 is $0, FIXME: find a better assert statement

    finally:
        pmac.disconnect()


def testExtractQ20AndOutput():
    retStr = b'10\r328\r42\r24\r-2\r\x06'
    nr = 4

    Q20, out = extractQ20AndOutput(retStr, nr, int)
    assert Q20 == 10
    assert nr == len(out)
    assert out[0] == 328
    assert out[3] == -2

    retStr = b'10\r328\r42\r24\r-2\r'
    nr = 4

    Q20, out = extractQ20AndOutput(retStr, nr, int)
    assert Q20 == 10
    assert nr == len(out)
    assert out[0] == 328
    assert out[3] == -2

    retStr = b'10\r328\r42\r24\r-2'
    nr = 4

    Q20, out = extractQ20AndOutput(retStr, nr, int)
    assert Q20 == 10
    assert nr == len(out)
    assert out[0] == 328
    assert out[3] == -2

    retStr = b'-1\r1\r2\r3\r4\r5\r\x06'
    nr = 5

    Q20, out = extractQ20AndOutput(retStr, nr, int)
    assert Q20 == -1
    assert nr == len(out)
    assert out[0] == 1
    assert out[1] == 2
    assert out[2] == 3
    assert out[3] == 4
    assert out[4] == 5


    retStr = b'-2\r1.3\r-2\r-3.14\r4\r5.\r\x06'
    nr = 5

    Q20, out = extractQ20AndOutput(retStr, nr, float)
    assert Q20 == -2
    assert nr == len(out)
    assert out[0] == approx(1.3)
    assert out[1] == approx(-2.0)
    assert out[2] == approx(-3.14)
    assert out[3] == approx(4.0)
    assert out[4] == approx(5.0)


    retStr = b'just a normal string'
    nr = 5

    with raises(PMACError):
        Q20, out = extractQ20AndOutput(retStr, nr, int)

