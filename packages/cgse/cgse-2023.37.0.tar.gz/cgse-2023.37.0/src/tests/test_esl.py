import logging
import pytest

from egse.dsi.esl import (
    esl_connection, esl_close_connection, esl_open_connection,
    esl_print_summary_of_structure, esl_print_info, esl_set_speed,
    esl_get_manufacturer_string, esl_get_product_string, esl_get_receive_speed)

from egse.settings import Settings
from egse.system import ping

logger = logging.getLogger(__name__)

dsi_settings = Settings.load("DSI")

dsi_available = True if ping(dsi_settings.DSI_DPU_IP_ADDRESS) else False


@pytest.mark.skipif(not dsi_available,
                    reason="requires DSI to be connected")
def test_esl_open_connection():
    """
    Test the esl connection as a normal open/close function call.
    """
    esl_link = esl_open_connection(dsi_settings.DSI_DPU_IP_ADDRESS)

    assert "4Links" in esl_get_manufacturer_string(esl_link)
    assert "DSI" in esl_get_product_string(esl_link)

    esl_close_connection(esl_link)


@pytest.mark.skipif(not dsi_available,
                    reason="requires DSI to be connected")
def test_esl_context_manager():
    """
    Test the esl connection as a context manager. `esl_connection` is in this
    case a context manager that shall be used with the `with` statement. No need
    to close the connection, this is automatically done when the `with` statement
    is out-of-scope.
    """
    with esl_connection(dsi_settings.DSI_DPU_IP_ADDRESS) as esl_link:
        assert "4Links" in esl_get_manufacturer_string(esl_link)
        assert "DSI" in esl_get_product_string(esl_link)


@pytest.mark.skipif(not dsi_available,
                    reason="requires DSI to be connected")
def test_esl_set_speed():
    with esl_connection(dsi_settings.DSI_DPU_IP_ADDRESS) as esl_link:
        esl_set_speed(esl_link, 50)
        esl_print_info(esl_link)

        # You might think the speed should be 50 Mbits/s, but the correct
        # speed will only be returned when data has actually been received
        # by the link.
        # TODO: it's not yet clear to me how to test this...
        assert esl_get_receive_speed(esl_link) == 0
        esl_set_speed(esl_link, 100)



