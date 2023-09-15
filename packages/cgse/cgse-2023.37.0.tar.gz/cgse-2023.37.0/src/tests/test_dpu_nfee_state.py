import pytest

from egse.dpu import NFEEState
from egse.reg import RegisterMap


def test_construction():

    state = NFEEState()

    for par_name in state.get_parameter_names():
        assert state.get_value(par_name) == 0

    state_tuple = state.get_state()

    assert state_tuple.v_start == 0
    assert state_tuple.ccd_mode_config == 0


def test_updates():

    reg_map = RegisterMap("N-FEE")

    state = NFEEState()

    assert state.sensor_sel == 0 != reg_map["sensor_sel"]
    assert state.ccd_read_en == 0 != reg_map["ccd_read_en"]

    state.update_at_200ms(reg_map)
    state_tuple = state.get_state()

    assert state_tuple.sensor_sel == state.sensor_sel == reg_map["sensor_sel"]
    assert state_tuple.ccd_read_en == state.ccd_read_en == reg_map["ccd_read_en"]

    assert state_tuple.v_end == state.v_end == 0 != reg_map["v_end"]
    assert state_tuple.int_sync_period == state.int_sync_period == 0 != reg_map["int_sync_period"]

    reg_map["reg_5_config", "sensor_sel"] = 1
    reg_map["reg_5_config", "ccd_read_en"] = 0

    reg_map["reg_0_config", "v_start"] = 1234

    state.update_at_400ms(reg_map)
    state_tuple = state.get_state()

    assert state_tuple.v_start == state.v_start == reg_map["v_start"] == 1234
    assert state_tuple.sensor_sel == state.sensor_sel == reg_map["sensor_sel"] == 1
    assert state_tuple.ccd_read_en == state.ccd_read_en == reg_map["ccd_read_en"] == 0

    for par_name in state.get_parameter_names():
        assert state.get_value(par_name) == reg_map[par_name]

    # NamedTuples are immutable

    with pytest.raises(AttributeError):
        state_tuple.v_end = 4500
