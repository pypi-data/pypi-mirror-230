import logging
import importlib

logger = logging.getLogger(__name__)


def test_constants():

    logger.info(f"Inside test_constants(): __name__ = {__name__}")

    import egse.dsi.constants as constants

    assert constants.ESL_DSI_TIMEOUT == 0x000100

    # The following three lines will generate log error messages, but no exception as intended.
    
    # The test shows that constants can be imported multiple times, but the error is logged
    # to remind the developer that the an import is unnecessary.

    importlib.reload(constants)

    import egse.dsi.constants
    assert egse.dsi.constants.ESL_DSI_TIMEOUT == 0x000100
