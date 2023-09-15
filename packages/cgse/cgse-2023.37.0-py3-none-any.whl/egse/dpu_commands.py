"""
This is a collection of all DPU commands that can be used by the test scripts for the PLATO Camera
testing. The functions are a one-to-one match to the methods defined in the DPUInterface,
but they take a parameter dictionary as the argument instead of keyword arguments.
"""

# TODO:
#  It is currently not clear to me anymore why this intermediate layer was created and why we
#  not just call the DPUInterface methods in the test scripts. Maybe for argument checking,
#  maybe to have just functions instead of methods (procedural call instead of OO calling).

import logging

from egse.state import GlobalState

logger = logging.getLogger(__name__)


def n_fee_set_full_image_mode(n_fee_parameters: dict):
    """
    Sets the N-FEE to full_image mode.

    Input values:
        n_fee_parameters = dict()
        n_fee_parameters["num_images"] = num_images
        n_fee_parameters["row_start"] = row_start
        n_fee_parameters["row_end"] = row_end
        n_fee_parameters["col_end"] = col_end
        n_fee_parameters["rows_final_clearout"] = rows_final_clearout
        n_fee_parameters["ccd_order"] = ccd_order
        n_fee_parameters["ccd_side"] = ccd_side

    where:
        num_images: Number images to acquire.
            If zero, images will continue to be acquired until the FEE is set to standby mode again.
        row_start: First row to read out.
        row_end: First row not to read out.
        col_end: First column not to read out.
        rows_final_clearout: number of rows for the clearout after the readout
        ccd_order: list of four integers containing the CCD numbers 1, 2, 3, 4
        ccd_side: in ['E','F'] with E = left, F = right

    Args:
        n_fee_parameters (dict): dictionary with N-FEE settings for this command.

    Returns:
        The status.
    """
    dpu = GlobalState.setup.camera.dpu.device
    status = dpu.n_fee_set_full_image_mode(n_fee_parameters)
    return status


def n_fee_set_reverse_clocking(n_fee_parameters):
    """
    Sets the N-FEE to reverse clocking mode.

    Args:
        n_fee_parameters (dict): dictionary with N-FEE settings for this command.

    """


def n_fee_get_mode() -> int:
    """
    Returns the mode in which the N-FEE currently is.

    The mode value that is returned can be checked against the n_fee_mode enumeration.

    >>> from egse.fee import n_fee_mode
    >>> if dpu_commands.get_n_fee_mode() == n_fee_mode.STAND_BY_MODE:
    ...    pass

    Returns:
        The N-FEE mode as an integer.
    """

    dpu = GlobalState.setup.camera.dpu.device
    mode = dpu.get_n_fee_mode()

    return mode
