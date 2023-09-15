"""
Execute this test as:

    $ cd ~/git/plato-common-egse
    $ pytest --setup-show -s --show-capture=no src/tests/test_fee.py

or to run individual tests

    $ pytest --setup-show -s --show-capture=no src/tests/test_fee.py::test_n_fee_sync_register_map


"""

from rich.console import Console

from egse.dpu import DPUMonitoring
from egse.dpu import DPUProxy
from egse.fee import fee_sync_mode


def test_sync_mode(setup_camera_access):

    console = Console()
    print()

    with DPUProxy() as dpu_proxy, DPUMonitoring() as moni:

        assert dpu_proxy.n_fee_get_sync_mode() == fee_sync_mode.EXTERNAL, "Expected to be in external sync mode."

        dpu_proxy.n_fee_set_internal_sync({'int_sync_period': 2500})

        while dpu_proxy.n_fee_get_sync_mode() != fee_sync_mode.INTERNAL:
            moni.wait_number_of_pulses(1)

        assert dpu_proxy.n_fee_get_sync_mode() == fee_sync_mode.INTERNAL, "Expected to be in internal sync mode."

        dpu_proxy.n_fee_set_external_sync({})
        moni.wait_number_of_pulses(1)

        assert dpu_proxy.n_fee_get_sync_mode() == fee_sync_mode.EXTERNAL, "Expected to be in external sync mode."


def test_n_fee_sync_register_map(setup_camera_access):

    from deepdiff import DeepDiff
    from egse.reg import RegisterMap

    print()

    with DPUProxy() as dpu_proxy:

        reg_map_1: RegisterMap = dpu_proxy.n_fee_sync_register_map()

        assert isinstance(reg_map_1, RegisterMap)

        dpu_proxy.n_fee_set_standby_mode()

        reg_map_2: RegisterMap = dpu_proxy.n_fee_sync_register_map()

        reg_diff = DeepDiff(reg_map_1.as_dict(), reg_map_2.as_dict())

        assert any([True for x in reg_diff['values_changed'] if "ccd_mode_config" in x])


def test_get_register_map(setup_camera_access):

    # This test demonstrates that the RegisterMap can be retrieved from the DPU.
    # It also tests that after sending a command to the N-FEE, the RegisterMap is actually updated on the DPU.

    from deepdiff import DeepDiff
    from egse.reg import RegisterMap

    print()

    with DPUProxy() as dpu_proxy:

        # We need to go (back) to on-mode since this test might be run after the sync register map test which would
        # result in a failure because that test leaves the N-FEE in standby-mode

        dpu_proxy.n_fee_set_on_mode()

        reg_map_1 = dpu_proxy.get_register_map()

        assert isinstance(reg_map_1, RegisterMap)

        dpu_proxy.n_fee_set_standby_mode()

        reg_map_2 = dpu_proxy.get_register_map()

        reg_diff = DeepDiff(reg_map_1.as_dict(), reg_map_2.as_dict())

        assert any([True for x in reg_diff['values_changed'] if "ccd_mode_config" in x])
