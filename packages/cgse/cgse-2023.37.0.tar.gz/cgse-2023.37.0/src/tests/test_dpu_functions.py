import multiprocessing
import time
from unittest import mock

import pytest

from egse.dpu import NFEECommandError
from egse.dpu import get_expected_last_packet_flags
from egse.dpu import got_all_last_packets
from egse.dpu import register_to_storage_manager
from egse.dpu import send_commands_to_n_fee
from egse.reg import RegisterMap
from egse.storage import StorageProxy


def test_last_packet_flags():

    register_map = RegisterMap("N-FEE")

    # default setting for register map is no overscan packets and both E- and F-side

    expected = get_expected_last_packet_flags(register_map)
    assert expected == [True, True, False, False]

    actual = [True, True, False, False]

    assert len(actual) == len(expected)
    assert got_all_last_packets(actual, expected)

    # --------------------------------------------------------------------------
    # All data packets and E- and F-side are expected

    register_map.set_value(reg_name="reg_0_config", var_name="v_end", value=4510)

    expected = get_expected_last_packet_flags(register_map)
    assert expected == [True, True, True, True]

    actual = [True, True, True, True]

    assert len(actual) == len(expected)
    assert got_all_last_packets(actual, expected)

    # --------------------------------------------------------------------------
    # Only F-side data is expected for both data and overscan packets

    register_map[("reg_0_config", "v_end")] = 4510
    register_map[("reg_5_config", "sensor_sel")] = 0b01  # only F side

    expected = get_expected_last_packet_flags(register_map)
    assert expected == [False, True, False, True]

    assert len(expected) == 4
    assert not got_all_last_packets([True, True, True, True], expected)
    assert got_all_last_packets([False, True, False, True], expected)

    # --------------------------------------------------------------------------
    # Only E-side is expected and only for data packets

    register_map[("reg_0_config", "v_start")] = 0
    register_map[("reg_0_config", "v_end")] = 9
    register_map[("reg_5_config", "sensor_sel")] = 0b10  # only E-side

    expected = get_expected_last_packet_flags(register_map)
    assert expected == [True, False, False, False]

    assert len(expected) == 4
    assert not got_all_last_packets([False, False, False, False], expected)
    assert got_all_last_packets([True, False, False, False], expected)


def command_raise_exception(transport, register_map, exc: Exception):
    raise exc


def test_send_commands_to_n_fee():

    # This is a first attempt to test this kind of function from egse.dpu

    mock_transport = mock.Mock()
    mock_transport.read_register.return_value = b'\x00\x1c@\x00'

    storage = StorageProxy()
    origin = "PYTEST"
    readout_count = 42
    register_map = RegisterMap("N-FEE")

    command_q = multiprocessing.Queue()
    response_q = multiprocessing.Queue()

    register_to_storage_manager(storage, origin)

    # command_q.put((command_get_mode, []))
    command_q.put((command_raise_exception, [RuntimeError("Error raised on purpose!")]))

    time.sleep(0.1)  # the command_q needs time to put the object on the queue

    with pytest.raises(NFEECommandError):
        send_commands_to_n_fee(mock_transport, storage, origin, readout_count,
                               register_map, command_q, response_q)

    (command, response) = response_q.get()

    assert command == command_raise_exception
    assert response is None


def test_fpga_defaults():
    """
    This test compares the result of two implementations of the `command_set_nfee_fpga_defaults()` DPU function.
    The test validates the pull request that covers issue #2427
    """

    default_values = {
        'reg_0_config': '119D0000',
        'reg_1_config': 0,
        'reg_2_config': 'E40FA36B',
        'reg_3_config': '8F60000',
        'reg_4_config': '186A7D8C',
        'reg_5_config': '3EA030D4',
        'reg_6_config': 0,
        'reg_7_config': 0,
        'reg_8_config': 0,
        'reg_9_config': 0,
        'reg_10_config': 0,
        'reg_11_config': 0,
        'reg_12_config': 0,
        'reg_13_config': 0,
        'reg_14_config': 0,
        'reg_15_config': 0,
        'reg_16_config': 0,
        'reg_17_config': 0,
        'reg_18_config': '7FE7EF17',
        'reg_19_config': 'FE7EE7FE',
        'reg_20_config': '19ACD',
        'reg_21_config': '5E5000',
        'reg_22_config': '4241AE9',
        'reg_23_config': 0,
        'reg_24_config': 0,
        'reg_25_config': '6400000',
        'reg_26_config': '3E807D0',
    }

    byte_strings_orig = {}
    byte_strings_new = {}

    # Original implementation

    import numpy as np

    for reg_name in default_values:
        hex_string = str(default_values[reg_name]).zfill(8)
        num_hex_numbers = len(hex_string) // 2

        # Loop over all hex numbers in the input string

        byte_string = bytes()
        for index in range(num_hex_numbers):
            index *= 2
            hex_number = hex_string[index:index + 2]
            hn = int(np.int(int(hex_number, 16)))
            byte_string += hn.to_bytes(length=1, byteorder="big", signed=False)

        byte_strings_orig[reg_name] = byte_string

    # Simplified implementation

    for reg_name in default_values:
        hex_string = str(default_values[reg_name])
        byte_string = int(hex_string, 16).to_bytes(length=4, byteorder='big', signed=False)

        byte_strings_new[reg_name] = byte_string

    assert byte_strings_orig == byte_strings_new
