"""
This unit test will check if after num_cycles <= 0 the N-FEE is instructed to go to DUMP mode.

If the N-FEE does not go back to DUMP mode after the num_cycles becomes <= 0, then the test will fail.

Execute this test as:

    $ cd ~/git/plato-common-egse
    $ pytest --setup-show -s --show-capture=no src/tests/test_automatic_dump_mode.py
or
    $ pytest --setup-show -s --show-capture=no src/tests/test_automatic_dump_mode.py::test_got_to_dump_mode_after_num_cycles
    $ pytest --setup-show -s --show-capture=no src/tests/test_automatic_dump_mode.py::test_got_to_dump_mode_int_sync_after_num_cycles

"""
import time

import pytest
from rich.console import Console

from egse.dpu import DPUMonitoring
from egse.dpu import DPUProxy


def test_got_to_dump_mode_after_num_cycles(setup_camera_access):

    console = Console()
    print()

    timeout = 1 * 25  # seconds

    with DPUProxy() as dpu_proxy, DPUMonitoring() as moni:

        def n_cam_to_standby_mode():
            dpu_proxy.n_fee_set_standby_mode()

        console.log("Go to STANDBY mode before the next long pulse")
        moni.on_frame_number_do(3, n_cam_to_standby_mode)

        n_fee_parameters = {
            'num_cycles': 2, 'v_start': 200, 'v_end': 500, 'n_final_dump': 4509,
            'ccd_readout_order': 78, 'sensor_sel': 3
        }

        console.log("Go to FULL IMAGE mode before the next long pulse")
        moni.on_frame_number_do(3, dpu_proxy.n_fee_set_full_image_mode, n_fee_parameters)

        moni.wait_until_synced_num_cycles_is_zero()

        while not bool(dpu_proxy.n_fee_is_dump_mode()) and timeout >= 0:
            time.sleep(1.0)
            timeout -= 1.0

        if not bool(dpu_proxy.n_fee_is_dump_mode()):
            pytest.fail("The N-FEE didn't go back to DUMP mode!")

        console.log("In DUMP mode EXTERNAL SYNC, waiting for next timecode")
        moni.wait_for_timecode()


def test_got_to_dump_mode_int_sync_after_num_cycles(setup_camera_access):

    console = Console()
    print()

    timeout = 1 * 6.25  # seconds

    with DPUProxy() as dpu_proxy, DPUMonitoring() as moni:

        def n_cam_to_standby_mode():
            dpu_proxy.n_fee_set_standby_mode()

        console.log("Go to STANDBY mode before the next long pulse")
        moni.on_frame_number_do(3, n_cam_to_standby_mode)

        n_fee_parameters = {
            'num_cycles': 2, 'v_start': 200, 'v_end': 500, 'n_final_dump': 4509,
            'ccd_readout_order': 78, 'sensor_sel': 3
        }

        console.log("Go to FULL IMAGE mode INTERNAL SYNC before the next long pulse")
        moni.on_frame_number_do(3, dpu_proxy.n_fee_set_full_image_mode_int_sync, n_fee_parameters)

        moni.wait_until_synced_num_cycles_is_zero()

        while not bool(dpu_proxy.n_fee_is_dump_mode()) and timeout >= 0:
            time.sleep(1.0)
            timeout -= 1.0

        if not bool(dpu_proxy.n_fee_is_dump_mode()):
            pytest.fail("The N-FEE didn't go back to DUMP mode INTERNAL SYNC!")

        console.log("In DUMP mode INTERNAL SYNC, waiting for next timecode")
        moni.wait_for_timecode()
