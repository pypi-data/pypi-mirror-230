import os
from pathlib import Path

from egse.confman import ConfigurationManagerController

# make sure the Setups are loaded from the tests folder

TEST_LOCATION = Path(__file__).parent
os.environ["PLATO_CONF_DATA_LOCATION"] = str(TEST_LOCATION / "data/conf")


def test_load_setup():

    ctrl = ConfigurationManagerController()
    setup = ctrl.load_setup(1)
    assert setup.site_id == "CSL"
    assert setup.gse.hexapod.ID == 2


def test_load_non_existing_setup():
    ctrl = ConfigurationManagerController()
    setup = ctrl.load_setup(42)

    assert isinstance(setup, Exception)
