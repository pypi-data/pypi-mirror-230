"""
This module defines all functionality with respect to the FEE. It defines the structure of the FEE
internal register map and the FEE housekeeping packet. The module also provides the FEE Simulator.

Currently, only the N-FEE functionality is implemented in this module.
"""
from enum import IntEnum
from typing import List

from egse.fee.fee import get_data
from egse.fee.fee import get_mode
from egse.fee.fee import increment_timecode
from egse.fee.fee import is_data_data_packet
from egse.fee.fee import is_hk_data_packet
from egse.fee.fee import is_last_packet
from egse.fee.fee import is_overscan_data_packet

from egse.setup import SetupError
from egse.state import GlobalState


def convert_ccd_order_list(value: List[int]):
    """
    Convert a list of CCD numbers into their binary representation that is used by the
    register map of the N-FEE.

    Examples:
        >>> bin(convert_ccd_order_list([1,2,3,4]))
        '0b1001110'
        >>> bin(convert_ccd_order_list([2,2,4,4]))
        '0b1011111'

    Args:
        value (List): a list of four CCD numbers in the range [1-4]

    Returns:
        The binary representation of the ccd_readout_order.

    """
    if len(value) != 4:
        raise ValueError(f"Expected a list of four CCD numbers, got {value}")
    if min(value) < 1 or max(value) > 4:
        raise ValueError(f"Expected all CCD numbers in the range [1-4], got {value}")
    try:
        return sum(GlobalState.setup.camera.fee.ccd_numbering.CCD_ID_TO_BIN[ccd] << idx * 2
                   for idx, ccd in enumerate(value))
    except AttributeError:
        raise SetupError("No entry in the setup for camera.fee.ccd_numbering.CCD_ID_TO_BIN")


def convert_ccd_order_value(value: int):
    """
    Convert a binary representation of the CCD readout order (ccd_readout_order) into a list
    of CCD numbers.

    Examples:
        >>> convert_ccd_order_value(228)
        [3, 4, 1, 2]
        >>> convert_ccd_order_value(0x4E)
        [1, 2, 3, 4]

    Args:
        value (int): the CCD readout order as returned by the N-FEE

    Returns:
        A list of CCD numbers.
    """

    try:
        return [GlobalState.setup.camera.fee.ccd_numbering.CCD_BIN_TO_ID[(value >> x) & 0b11] for x in [0, 2, 4, 6]]
    except AttributeError:
        raise SetupError("No entry in the setup for camera.fee.ccd_numbering.CCD_BIN_TO_ID")


# The name of the of the enum class `fee_mode` is deliberately chosen in snake case,
# although PEP8 prescribes the use of CamelCase for class names. The reason for this choice
# is readability because the members of the enum are in all caps anyway.
#
# fee_mode.ON_MODE is more readable than NFEEMode.ON_MODE (IMHO)

# noinspection PyPep8Naming

# noinspection PyPep8Naming
class fee_sync_mode(IntEnum):
    """
    The sync mode defines if the FEE is using external or internal synchronisation signals.
    """

    EXTERNAL = 0
    INTERNAL = 1


# noinspection PyPep8Naming
class n_fee_mode(IntEnum):
    """
    Enumeration of the operating modes for the N-FEE.
    """

    ON_MODE = 0x0
    FULL_IMAGE_PATTERN_MODE = 0x1
    WINDOWING_PATTERN_MODE = 0x2
    # NOT_DEFINED_MODE = 0x3
    STAND_BY_MODE = 0x4
    FULL_IMAGE_MODE = 0x5
    WINDOWING_MODE = 0x6
    PERFORMANCE_TEST_MODE = 0x7
    IMMEDIATE_ON_MODE = 0x8
    PARALLEL_TRAP_PUMPING_1_MODE = 0x9
    PARALLEL_TRAP_PUMPING_2_MODE = 0xA
    SERIAL_TRAP_PUMPING_1_MODE = 0xB
    SERIAL_TRAP_PUMPING_2_MODE = 0xC
    # RESERVED_MODE = 0xD
    # RESERVED_MODE = 0xE
    # RESERVED_MODE = 0xF
