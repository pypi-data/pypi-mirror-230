import pytest
import rich

from egse.state import GlobalState
from egse.state import GlobalState as GS

# This needs to be looked into again:
# from tests.helper import load_test_setup
# load_test_setup()


@pytest.mark.skip
def test_global_state_setup():

    with pytest.raises(AttributeError):
        _ = GS.setup.unknown

    # For this test to succeed we need the configuration manager running and a proper
    # Setup loaded into the configuration manager.
    # Assumptions:
    #   * Setup loaded: CSL
    #   * Setup ID: 97

    assert GS.setup.site_id == "CSL"
    assert GS.setup.get_id() == '00097'
    assert GS.setup.gse.stages.BIG_ROTATION_STAGE_ID == '420-20912'
    assert GS.setup.gse.stages.device.__class__.__name__ == "HuberSMC9300Proxy"
    assert GS.setup.gse.stages.get_raw_value("device").startswith("class//")


def test_global_state_dry_run():

    assert GS.dry_run is False

    GlobalState.dry_run = True

    assert GS.dry_run is True

    GlobalState.dry_run = False
