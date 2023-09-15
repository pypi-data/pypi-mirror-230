from egse.bits import toggle_bit


def test_twos_complement_simple():

    x = 0b1000_0000_0000_1000
    assert x == 32776
    assert toggle_bit(x, 15) == 8

    x = 0b1100_0000_0000_0110
    assert x == 49158
    assert toggle_bit(x, 15) == 8
