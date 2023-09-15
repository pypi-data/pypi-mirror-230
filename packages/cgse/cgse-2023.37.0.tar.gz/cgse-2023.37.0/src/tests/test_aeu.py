import time
from functools import lru_cache
from pathlib import Path

import pytest

from egse.aeu.aeu import CRIOController, CRIOSimulator, PSUController, PSUSimulator, AWGController, AWGSimulator, \
    OperatingMode, PriorityMode, IntSwitch, SyncData, Waveform, Switch, ARB, ArbData
from egse.aeu.aeu_devif import AEUError
from egse.resource import get_resource, add_resource_id
from egse.setup import Setup
import numpy as np


add_resource_id("testdata", str(Path(__file__).parent) + "/data")
SETUP = Setup.from_yaml_file(get_resource(f":/testdata/conf/SETUP_CSL_00010_210308_083016.yaml"))

# When the 'real' AEU controllers are connected, the pytest can be run with the
# controller classes. However, by default we use the simulator classes for testing.


@pytest.fixture
@lru_cache
def crio():
    try:
        crio = CRIOController()
        crio.connect()
        crio.disconnect()
    except AEUError:
        crio = CRIOSimulator()

    return crio


@pytest.fixture
@lru_cache
def psu_array(psu1, psu2, psu3, psu4, psu5, psu6):

    return [psu1, psu2, psu3, psu4, psu5, psu6]


@pytest.fixture
@lru_cache
def psu_cal_array():

    return [
        SETUP.gse.aeu.psu1.calibration,
        SETUP.gse.aeu.psu2.calibration,
        SETUP.gse.aeu.psu3.calibration,
        SETUP.gse.aeu.psu4.calibration,
        SETUP.gse.aeu.psu5.calibration,
        SETUP.gse.aeu.psu6.calibration
    ]


@pytest.fixture
@lru_cache
def psu1():
    try:
        psu = PSUController(1)
        psu.connect()
        psu.disconnect()
    except AEUError:
        psu = PSUSimulator(1)

    return psu


@pytest.fixture
@lru_cache
def psu2():
    try:
        psu = PSUController(2)
        psu.connect()
        psu.disconnect()
    except AEUError:
        psu = PSUSimulator(2)

    return psu


@pytest.fixture
@lru_cache
def psu3():
    try:
        psu = PSUController(3)
        psu.connect()
        psu.disconnect()
    except AEUError:
        psu = PSUSimulator(3)

    return psu


@pytest.fixture
@lru_cache
def psu4():
    try:
        psu = PSUController(4)
        psu.connect()
        psu.disconnect()
    except AEUError:
        psu = PSUSimulator(4)

    return psu


@pytest.fixture
@lru_cache
def psu5():
    try:
        psu = PSUController(5)
        psu.connect()
        psu.disconnect()
    except AEUError:
        psu = PSUSimulator(5)

    return psu


@pytest.fixture
@lru_cache
def psu6():
    try:
        psu = PSUController(6)
        psu.connect()
        psu.disconnect()
    except AEUError:
        psu = PSUSimulator(6)

    return psu


@pytest.fixture
@lru_cache
def awg_array(awg1, awg2):

    return [awg1, awg2]


@pytest.fixture
@lru_cache
def awg_cal_array():

    return [
        SETUP.gse.aeu.awg1.calibration,
        SETUP.gse.aeu.awg2.calibration
    ]


@pytest.fixture
@lru_cache
def awg1():
    try:
        awg = AWGController(1)
        awg.connect()
        awg.disconnect()
    except AEUError:
        awg = AWGSimulator(1)

    return awg


@pytest.fixture
@lru_cache
def awg2():
    try:
        awg = AWGController(2)
        awg.connect()
        awg.disconnect()
    except AEUError:
        awg = AWGSimulator(2)

    return awg


##########
# Usecases
##########


def test_n_cam(crio, psu_array, psu_cal_array, awg_array, awg_cal_array):

    # crio.connect()
    crio_cal = SETUP.gse.aeu.crio.calibration

    # 1. Change the operating mode to "Functional & TVAC Operating Mode"

    crio.set_operating_mode(OperatingMode.FC_TVAC)

    # 2. Check the actual operating mode

    assert crio.get_operating_mode() == OperatingMode.FC_TVAC

    # 3. Configure the OCP for the N-CAM

    n_cam_ocp = crio_cal.n_cam_ocp
    crio.set_n_cam_ocp(*n_cam_ocp)

    # 4. Check the OCP for the N-CAM

    assert len(crio.get_n_cam_ocp()) == 6

    for index in range(6):

        assert crio.get_n_cam_ocp()[index] == n_cam_ocp[index]

    # 5. Configure the OVP for the N-CAM

    n_cam_ovp = crio_cal.n_cam_ovp
    crio.set_n_cam_ovp(*n_cam_ovp)

    # 6. Check the OVP for the N-CAM

    assert len(crio.get_n_cam_ovp()) == 6

    for index in range(6):

        assert crio.get_n_cam_ovp()[index] == n_cam_ovp[index]

    # 7. Configure the UVP for the N-CAM

    n_cam_uvp = crio_cal.n_cam_uvp
    crio.set_n_cam_uvp(*n_cam_uvp)

    # 8. Check the UVP for the N-CAM

    assert len(crio.get_n_cam_ocp()) == 6

    for index in range(6):

        assert crio.get_n_cam_uvp()[index] == n_cam_uvp[index]

    voltages = np.array([])
    ovp = np.array([])
    currents = np.array([])
    ocp = np.array([])

    for index in range(6):

        psu = psu_array[index]
        psu_cal = psu_cal_array[index]

        psu.set_current(psu_cal.n_cam_current)
        currents = np.append(currents, psu_cal.n_cam_current)
        assert psu.get_current_config() == psu_cal.n_cam_current

        psu.set_ocp(psu_cal.n_cam_ocp)
        ocp = np.append(ocp, psu_cal.n_cam_ocp)
        assert psu.get_ocp() == psu_cal.n_cam_ocp

        psu.set_voltage(psu_cal.n_cam_voltage)
        voltages = np.append(voltages, psu_cal.n_cam_voltage)
        assert psu.get_voltage_config() == psu_cal.n_cam_voltage

        psu.set_ovp(psu_cal.n_cam_ovp)
        ovp = np.append(ovp, psu_cal.n_cam_ovp)
        assert psu.get_ovp() == psu_cal.n_cam_ovp

        psu.set_priority_mode(PriorityMode.CONSTANT_CURRENT)
        assert psu.get_priority_mode() == PriorityMode.CONSTANT_CURRENT

        psu.set_output_status(IntSwitch.ON)
        assert psu.get_output_status() == IntSwitch.ON

    try:

        crio.current_n_cam = currents
        crio.voltage_n_cam = voltages
        crio.ocp_n_cam = ocp
        crio.ovp_n_cam = ovp

    except:

        pass

    # 81. Turn on the secondary power lines in N-CAM

    crio.set_n_cam_secondary_power_status(IntSwitch.ON)

    # 82. Check whether the secondary power lines are on

    assert crio.get_n_cam_secondary_power_status() == IntSwitch.ON

    # 83. Get the secondary power line voltage quality for N-CAM

    assert len(crio.get_n_cam_voltage_quality()) == 6

    for index in range(6):

        assert crio.get_n_cam_voltage_quality()[index] == 0

    # 84. Get the secondary power line current quality for N-CAM

    assert len(crio.get_n_cam_current_quality()) == 6

    for index in range(6):

        assert crio.get_n_cam_current_quality()[index] == 0

    # 85. Measure the voltage values in N-CAM

    assert len(crio.get_n_cam_voltage()) == 6

    if crio.is_simulator():

        for index in range(6):

            assert crio.get_n_cam_voltage()[index] == voltages[index]

    # 86. Measure the current values in N-CAM

    assert len(crio.get_n_cam_current()) == 6

    if crio.is_simulator():

        for index in range(6):

            assert crio.get_n_cam_current()[index] == currents[index]

    assert crio.get_led_status()["Standby"] == IntSwitch.OFF
    assert crio.get_led_status()["Selftest"] == IntSwitch.OFF
    assert crio.get_led_status()["FC_TVAC"] == IntSwitch.ON
    assert crio.get_led_status()["Alignment"] == IntSwitch.OFF

    assert crio.get_led_status()["N-CAM"] == IntSwitch.ON
    assert crio.get_led_status()["F-CAM"] == IntSwitch.OFF

    assert crio.get_led_status()["V_CCD"] == IntSwitch.ON
    assert crio.get_led_status()["V_CLK"] == IntSwitch.ON
    assert crio.get_led_status()["V_AN1"] == IntSwitch.ON
    assert crio.get_led_status()["V_AN2"] == IntSwitch.ON
    assert crio.get_led_status()["V_AN3"] == IntSwitch.ON
    assert crio.get_led_status()["V_DIG"] == IntSwitch.ON

    assert crio.get_led_status()["S_voltage_oor"] == IntSwitch.OFF
    assert crio.get_led_status()["S_current_oor"] == IntSwitch.OFF
    assert crio.get_led_status()["Sync_gf"] == IntSwitch.OFF

    assert crio.get_led_status()["Clk_50MHz"] == IntSwitch.OFF
    assert crio.get_led_status()["Clk_ccdread"] == IntSwitch.OFF
    assert crio.get_led_status()["Clk_heater"] == IntSwitch.OFF
    assert crio.get_led_status()["Clk_F_FEE_N"] == IntSwitch.OFF
    assert crio.get_led_status()["Clk_F_FEE_R"] == IntSwitch.OFF
    assert crio.get_led_status()["TestPort"] == IntSwitch.OFF

    awg1 = awg_array[0]
    awg2 = awg_array[1]
    awg1_cal = awg_cal_array[0]
    awg2_cal = awg_cal_array[1]

    for identifier in ["A", "B", "C", "D", "E"]:

        sync_data_string = awg2_cal.n_cam_sync_data[identifier]
        awg2_sync_data = SyncData(sync_data_string)

        # 13. Configure the AWG1 channel (Clk_50MHz)

        awg1.set_channel(1)

        # 14. Check the channel for AWG1

        assert awg1.get_channel() == 1

        # 15. Configure the waveform type

        awg1.set_waveform_type(Waveform.SQUARE)

        # 16. Configure the output load

        awg1.set_output_load(awg1_cal.output_load)

        # 17. Configure the amplitude

        awg1.set_amplitude(awg1_cal.amplitude)

        # 18. Configure the DC offset

        awg1.set_dc_offset(awg1_cal.dc_offset)

        # 19. Configure the duty cycle

        awg1.set_duty_cycle(awg1_cal.duty_cycle)

        # 20. Configure the frequency

        awg1.set_frequency(awg1_cal.frequency)

        # 21. Turn on the channel

        awg1.set_output_status(Switch.ON)

        # 22. Check that there are no execution errors

        assert awg1.execution_error_register() == 0

        # 23. Check that there are no query errors

        assert awg1.query_error_register() == 0

        # 24. Configure the AWG2 channel (Clk_ccdread)

        awg2.set_channel(1)

        # 25. Check the channel for AWG2

        assert awg2.get_channel() == 1

        # 26. Configure the waveform type

        awg2.set_waveform_type(Waveform.ARB)

        # 27. Configure the output load

        awg2.set_output_load(awg2_cal.output_load)

        # 28. Configure the amplitude

        awg2.set_amplitude(awg2_cal.amplitude)

        # 29. Configure the DC offset

        awg2.set_dc_offset(awg2_cal.dc_offset)

        # 30. Configure the frequency

        awg2.set_frequency(awg2_sync_data.frequency)

        # 31. Define ARB1

        awg2.define_arb_waveform(ARB.ARB1, f"CCDREAD{awg2_sync_data.id}", Switch.OFF)

        # 32. Load ARB1 #46000 [See AD5; Annex 5.1]

        awg2.load_arb1_data(awg2_sync_data.ccdread_arb_data)

        if not awg2.is_simulator():

            time.sleep(2)

        # 33. Check waveform configuration of ARB1

        arb_data = ArbData()
        arb_data.init_from_file(awg2_sync_data.ccdread_arb_data)

        assert awg2.get_arb1() == arb_data.string

        # 34. Check the definition of ARB1

        assert len(awg2.get_arb1_def()) == 3

        assert awg2.get_arb1_def()[0] == f"CCDREAD{awg2_sync_data.id}"
        assert awg2.get_arb1_def()[1] == Switch.OFF

        # 35. Set the output waveform with ARB1 data

        awg2.set_arb_waveform(ARB.ARB1)

        # 36. Turn on the channel

        awg2.set_output_status(Switch.ON)

        # 37. Configure the AWG2 channel (Clk_heater)

        awg2.set_channel(2)

        # 38. Check the channel for AWG2

        assert awg2.get_channel() == 2

        # 39. Configure the waveform type

        awg2.set_waveform_type(Waveform.ARB)

        # 40. Configure the output load

        awg2.set_output_load(awg2_cal.output_load)

        # 41. Configure the amplitude

        awg2.set_amplitude(awg2_cal.amplitude)

        # 42. Configure the DC offset

        awg2.set_dc_offset(awg2_cal.dc_offset)

        # 43. Configure the frequency

        awg2.set_frequency(awg2_sync_data.frequency)

        # 44. Define ARB2

        awg2.define_arb_waveform(ARB.ARB2, f"HEATER{awg2_sync_data.id}", Switch.OFF)

        # 45. Load ARB2 #46000 [See AD5; Annex 5.7]

        awg2.load_arb2_data(awg2_sync_data.heater_arb_data)

        if not awg2.is_simulator():

            time.sleep(2)

        # 46. Check waveform configuration of ARB2

        arb_data = ArbData()
        arb_data.init_from_file(awg2_sync_data.heater_arb_data)

        assert awg2.get_arb2() == arb_data.string

        # 47. Check the definition of ARB2

        assert len(awg2.get_arb2_def()) == 3

        assert awg2.get_arb2_def()[0] == f"HEATER{awg2_sync_data.id}"
        assert awg2.get_arb2_def()[1] == Switch.OFF
        assert awg2.get_arb2_def()[2] > 0

        # 48. Set the output waveform with ARB2 data

        awg2.set_arb_waveform(ARB.ARB2)

        # 49. Turn on the channel

        awg2.set_output_status(Switch.ON)

        # 50. Synchronise both channels

        awg2.align()

        # 51. Check that there are no execution errors

        assert awg2.execution_error_register() == 0

        # 52. Check that there are no query errors

        assert awg2.query_error_register() == 0

        # 53. Enable all clocks in N-CAM

        crio.set_n_cam_clock_status(IntSwitch.ON, IntSwitch.ON)

        # 54. Check that all clocks are enabled

        assert len(crio.get_n_cam_clock_status()) == 2

        assert crio.get_n_cam_clock_status()[0] == IntSwitch.ON
        assert crio.get_n_cam_clock_status()[1] == IntSwitch.ON

        # 55. Enable all SVM nominal clocks

        crio.set_svm_clock_status(IntSwitch.ON, IntSwitch.OFF, IntSwitch.ON, IntSwitch.OFF)

        # 56. Check that all nominal SVM clock are enabled

        assert len(crio.get_svm_clock_status()) == 4

        assert crio.get_svm_clock_status()[0] == IntSwitch.ON
        assert crio.get_svm_clock_status()[1] == IntSwitch.OFF
        assert crio.get_svm_clock_status()[2] == IntSwitch.ON
        assert crio.get_svm_clock_status()[3] == IntSwitch.OFF

        assert crio.get_led_status()["Standby"] == IntSwitch.OFF
        assert crio.get_led_status()["Selftest"] == IntSwitch.OFF
        assert crio.get_led_status()["FC_TVAC"] == IntSwitch.ON
        assert crio.get_led_status()["Alignment"] == IntSwitch.OFF

        assert crio.get_led_status()["N-CAM"] == IntSwitch.ON
        assert crio.get_led_status()["F-CAM"] == IntSwitch.OFF

        assert crio.get_led_status()["V_CCD"] == IntSwitch.ON
        assert crio.get_led_status()["V_CLK"] == IntSwitch.ON
        assert crio.get_led_status()["V_AN1"] == IntSwitch.ON
        assert crio.get_led_status()["V_AN2"] == IntSwitch.ON
        assert crio.get_led_status()["V_AN3"] == IntSwitch.ON
        assert crio.get_led_status()["V_DIG"] == IntSwitch.ON

        assert crio.get_led_status()["S_voltage_oor"] == IntSwitch.OFF
        assert crio.get_led_status()["S_current_oor"] == IntSwitch.OFF
        assert crio.get_led_status()["Sync_gf"] == IntSwitch.OFF

        assert crio.get_led_status()["Clk_50MHz"] == IntSwitch.ON
        assert crio.get_led_status()["Clk_ccdread"] == IntSwitch.ON
        assert crio.get_led_status()["Clk_heater"] == IntSwitch.ON
        assert crio.get_led_status()["Clk_F_FEE_N"] == IntSwitch.OFF
        assert crio.get_led_status()["Clk_F_FEE_R"] == IntSwitch.OFF
        assert crio.get_led_status()["TestPort"] == IntSwitch.OFF

        # 13. Disable all clocks in N-CAM

        crio.set_n_cam_clock_status(IntSwitch.OFF, IntSwitch.OFF)

        # 14. Check that all clocks are disabled

        assert len(crio.get_n_cam_clock_status()) == 2

        assert crio.get_n_cam_clock_status()[0] == IntSwitch.OFF
        assert crio.get_n_cam_clock_status()[1] == IntSwitch.OFF

        # 15. Disable all SVM nominal clocks

        crio.set_svm_clock_status(IntSwitch.OFF, IntSwitch.OFF, IntSwitch.OFF, IntSwitch.OFF)

        # 16. Check that all nominal SVM clock are disabled

        assert len(crio.get_svm_clock_status()) == 4

        for index in range(4):

            assert crio.get_svm_clock_status()[index] == IntSwitch.OFF

        # 17. Configure the channel for AWG2 (Clk_heater)

        awg2.set_channel(2)
        assert awg2.get_channel() == 2

        # 18. Turn off the channel

        awg2.set_output_status(Switch.OFF)
        assert awg2.get_output_status() == Switch.OFF

        # 19. Configure the channel for AWG2 (Clk_ccdread)

        awg2.set_channel(1)
        assert awg2.get_channel() == 1

        # 20. Turn off the channel

        awg2.set_output_status(Switch.OFF)
        assert awg2.get_output_status() == Switch.OFF

        # 21. Configure the channel for AWG1 (Clk_50MHz)

        awg1.set_channel(1)
        assert awg1.get_channel() == 1

        # 22. Turn off the channel

        awg1.set_output_status(Switch.OFF)
        assert awg1.get_output_status() == Switch.OFF

        assert crio.get_led_status()["Standby"] == IntSwitch.OFF
        assert crio.get_led_status()["Selftest"] == IntSwitch.OFF
        assert crio.get_led_status()["FC_TVAC"] == IntSwitch.ON
        assert crio.get_led_status()["Alignment"] == IntSwitch.OFF

        assert crio.get_led_status()["N-CAM"] == IntSwitch.ON
        assert crio.get_led_status()["F-CAM"] == IntSwitch.OFF

        assert crio.get_led_status()["V_CCD"] == IntSwitch.ON
        assert crio.get_led_status()["V_CLK"] == IntSwitch.ON
        assert crio.get_led_status()["V_AN1"] == IntSwitch.ON
        assert crio.get_led_status()["V_AN2"] == IntSwitch.ON
        assert crio.get_led_status()["V_AN3"] == IntSwitch.ON
        assert crio.get_led_status()["V_DIG"] == IntSwitch.ON

        assert crio.get_led_status()["S_voltage_oor"] == IntSwitch.OFF
        assert crio.get_led_status()["S_current_oor"] == IntSwitch.OFF
        assert crio.get_led_status()["Sync_gf"] == IntSwitch.OFF

        assert crio.get_led_status()["Clk_50MHz"] == IntSwitch.OFF
        assert crio.get_led_status()["Clk_ccdread"] == IntSwitch.OFF
        assert crio.get_led_status()["Clk_heater"] == IntSwitch.OFF
        assert crio.get_led_status()["Clk_F_FEE_N"] == IntSwitch.OFF
        assert crio.get_led_status()["Clk_F_FEE_R"] == IntSwitch.OFF
        assert crio.get_led_status()["TestPort"] == IntSwitch.OFF

    # 13. Turn off the secondary power lines in N-CAM

    crio.set_n_cam_secondary_power_status(IntSwitch.OFF)

    # 14. Check whether the secondary power lines are off

    assert crio.get_n_cam_secondary_power_status() == IntSwitch.OFF

    # 15. Measure the voltage values in N-CAM

    assert len(crio.get_n_cam_voltage()) == 6

    for index in range(6):

        assert crio.get_n_cam_voltage()[index] == 0

    # 16. Measure the current values in N-CAM

    assert len(crio.get_n_cam_current()) == 6

    for index in range(6):

        assert crio.get_n_cam_current()[index] == 0

    for psu in psu_array:

        psu.set_output_status(IntSwitch.OFF)
        assert psu.get_output_status() == IntSwitch.OFF

    crio.set_operating_mode(OperatingMode.STANDBY)
    assert crio.get_operating_mode() == OperatingMode.STANDBY

    assert crio.get_led_status()["Standby"] == IntSwitch.ON
    assert crio.get_led_status()["Selftest"] == IntSwitch.OFF
    assert crio.get_led_status()["FC_TVAC"] == IntSwitch.OFF
    assert crio.get_led_status()["Alignment"] == IntSwitch.OFF

    assert crio.get_led_status()["N-CAM"] == IntSwitch.OFF
    assert crio.get_led_status()["F-CAM"] == IntSwitch.OFF

    assert crio.get_led_status()["V_CCD"] == IntSwitch.OFF
    assert crio.get_led_status()["V_CLK"] == IntSwitch.OFF
    assert crio.get_led_status()["V_AN1"] == IntSwitch.OFF
    assert crio.get_led_status()["V_AN2"] == IntSwitch.OFF
    assert crio.get_led_status()["V_AN3"] == IntSwitch.OFF
    assert crio.get_led_status()["V_DIG"] == IntSwitch.OFF

    assert crio.get_led_status()["S_voltage_oor"] == IntSwitch.OFF
    assert crio.get_led_status()["S_current_oor"] == IntSwitch.OFF
    assert crio.get_led_status()["Sync_gf"] == IntSwitch.OFF

    assert crio.get_led_status()["Clk_50MHz"] == IntSwitch.OFF
    assert crio.get_led_status()["Clk_ccdread"] == IntSwitch.OFF
    assert crio.get_led_status()["Clk_heater"] == IntSwitch.OFF
    assert crio.get_led_status()["Clk_F_FEE_N"] == IntSwitch.OFF
    assert crio.get_led_status()["Clk_F_FEE_R"] == IntSwitch.OFF
    assert crio.get_led_status()["TestPort"] == IntSwitch.OFF


def test_f_cam(crio, psu_array, psu_cal_array, awg_array, awg_cal_array):

    crio_cal = SETUP.gse.aeu.crio.calibration

    # 1. Change the operating mode to "Functional & TVAC Operating Mode"

    crio.set_operating_mode(OperatingMode.FC_TVAC)

    # 2. Check the actual operating mode

    assert crio.get_operating_mode() == OperatingMode.FC_TVAC

    # 3. Configure the OCP for the F-CAM

    crio.set_f_cam_ocp(*crio_cal.f_cam_ocp)

    # 4. Check the OCP for the F-CAM

    assert len(crio.get_f_cam_ocp()) == 6

    for index in range(6):

        assert crio.get_f_cam_ocp()[index] == crio_cal.f_cam_ocp[index]

    # 5. Configure the OVP for the F-CAM

    crio.set_f_cam_ovp(*crio_cal.f_cam_ovp)

    # 6. Check the OVP for the F-CAM

    assert len(crio.get_f_cam_ovp()) == 6

    for index in range(6):

        assert crio.get_f_cam_ovp()[index] == crio_cal.f_cam_ovp[index]

    # 7. Configure the UVP for the F-CAM

    crio.set_f_cam_uvp(*crio_cal.f_cam_uvp)

    # 8. Check the UVP for the F-CAM

    assert len(crio.get_f_cam_uvp()) == 6

    for index in range(6):

        assert crio.get_f_cam_uvp()[index] == crio_cal.f_cam_uvp[index]

    voltages = np.array([])
    ovp = np.array([])
    currents = np.array([])
    ocp = np.array([])

    for index in range(6):

        psu = psu_array[index]
        psu_cal = psu_cal_array[index]

        psu.set_current(psu_cal.f_cam_current)
        currents = np.append(currents, psu_cal.f_cam_current)
        assert psu.get_current_config() == psu_cal.f_cam_current

        psu.set_ocp(psu_cal.f_cam_ocp)
        ocp = np.append(ocp, psu_cal.f_cam_ocp)
        assert psu.get_ocp() == psu_cal.f_cam_ocp

        psu.set_voltage(psu_cal.f_cam_voltage)
        voltages = np.append(voltages, psu_cal.f_cam_voltage)
        assert psu.get_voltage_config() == psu_cal.f_cam_voltage

        psu.set_ovp(psu_cal.f_cam_ovp)
        ovp = np.append(ovp, psu_cal.f_cam_ovp)
        assert psu.get_ovp() == psu_cal.f_cam_ovp

        psu.set_priority_mode(PriorityMode.CONSTANT_CURRENT)
        assert psu.get_priority_mode() == PriorityMode.CONSTANT_CURRENT

        psu.set_output_status(IntSwitch.ON)
        assert psu.get_output_status() == IntSwitch.ON

    try:

        crio.current_f_cam = currents
        crio.voltage_f_cam = voltages
        crio.ocp_f_cam = ocp
        crio.ovp_f_cam = ovp

    except:

        pass

    # 81. Turn on the secondary power lines in F-CAM

    crio.set_f_cam_secondary_power_status(IntSwitch.ON)

    # 82. Check whether the secondary power lines are on

    assert crio.get_f_cam_secondary_power_status() == IntSwitch.ON

    # 83. Get the secondary power line voltage quality for F-CAM

    assert len(crio.get_f_cam_voltage_quality()) == 6

    for index in range(6):

        assert crio.get_f_cam_voltage_quality()[index] == 0

    # 84. Get the secondary power line current quality for F-CAM

    assert len(crio.get_f_cam_current_quality()) == 6

    for index in range(6):

        assert crio.get_f_cam_current_quality()[index] == 0

    # 85. Measure the voltage values in F-CAM

    assert len(crio.get_f_cam_voltage()) == 6

    if crio.is_simulator():

        for index in range(6):

            assert crio.get_f_cam_voltage()[index] == voltages[index]

    # 86. Measure the current values in F-CAM

    assert len(crio.get_f_cam_current()) == 6

    if crio.is_simulator():

        for index in range(6):

            assert crio.get_f_cam_current()[index] == currents[index]

    assert crio.get_led_status()["Standby"] == IntSwitch.OFF
    assert crio.get_led_status()["Selftest"] == IntSwitch.OFF
    assert crio.get_led_status()["FC_TVAC"] == IntSwitch.ON
    assert crio.get_led_status()["Alignment"] == IntSwitch.OFF

    assert crio.get_led_status()["N-CAM"] == IntSwitch.OFF
    assert crio.get_led_status()["F-CAM"] == IntSwitch.ON

    assert crio.get_led_status()["V_CCD"] == IntSwitch.ON
    assert crio.get_led_status()["V_CLK"] == IntSwitch.ON
    assert crio.get_led_status()["V_AN1"] == IntSwitch.ON
    assert crio.get_led_status()["V_AN2"] == IntSwitch.ON
    assert crio.get_led_status()["V_AN3"] == IntSwitch.ON
    assert crio.get_led_status()["V_DIG"] == IntSwitch.ON

    assert crio.get_led_status()["S_voltage_oor"] == IntSwitch.OFF
    assert crio.get_led_status()["S_current_oor"] == IntSwitch.OFF
    assert crio.get_led_status()["Sync_gf"] == IntSwitch.OFF

    assert crio.get_led_status()["Clk_50MHz"] == IntSwitch.OFF
    assert crio.get_led_status()["Clk_ccdread"] == IntSwitch.OFF
    assert crio.get_led_status()["Clk_heater"] == IntSwitch.OFF
    assert crio.get_led_status()["Clk_F_FEE_N"] == IntSwitch.OFF
    assert crio.get_led_status()["Clk_F_FEE_R"] == IntSwitch.OFF
    assert crio.get_led_status()["TestPort"] == IntSwitch.OFF

    awg1 = awg_array[0]
    awg2 = awg_array[1]
    awg1_cal = SETUP.gse.aeu.awg1.calibration
    awg2_cal = SETUP.gse.aeu.awg2.calibration

    sync_data_string = awg2_cal.f_cam_sync_data["F"]
    awg2_sync_data = SyncData(sync_data_string)

    # 13. Configure the AWG1 channel (Clk_50MHz)

    awg1.set_channel(1)

    # 14. Check the channel for AWG1

    assert awg1.get_channel() == 1

    # 15. Configure the waveform type

    awg1.set_waveform_type(Waveform.SQUARE)

    # 16. Configure the output load

    awg1.set_output_load(awg1_cal.output_load)

    # 17. Configure the amplitude

    awg1.set_amplitude(awg1_cal.amplitude)

    # 18. Configure the DC offset

    awg1.set_dc_offset(awg1_cal.dc_offset)

    # 19. Configure the duty cycle

    awg1.set_duty_cycle(awg1_cal.duty_cycle)

    # 20. Configure the frequency

    awg1.set_frequency(awg1_cal.frequency)

    # 21. Turn on the channel

    awg1.set_output_status(Switch.ON)

    # 22. Check that there are no execution errors

    assert awg1.execution_error_register() == 0

    # 23. Check that there are no query errors

    assert awg1.query_error_register() == 0

    # 24. Configure the AWG2 channel (Clk_ccdread)

    awg2.set_channel(1)

    # 25. Check the channel for AWG2

    assert awg2.get_channel() == 1

    # 26. Configure the waveform type

    awg2.set_waveform_type(Waveform.ARB)

    # 27. Configure the output load

    awg2.set_output_load(awg2_cal.output_load)

    # 28. Configure the amplitude

    awg2.set_amplitude(awg2_cal.amplitude)

    # 29. Configure the DC offset

    awg2.set_dc_offset(awg2_cal.dc_offset)

    # 30. Configure the frequency

    awg2.set_frequency(awg2_sync_data.frequency)

    # 31. Define ARB1

    awg2.define_arb_waveform(ARB.ARB1, f"{awg2_sync_data.id}CCDREAD", Switch.OFF)

    # 32. Load ARB1 #46000 [See AD5; Annex 5.6]

    awg2.load_arb1_data(awg2_sync_data.ccdread_arb_data)

    if not awg2.is_simulator():

        time.sleep(2)

    # 33. Check waveform configuration of ARB1

    arb_data = ArbData()
    arb_data.init_from_file(awg2_sync_data.ccdread_arb_data)

    assert awg2.get_arb1() == arb_data.string

    # 34. Check the definition of ARB1

    assert len(awg2.get_arb1_def()) == 3

    assert awg2.get_arb1_def()[0] == f"{awg2_sync_data.id}CCDREAD"
    assert awg2.get_arb1_def()[1] == Switch.OFF
    assert awg2.get_arb1_def()[2] == 3000

    # 35. Set the output waveform with ARB1 data

    awg2.set_arb_waveform(ARB.ARB1)

    # 36. Turn on the channel

    awg2.set_output_status(Switch.ON)

    # 37. Configure the AWG2 channel (Clk_heater)

    awg2.set_channel(2)

    # 38. Check the channel for AWG2

    assert awg2.get_channel() == 2

    # 39. Configure the waveform type

    awg2.set_waveform_type(Waveform.ARB)

    # 40. Configure the output load

    awg2.set_output_load(awg2_cal.output_load)

    # 41. Configure the amplitude

    awg2.set_amplitude(awg2_cal.amplitude)

    # 42. Configure the DC offset

    awg2.set_dc_offset(awg2_cal.dc_offset)

    # 43. Configure the frequency

    awg2.set_frequency(awg2_sync_data.frequency)

    # 44. Define ARB2

    awg2.define_arb_waveform(ARB.ARB2, f"{awg2_sync_data.id}HEATER", Switch.OFF)

    # 45. Load ARB2 #46000 [See AD5; Annex 5.12]

    awg2.load_arb2_data(awg2_sync_data.heater_arb_data)

    if not awg2.is_simulator():

        time.sleep(2)

    # 46. Check waveform configuration of ARB2

    arb_data = ArbData()
    arb_data.init_from_file(awg2_sync_data.heater_arb_data)

    assert awg2.get_arb2() == arb_data.string

    # 47. Check the definition of ARB2

    assert len(awg2.get_arb2_def()) == 3

    assert awg2.get_arb2_def()[0] == f"{awg2_sync_data.id}HEATER"
    assert awg2.get_arb2_def()[1] == Switch.OFF
    assert awg2.get_arb2_def()[2] == 3000

    # 48. Set the output waveform with ARB2 data

    awg2.set_arb_waveform(ARB.ARB2)

    # 49. Turn on the channel

    awg2.set_output_status(Switch.ON)

    # 50. Synchronise both channels

    awg2.align()

    # 51. Check that there are no execution errors

    assert awg2.execution_error_register() == 0

    # 52. Check that there are no query errors

    assert awg2.query_error_register() == 0

    # 53. Enable all clocks in F-CAM

    crio.set_f_cam_clock_status(IntSwitch.ON, IntSwitch.OFF, IntSwitch.ON, IntSwitch.OFF)

    # 54. Check that all clocks are enabled

    assert len(crio.get_f_cam_clock_status()) == 4

    assert crio.get_f_cam_clock_status()[0] == IntSwitch.ON
    assert crio.get_f_cam_clock_status()[1] == IntSwitch.OFF
    assert crio.get_f_cam_clock_status()[2] == IntSwitch.ON
    assert crio.get_f_cam_clock_status()[3] == IntSwitch.OFF

    # 55. Enable all SVM nominal clocks

    crio.set_svm_clock_status(IntSwitch.ON, IntSwitch.OFF, IntSwitch.ON, IntSwitch.OFF)

    # 56. Check that all nominal SVM clock are enabled

    assert len(crio.get_svm_clock_status()) == 4

    assert crio.get_svm_clock_status()[0] == IntSwitch.ON
    assert crio.get_svm_clock_status()[1] == IntSwitch.OFF
    assert crio.get_svm_clock_status()[2] == IntSwitch.ON
    assert crio.get_svm_clock_status()[3] == IntSwitch.OFF

    assert crio.get_led_status()["Standby"] == IntSwitch.OFF
    assert crio.get_led_status()["Selftest"] == IntSwitch.OFF
    assert crio.get_led_status()["FC_TVAC"] == IntSwitch.ON
    assert crio.get_led_status()["Alignment"] == IntSwitch.OFF

    assert crio.get_led_status()["N-CAM"] == IntSwitch.OFF
    assert crio.get_led_status()["F-CAM"] == IntSwitch.ON

    assert crio.get_led_status()["V_CCD"] == IntSwitch.ON
    assert crio.get_led_status()["V_CLK"] == IntSwitch.ON
    assert crio.get_led_status()["V_AN1"] == IntSwitch.ON
    assert crio.get_led_status()["V_AN2"] == IntSwitch.ON
    assert crio.get_led_status()["V_AN3"] == IntSwitch.ON
    assert crio.get_led_status()["V_DIG"] == IntSwitch.ON

    assert crio.get_led_status()["S_voltage_oor"] == IntSwitch.OFF
    assert crio.get_led_status()["S_current_oor"] == IntSwitch.OFF
    assert crio.get_led_status()["Sync_gf"] == IntSwitch.OFF

    assert crio.get_led_status()["Clk_50MHz"] == IntSwitch.ON
    assert crio.get_led_status()["Clk_ccdread"] == IntSwitch.ON
    assert crio.get_led_status()["Clk_heater"] == IntSwitch.ON
    assert crio.get_led_status()["Clk_F_FEE_N"] == IntSwitch.ON
    assert crio.get_led_status()["Clk_F_FEE_R"] == IntSwitch.OFF
    assert crio.get_led_status()["TestPort"] == IntSwitch.OFF

    # 13. Turn off the secondary power lines in F-CAM

    crio.set_f_cam_secondary_power_status(IntSwitch.OFF)

    # 14. Check whether the secondary power lines are off

    assert crio.get_f_cam_secondary_power_status() == IntSwitch.OFF

    # 15. Measure the voltage values in F-CAM

    assert len(crio.get_f_cam_voltage()) == 6

    for index in range(6):

        assert crio.get_f_cam_voltage()[index] == 0

    # 16. Measure the current values in F-CAM

    assert len(crio.get_f_cam_current()) == 6

    for index in range(6):

        assert crio.get_f_cam_current()[index] == 0

    for psu in psu_array:

        psu.set_output_status(IntSwitch.OFF)
        assert psu.get_output_status() == IntSwitch.OFF

    crio.set_operating_mode(OperatingMode.STANDBY)
    assert crio.get_operating_mode() == OperatingMode.STANDBY

    assert crio.get_led_status()["Standby"] == IntSwitch.ON
    assert crio.get_led_status()["Selftest"] == IntSwitch.OFF
    assert crio.get_led_status()["FC_TVAC"] == IntSwitch.OFF
    assert crio.get_led_status()["Alignment"] == IntSwitch.OFF

    assert crio.get_led_status()["N-CAM"] == IntSwitch.OFF
    assert crio.get_led_status()["F-CAM"] == IntSwitch.OFF

    assert crio.get_led_status()["V_CCD"] == IntSwitch.OFF
    assert crio.get_led_status()["V_CLK"] == IntSwitch.OFF
    assert crio.get_led_status()["V_AN1"] == IntSwitch.OFF
    assert crio.get_led_status()["V_AN2"] == IntSwitch.OFF
    assert crio.get_led_status()["V_AN3"] == IntSwitch.OFF
    assert crio.get_led_status()["V_DIG"] == IntSwitch.OFF

    assert crio.get_led_status()["S_voltage_oor"] == IntSwitch.OFF
    assert crio.get_led_status()["S_current_oor"] == IntSwitch.OFF
    assert crio.get_led_status()["Sync_gf"] == IntSwitch.OFF

    assert crio.get_led_status()["Clk_50MHz"] == IntSwitch.OFF
    assert crio.get_led_status()["Clk_ccdread"] == IntSwitch.OFF
    assert crio.get_led_status()["Clk_heater"] == IntSwitch.OFF
    assert crio.get_led_status()["Clk_F_FEE_N"] == IntSwitch.OFF
    assert crio.get_led_status()["Clk_F_FEE_R"] == IntSwitch.OFF
    assert crio.get_led_status()["TestPort"] == IntSwitch.OFF
