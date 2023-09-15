"""
Unit Tests for the RMAP module.
"""

import pytest

from egse.dsi.esl import esl_connection, pp_packet, pretty_print_packet
from egse.dsi.rmap import (
    get_initiator_logical_address, RMAPError, check_address_and_data_length,
    create_rmap_verified_write_packet,
    rmap_connection, get_address, get_data, check_data_crc, check_header_crc, create_rmap_unverified_write_packet)
from egse.settings import Settings
from egse.system import ping

dsi_settings = Settings.load("DSI")

dsi_available = True if ping(dsi_settings.DSI_DPU_IP_ADDRESS) else False


def test_check_data_length():

    # When you want to check on the exceptions, use:
    # print(exc_info.value)

    with pytest.raises(RMAPError) as exc_info:
        assert check_address_and_data_length(0x0000_0000, 3)

    with pytest.raises(RMAPError) as exc_info:
        assert check_address_and_data_length(0x0000_0001, 4)

    # Tests for critical area

    with pytest.raises(RMAPError) as exc_info:
        assert check_address_and_data_length(0x0000_0000, 0)

    with pytest.raises(RMAPError) as exc_info:
        assert check_address_and_data_length(0x0000_0010, 12)

    assert check_address_and_data_length(0x0000_0004, 4) is None
    assert check_address_and_data_length(0x0000_00FC, 4) is None

    # Tests for general area

    assert check_address_and_data_length(0x0000_0100,  12) is None
    assert check_address_and_data_length(0x0000_01F0,  20) is None

    with pytest.raises(RMAPError) as exc_info:
        assert check_address_and_data_length(0x0000_01F0, 300)

    assert check_address_and_data_length(0x0000_06FC, 4) is None
    with pytest.raises(RMAPError) as exc_info:
        assert check_address_and_data_length(0x0000_06FC, 8)

    # Tests for housekeeping area

    assert check_address_and_data_length(0x0000_0700,  12) is None
    assert check_address_and_data_length(0x0000_07AC,  20) is None
    with pytest.raises(RMAPError) as exc_info:
        assert check_address_and_data_length(0x0000_07FC, 260) is None

    assert check_address_and_data_length(0x0000_07FC, 4) is None
    with pytest.raises(RMAPError) as exc_info:
        assert check_address_and_data_length(0x0000_07FC, 8) is None

    # Tests for windowing area

    assert check_address_and_data_length(0x0080_0000, 12) is None
    assert check_address_and_data_length(0x0090_0000, 20) is None
    with pytest.raises(RMAPError) as exc_info:
        assert check_address_and_data_length(0x0090_0000, 5000) is None

    assert check_address_and_data_length(0x00FF_FFFC, 4) is None
    with pytest.raises(RMAPError) as exc_info:
        assert check_address_and_data_length(0x00FF_FFFC, 8) is None

    # Tests out of any area

    with pytest.raises(RMAPError) as exc_info:
        assert check_address_and_data_length(0x0FFF_0000, 4) is None
    with pytest.raises(RMAPError) as exc_info:
        assert check_address_and_data_length(0x0000_1000, 4) is None
    with pytest.raises(RMAPError) as exc_info:
        assert check_address_and_data_length(0x0011_0000, 4) is None


@pytest.mark.skipif(not dsi_available,
                    reason="requires DSI to be connected")
def test_create_verified_write_request():

    dsi_address = dsi_settings.DSI_DPU_IP_ADDRESS

    # FIXME: We should find a way to test these functions without the need for an rmap_link or esl_link
    #        or we should be able to mock this.

    with esl_connection(dsi_address) as esl_link, rmap_connection(esl_link) as rmap_link:
        packet = create_rmap_verified_write_packet(
            rmap_link, 0x0000_0042, int.to_bytes(0x0101_0101, 4, byteorder='big')
        )

    assert get_address(packet.raw) == 0x42
    assert int.from_bytes(get_data(packet.raw), 'big') == 0x0101_0101

    check_header_crc(packet.raw)
    check_data_crc(packet.raw)

    print()
    print(pretty_print_packet(packet))


@pytest.mark.skipif(not dsi_available,
                    reason="requires DSI to be connected")
def test_create_unverified_write_request():

    dsi_address = dsi_settings.DSI_DPU_IP_ADDRESS

    # FIXME: We should find a way to test these functions without the need for an rmap_link or esl_link
    #        or we should be able to mock this.

    buffer = b'abcdefghijklmnopqrstuvwxyz'

    with esl_connection(dsi_address) as esl_link, rmap_connection(esl_link) as rmap_link:
        packet = create_rmap_unverified_write_packet(rmap_link, 0x0000_0142, buffer, len(buffer))

    print()
    print(pretty_print_packet(packet))

    assert get_address(packet.raw) == 0x142
    assert get_data(packet.raw) == buffer

    check_header_crc(packet.raw)
    check_data_crc(packet.raw)


