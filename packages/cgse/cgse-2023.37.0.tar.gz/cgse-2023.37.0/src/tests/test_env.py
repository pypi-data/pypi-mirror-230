import os
import warnings

import pytest

from egse.env import get_conf_data_location
from egse.env import get_data_storage_location
from egse.env import ENV_PLATO_STORAGE_DATA
from egse.env import get_log_file_location


def test_get_data_storage_location():

    # A ValueError will only be raised when the configuration manager is not running or is not reachable.

    try:
        _ = get_data_storage_location()
        warnings.warn("You have a configuration manager running during the unit tests!")
    except ValueError:
        warnings.warn("No Setup could be loaded, since we are running a unit test, this is probably intended.")

    from egse.setup import Setup

    setup = Setup()
    setup.site_id = "KUL"

    os.environ[ENV_PLATO_STORAGE_DATA] = "/data"
    assert get_data_storage_location(setup) == "/data/KUL"

    # We decided not to include the camera name in the data storage location

    setup.camera = {}
    setup.camera.ID = "achel"

    assert get_data_storage_location(setup) == "/data/KUL"

    # The site_id argument takes precedence over the site_id in the Setup!

    assert get_data_storage_location(setup=setup, site_id="ESA") == '/data/ESA'

    try:
        _ = get_data_storage_location()
        warnings.warn("You have a configuration manager running during the unit tests!")
    except ValueError:
        warnings.warn("No Setup could be loaded, since we are running a unit test, this is probably intended.")


def test_get_conf_data_location():

    # A ValueError will only be raised when the configuration manager is not running or is not reachable.

    try:
        _ = get_conf_data_location()
    except ValueError:
        warnings.warn("No Setup could be loaded, since we are running a unit test, this is probably intended.")

    from egse.setup import Setup

    setup = Setup()
    setup.site_id = "KUL"

    os.environ[ENV_PLATO_STORAGE_DATA] = "/data"
    assert get_conf_data_location(setup) == "/data/KUL/conf"

    setup.camera = {}
    setup.camera.ID = "achel"

    assert get_conf_data_location(setup) == "/data/KUL/conf"

    try:
        _ = get_conf_data_location()
    except ValueError:
        warnings.warn("No Setup could be loaded, since we are running a unit test, this is probably intended.")


def test_get_log_file_location():

    from egse.settings import get_site_id

    # A ValueError will only be raised when the configuration manager is not running or is not reachable.

    try:
        _ = get_log_file_location()
    except ValueError:
        warnings.warn("No Setup could be loaded, since we are running a unit test, this is probably intended.")

    os.environ[ENV_PLATO_STORAGE_DATA] = "/data"
    assert get_log_file_location() == f"/data/{get_site_id()}/log"

    try:
        _ = get_log_file_location()
    except ValueError:
        warnings.warn("No Setup could be loaded, since we are running a unit test, this is probably intended.")
