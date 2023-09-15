import os
import pathlib
import pytest
import logging

import egse
from egse.settings import Settings
from egse.settings import SettingsError

logger = logging.getLogger(__name__)

_THIS_FILE_LOCATION = pathlib.Path(__file__).resolve().parent


@pytest.fixture(autouse=True)
def define_location():
    """
    This fixture will change the current working directory for each test to the location of
    this test script. That way, the location keyword given in the Settings.load() method can
    be a relative path and tests are not affected by the test_location() method which also
    changes the current working directory.
    """
    tests_loc = pathlib.Path(__file__).resolve().parent
    os.chdir(tests_loc)


def test_default_loading():
    # This loads the complete settings.yaml, no specific group

    settings = Settings.load()

    logger.info(Settings.to_string())

    assert settings.DSI
    assert hasattr(settings, "PMAC Controller")

    # This loads the complete settings.yaml, no specific group

    settings = Settings.load(location="./data")

    assert settings.GROUP_1
    assert settings.GROUP_2

    assert settings.GROUP_1["VAR_1"]
    assert settings.GROUP_1["VAR_1"] == "variable one"

    assert settings.GROUP_2["VAR_2"]
    assert settings.GROUP_2["VAR_2"] == 2


def test_locations():
    """
    This test checks the proper location of the YAML file based on different location keywords.
    """

    # Change working directory to the location of the settings module, there is a user.yaml file there

    settings_loc = pathlib.Path(egse.settings.__file__).resolve().parent
    os.chdir(settings_loc)

    # load the user.yaml file from this location

    settings = Settings.load(filename="user.yaml", location=".")

    assert settings.META_DATA

    # Change working directory to the tests directory at the location of the settings module

    os.chdir(settings_loc / "../tests")

    # load the settings.yaml file from the data directory at this location

    settings = Settings.load(location="./data")

    assert settings.GROUP_3


def test_loading_problems():
    with pytest.raises(SettingsError):
        settings = Settings.load(location=pathlib.Path(__file__).parent.resolve())

    with pytest.raises(SettingsError):
        settings = Settings.load(filename="empty.yaml")

    with pytest.raises(SettingsError):
        settings = Settings.load(filename="empty.yaml", location="data")

    with pytest.raises(SettingsError):
        settings = Settings.load(filename="empty.yaml", location="tests/data")

    with pytest.raises(SettingsError):
        settings = Settings.load(filename="corrupt.yaml", location="data")


def test_loading_unknown_group():
    with pytest.raises(SettingsError):
        settings = Settings.load("UNKNOWN_GROUP", location="./data")


def test_loading_empty_group():
    with pytest.raises(SettingsError):
        settings = Settings.load("EMPTY_GROUP", location="./data")


def test_constants_known():
    dsi_settings = Settings.load("DSI")

    assert dsi_settings.INITIATOR_LOGICAL_ADDRESS == 0x50
    assert dsi_settings.TARGET_LOGICAL_ADDRESS == 0x51

    assert 0 <= dsi_settings.LINK_SPEED <= 500


def test_duplicates():
    dup = Settings.load("DUPLICATES", location="./data")

    assert dup.VAR_X
    assert dup.VAR_X == "y"


def test_types():
    group_1 = Settings.load("GROUP_1", location="./data")

    assert group_1.VAR_1 == "variable one"
    assert group_1.VAR_2 == "variable_two"
    assert isinstance(group_1.VAR_1, str)

    # was this: assert group_1.is_defined('VAR_2')
    assert "VAR_2" in group_1
    # was this: assert not group_1.is_defined('VAR_3')
    assert "VAR_3" not in group_1

    group_2 = Settings.load("GROUP_2", location="./data")

    assert group_2.VAR_1 == 1
    assert group_2.VAR_2 == 2

    assert isinstance(group_2.VAR_1, int)

    group_3 = Settings.load("GROUP_3", location="./data")

    assert group_3.ARR_1 == [1, 2, 3, 4, 5]
    assert isinstance(group_3.ARR_1, list)

    assert group_3.ARR_2 == {"one": 1, "two": 2}
    assert isinstance(group_3.ARR_2, dict)

    assert group_3.FLT_1 == 3.14
    assert isinstance(group_3.FLT_1, float)

    assert group_3.FLT_2 == 0.0062
    assert isinstance(group_3.FLT_2, float)
