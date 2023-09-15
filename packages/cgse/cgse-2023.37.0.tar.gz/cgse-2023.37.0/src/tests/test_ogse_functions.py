"""
This pytest module will test decoding functions for the OGSE commanding.
"""
import math

import pytest

from egse.collimator.fcul.ogse import decode_read_command, decode_status_command, \
    decode_att_get_level_command
from egse.control import Failure


def test_decode_read_command():

    response = b'pm1: -3.190398e-11 W +21.6 \xc2\xbaC, pm2: +2.160530e-07 W +22.7 \xc2\xbaC\n'

    x = decode_read_command(response)

    assert x['power1'] == pytest.approx(-3.190398e-11)
    assert x['temp1'] == pytest.approx(21.6)
    assert x['power2'] == pytest.approx(+2.160530e-07)
    assert x['temp2'] == pytest.approx(22.7)

    # We put a NaN value in one of the readings

    response = b'pm1: -3.190398e-11 W +21.6 \xc2\xbaC, pm2: NaN W +22.7 \xc2\xbaC\n'

    x = decode_read_command(response)
    a, b, c, d = x['power1'], x['temp1'], x['power2'], x['temp2']

    assert a == pytest.approx(-3.190398e-11)
    assert b == pytest.approx(+21.6)
    assert math.isnan(c)
    assert d == pytest.approx(+22.7)

    # What happens when a weird response is given?

    response = b"some weird string"

    a = decode_read_command(response)

    assert isinstance(a, Failure)
    assert isinstance(a.cause, ValueError)
    assert "Unexpected response" in a.message
    assert "weird" in a.message

    # What happens when the given response is not even a bytes object?

    response = 3.14

    a = decode_read_command(response)

    assert isinstance(a, Failure)
    assert a.cause is None
    assert "not a bytes object" in a.message


def test_decode_status_command():
    response = b'power: OFF, lamp: OFF, interlock: OFF, psu: OFF, att: 0E-9 #0, ' \
               b'power-ch1: +3.185751e-11 W, power-ch2: +2.068336e-07 W, ' \
               b'temp-ch1: +21.5 \xc2\xbaC, temp-ch2: +22.6 \xc2\xbaC\n'

    values = decode_status_command(response)

    assert len(values) == 11

    (pow_status, lamp_status, interlock_status, psu_status, att_moving, att_level, att_factor,
     pow1, t1, pow2, t2) = values.values()

    assert pow_status == 'OFF'
    assert lamp_status == 'OFF'
    assert interlock_status == 'OFF'
    assert psu_status == 'OFF'
    assert att_moving is False
    assert att_level == pytest.approx(0E-9)
    assert att_factor == 0
    assert (pow1, t1, pow2, t2) == pytest.approx((3.185751e-11, 21.5, 2.068336e-07, 22.6))

    response = b'power: OFF, lamp: ON, interlock: OFF, psu: ON, att: * 800E-3 #45, ' \
               b'power-ch1: -2.323670e-14 W, power-ch2: +2.062890e-07 W, ' \
               b'temp-ch1: +21.5 \xc2\xbaC, temp-ch2: +22.5 \xc2\xbaC\n'

    values = decode_status_command(response)

    assert len(values) == 11

    (pow_status, lamp_status, interlock_status, psu_status, att_moving, att_level, att_factor,
     pow1, t1, pow2, t2) = values.values()

    assert pow_status == 'OFF'
    assert lamp_status == 'ON'
    assert interlock_status == 'OFF'
    assert psu_status == 'ON'
    assert att_moving is True
    assert att_level == pytest.approx(800E-3)
    assert att_factor == 45
    assert (pow1, t1, pow2, t2) == pytest.approx((-2.323670e-14, 21.5, +2.062890e-07, 22.5))

    # What happens when a weird response is given?

    response = b"some weird string"

    values = decode_status_command(response)

    assert isinstance(values, Failure)
    assert isinstance(values.cause, ValueError)
    assert "Unexpected response" in values.message
    assert "weird" in values.message

    # What happens when the given response is not even a bytes object?

    response = 3.14

    values = decode_status_command(response)

    assert isinstance(values, Failure)
    assert values.cause is None
    assert "not a bytes object" in values.message


def test_get_level_command():

    response = b'att-level: *    480E-3  #42\n'

    x = decode_att_get_level_command(response)
    att_moving, att_level, att_factor = x.values()

    assert att_moving is True
    assert att_level ==  pytest.approx(0.48)
    assert att_factor == 42

    response = b'att-level:        1E+0  #46\n'

    x = decode_att_get_level_command(response)
    att_moving, att_level, att_factor = x.values()

    assert att_moving is False
    assert att_level == pytest.approx(1.0)
    assert att_factor == 46

    # What happens when a weird response is given?

    response = b"some weird string"

    x = decode_att_get_level_command(response)

    assert isinstance(x, Failure)
    assert isinstance(x.cause, ValueError)

    # The following exception happens because the response string is three words long, exactly
    # the number of items after splitting a normal response, but the values can not be converted
    # of course, more specifically the factor which is an integer.

    assert "Exception caught when converting values" in x.message

    assert "weird" in x.message

    # What happens when the given response is not even a bytes object?

    response = 3.14

    x = decode_att_get_level_command(response)

    assert isinstance(x, Failure)
    assert x.cause is None
    assert "not a bytes object" in x.message
