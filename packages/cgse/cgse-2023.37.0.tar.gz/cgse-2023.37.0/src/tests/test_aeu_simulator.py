from pathlib import Path

from egse.aeu.aeu import CRIOSimulator, LoopBack, IntSwitch, OperatingMode, PSUSimulator, PriorityMode, AWGSimulator, \
    Waveform, Switch, ARB, ArbDataFile, ArbData, CounterSource, CounterType, SyncData
from numpy import sign

from egse.resource import get_resource, add_resource_id
from egse.setup import Setup
import numpy as np

add_resource_id("testdata", str(Path(__file__).parent) + "/data")
SETUP = Setup.from_yaml_file(get_resource(f":/testdata/conf/SETUP_CSL_00010_210308_083016.yaml"))

##########
# AEU cRIO
##########


def test_crio_is_simulator():

    crio = CRIOSimulator()
    assert crio.is_simulator()


def test_crio_get_id():

    crio = CRIOSimulator()
    manufacturer, model, serial_number, build_version = crio.get_id()

    assert manufacturer == "National Instruments"
    assert model == "cRIO-9063"
    assert serial_number == "E7CB6B"
    assert build_version == 01.00


def test_crio_reset():

    pass


def test_crio_clear_error_queue():

    pass


def test_crio_n_cam_current():

    crio = CRIOSimulator()

    # Secondary power on

    crio.set_n_cam_secondary_power_status(IntSwitch.ON)
    n_cam_current = crio.get_n_cam_current()
    expected_current_n_cam = (0.105, 0.208, 0.190, 0.058, -0.224, 0.553)

    assert len(n_cam_current) == len(expected_current_n_cam)

    for index in range(len(n_cam_current)):

        assert n_cam_current[index] == expected_current_n_cam[index]

    # Secondary power off

    crio.set_n_cam_secondary_power_status(IntSwitch.OFF)

    n_cam_current = crio.get_n_cam_current()

    assert len(n_cam_current) == len(expected_current_n_cam)

    for index in range(len(n_cam_current)):

        assert n_cam_current[index] == 0


def test_crio_n_cam_ocp():

    crio = CRIOSimulator()
    n_cam_ocp = SETUP.gse.aeu.crio.calibration.n_cam_ocp
    crio.set_n_cam_ocp(*n_cam_ocp)
    ocp_ccd, ocp_clk, ocp_an1, ocp_an2, ocp_an3, ocp_dig = crio.get_n_cam_ocp()

    assert ocp_ccd == n_cam_ocp[0]
    assert ocp_clk == n_cam_ocp[1]
    assert ocp_an1 == n_cam_ocp[2]
    assert ocp_an2 == n_cam_ocp[3]
    assert ocp_an3 == n_cam_ocp[4]
    assert ocp_dig == n_cam_ocp[5]


def test_crio_n_cam_voltage():

    crio = CRIOSimulator()

    # Secondary power on

    crio.set_n_cam_secondary_power_status(IntSwitch.ON)
    n_cam_voltage = crio.get_n_cam_voltage()
    expected_voltage_n_cam = (34.70, 16.05, 6.65, 6.65, -6.65, 4.55)

    assert len(n_cam_voltage) == len(expected_voltage_n_cam)

    for index in range(len(n_cam_voltage)):

        assert n_cam_voltage[index] == expected_voltage_n_cam[index]

    # Secondary power off

    crio.set_n_cam_secondary_power_status(IntSwitch.OFF)
    n_cam_voltage = crio.get_n_cam_voltage()

    assert len(n_cam_voltage) == len(expected_voltage_n_cam)

    for index in range(len(n_cam_voltage)):

        assert n_cam_voltage[index] == 0


def test_crio_n_cam_uvp():

    crio = CRIOSimulator()
    n_cam_uvp = SETUP.gse.aeu.crio.calibration.n_cam_uvp
    crio.set_n_cam_uvp(*n_cam_uvp)
    uvp_ccd, uvp_clk, uvp_an1, uvp_an2, uvp_an3, uvp_dig = crio.get_n_cam_uvp()

    assert uvp_ccd == n_cam_uvp[0]
    assert uvp_clk == n_cam_uvp[1]
    assert uvp_an1 == n_cam_uvp[2]
    assert uvp_an2 == n_cam_uvp[3]
    assert uvp_an3 == n_cam_uvp[4]
    assert uvp_dig == n_cam_uvp[5]


def test_crio_n_cam_ovp():

    crio = CRIOSimulator()
    n_cam_ovp = SETUP.gse.aeu.crio.calibration.n_cam_ovp
    crio.set_n_cam_ovp(*n_cam_ovp)
    ovp_ccd, ovp_clk, ovp_an1, ovp_an2, ovp_an3, ovp_dig = crio.get_n_cam_ovp()

    assert ovp_ccd == n_cam_ovp[0]
    assert ovp_clk == n_cam_ovp[1]
    assert ovp_an1 == n_cam_ovp[2]
    assert ovp_an2 == n_cam_ovp[3]
    assert ovp_an3 == n_cam_ovp[4]
    assert ovp_dig == n_cam_ovp[5]


def test_crio_f_cam_current():
    crio = CRIOSimulator()

    # Secondary power on

    crio.set_f_cam_secondary_power_status(IntSwitch.ON)
    f_cam_current = crio.get_f_cam_current()
    expected_current_f_cam = (0.164, 0.708, 0.511, 1.400, -0.171, 2.379)

    assert len(f_cam_current) == len(expected_current_f_cam)

    for index in range(len(f_cam_current)):

        assert f_cam_current[index] == expected_current_f_cam[index]

    # Secondary power off

    crio.set_f_cam_secondary_power_status(IntSwitch.OFF)
    f_cam_current = crio.get_f_cam_current()

    assert len(f_cam_current) == len(expected_current_f_cam)

    for index in range(len(f_cam_current)):

        assert f_cam_current[index] == 0


def test_crio_f_cam_ocp():

    crio = CRIOSimulator()
    f_cam_ocp = SETUP.gse.aeu.crio.calibration.n_cam_ocp
    crio.set_f_cam_ocp(*f_cam_ocp)
    ocp_ccd, ocp_clk, ocp_an1, ocp_an2, ocp_an3, ocp_dig = crio.get_f_cam_ocp()

    assert ocp_ccd == f_cam_ocp[0]
    assert ocp_clk == f_cam_ocp[1]
    assert ocp_an1 == f_cam_ocp[2]
    assert ocp_an2 == f_cam_ocp[3]
    assert ocp_an3 == f_cam_ocp[4]
    assert ocp_dig == f_cam_ocp[5]


def test_crio_f_cam_voltage():

    crio = CRIOSimulator()

    # Secondary power on

    crio.set_f_cam_secondary_power_status(IntSwitch.ON)
    expected_voltage_f_cam = (31.6, 16.2, 7.7, 5.4, -7.6, 5.3)
    f_cam_voltage = crio.get_f_cam_voltage()

    assert len(f_cam_voltage) == len(expected_voltage_f_cam)

    for index in range(len(f_cam_voltage)):

        assert f_cam_voltage[index] == expected_voltage_f_cam[index]

    # Secondary power off

    crio.set_f_cam_secondary_power_status(IntSwitch.OFF)
    f_cam_voltage = crio.get_f_cam_voltage()

    assert len(f_cam_voltage) == len(expected_voltage_f_cam)

    for index in range(len(f_cam_voltage)):

        assert f_cam_voltage[index] == 0


def test_crio_f_cam_uvp():

    crio = CRIOSimulator()
    f_cam_uvp = SETUP.gse.aeu.crio.calibration.n_cam_uvp
    crio.set_f_cam_uvp(*f_cam_uvp)
    uvp_ccd, uvp_clk, uvp_an1, uvp_an2, uvp_an3, uvp_dig = crio.get_f_cam_uvp()

    assert uvp_ccd == f_cam_uvp[0]
    assert uvp_clk == f_cam_uvp[1]
    assert uvp_an1 == f_cam_uvp[2]
    assert uvp_an2 == f_cam_uvp[3]
    assert uvp_an3 == f_cam_uvp[4]
    assert uvp_dig == f_cam_uvp[5]


def test_crio_f_cam_ovp():

    crio = CRIOSimulator()
    f_cam_ovp = SETUP.gse.aeu.crio.calibration.n_cam_ovp
    crio.set_f_cam_ovp(*f_cam_ovp)
    ovp_ccd, ovp_clk, ovp_an1, ovp_an2, ovp_an3, ovp_dig = crio.get_f_cam_ovp()

    assert ovp_ccd == f_cam_ovp[0]
    assert ovp_clk == f_cam_ovp[1]
    assert ovp_an1 == f_cam_ovp[2]
    assert ovp_an2 == f_cam_ovp[3]
    assert ovp_an3 == f_cam_ovp[4]
    assert ovp_dig == f_cam_ovp[5]


def test_crio_loopback_option():

    crio = CRIOSimulator()

    for loopback_option in LoopBack:

        crio.set_loopback_option(loopback_option)
        assert crio.get_loopback_option() == loopback_option


def test_crio_n_cam_secondary_power_status():

    crio = CRIOSimulator()

    for secondary_power_status in IntSwitch:

        crio.set_n_cam_secondary_power_status(secondary_power_status)
        assert crio.get_n_cam_secondary_power_status() == secondary_power_status


def test_crio_f_cam_secondary_power_status():

    crio = CRIOSimulator()

    for secondary_power_status in IntSwitch:

        crio.set_f_cam_secondary_power_status(secondary_power_status)
        assert crio.get_f_cam_secondary_power_status() == secondary_power_status


def test_crio_n_cam_voltage_quality():

    crio = CRIOSimulator()
    crio.set_n_cam_secondary_power_status(IntSwitch.ON)
    n_cam_voltage = crio.get_n_cam_voltage()

    # OVP detected

    bad_n_cam_ovp = list(n_cam_voltage)

    for index in range(6):

        bad_n_cam_ovp[index] = sign(n_cam_voltage[index]) * (abs(bad_n_cam_ovp[index]) - 1)

    crio.set_n_cam_ovp(*bad_n_cam_ovp)
    quality = crio.get_n_cam_voltage_quality()

    assert len(quality) == 6

    for index in range(1):

        assert quality[index] == 1

    # Inside of range

    crio.set_n_cam_ovp(*n_cam_voltage)
    quality = crio.get_n_cam_voltage_quality()

    assert len(quality) == 6

    for index in range(6):

        assert quality[index] == 0

    # UVP detected

    bad_n_cam_uvp = list(n_cam_voltage)

    for index in range(6):

        bad_n_cam_uvp[index] = sign(n_cam_voltage[index]) * (abs(bad_n_cam_uvp[index]) + 1)

    crio.set_n_cam_uvp(*bad_n_cam_uvp)
    quality = crio.get_n_cam_voltage_quality()

    assert len(quality) == 6

    for index in range(6):

        assert quality[index] == 2


def test_crio_n_cam_current_quality():

    crio = CRIOSimulator()
    crio.set_n_cam_secondary_power_status(IntSwitch.ON)
    n_cam_current = crio.get_n_cam_current()

    # OCP detected

    bad_n_cam_ocp = list(n_cam_current)

    for index in range(6):

        bad_n_cam_ocp[index] = n_cam_current[index] - 1

    crio.set_n_cam_ocp(*bad_n_cam_ocp)
    quality = crio.get_n_cam_current_quality()

    assert len(quality) == 6

    for index in range(6):

        assert quality[index] == 1

    # Inside of range

    crio.set_n_cam_ocp(*n_cam_current)
    quality = crio.get_n_cam_current_quality()

    assert len(quality) == 6

    for index in range(6):

        quality[index] == 0


def test_crio_f_cam_voltage_quality():

    crio = CRIOSimulator()
    crio.set_f_cam_secondary_power_status(IntSwitch.ON)
    f_cam_voltage = crio.get_f_cam_voltage()

    # OVP detected

    bad_f_cam_ovp = list(f_cam_voltage)

    for index in range(6):

        bad_f_cam_ovp[index] = sign(f_cam_voltage[index]) * (abs(f_cam_voltage[index]) - 1)

    crio.set_f_cam_ovp(*bad_f_cam_ovp)
    quality = crio.get_f_cam_voltage_quality()

    assert len(quality) == 6

    for index in range(1):

        assert quality[index] == 1

    # Inside of range

    crio.set_f_cam_ovp(*f_cam_voltage)
    quality = crio.get_f_cam_voltage_quality()

    assert len(quality) == 6

    for index in range(6):

        assert quality[index] == 0

    # UVP detected

    bad_f_cam_uvp = list(f_cam_voltage)

    for index in range(6):

        bad_f_cam_uvp[index] = sign(f_cam_voltage[index]) * (abs(bad_f_cam_uvp[index]) + 1)

    crio.set_f_cam_uvp(*bad_f_cam_uvp)
    quality = crio.get_f_cam_voltage_quality()

    assert len(quality) == 6

    for index in range(6):

        assert quality[index] == 2


def test_crio_f_cam_current_quality():

    crio = CRIOSimulator()
    crio.set_f_cam_secondary_power_status(IntSwitch.ON)
    f_cam_current = crio.get_f_cam_current()

    # OCP detected

    bad_f_cam_ocp = list(f_cam_current)
    for index in range(6):
        bad_f_cam_ocp[index] = f_cam_current[index] - 1

    crio.set_f_cam_ocp(*bad_f_cam_ocp)
    quality = crio.get_f_cam_current_quality()

    assert len(quality) == 6

    for index in range(6):

        assert quality[index] == 1

    # Inside of range

    crio.set_f_cam_ocp(*f_cam_current)
    quality = crio.get_f_cam_current_quality()

    assert len(quality) == 6

    for index in range(6):

        quality[index] == 0


def test_crio_n_cam_clock_status():

    crio = CRIOSimulator()

    crio.set_f_cam_secondary_power_status(IntSwitch.OFF)

    for secondary_power_status in IntSwitch:

        crio.set_n_cam_secondary_power_status(secondary_power_status)

        for clk_50mhz in IntSwitch:

            for clk_ccdread in IntSwitch:

                crio.set_n_cam_clock_status(clk_50mhz, clk_ccdread)

                if secondary_power_status == IntSwitch.ON:

                    assert crio.get_n_cam_clock_status()[0] == clk_50mhz
                    assert crio.get_n_cam_clock_status()[1] == clk_ccdread


def test_crio_f_cam_clock_status():

    crio = CRIOSimulator()

    crio.set_n_cam_secondary_power_status(IntSwitch.OFF)

    for secondary_power_status in IntSwitch:

        crio.set_f_cam_secondary_power_status(secondary_power_status)

        for clk_50mhz_nom in IntSwitch:

            for clk_50mhz_red in IntSwitch:

                for clk_ccdread_nom in IntSwitch:

                    for clk_ccdread_red in IntSwitch:

                        crio.set_f_cam_clock_status(clk_50mhz_nom, clk_50mhz_red, clk_ccdread_nom, clk_ccdread_red)

                        if secondary_power_status == IntSwitch.ON:

                            assert crio.get_f_cam_clock_status()[0] == clk_50mhz_nom
                            assert crio.get_f_cam_clock_status()[1] == clk_50mhz_red
                            assert crio.get_f_cam_clock_status()[2] == clk_ccdread_nom
                            assert crio.get_f_cam_clock_status()[3] == clk_ccdread_red

                        else:

                            for index in range(4):

                                assert crio.get_f_cam_clock_status()[index] == IntSwitch.OFF


def test_crio_svm_clock_status():

    crio = CRIOSimulator()

    crio.set_f_cam_secondary_power_status(IntSwitch.OFF)

    for secondary_power_output in IntSwitch:

        crio.set_n_cam_secondary_power_status(secondary_power_output)

        for clk_50mhz_nom in IntSwitch:

            for clk_50mhz_red in IntSwitch:

                for clk_heater_nom in IntSwitch:

                    for clk_heater_red in IntSwitch:

                        crio.set_svm_clock_status(clk_50mhz_nom, clk_50mhz_red, clk_heater_nom, clk_heater_red)

                        if secondary_power_output == IntSwitch.ON:

                            assert crio.get_svm_clock_status()[0] == clk_50mhz_nom
                            assert crio.get_svm_clock_status()[1] == clk_50mhz_red
                            assert crio.get_svm_clock_status()[2] == clk_heater_nom
                            assert crio.get_svm_clock_status()[3] == clk_heater_red

                        else:

                            for index in range(4):

                                assert crio.get_svm_clock_status()[index] == IntSwitch.OFF

    crio.set_n_cam_secondary_power_status(IntSwitch.OFF)

    for secondary_power_output in IntSwitch:

        crio.set_f_cam_secondary_power_status(secondary_power_output)

        for clk_50mhz_nom in IntSwitch:

            for clk_50mhz_red in IntSwitch:

                for clk_heater_nom in IntSwitch:

                    for clk_heater_red in IntSwitch:

                        crio.set_svm_clock_status(clk_50mhz_nom, clk_50mhz_red, clk_heater_nom, clk_heater_red)

                        if secondary_power_output:

                            assert crio.get_svm_clock_status()[0] == clk_50mhz_nom
                            assert crio.get_svm_clock_status()[1] == clk_50mhz_red
                            assert crio.get_svm_clock_status()[2] == clk_heater_nom
                            assert crio.get_svm_clock_status()[3] == clk_heater_red

    crio.set_n_cam_secondary_power_status(IntSwitch.OFF)
    crio.set_f_cam_secondary_power_status(IntSwitch.OFF)

    for clk_50mhz_nom in IntSwitch:

        for clk_50mhz_red in IntSwitch:

            for clk_heater_nom in IntSwitch:

                for clk_heater_red in IntSwitch:

                    crio.set_svm_clock_status(clk_50mhz_nom, clk_50mhz_red, clk_heater_nom, clk_heater_red)

                    for index in range(4):

                        assert crio.get_svm_clock_status()[index] == IntSwitch.OFF


def test_crio_led_status():

    crio = CRIOSimulator()

    # EGSE mode

    crio.set_operating_mode(OperatingMode.STANDBY)
    led_status = crio.get_led_status()

    assert led_status["Standby"] == 1
    assert led_status["Selftest"] == 0
    assert led_status["FC_TVAC"] == 0
    assert led_status["Alignment"] == 0

    crio.set_operating_mode(OperatingMode.SELFTEST)
    led_status = crio.get_led_status()

    assert led_status["Standby"] == 0
    assert led_status["Selftest"] == 1
    assert led_status["FC_TVAC"] == 0
    assert led_status["Alignment"] == 0

    crio.set_operating_mode(OperatingMode.FC_TVAC)
    led_status = crio.get_led_status()

    assert led_status["Standby"] == 0
    assert led_status["Selftest"] == 0
    assert led_status["FC_TVAC"] == 1
    assert led_status["Alignment"] == 0

    crio.set_operating_mode(OperatingMode.ALIGNMENT)
    led_status = crio.get_led_status()

    assert led_status["Standby"] == 0
    assert led_status["Selftest"] == 0
    assert led_status["FC_TVAC"] == 0
    assert led_status["Alignment"] == 1

    # Camera selection + Power lines

    crio.set_n_cam_secondary_power_status(IntSwitch.ON)
    crio.set_f_cam_secondary_power_status(IntSwitch.OFF)
    led_status = crio.get_led_status()

    assert led_status["N-CAM"] == 1
    assert led_status["F-CAM"] == 0

    assert led_status["V_CCD"] == 1
    assert led_status["V_CLK"] == 1
    assert led_status["V_AN1"] == 1
    assert led_status["V_AN2"] == 1
    assert led_status["V_AN3"] == 1
    assert led_status["V_DIG"] == 1

    crio.set_n_cam_secondary_power_status(IntSwitch.OFF)
    crio.set_f_cam_secondary_power_status(IntSwitch.ON)
    led_status = crio.get_led_status()

    assert led_status["N-CAM"] == 0
    assert led_status["F-CAM"] == 1

    assert led_status["V_CCD"] == 1
    assert led_status["V_CLK"] == 1
    assert led_status["V_AN1"] == 1
    assert led_status["V_AN2"] == 1
    assert led_status["V_AN3"] == 1
    assert led_status["V_DIG"] == 1

    crio.set_n_cam_secondary_power_status(IntSwitch.OFF)
    crio.set_f_cam_secondary_power_status(IntSwitch.OFF)
    led_status = crio.get_led_status()

    assert led_status["N-CAM"] == 0
    assert led_status["F-CAM"] == 0

    assert led_status["V_CCD"] == 0
    assert led_status["V_CLK"] == 0
    assert led_status["V_AN1"] == 0
    assert led_status["V_AN2"] == 0
    assert led_status["V_AN3"] == 0
    assert led_status["V_DIG"] == 0

    # Error detection

    assert led_status["S_voltage_oor"] == 0
    assert led_status["S_current_oor"] == 0
    assert led_status["Sync_gf"] == 0

    # Clk signals selection

    crio.set_f_cam_secondary_power_status(IntSwitch.OFF)

    for secondary_output_status in [IntSwitch.ON, IntSwitch.OFF]:

        crio.set_n_cam_secondary_power_status(secondary_output_status)

        for clk_n_50mhz in [IntSwitch.ON, IntSwitch.OFF]:

            for clk_n_ccdread in [IntSwitch.ON, IntSwitch.OFF]:

                crio.set_n_cam_clock_status(clk_n_50mhz, clk_n_ccdread)

                for clk_tcs_50mhz_nom in [IntSwitch.ON, IntSwitch.OFF]:

                    for clk_tcs_50mhz_red in [IntSwitch.ON, IntSwitch.OFF]:

                        for clk_heater_nom in [IntSwitch.ON, IntSwitch.OFF]:

                            for clk_heater_red in [IntSwitch.ON, IntSwitch.OFF]:

                                crio.set_svm_clock_status(clk_tcs_50mhz_nom, clk_tcs_50mhz_red, clk_heater_nom,
                                                          clk_heater_red)
                                led_status = crio.get_led_status()

                                if secondary_output_status == IntSwitch.ON:

                                    if clk_n_50mhz == IntSwitch.ON or clk_tcs_50mhz_nom == IntSwitch.ON or \
                                            clk_tcs_50mhz_red == IntSwitch.ON:

                                        led_status["Clk_50MHz"] == IntSwitch.ON

                                    else:

                                        led_status["Clk_50MHz"] == IntSwitch.OFF

                                    assert led_status["Clk_ccdread"] == clk_n_ccdread

                                    if clk_heater_nom == IntSwitch.ON or clk_heater_red == IntSwitch.ON:

                                        assert led_status["Clk_heater"] == IntSwitch.ON

                                    else:

                                        assert led_status["Clk_heater"] == IntSwitch.OFF

                                else:

                                    assert led_status["Clk_50MHz"] == IntSwitch.OFF
                                    assert led_status["Clk_ccdread"] == IntSwitch.OFF
                                    assert led_status["Clk_heater"] == IntSwitch.OFF

                                assert led_status["Clk_F_FEE_N"] == IntSwitch.OFF
                                assert led_status["Clk_F_FEE_R"] == IntSwitch.OFF

    crio.set_n_cam_secondary_power_status(IntSwitch.OFF)

    for secondary_output_status in [IntSwitch.ON, IntSwitch.OFF]:

        crio.set_f_cam_secondary_power_status(secondary_output_status)

        for clk_f_50mhz_nom in [IntSwitch.ON, IntSwitch.OFF]:

            for clk_f_50mhz_red in [IntSwitch.ON, IntSwitch.OFF]:

                for clk_f_ccdread_nom in [IntSwitch.ON, IntSwitch.OFF]:

                    for clk_f_ccdread_red in [IntSwitch.ON, IntSwitch.OFF]:

                        crio.set_f_cam_clock_status(clk_f_50mhz_nom, clk_f_50mhz_red, clk_f_ccdread_nom, clk_f_ccdread_red)

                        for clk_tcs_50mhz_nom in [IntSwitch.ON, IntSwitch.OFF]:

                            for clk_tcs_50mhz_red in [IntSwitch.ON, IntSwitch.OFF]:

                                for clk_heater_nom in [IntSwitch.ON, IntSwitch.OFF]:

                                    for clk_heater_red in [IntSwitch.ON, IntSwitch.OFF]:

                                        crio.set_svm_clock_status(clk_tcs_50mhz_nom, clk_tcs_50mhz_red, clk_heater_nom,
                                                                  clk_heater_red)
                                        led_status = crio.get_led_status()

                                        if secondary_output_status == IntSwitch.ON:

                                            if clk_f_50mhz_nom == IntSwitch.ON or clk_f_50mhz_red == IntSwitch.ON or \
                                                    clk_tcs_50mhz_nom == IntSwitch.ON or \
                                                    clk_tcs_50mhz_red == IntSwitch.ON:

                                                led_status["Clk_50MHz"] == IntSwitch.ON

                                            else:

                                                led_status["Clk_50MHz"] == IntSwitch.OFF

                                            assert led_status["Clk_F_FEE_N"] == clk_f_ccdread_nom
                                            assert led_status["Clk_F_FEE_R"] == clk_f_ccdread_red

                                            if clk_f_ccdread_nom == IntSwitch.ON or clk_f_ccdread_red == IntSwitch.ON:

                                                assert led_status["Clk_ccdread"] == IntSwitch.ON

                                            else:

                                                assert led_status["Clk_ccdread"] == IntSwitch.OFF

                                            if clk_heater_nom == IntSwitch.ON or clk_heater_red == IntSwitch.ON:

                                                assert led_status["Clk_heater"] == IntSwitch.ON

                                            else:

                                                assert led_status["Clk_heater"] == IntSwitch.OFF

                                        else:

                                            assert led_status["Clk_50MHz"] == IntSwitch.OFF
                                            assert led_status["Clk_ccdread"] == IntSwitch.OFF
                                            assert led_status["Clk_heater"] == IntSwitch.OFF
                                            assert led_status["Clk_F_FEE_N"] == IntSwitch.OFF
                                            assert led_status["Clk_F_FEE_R"] == IntSwitch.OFF

    crio.set_n_cam_secondary_power_status(IntSwitch.OFF)
    crio.set_f_cam_secondary_power_status(IntSwitch.OFF)

    for clk_n_50mhz in [IntSwitch.ON, IntSwitch.OFF]:

        for clk_n_ccdread in [IntSwitch.ON, IntSwitch.OFF]:

            crio.set_n_cam_clock_status(clk_n_50mhz, clk_n_ccdread)

            for clk_f_50mhz_nom in [IntSwitch.ON, IntSwitch.OFF]:

                for clk_f_50mhz_red in [IntSwitch.ON, IntSwitch.OFF]:

                    for clk_f_ccdread_nom in [IntSwitch.ON, IntSwitch.OFF]:

                        for clk_f_ccdread_red in [IntSwitch.ON, IntSwitch.OFF]:

                            crio.set_f_cam_clock_status(clk_f_50mhz_nom, clk_f_50mhz_red, clk_f_ccdread_nom,
                                                        clk_f_ccdread_red)

                            for clk_tcs_50mhz_nom in [IntSwitch.ON, IntSwitch.OFF]:

                                for clk_tcs_50mhz_red in [IntSwitch.ON, IntSwitch.OFF]:

                                    for clk_heater_nom in [IntSwitch.ON, IntSwitch.OFF]:

                                        for clk_heater_red in [IntSwitch.ON, IntSwitch.OFF]:

                                            crio.set_svm_clock_status(clk_tcs_50mhz_nom, clk_tcs_50mhz_red,
                                                                      clk_heater_nom, clk_heater_red)

                                            led_status = crio.get_led_status()

                                            assert led_status["Clk_50MHz"] == IntSwitch.OFF
                                            assert led_status["Clk_ccdread"] == IntSwitch.OFF
                                            assert led_status["Clk_heater"] == IntSwitch.OFF
                                            assert led_status["Clk_F_FEE_N"] == IntSwitch.OFF
                                            assert led_status["Clk_F_FEE_R"] == IntSwitch.OFF


def test_crio_operating_mode():

    crio = CRIOSimulator()

    for operating_mode in OperatingMode:

        crio.set_operating_mode(operating_mode)
        assert crio.get_operating_mode() == operating_mode


def test_crio_data():

    crio = CRIOSimulator()

    # EGSE mode

    crio.set_operating_mode(OperatingMode.STANDBY)
    data = crio.get_data()

    assert data["Standby"] == 1
    assert data["Selftest"] == 0
    assert data["FC_TVAC"] == 0
    assert data["Alignment"] == 0

    crio.set_operating_mode(OperatingMode.SELFTEST)
    data = crio.get_data()

    assert data["Standby"] == 0
    assert data["Selftest"] == 1
    assert data["FC_TVAC"] == 0
    assert data["Alignment"] == 0

    crio.set_operating_mode(OperatingMode.FC_TVAC)
    data = crio.get_data()

    assert data["Standby"] == 0
    assert data["Selftest"] == 0
    assert data["FC_TVAC"] == 1
    assert data["Alignment"] == 0

    crio.set_operating_mode(OperatingMode.ALIGNMENT)
    data = crio.get_data()

    assert data["Standby"] == 0
    assert data["Selftest"] == 0
    assert data["FC_TVAC"] == 0
    assert data["Alignment"] == 1

    # Camera selection + Power lines

    crio.set_n_cam_secondary_power_status(IntSwitch.ON)
    crio.set_f_cam_secondary_power_status(IntSwitch.OFF)
    data = crio.get_data()

    assert data["N-CAM"] == 1
    assert data["F-CAM"] == 0

    assert data["V_CCD"] == 1
    assert data["V_CLK"] == 1
    assert data["V_AN1"] == 1
    assert data["V_AN2"] == 1
    assert data["V_AN3"] == 1
    assert data["V_DIG"] == 1

    expected_current_n_cam = (0.105, 0.208, 0.190, 0.058, -0.224, 0.553)
    expected_voltage_n_cam = (34.70, 16.05, 6.65, 6.65, -6.65, 4.55)

    assert data["I_N_CCD"] == expected_current_n_cam[0]
    assert data["I_N_CLK"] == expected_current_n_cam[1]
    assert data["I_N_AN1"] == expected_current_n_cam[2]
    assert data["I_N_AN2"] == expected_current_n_cam[3]
    assert data["I_N_AN3"] == expected_current_n_cam[4]
    assert data["I_N_DIG"] == expected_current_n_cam[5]

    assert data["V_N_CCD"] == expected_voltage_n_cam[0]
    assert data["V_N_CLK"] == expected_voltage_n_cam[1]
    assert data["V_N_AN1"] == expected_voltage_n_cam[2]
    assert data["V_N_AN2"] == expected_voltage_n_cam[3]
    assert data["V_N_AN3"] == expected_voltage_n_cam[4]
    assert data["V_N_DIG"] == expected_voltage_n_cam[5]

    assert data["I_F_CCD"] == 0
    assert data["I_F_CLK"] == 0
    assert data["I_F_AN1"] == 0
    assert data["I_F_AN2"] == 0
    assert data["I_F_AN3"] == 0
    assert data["I_F_DIG"] == 0

    assert data["V_F_CCD"] == 0
    assert data["V_F_CLK"] == 0
    assert data["V_F_AN1"] == 0
    assert data["V_F_AN2"] == 0
    assert data["V_F_AN3"] == 0
    assert data["V_F_DIG"] == 0

    crio.set_n_cam_secondary_power_status(IntSwitch.OFF)
    crio.set_f_cam_secondary_power_status(IntSwitch.ON)
    data = crio.get_data()

    assert data["N-CAM"] == 0
    assert data["F-CAM"] == 1

    assert data["V_CCD"] == 1
    assert data["V_CLK"] == 1
    assert data["V_AN1"] == 1
    assert data["V_AN2"] == 1
    assert data["V_AN3"] == 1
    assert data["V_DIG"] == 1

    expected_current_f_cam = (0.164, 0.708, 0.511, 1.400, -0.171, 2.379)
    expected_voltage_f_cam = (31.6, 16.2, 7.7, 5.4, -7.6, 5.3)

    assert data["I_N_CCD"] == 0
    assert data["I_N_CLK"] == 0
    assert data["I_N_AN1"] == 0
    assert data["I_N_AN2"] == 0
    assert data["I_N_AN3"] == 0
    assert data["I_N_DIG"] == 0

    assert data["V_N_CCD"] == 0
    assert data["V_N_CLK"] == 0
    assert data["V_N_AN1"] == 0
    assert data["V_N_AN2"] == 0
    assert data["V_N_AN3"] == 0
    assert data["V_N_DIG"] == 0

    assert data["I_F_CCD"] == expected_current_f_cam[0]
    assert data["I_F_CLK"] == expected_current_f_cam[1]
    assert data["I_F_AN1"] == expected_current_f_cam[2]
    assert data["I_F_AN2"] == expected_current_f_cam[3]
    assert data["I_F_AN3"] == expected_current_f_cam[4]
    assert data["I_F_DIG"] == expected_current_f_cam[5]

    assert data["V_F_CCD"] == expected_voltage_f_cam[0]
    assert data["V_F_CLK"] == expected_voltage_f_cam[1]
    assert data["V_F_AN1"] == expected_voltage_f_cam[2]
    assert data["V_F_AN2"] == expected_voltage_f_cam[3]
    assert data["V_F_AN3"] == expected_voltage_f_cam[4]
    assert data["V_F_DIG"] == expected_voltage_f_cam[5]

    crio.set_n_cam_secondary_power_status(IntSwitch.OFF)
    crio.set_f_cam_secondary_power_status(IntSwitch.OFF)
    data = crio.get_data()

    assert data["N-CAM"] == 0
    assert data["F-CAM"] == 0

    assert data["V_CCD"] == 0
    assert data["V_CLK"] == 0
    assert data["V_AN1"] == 0
    assert data["V_AN2"] == 0
    assert data["V_AN3"] == 0
    assert data["V_DIG"] == 0

    # Error detection

    assert data["S_voltage_oor"] == 0
    assert data["S_current_oor"] == 0
    assert data["Sync_gf"] == 0


    # Clk signals selection

    crio.set_f_cam_secondary_power_status(IntSwitch.OFF)

    for secondary_output_status in [IntSwitch.ON, IntSwitch.OFF]:

        crio.set_n_cam_secondary_power_status(secondary_output_status)

        for clk_n_50mhz in [IntSwitch.ON, IntSwitch.OFF]:

            for clk_n_ccdread in [IntSwitch.ON, IntSwitch.OFF]:

                crio.set_n_cam_clock_status(clk_n_50mhz, clk_n_ccdread)

                for clk_tcs_50mhz_nom in [IntSwitch.ON, IntSwitch.OFF]:

                    for clk_tcs_50mhz_red in [IntSwitch.ON, IntSwitch.OFF]:

                        for clk_heater_nom in [IntSwitch.ON, IntSwitch.OFF]:

                            for clk_heater_red in [IntSwitch.ON, IntSwitch.OFF]:

                                crio.set_svm_clock_status(clk_tcs_50mhz_nom, clk_tcs_50mhz_red, clk_heater_nom,
                                                          clk_heater_red)
                                data = crio.get_data()

                                if secondary_output_status == IntSwitch.ON:

                                    if clk_n_50mhz == IntSwitch.ON or clk_tcs_50mhz_nom == IntSwitch.ON or \
                                            clk_tcs_50mhz_red == IntSwitch.ON:

                                        data["Clk_50MHz"] == IntSwitch.ON

                                    else:

                                        data["Clk_50MHz"] == IntSwitch.OFF

                                    assert data["Clk_ccdread"] == clk_n_ccdread

                                    if clk_heater_nom == IntSwitch.ON or clk_heater_red == IntSwitch.ON:

                                        assert data["Clk_heater"] == IntSwitch.ON

                                    else:

                                        assert data["Clk_heater"] == IntSwitch.OFF

                                else:

                                    assert data["Clk_50MHz"] == IntSwitch.OFF
                                    assert data["Clk_ccdread"] == IntSwitch.OFF
                                    assert data["Clk_heater"] == IntSwitch.OFF

                                assert data["Clk_F_FEE_N"] == IntSwitch.OFF
                                assert data["Clk_F_FEE_R"] == IntSwitch.OFF

    crio.set_n_cam_secondary_power_status(IntSwitch.OFF)

    for secondary_output_status in [IntSwitch.ON, IntSwitch.OFF]:

        crio.set_f_cam_secondary_power_status(secondary_output_status)

        for clk_f_50mhz_nom in [IntSwitch.ON, IntSwitch.OFF]:

            for clk_f_50mhz_red in [IntSwitch.ON, IntSwitch.OFF]:

                for clk_f_ccdread_nom in [IntSwitch.ON, IntSwitch.OFF]:

                    for clk_f_ccdread_red in [IntSwitch.ON, IntSwitch.OFF]:

                        crio.set_f_cam_clock_status(clk_f_50mhz_nom, clk_f_50mhz_red, clk_f_ccdread_nom, clk_f_ccdread_red)

                        for clk_tcs_50mhz_nom in [IntSwitch.ON, IntSwitch.OFF]:

                            for clk_tcs_50mhz_red in [IntSwitch.ON, IntSwitch.OFF]:

                                for clk_heater_nom in [IntSwitch.ON, IntSwitch.OFF]:

                                    for clk_heater_red in [IntSwitch.ON, IntSwitch.OFF]:

                                        crio.set_svm_clock_status(clk_tcs_50mhz_nom, clk_tcs_50mhz_red, clk_heater_nom,
                                                                  clk_heater_red)
                                        data = crio.get_data()

                                        if secondary_output_status == IntSwitch.ON:

                                            if clk_f_50mhz_nom == IntSwitch.ON or clk_f_50mhz_red == IntSwitch.ON or \
                                                    clk_tcs_50mhz_nom == IntSwitch.ON or \
                                                    clk_tcs_50mhz_red == IntSwitch.ON:

                                                data["Clk_50MHz"] == IntSwitch.ON

                                            else:

                                                data["Clk_50MHz"] == IntSwitch.OFF

                                            assert data["Clk_F_FEE_N"] == clk_f_ccdread_nom
                                            assert data["Clk_F_FEE_R"] == clk_f_ccdread_red

                                            if clk_f_ccdread_nom == IntSwitch.ON or clk_f_ccdread_red == IntSwitch.ON:

                                                assert data["Clk_ccdread"] == IntSwitch.ON

                                            else:

                                                assert data["Clk_ccdread"] == IntSwitch.OFF

                                            if clk_heater_nom == IntSwitch.ON or clk_heater_red == IntSwitch.ON:

                                                assert data["Clk_heater"] == IntSwitch.ON

                                            else:

                                                assert data["Clk_heater"] == IntSwitch.OFF

                                        else:

                                            assert data["Clk_50MHz"] == IntSwitch.OFF
                                            assert data["Clk_ccdread"] == IntSwitch.OFF
                                            assert data["Clk_heater"] == IntSwitch.OFF
                                            assert data["Clk_F_FEE_N"] == IntSwitch.OFF
                                            assert data["Clk_F_FEE_R"] == IntSwitch.OFF

    crio.set_n_cam_secondary_power_status(IntSwitch.OFF)
    crio.set_f_cam_secondary_power_status(IntSwitch.OFF)

    for clk_n_50mhz in [IntSwitch.ON, IntSwitch.OFF]:

        for clk_n_ccdread in [IntSwitch.ON, IntSwitch.OFF]:

            crio.set_n_cam_clock_status(clk_n_50mhz, clk_n_ccdread)

            for clk_f_50mhz_nom in [IntSwitch.ON, IntSwitch.OFF]:

                for clk_f_50mhz_red in [IntSwitch.ON, IntSwitch.OFF]:

                    for clk_f_ccdread_nom in [IntSwitch.ON, IntSwitch.OFF]:

                        for clk_f_ccdread_red in [IntSwitch.ON, IntSwitch.OFF]:

                            crio.set_f_cam_clock_status(clk_f_50mhz_nom, clk_f_50mhz_red, clk_f_ccdread_nom,
                                                        clk_f_ccdread_red)

                            for clk_tcs_50mhz_nom in [IntSwitch.ON, IntSwitch.OFF]:

                                for clk_tcs_50mhz_red in [IntSwitch.ON, IntSwitch.OFF]:

                                    for clk_heater_nom in [IntSwitch.ON, IntSwitch.OFF]:

                                        for clk_heater_red in [IntSwitch.ON, IntSwitch.OFF]:

                                            crio.set_svm_clock_status(clk_tcs_50mhz_nom, clk_tcs_50mhz_red,
                                                                      clk_heater_nom, clk_heater_red)

                                            data = crio.get_data()

                                            assert data["Clk_50MHz"] == IntSwitch.OFF
                                            assert data["Clk_ccdread"] == IntSwitch.OFF
                                            assert data["Clk_heater"] == IntSwitch.OFF
                                            assert data["Clk_F_FEE_N"] == IntSwitch.OFF
                                            assert data["Clk_F_FEE_R"] == IntSwitch.OFF


def test_crio_get_error_info():

    pass


def test_crio_get_num_errors():

    crio = CRIOSimulator()

    assert crio.get_num_errors() == 0


def test_crio_get_selftest_result():

    crio = CRIOSimulator()

    assert crio.get_selftest_result() == 0


def test_crio_protection_status():

    pass


def test_crio_time():

    crio = CRIOSimulator()
    expected_times = (2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 14, 21, 14,
                      14, 14, 17, 14, 21, 14, 14, 14, 17, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 150, 150, 150, 150, 150,
                      150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150)

    crio.set_time(*expected_times)
    actual_times = crio.get_time()

    assert len(expected_times) == len(actual_times)

    for index in range(len(expected_times)):

        assert actual_times[index] == expected_times[index]


#########
# AEU PSU
#########


psu_index_range = range(1, 7)


def test_psu_is_simulator():

    for psu_index in psu_index_range:

        psu = PSUSimulator(psu_index)
        assert psu.is_simulator()


def test_psu_get_id():

    for psu_index in psu_index_range:

        psu = PSUSimulator(psu_index)
        manufacturer, model, serial_number, ifc, ioc = psu.get_id()

        assert manufacturer == "KIKUSUI"
        assert model == "PMX18-5"
        serial_number == "AB123456"
        ifc == "IFC01.00.0016"
        ioc == "IOC01.00.0015"


def test_psu_reset():

    pass


def test_psu_test():

    pass


def test_psu_get_error_info():

    pass


def test_psu_clear():

    pass


def test_channel():

    for psu_index in psu_index_range:

        psu = PSUSimulator(psu_index)
        psu.set_channel(1)

        assert psu.get_channel() == 1


def test_get_channel_list():

    for psu_index in psu_index_range:

        psu = PSUSimulator(psu_index)

        assert psu.get_channel_list() == 1


def test_get_channel_info():

    for psu_index in psu_index_range:

        psu = PSUSimulator(psu_index)

        assert len(psu.get_channel_info()) == 2

        expected_channel_list = +3.5000E+01, +1.0000E+00
        assert psu.get_channel_info()[0] == expected_channel_list[0]
        assert psu.get_channel_info()[1] == expected_channel_list[1]


def test_get_current():

    for psu_index in psu_index_range:

        psu = PSUSimulator(psu_index)

        psu.set_output_status(IntSwitch.ON)
        assert psu.get_current() == psu.current

        psu.set_output_status(IntSwitch.OFF)
        assert psu.get_current() == 0


def test_get_voltage():

    for psu_index in psu_index_range:

        psu = PSUSimulator(psu_index)

        psu.set_output_status(IntSwitch.ON)
        assert psu.get_voltage() == psu.voltage

        psu.set_output_status(IntSwitch.OFF)
        assert psu.get_voltage() == 0


def test_recall_memory():

    pass


def test_memory_conf_settings():

    pass


def test_memory_setting():

    pass


def test_save_memory():

    pass


def test_output_status():

    for psu_index in psu_index_range:

        psu = PSUSimulator(psu_index)

        psu.set_output_status(IntSwitch.ON)
        assert psu.get_output_status() == IntSwitch.ON

        psu.set_output_status(IntSwitch.OFF)
        assert psu.get_output_status() == IntSwitch.OFF


def test_current_setpoint():

    for psu_index in psu_index_range:

        psu = PSUSimulator(psu_index)

        psu.set_current(2.0)
        assert psu.get_current_config() == 2.0


def test_ocp():

    for psu_index in psu_index_range:

        psu = PSUSimulator(psu_index)

        psu.set_ocp(5.1)
        assert psu.get_ocp() == 5.1


def test_voltage_setpoint():

    for psu_index in psu_index_range:

        psu = PSUSimulator(psu_index)

        psu.set_voltage(3.0)
        assert psu.get_voltage() == 3.0


def test_ovp():

    for psu_index in psu_index_range:

        psu = PSUSimulator(psu_index)

        psu.set_ovp(13.1)
        assert psu.get_ovp() == 13.1


def test_priority_mode():

    for psu_index in psu_index_range:

        psu = PSUSimulator(psu_index)

        for priority_mode in PriorityMode:

            psu.set_priority_mode(priority_mode)
            assert psu.get_priority_mode() == priority_mode


def test_clear_alarms():

    pass


def test_questionable_status_register():

    pass


#########
# AEU PSU
#########


awg_index_range = [1, 2]


def test_reset():

    pass


def test_channel():

    for awg_index in awg_index_range:

        awg = AWGSimulator(awg_index)

        for channel in [1, 2]:

            awg.set_channel(channel)
            assert awg.get_channel() == channel


def test_waveform_type():
    for awg_index in awg_index_range:

        awg = AWGSimulator(awg_index)

        for channel in [1, 2]:

            awg.set_channel(channel)

            for waveform_type in Waveform:

                awg.set_waveform_type(waveform_type)
                assert awg.get_waveform_type() == waveform_type


def def_output_load():

    for awg_index in awg_index_range:

        awg = AWGSimulator(awg_index)

        for channel in [1, 2]:

            awg.set_channel(channel)
            awg.set_output_load(50)

            assert awg.get_output_load() == 50


def test_amplitude():

    for awg_index in awg_index_range:

        awg = AWGSimulator(awg_index)

        for channel in [1, 2]:

            awg.set_channel(channel)
            awg.set_amplitude(2.7)

            assert awg.get_amplitude() == 2.7


def test_dc_offset():

    for awg_index in awg_index_range:

        awg = AWGSimulator(awg_index)

        for channel in [1, 2]:

            awg.set_channel(channel)
            awg.set_dc_offset(1.35)

            assert awg.get_dc_offset() == 1.35


def test_duty_cycle():

    for awg_index in awg_index_range:

        awg = AWGSimulator(awg_index)

        for channel in [1, 2]:

            awg.set_channel(channel)
            awg.set_duty_cycle(50)

            assert awg.get_duty_cycle() == 50


def test_frequency():

    for awg_index in awg_index_range:

        awg = AWGSimulator(awg_index)

        for channel in [1, 2]:

            awg.set_channel(channel)

            for frequency in [0.006667, 0.016, 0.0114286, 50000000]:

                awg.set_frequency(frequency)
                assert awg.get_frequency() == frequency


def test_output_status():

    for awg_index in awg_index_range:

        awg = AWGSimulator(awg_index)

        for channel in [1, 2]:

            awg.set_channel(channel)

            for output_status in Switch:

                awg.set_output_status(output_status)
                assert awg.get_output_status() == output_status


def test_arb_waveform():

    for awg_index in awg_index_range:

        awg = AWGSimulator(awg_index)

        for channel in [1, 2]:

            awg.set_channel(channel)

            for arb_waveform in ARB:

                awg.set_arb_waveform(arb_waveform)
                assert awg.get_arb_waveform() == arb_waveform


def test_define_arb_waveform():

    for awg_index in awg_index_range:

        awg = AWGSimulator(awg_index)

        arb_waveforms = [ARB.ARB1, ARB.ARB2, ARB.ARB3, ARB.ARB4]
        names = ["WAWE-ARB1", "WAWE-ARB2", "WAWE-ARB3", "WAWE-ARB4"]

        for interpolation in Switch:

            awg.define_arb_waveform(arb_waveforms[0], names[0], interpolation)
            assert awg.get_arb1_def()[0] == names[0]
            assert awg.get_arb1_def()[1] == interpolation
            assert awg.get_arb1_def()[2] == 0

            awg.define_arb_waveform(arb_waveforms[1], names[1], interpolation)
            assert awg.get_arb2_def()[0] == names[1]
            assert awg.get_arb2_def()[1] == interpolation
            assert awg.get_arb2_def()[2] == 0

            awg.define_arb_waveform(arb_waveforms[2], names[2], interpolation)
            assert awg.get_arb3_def()[0] == names[2]
            assert awg.get_arb3_def()[1] == interpolation
            assert awg.get_arb3_def()[2] == 0

            awg.define_arb_waveform(arb_waveforms[3], names[3], interpolation)
            assert awg.get_arb4_def()[0] == names[3]
            assert awg.get_arb4_def()[1] == interpolation
            assert awg.get_arb4_def()[2] == 0


def test_load_arb1_data():

    for awg_index in awg_index_range:

        awg = AWGSimulator(awg_index)

        for interpolation in Switch:

            awg.define_arb_waveform(ARB.ARB1, f"ARB1-{awg_index}", interpolation)

            awg.load_arb1_data(ArbDataFile.N_CCD_READ_25)
            assert awg.get_arb1_def()[2] == 6000 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.N_CCD_READ_25)
            assert awg.get_arb1() == arb_data.string

            awg.load_arb1_data(ArbDataFile.N_CCD_READ_31_25)
            assert awg.get_arb1_def()[2] == 2500 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.N_CCD_READ_31_25)
            assert awg.get_arb1() == arb_data.string

            awg.load_arb1_data(ArbDataFile.N_CCD_READ_37_50)
            assert awg.get_arb1_def()[2] == 6000 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.N_CCD_READ_37_50)
            assert awg.get_arb1() == arb_data.string

            awg.load_arb1_data(ArbDataFile.N_CCD_READ_43_75)
            assert awg.get_arb1_def()[2] == 3500 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.N_CCD_READ_43_75)
            assert awg.get_arb1() == arb_data.string

            awg.load_arb1_data(ArbDataFile.N_CCD_READ_50)
            assert awg.get_arb1_def()[2] == 6000 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.N_CCD_READ_50)
            assert awg.get_arb1() == arb_data.string

            awg.load_arb1_data(ArbDataFile.F_CCD_READ)
            assert awg.get_arb1_def()[2] == 6000 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.F_CCD_READ)
            assert awg.get_arb1() == arb_data.string

            awg.load_arb1_data(ArbDataFile.SVM_SYNC_CCD_READ_25)
            assert awg.get_arb1_def()[2] == 6000 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.SVM_SYNC_CCD_READ_25)
            assert awg.get_arb1() == arb_data.string

            awg.load_arb1_data(ArbDataFile.SVM_SYNC_CCD_READ_31_25)
            assert awg.get_arb1_def()[2] == 2500 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.SVM_SYNC_CCD_READ_31_25)
            assert awg.get_arb1() == arb_data.string

            awg.load_arb1_data(ArbDataFile.SVM_SYNC_CCD_READ_37_50)
            assert awg.get_arb1_def()[2] == 6000 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.SVM_SYNC_CCD_READ_37_50)
            assert awg.get_arb1() == arb_data.string

            awg.load_arb1_data(ArbDataFile.SVM_SYNC_CCD_READ_43_75)
            assert awg.get_arb1_def()[2] == 3500 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.SVM_SYNC_CCD_READ_43_75)
            assert awg.get_arb1() == arb_data.string

            awg.load_arb1_data(ArbDataFile.SVM_SYNC_CCD_READ_50)
            assert awg.get_arb1_def()[2] == 6000 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.SVM_SYNC_CCD_READ_50)
            assert awg.get_arb1() == arb_data.string

            awg.load_arb1_data(ArbDataFile.SVM_SYNC_F_CAM)
            assert awg.get_arb1_def()[2] == 6000 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.SVM_SYNC_F_CAM)
            assert awg.get_arb1() == arb_data.string


def test_load_arb2_data():

    for awg_index in awg_index_range:

        awg = AWGSimulator(awg_index)

        for interpolation in Switch:

            awg.define_arb_waveform(ARB.ARB2, f"ARB2-{awg_index}", interpolation)

            awg.load_arb2_data(ArbDataFile.N_CCD_READ_25)
            assert awg.get_arb2_def()[2] == 6000 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.N_CCD_READ_25)
            assert awg.get_arb2() == arb_data.string

            awg.load_arb2_data(ArbDataFile.N_CCD_READ_31_25)
            assert awg.get_arb2_def()[2] == 2500 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.N_CCD_READ_31_25)
            assert awg.get_arb2() == arb_data.string

            awg.load_arb2_data(ArbDataFile.N_CCD_READ_37_50)
            assert awg.get_arb2_def()[2] == 6000 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.N_CCD_READ_37_50)
            assert awg.get_arb2() == arb_data.string

            awg.load_arb2_data(ArbDataFile.N_CCD_READ_43_75)
            assert awg.get_arb2_def()[2] == 3500 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.N_CCD_READ_43_75)
            assert awg.get_arb2() == arb_data.string

            awg.load_arb2_data(ArbDataFile.N_CCD_READ_50)
            assert awg.get_arb2_def()[2] == 6000 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.N_CCD_READ_50)
            assert awg.get_arb2() == arb_data.string

            awg.load_arb2_data(ArbDataFile.F_CCD_READ)
            assert awg.get_arb2_def()[2] == 6000 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.F_CCD_READ)
            assert awg.get_arb2() == arb_data.string

            awg.load_arb2_data(ArbDataFile.SVM_SYNC_CCD_READ_25)
            assert awg.get_arb2_def()[2] == 6000 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.SVM_SYNC_CCD_READ_25)
            assert awg.get_arb2() == arb_data.string

            awg.load_arb2_data(ArbDataFile.SVM_SYNC_CCD_READ_31_25)
            assert awg.get_arb2_def()[2] == 2500 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.SVM_SYNC_CCD_READ_31_25)
            assert awg.get_arb2() == arb_data.string

            awg.load_arb2_data(ArbDataFile.SVM_SYNC_CCD_READ_37_50)
            assert awg.get_arb2_def()[2] == 6000 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.SVM_SYNC_CCD_READ_37_50)
            assert awg.get_arb2() == arb_data.string

            awg.load_arb2_data(ArbDataFile.SVM_SYNC_CCD_READ_43_75)
            assert awg.get_arb2_def()[2] == 3500 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.SVM_SYNC_CCD_READ_43_75)
            assert awg.get_arb2() == arb_data.string

            awg.load_arb2_data(ArbDataFile.SVM_SYNC_CCD_READ_50)
            assert awg.get_arb2_def()[2] == 6000 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.SVM_SYNC_CCD_READ_50)
            assert awg.get_arb2() == arb_data.string

            awg.load_arb2_data(ArbDataFile.SVM_SYNC_F_CAM)
            assert awg.get_arb2_def()[2] == 6000 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.SVM_SYNC_F_CAM)
            assert awg.get_arb2() == arb_data.string


def test_load_arb3_data():

    for awg_index in awg_index_range:

        awg = AWGSimulator(awg_index)

        for interpolation in Switch:

            awg.define_arb_waveform(ARB.ARB2, f"ARB2-{awg_index}", interpolation)

            awg.load_arb3_data(ArbDataFile.N_CCD_READ_25)
            assert awg.get_arb3_def()[2] == 6000 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.N_CCD_READ_25)
            assert awg.get_arb3() == arb_data.string

            awg.load_arb3_data(ArbDataFile.N_CCD_READ_31_25)
            assert awg.get_arb3_def()[2] == 2500 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.N_CCD_READ_31_25)
            assert awg.get_arb3() == arb_data.string

            awg.load_arb3_data(ArbDataFile.N_CCD_READ_37_50)
            assert awg.get_arb3_def()[2] == 6000 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.N_CCD_READ_37_50)
            assert awg.get_arb3() == arb_data.string

            awg.load_arb3_data(ArbDataFile.N_CCD_READ_43_75)
            assert awg.get_arb3_def()[2] == 3500 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.N_CCD_READ_43_75)
            assert awg.get_arb3() == arb_data.string

            awg.load_arb3_data(ArbDataFile.N_CCD_READ_50)
            assert awg.get_arb3_def()[2] == 6000 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.N_CCD_READ_50)
            assert awg.get_arb3() == arb_data.string

            awg.load_arb3_data(ArbDataFile.F_CCD_READ)
            assert awg.get_arb3_def()[2] == 6000 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.F_CCD_READ)
            assert awg.get_arb3() == arb_data.string

            awg.load_arb3_data(ArbDataFile.SVM_SYNC_CCD_READ_25)
            assert awg.get_arb3_def()[2] == 6000 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.SVM_SYNC_CCD_READ_25)
            assert awg.get_arb3() == arb_data.string

            awg.load_arb3_data(ArbDataFile.SVM_SYNC_CCD_READ_31_25)
            assert awg.get_arb3_def()[2] == 2500 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.SVM_SYNC_CCD_READ_31_25)
            assert awg.get_arb3() == arb_data.string

            awg.load_arb3_data(ArbDataFile.SVM_SYNC_CCD_READ_37_50)
            assert awg.get_arb3_def()[2] == 6000 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.SVM_SYNC_CCD_READ_37_50)
            assert awg.get_arb3() == arb_data.string

            awg.load_arb3_data(ArbDataFile.SVM_SYNC_CCD_READ_43_75)
            assert awg.get_arb3_def()[2] == 3500 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.SVM_SYNC_CCD_READ_43_75)
            assert awg.get_arb3() == arb_data.string

            awg.load_arb3_data(ArbDataFile.SVM_SYNC_CCD_READ_50)
            assert awg.get_arb3_def()[2] == 6000 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.SVM_SYNC_CCD_READ_50)
            assert awg.get_arb3() == arb_data.string

            awg.load_arb3_data(ArbDataFile.SVM_SYNC_F_CAM)
            assert awg.get_arb3_def()[2] == 6000 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.SVM_SYNC_F_CAM)
            assert awg.get_arb3() == arb_data.string


def test_load_arb4_data():

    for awg_index in awg_index_range:

        awg = AWGSimulator(awg_index)

        for interpolation in Switch:

            awg.define_arb_waveform(ARB.ARB2, f"ARB2-{awg_index}", interpolation)

            awg.load_arb4_data(ArbDataFile.N_CCD_READ_25)
            assert awg.get_arb4_def()[2] == 6000 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.N_CCD_READ_25)
            assert awg.get_arb4() == arb_data.string

            awg.load_arb4_data(ArbDataFile.N_CCD_READ_31_25)
            assert awg.get_arb4_def()[2] == 2500 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.N_CCD_READ_31_25)
            assert awg.get_arb4() == arb_data.string

            awg.load_arb4_data(ArbDataFile.N_CCD_READ_37_50)
            assert awg.get_arb4_def()[2] == 6000 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.N_CCD_READ_37_50)
            assert awg.get_arb4() == arb_data.string

            awg.load_arb4_data(ArbDataFile.N_CCD_READ_43_75)
            assert awg.get_arb4_def()[2] == 3500 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.N_CCD_READ_43_75)
            assert awg.get_arb4() == arb_data.string

            awg.load_arb4_data(ArbDataFile.N_CCD_READ_50)
            assert awg.get_arb4_def()[2] == 6000 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.N_CCD_READ_50)
            assert awg.get_arb4() == arb_data.string

            awg.load_arb4_data(ArbDataFile.F_CCD_READ)
            assert awg.get_arb4_def()[2] == 6000 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.F_CCD_READ)
            assert awg.get_arb4() == arb_data.string

            awg.load_arb4_data(ArbDataFile.SVM_SYNC_CCD_READ_25)
            assert awg.get_arb4_def()[2] == 6000 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.SVM_SYNC_CCD_READ_25)
            assert awg.get_arb4() == arb_data.string

            awg.load_arb4_data(ArbDataFile.SVM_SYNC_CCD_READ_31_25)
            assert awg.get_arb4_def()[2] == 2500 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.SVM_SYNC_CCD_READ_31_25)
            assert awg.get_arb4() == arb_data.string

            awg.load_arb4_data(ArbDataFile.SVM_SYNC_CCD_READ_37_50)
            assert awg.get_arb4_def()[2] == 6000 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.SVM_SYNC_CCD_READ_37_50)
            assert awg.get_arb4() == arb_data.string

            awg.load_arb4_data(ArbDataFile.SVM_SYNC_CCD_READ_43_75)
            assert awg.get_arb4_def()[2] == 3500 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.SVM_SYNC_CCD_READ_43_75)
            assert awg.get_arb4() == arb_data.string

            awg.load_arb4_data(ArbDataFile.SVM_SYNC_CCD_READ_50)
            assert awg.get_arb4_def()[2] == 6000 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.SVM_SYNC_CCD_READ_50)
            assert awg.get_arb4() == arb_data.string

            awg.load_arb4_data(ArbDataFile.SVM_SYNC_F_CAM)
            assert awg.get_arb4_def()[2] == 6000 / 2
            arb_data = ArbData()
            arb_data.init_from_file(ArbDataFile.SVM_SYNC_F_CAM)
            assert awg.get_arb4() == arb_data.string


def test_clear_status():

    pass


def test_execution_error_register():

    pass


def test_query_error_register():

    pass


def test_awg_get_id():

    for awg_index in awg_index_range:

        awg = AWGSimulator(awg_index)
        manufacturer, model, serial_number, main_firmware, remote_interface_firmware, usb_flash_drive_firmware = awg.get_id()

        assert manufacturer == "THURLY THANDAR"
        assert model == "TGF4162"
        assert serial_number == "527758"
        assert main_firmware == 01.00
        assert remote_interface_firmware == 02.10
        assert usb_flash_drive_firmware == 01.20


def test_counter_status():

    for awg_index in awg_index_range:

        awg = AWGSimulator(awg_index)

        for channel in [1, 2]:

            awg.set_channel(channel)

            for counter_status in Switch:

                awg.set_counter_status(counter_status)
                assert awg.get_counter_status() == counter_status


def test_counter_source():

    for awg_index in awg_index_range:

        awg = AWGSimulator(awg_index)

        for channel in [1, 2]:

            awg.set_channel(channel)

            for counter_source in CounterSource:

                awg.set_counter_source(counter_source)
                assert awg.get_counter_source() == counter_source


def test_counter_type():

    for awg_index in awg_index_range:

        awg = AWGSimulator(awg_index)

        for channel in [1, 2]:

            awg.set_channel(channel)

            for counter_type in CounterType:

                awg.set_counter_type(counter_type)
                assert awg.get_counter_type() == counter_type


def test_counter_value():

    for awg_index in awg_index_range:

        awg = AWGSimulator(awg_index)

        for channel in [1, 2]:

            awg.set_channel(channel)

            assert awg.get_counter_value() == 1


def test_align():

    pass


def test_connect():

    pass


def test_disconnect():

    pass


def test_reconnect():

    pass


def test_is_connected():

    for awg_index in awg_index_range:

        awg = AWGSimulator(awg_index)

        assert awg.is_connected()


def test_is_simulator():

    for awg_index in awg_index_range:

        awg = AWGSimulator(awg_index)

        assert awg.is_simulator()


##########
# Usecases
##########


def test_n_cam():

    crio = CRIOSimulator()
    crio.reconnect()
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

    for psu_index in psu_index_range:

        psu = PSUSimulator(psu_index)
        psu.reconnect()
        psu_cal = SETUP.gse.aeu[f"psu{psu_index}"].calibration

        # Configure the current

        psu.set_current(psu_cal.n_cam_current)
        currents = np.append(currents, psu_cal.n_cam_current)

        # Check the current

        assert psu.get_current_config() == psu_cal.n_cam_current

        # Configure the current protection

        psu.set_ocp(psu_cal.n_cam_ocp)
        ocp = np.append(ocp, psu_cal.n_cam_ocp)

        # Check the current protection

        assert psu.get_ocp() == psu_cal.n_cam_ocp

        # Configure the voltage

        psu.set_voltage(psu_cal.n_cam_voltage)
        voltages = np.append(voltages, psu_cal.n_cam_voltage)

        # Check the voltage

        assert psu.get_voltage_config() == psu_cal.n_cam_voltage

        # Configure the OVP

        psu.set_ovp(psu_cal.n_cam_ovp)
        ovp = np.append(ovp, psu_cal.n_cam_ovp)

        # Check the OVP

        assert psu.get_ovp() == psu_cal.n_cam_ovp

        # Configure the operation mode to be prioritised when the output is turned on

        psu.set_priority_mode(PriorityMode.CONSTANT_CURRENT)

        # Check the operation mode to be prioritised when the output is turned on

        assert psu.get_priority_mode() == PriorityMode.CONSTANT_CURRENT

        # Turn on the signal output

        psu.set_output_status(IntSwitch.ON)

        # Check the output status

        assert psu.get_output_status() == IntSwitch.ON

    crio.current_n_cam = currents
    crio.voltage_n_cam = voltages
    crio.ocp_n_cam = ocp
    crio.ovp_n_cam = ovp

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

    for index in range(6):

        assert crio.get_n_cam_voltage()[index] == voltages[index]

    # 86. Measure the current values in N-CAM

    assert len(crio.get_n_cam_current()) == 6

    for index in range(6):

        assert crio.get_n_cam_current()[index] == currents[index]

    awg1 = AWGSimulator(1)
    awg2 = AWGSimulator(2)
    awg1.reconnect()
    awg2.reconnect()

    awg1_cal = SETUP.gse.aeu.awg1.calibration
    awg2_cal = SETUP.gse.aeu.awg2.calibration

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

    for psu_index in psu_index_range:

        psu = PSUSimulator(psu_index)
        psu.reconnect()

        # Turn off the signal output

        psu.set_output_status(IntSwitch.OFF)

        # Check the output status of V_CCD (PSU1)

        assert psu.get_output_status() == IntSwitch.OFF

    crio.set_operating_mode(OperatingMode.STANDBY)
    assert crio.get_operating_mode() == OperatingMode.STANDBY


def test_f_cam():

    crio = CRIOSimulator()
    crio.reconnect()
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

    for psu_index in psu_index_range:

        psu = PSUSimulator(psu_index)
        psu.reconnect()
        psu_cal = SETUP.gse.aeu[f"psu{psu_index}"].calibration

        # Configure the current

        psu.set_current(psu_cal.f_cam_current)
        currents = np.append(currents, psu_cal.f_cam_current)

        # Check the current

        assert psu.get_current_config() == psu_cal.f_cam_current

        # Configure the current protection

        psu.set_ocp(psu_cal.f_cam_ocp)
        ocp = np.append(ocp, psu_cal.f_cam_ocp)

        # Check the current protection

        assert psu.get_ocp() == psu_cal.f_cam_ocp

        # Configure the voltage

        psu.set_voltage(psu_cal.f_cam_voltage)
        voltages = np.append(voltages, psu_cal.f_cam_voltage)

        # Check the voltage

        assert psu.get_voltage_config() == psu_cal.f_cam_voltage

        # Configure the OVP

        psu.set_ovp(psu_cal.f_cam_ovp)
        ovp = np.append(ovp, psu_cal.f_cam_ovp)

        # Check the OVP

        assert psu.get_ovp() == psu_cal.f_cam_ovp

        # Configure the operation mode to be prioritised when the output is turned on

        psu.set_priority_mode(PriorityMode.CONSTANT_CURRENT)

        # Check the operation mode to be prioritised when the output is turned on

        assert psu.get_priority_mode() == PriorityMode.CONSTANT_CURRENT

        # Turn on the signal output

        psu.set_output_status(IntSwitch.ON)

        # Check the output status

        assert psu.get_output_status() == IntSwitch.ON

    crio.current_f_cam = currents
    crio.voltage_f_cam = voltages
    crio.ocp_f_cam = ocp
    crio.ovp_f_cam = ovp

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

    for index in range(6):

        assert crio.get_f_cam_voltage()[index] == voltages[index]

    # 86. Measure the current values in F-CAM

    assert len(crio.get_f_cam_current()) == 6

    for index in range(6):

        assert crio.get_f_cam_current()[index] == currents[index]

    awg1 = AWGSimulator(1)
    awg2 = AWGSimulator(2)
    awg1.reconnect()
    awg2.reconnect()

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

    for psu_index in psu_index_range:

        psu = PSUSimulator(psu_index)
        psu.reconnect()

        # Turn off the signal output

        psu.set_output_status(IntSwitch.OFF)

        # Check the output status of V_CCD (PSU1)

        assert psu.get_output_status() == IntSwitch.OFF

    crio.set_operating_mode(OperatingMode.STANDBY)
    assert crio.get_operating_mode() == OperatingMode.STANDBY
