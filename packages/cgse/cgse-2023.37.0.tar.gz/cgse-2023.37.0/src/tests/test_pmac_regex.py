from pytest import approx

from egse.hexapod.symetrie.pmac_regex import (regex_response, match_regex_response,
                                              match_float_response, match_int_response,
                                              match_error_response, match_string_response)


def test_regex_anything_here():
    sourceStr = b'Any Text Here!\r\x06'
    match_obj = match_regex_response(regex_response['ANY'], sourceStr)

    assert match_obj is not None
    assert len(match_obj.groups()) == 1
    assert match_obj[0] == sourceStr.decode()
    assert match_obj[1] == 'Any Text Here!\r'

    # The string should have the trailing \r removed

    assert match_string_response(sourceStr) == 'Any Text Here!'

    sourceStr = b'\r\x06'
    match_obj = match_regex_response(regex_response['ANY'], sourceStr)

    assert match_obj is not None
    assert len(match_obj.groups()) == 1
    assert match_obj[0] == sourceStr.decode()
    assert match_obj[1] == '\r'

    # The string should have the trailing \r removed

    assert match_string_response(sourceStr) == ''

    sourceStr = b'\x06'
    assert match_string_response(sourceStr) == ''

    sourceStr = b'ACK expected at the end!'
    assert match_string_response(sourceStr) == None


def test_regex_error_msg_here():
    sourceStr = b'\x07ERR005\r'
    match_obj = match_regex_response(regex_response['ERROR'], sourceStr)

    assert match_obj is not None
    assert len(match_obj.groups()) == 1
    assert match_obj[1] == 'ERR005'

    assert match_error_response(sourceStr) == 'ERR005'

    # Too many zeros

    sourceStr = b'\x07ERR0005\r'
    assert match_error_response(sourceStr) == None


def test_regex_int():
    sourceStr = b'1234\r\x06'
    match_obj = match_regex_response(regex_response['INT'], sourceStr)

    assert match_obj is not None
    assert len(match_obj.groups(0)) == 1
    assert match_obj[0] == '1234\r\x06'
    assert match_obj[1] == '1234'

    assert len(match_obj[0]) == 6  # Full Pattern matched
    assert len(match_obj[1]) == 4  # First Group match

    assert match_int_response(sourceStr) == 1234

    sourceStr = b'-42  \r\x06'
    match_obj = match_regex_response(regex_response['INT'], sourceStr)

    assert match_obj is not None
    assert len(match_obj.groups(0)) == 1
    assert match_obj[0] == sourceStr.decode()
    assert match_obj[1] == '-42'

    assert len(match_obj[0]) == 7  # Full Pattern matched
    assert len(match_obj[1]) == 3  # First Group match

    assert match_int_response(sourceStr) == -42

    # This should be parsed as a float, so the following returns None!

    sourceStr = b'23.5672\r\x06'
    assert match_int_response(sourceStr) == None


def test_regex_float():
    sourceStr = b'1.234\r\x06'
    match_obj = match_regex_response(regex_response['FLOAT'], sourceStr)

    assert match_obj is not None
    assert len(match_obj.groups(0)) == 2
    assert match_obj[0] == sourceStr.decode()
    assert match_obj[1] == '1.234'
    assert match_obj[2] == '1.'

    assert len(match_obj[0]) == 7  # Full Pattern matched
    assert len(match_obj[1]) == 5  # First Group match

    assert match_float_response(sourceStr) == approx(1.234)

    sourceStr = b'-3\r\x06'
    match_obj = match_regex_response(regex_response['FLOAT'], sourceStr)

    assert match_obj is not None
    assert len(match_obj.groups(0)) == 2
    assert match_obj[0] == '-3\r\x06'
    assert match_obj[1] == '-3'
    assert match_obj[2] is None

    assert len(match_obj[0]) == 4  # Full Pattern matched
    assert len(match_obj[1]) == 2  # First Group match

    assert match_float_response(sourceStr) == approx(-3.0)

    sourceStr = b'-7.4322   \r\x06'
    match_obj = match_regex_response(regex_response['FLOAT'], sourceStr)

    assert match_obj is not None
    assert len(match_obj.groups()) == 2
    assert match_obj[0] == '-7.4322   \r\x06'
    assert match_obj[1] == '-7.4322'
    assert match_obj[2] == '7.'

    assert len(match_obj[0]) == 12  # Full Pattern matched
    assert len(match_obj[1]) == 7   # First Group match

    assert match_float_response(sourceStr) == approx(-7.4322)

    # There is a missing \r in the sourceStr!

    sourceStr = b'23.5672\x06'
    assert match_float_response(sourceStr) == None


