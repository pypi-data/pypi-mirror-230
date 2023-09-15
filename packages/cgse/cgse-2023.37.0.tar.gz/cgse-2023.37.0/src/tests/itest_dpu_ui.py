"""
These tests are indirectly testing the DPU GUI by sending commands to the DPU CS to configure
the N-FEE. The DPU GUI will then react to these commands.

Pre-requisites:

  * The feesim shall be running: `feesim start --zeromq`
  * The dpu_cs shall be running: `dpu_cs start --zeromq`
  * The DPU GUI shall be running: `dpu_ui`

"""
import logging

from egse.dpu import DPUMonitoring
from egse.dpu import DPUProxy
from egse.system import wait_until

LOGGER = logging.getLogger()


def wait_num_cycles(num_cycles: int):
    with DPUMonitoring() as moni:
        moni.wait_num_cycles(num_cycles)


def take_five_full_image_pattern_frames():

    with DPUProxy() as dpu:

        LOGGER.info("Going to STANDBY mode")
        dpu.n_fee_set_standby_mode()
        wait_until(lambda: dpu.n_fee_get_mode() == 4, timeout=25, interval=5)

        num_cycles = 5

        LOGGER.info("Going to FULL IMAGE PATTERN MODE")

        dpu.n_fee_set_full_image_pattern_mode(
            dict(num_cycles=num_cycles, v_start=0, v_end=4509, ccd_readout_order=0b11100100)
        )
        wait_num_cycles(num_cycles)

        dpu.n_fee_set_full_image_pattern_mode(
            dict(num_cycles=num_cycles, v_start=200, v_end=449)
        )
        wait_num_cycles(num_cycles)

        dpu.n_fee_set_full_image_pattern_mode(
            dict(num_cycles=num_cycles, v_start=600, v_end=899)
        )
        wait_num_cycles(num_cycles)

        dpu.n_fee_set_full_image_pattern_mode(
            dict(num_cycles=num_cycles, v_start=400, v_end=649)
        )
        wait_num_cycles(num_cycles)

        dpu.n_fee_set_full_image_pattern_mode(
            dict(num_cycles=num_cycles, v_start=100, v_end=3649)
        )
        wait_num_cycles(num_cycles)

        LOGGER.info("Going to STANDBY mode")
        dpu.n_fee_set_standby_mode()
        wait_until(lambda: dpu.n_fee_get_mode() == 4, timeout=25, interval=5)

        LOGGER.info("Going to ON mode")
        dpu.n_fee_set_on_mode()
        wait_until(lambda: dpu.n_fee_get_mode() == 0, timeout=25, interval=5)


if __name__ == "__main__":

    take_five_full_image_pattern_frames()
