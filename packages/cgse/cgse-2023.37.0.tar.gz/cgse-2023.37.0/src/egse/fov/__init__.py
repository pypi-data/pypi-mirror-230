import logging

from egse.control import Failure
from egse.storage import StorageProxy
from egse.synoptics import SynopticsManagerProxy
from egse.system import format_datetime

LOGGER = logging.getLogger(__name__)
ORIGIN = "FOV"


def store_actual_fov_position(theta: float, phi: float):
    """ Store the given actual FOV position in the FOV position HK file.

    Args:
        - theta: Actual gnomonic distance to the optical axis [degrees].
        - phi: Actual in-field angle [degrees].
    """

    try:

        with StorageProxy() as storage:

            data = {"timestamp": format_datetime(), "FOV_ACT_THETA": theta, "FOV_ACT_PHI": phi}
            response = storage.save({"origin": ORIGIN, "data": data})

            # Store the actual FOV positions as synoptics

            with SynopticsManagerProxy() as synoptics:
                synoptics.store_common_synoptics(data)

            if isinstance(response, Failure):
                LOGGER.warning("Failed to store the actual FOV position.  Check the status of fov_hk.")

    except ConnectionError as exc:
        LOGGER.warning(f"Couldn't connect to the Storage Manager to store the actual FOV position: {exc}")


def store_commanded_fov_position(theta: float, phi: float):
    """ Store the given commanded FOV position in the FOV position HK file.

    This method will be called from the MGSE commanding in plato-test-scripts.

    Args:
        - theta: Commanded gnomonic distance to the optical axis [degrees].
        - phi: Commanded in-field angle [degrees].
    """

    try:

        with StorageProxy() as storage:

            data = {"timestamp": format_datetime(), "FOV_CMD_THETA": theta, "FOV_CMD_PHI": phi}
            response = storage.save({"origin": ORIGIN, "data": data})

            # Store the commanded FOV positions as synoptics

            with SynopticsManagerProxy() as synoptics:
                synoptics.store_common_synoptics(data)

            if isinstance(response, Failure):
                LOGGER.info("fov_hk is not running: the commanded position cannot be stored")

    except ConnectionError as exc:
        LOGGER.warning(f"Couldn't connect to the Storage Manager to store the actual FOV position: {exc}")
