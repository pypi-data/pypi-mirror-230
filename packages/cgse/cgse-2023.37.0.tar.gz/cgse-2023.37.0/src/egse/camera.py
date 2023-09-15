from __future__ import annotations

import logging

LOGGER = logging.getLogger(__name__)


def get_camera_name() -> str | None:
    """
    Retrieve the camera name from the configuration manager.

    Notes:
        This function contacts the configuration manager control server in order to determine the camera name.
        On a typical not too heavy loaded system/network, this function takes about 10ms to return. Keep that in mind
        when using this function in a time critical situation.

    Returns:
        the camera name in lower case or None when an error occurred.
    """
    from egse.confman import is_configuration_manager_active
    if not is_configuration_manager_active():
        LOGGER.warning("Configuration Manager is not running...")
        return None

    LOGGER.info("Configuration Manager is ACTIVE")

    from egse.confman import ConfigurationManagerProxy
    from egse.control import Failure

    try:
        with ConfigurationManagerProxy() as cm_proxy:
            setup = cm_proxy.get_setup()
            try:
                LOGGER.info(f"{setup = }")
                return None if isinstance(setup, Failure) else setup.camera.ID.lower()
            except AttributeError as exc:
                LOGGER.error(f"Caught AttributeError: {exc}", exc_info=True)
                return None
    except Exception as exc:
        LOGGER.warning(f"Caught Exception: {exc}", exc_info=True)

    LOGGER.info("How did I end up here????")

    return None
