import logging

import pytest

from egse.confman import ConfigurationManagerProxy
from egse.confman import is_configuration_manager_active
from egse.obsid import LAB_SETUP_TEST, TEST_LAB_SETUP
from egse.obsid import ObservationIdentifier
from egse.system import Timer

cm_cs_available = True if is_configuration_manager_active() else False


@pytest.mark.skipif(
    not cm_cs_available,
    reason="requires the Configuration Manager Control Server to be available.")
def test_performance_of_get_obsid():

    with ConfigurationManagerProxy() as cm:

        cm.start_observation({"description": "Test for get_obsid() performance 1"})

        with Timer("Only get_obsid()", precision=4, log_level=logging.WARNING):
            rc = cm.get_obsid()

        assert rc.successful

        obsid: ObservationIdentifier = rc.return_code

        print(f"{obsid=!s}")

        cm.end_observation()


@pytest.mark.skipif(
    not cm_cs_available,
    reason="requires the Configuration Manager Control Server to be available.")
def test_performance_of_requests():

    with Timer("get_obsid() including start/end observation", log_level=logging.WARNING), \
            ConfigurationManagerProxy() as cm:

        cm.start_observation({"description": "Test for get_obsid() performance 2"})
        rc = cm.get_obsid()
        cm.end_observation()

    obsid: ObservationIdentifier = rc.return_code

    assert obsid is not None
