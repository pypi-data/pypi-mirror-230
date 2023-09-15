import os
from pathlib import Path

# make sure to set the environment variables before importing anything from egse

os.environ["PLATO_CONF_DATA_LOCATION"] = str(Path(__file__).parent / "data/conf")
os.environ["PLATO_LOCAL_SETTINGS"] = str(Path(__file__).parent / "data/confman_settings.yaml")

from egse.config import find_file
from egse.confman import ConfigurationManagerController
from egse.system import format_datetime


def test_new_setup_id():
    site_id = "CSL"

    cm_controller = ConfigurationManagerController()

    assert cm_controller.data_location

    setup_id = cm_controller.get_next_setup_id_for_site(site_id)

    # check if there is indeed no file with this id

    assert (
        find_file(name=f"SETUP_{site_id}_{setup_id:05d}_*.yaml", root=cm_controller.data_location)
        is None
    )

    # verify that there is a file for the previous id

    assert find_file(f"SETUP_{site_id}_{setup_id - 1:05d}_*.yaml", root=cm_controller.data_location)


def test_submit_setup():

    site_id = "CSL"

    cm = ConfigurationManagerController()

    setup_id = cm.get_next_setup_id_for_site(site_id)
    setup = cm.load_setup(setup_id - 1)

    dts = format_datetime()
    setup.X = dts

    setup = cm.submit_setup(setup, "updated X with current time")

    assert str(setup_id) in setup.history

    os.unlink(setup.get_private_attribute("_filename"))


def test_cached_setup_info():

    cm = ConfigurationManagerController()

    assert cm.get_setup_id() == 0

    setups = cm.list_setups()

    assert len(setups) == 3
    assert '00001' in setups[1]

    cm.load_setup(1)
    assert cm.get_setup_id() == 1

    cm.reload_setups()

    assert cm.get_setup_id() == 1


def test_list_setups():

    cm = ConfigurationManagerController()

    setups = cm.list_setups()

    assert len(setups) == 3

    setups = cm.list_setups(gse__hexapod__ID=2)

    assert len(setups) == 1

    setups = cm.list_setups(gse__aeu=(hasattr, True))

    assert len(setups) == 1

    setups = cm.list_setups(history=(hasattr, True))

    assert len(setups) == 2
