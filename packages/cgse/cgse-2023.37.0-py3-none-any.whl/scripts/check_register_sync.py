"""
This module contains commands and strategies to test the synchronisation of the Register Map
between the DPU Processor and the N-FEE.

The reason for this test is that the DPU Processor seems to be out of sync with the N-FEE at some
points in time:

* When the N-FEE is power-cycled and the DPU CS is not restarted, the register map is not
  refreshed from the newly pwoered N-FEE

* ...

The DPU CS has a few commands available to fix this:

* dpu.n_fee_sync_register_map() — reads the register map from the N-FEE, updates the DPU internal
  register map and returns the register map.

* dpu.reset() — sets a special register in the N-FEE ccd_mode_config which commands the N-FEE to
  resets its register map to its default state.

"""

from egse.dpu import DPUProxy
from egse.reg import compare_register_maps

dpu_proxy = DPUProxy()


reg_1 = dpu_proxy.n_fee_sync_register_map()

# Put the N-FEE in DUMP mode

dpu_proxy.n_fee_set_dump_mode(
    dict(v_start=0, v_end=2000, ccd_readout_order=0b11111111, n_final_dump=4510))

reg_2 = dpu_proxy.n_fee_sync_register_map()

# Put the N-FEE back into its default mode (same as after a power cycle?)

dpu_proxy.n_fee_reset()

reg_3 = dpu_proxy.n_fee_sync_register_map()


compare_register_maps(reg_1, reg_2)
compare_register_maps(reg_2, reg_3)
compare_register_maps(reg_1, reg_3)
