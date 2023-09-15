
def test_encoding():

    from egse.lampcontrol.energetiq.lampEQ99_encode_decode_errors import encode_lamp_errors

    assert encode_lamp_errors([0]) == 0b01
    assert encode_lamp_errors([600, 603]) == 0b10010000000000000
    assert encode_lamp_errors([3, 4, 127]) == 0b1000000110


def test_decoding():

    from egse.lampcontrol.energetiq.lampEQ99_encode_decode_errors import decode_lamp_errors

    assert 0 in decode_lamp_errors(0b01)

    assert 100 not in decode_lamp_errors(0b10010000000000000)
    assert 600 in decode_lamp_errors(0b10010000000000000)
    assert 603 in decode_lamp_errors(0b10010000000000000)

    assert 3 in decode_lamp_errors(0b1000000110)
    assert 4 in decode_lamp_errors(0b1000000110)
    assert 127 in decode_lamp_errors(0b1000000110)
    assert 100 not in decode_lamp_errors(0b1000000110)


def test_description():

    from egse.lampcontrol.energetiq.lampEQ99_encode_decode_errors import LAMP_ERRORS
    from egse.lampcontrol.energetiq.lampEQ99_encode_decode_errors import decode_lamp_errors

    assert decode_lamp_errors(0b10010000000000000)[603] == ": ".join(LAMP_ERRORS[603])
    assert decode_lamp_errors(0b01)[0] == ": ".join(LAMP_ERRORS[0])
