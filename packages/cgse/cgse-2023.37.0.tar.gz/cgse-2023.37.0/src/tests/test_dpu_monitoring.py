"""
Execute this test as:

    $ cd ~/git/plato-common-egse
    $ pytest --setup-show -s --show-capture=no src/tests/test_dpu_monitoring.py

"""

from rich.console import Console

from egse.dpu import DPUMonitoring
from egse.dpu import DPUProxy
from egse.fee import fee_sync_mode
from egse.fee import n_fee_mode


def test_wait_number_of_pulses(setup_camera_access):

    console = Console()
    print()

    with DPUProxy() as dpu_proxy, DPUMonitoring() as moni:

        def n_cam_to_standby_mode():
            dpu_proxy.n_fee_set_standby_mode()

        def n_cam_to_on_mode():
            dpu_proxy.n_fee_set_on_mode()

        def n_cam_to_int_sync_mode():
            dpu_proxy.n_fee_set_internal_sync({"int_sync_period": 2500})

        def n_cam_to_ext_sync_mode():
            dpu_proxy.n_fee_set_external_sync({})

        # First go to internal sync mode

        console.log("Go to internal sync mode.")
        moni.on_long_pulse_do(n_cam_to_int_sync_mode)
        console.log("Wait 1 full cycle...")
        moni.wait_num_cycles(1)

        # Now go to external sync and wait for the next pulse before checking that we are indeed in external sync

        console.log("Go to external sync mode.")
        moni.on_long_pulse_do(n_cam_to_ext_sync_mode)

        assert dpu_proxy.n_fee_get_sync_mode() == fee_sync_mode.INTERNAL, "Expected to be in internal sync mode still."

        moni.wait_number_of_pulses(1)  # only need to wait one pulse since we are in internal sync

        assert dpu_proxy.n_fee_get_sync_mode() == fee_sync_mode.EXTERNAL, "Expected to be in external sync mode."

        console.log("Go to STANDBY mode on long pulse")
        moni.on_long_pulse_do(n_cam_to_standby_mode)

        assert dpu_proxy.n_fee_get_mode() != n_fee_mode.STAND_BY_MODE

        console.log("Wait 3 pulses..")
        moni.wait_number_of_pulses(3)

        assert dpu_proxy.n_fee_get_mode() != n_fee_mode.STAND_BY_MODE

        console.log("Wait 1 pulse..")
        moni.wait_number_of_pulses(1)

        assert dpu_proxy.n_fee_get_mode() == n_fee_mode.STAND_BY_MODE

        console.log("Go to ON mode on 3rd pulse")
        moni.on_frame_number_do(3, n_cam_to_on_mode)

        assert dpu_proxy.n_fee_get_mode() == n_fee_mode.STAND_BY_MODE

        console.log("Wait 1 pulse...")
        moni.wait_number_of_pulses(1)

        assert dpu_proxy.n_fee_get_mode() == n_fee_mode.ON_MODE


def test_switch_int_ext_sync_mode(setup_camera_access):

    with DPUProxy() as dpu_proxy, DPUMonitoring() as moni:

        def n_cam_to_standby_mode():
            dpu_proxy.n_fee_set_standby_mode()

        def n_cam_to_on_mode():
            dpu_proxy.n_fee_set_on_mode()

        def n_cam_to_int_sync_mode():
            dpu_proxy.n_fee_set_internal_sync({"int_sync_period": 2500})

        def n_cam_to_ext_sync_mode():
            dpu_proxy.n_fee_set_external_sync({})

        if dpu_proxy.n_fee_get_sync_mode() == fee_sync_mode.EXTERNAL:
            n_cam_to_int_sync_mode()
            moni.wait_num_cycles(1)

        n_cam_to_ext_sync_mode()
        moni.wait_number_of_pulses(1)

        assert dpu_proxy.n_fee_get_sync_mode() == fee_sync_mode.EXTERNAL, "Expected to be in external sync mode."
