import os
from pathlib import Path

import math

from egse.fee.n_fee_hk import get_calibrated_temperatures, get_calibrated_supply_voltages
from egse.settings import Settings
from egse.setup import NavigableDict


def test_get_calibrated_temperatures():
    """ Test N-FEE temperature calibration.

     This test is based on Table 14-13 in PLATO-MSSL-PL-TP-0058=ASR=25102022-PFM (N-FEE FPA PFM/FM/FS Short Functional
     Test Procedure).
     """

    # TODO Load setup with sensor calibration information (e.g. CSL setup 101)

    # Raw, uncalibrated values [ADU]

    counts = {}
    counts["NFEE_TOU_TRP5_RAW"] = 6194
    counts["NFEE_TOU_TRP10_RAW"] = 26936
    counts["NFEE_TOU_TRP8_RAW"] = 20895
    counts["NFEE_TOU_TRP21_RAW"] = 48331
    counts["NFEE_TOU_TRP31_RAW"] = 13166
    counts["NFEE_TOU_TRP41_RAW"] = 33442
    counts["NFEE_T_CCD1_RAW"] = 40503
    counts["NFEE_T_CCD2_RAW"] = 40489
    counts["NFEE_T_CCD3_RAW"] = 40452
    counts["NFEE_T_CCD4_RAW"] = 40400
    counts["NFEE_T_PCB1_RAW"] = 41149
    counts["NFEE_T_PCB2_RAW"] = 41172
    counts["NFEE_T_ADC_RAW"] = 41664
    counts["NFEE_T_CDS_RAW"] = 41920
    counts["NFEE_T_ANALOG_RAW"] = 41462
    counts["NFEE_T_PCB3_RAW"] = 4797
    counts["NFEE_T_PCB4_RAW"] = 4786

    # Temperature calibration (Achel v1)

    yaml_location = Path(os.environ["PLATO_CONF_REPO_LOCATION"]) / "data" / "common" / "n-fee"\
        / "nfee_sensor_calibration_achel_v3.yaml"
    sensor_calibration = NavigableDict(Settings.load(filename=yaml_location, add_local_settings=False))
    sensor_calibration = sensor_calibration.temperatures

    temperatures = get_calibrated_temperatures(counts, sensor_calibration)

    # Expected temperatures [°C]

    expected_temperatures = {}
    expected_temperatures["NFEE_TOU_TRP5"] = -96.04
    expected_temperatures["NFEE_TOU_TRP10"] = -23.63
    expected_temperatures["NFEE_TOU_TRP8"] = -45.18
    expected_temperatures["NFEE_TOU_TRP21"] = 52.93
    expected_temperatures["NFEE_TOU_TRP31"] = -72.28
    expected_temperatures["NFEE_TOU_TRP41"] = -0.74
    expected_temperatures["NFEE_T_CCD1"] = 24.85
    expected_temperatures["NFEE_T_CCD2"] = 24.57
    expected_temperatures["NFEE_T_CCD3"] = 24.82
    expected_temperatures["NFEE_T_CCD4"] = 24.84
    expected_temperatures["NFEE_T_CCD1_AMB"] = 24.85
    expected_temperatures["NFEE_T_CCD2_AMB"] = 24.57
    expected_temperatures["NFEE_T_CCD3_AMB"] = 24.82
    expected_temperatures["NFEE_T_CCD4_AMB"] = 24.84
    expected_temperatures["NFEE_T_PCB1"] = 23.84
    expected_temperatures["NFEE_T_PCB2"] = 25.55
    expected_temperatures["NFEE_T_ADC"] = 27.46
    expected_temperatures["NFEE_T_CDS"] = 28.49
    expected_temperatures["NFEE_T_ANALOG"] = 26.95
    expected_temperatures["NFEE_T_PCB3"] = 27.4
    expected_temperatures["NFEE_T_PCB4"] = 26.71

    for sensor_type in sensor_calibration:
        cal = sensor_calibration[sensor_type]
        for sensor_name in cal.sensor_names:

            if "CCD" in sensor_name:
                # Table 14-13 in PLATO-MSSL-PL-TP-0058=ASR=25102022-PFM uses CvD instead of the E2V calibration
                assert math.isclose(temperatures[sensor_name], expected_temperatures[sensor_name], abs_tol=4)
            else:
                assert math.isclose(temperatures[sensor_name], expected_temperatures[sensor_name], rel_tol=0.005)

def test_get_calibrated_supply_voltages():
    """ Test N-FEE supply voltage calibration.

     This test is based on PLATO-MSSL-PL-FI-0063 (v1.1).
     """

    # TODO Load setup with sensor calibration information (e.g. CSL setup 101)

    # Raw, uncalibrated values [ADU]

    counts = {}
    counts["NFEE_CCD1_VOD_E_RAW"] = 49176
    counts["NFEE_CCD1_VOD_F_RAW"] = 32768
    counts["NFEE_CCD1_VOG_RAW"] = 32768
    counts["NFEE_CCD1_VRD_E_RAW"] = 32768
    counts["NFEE_CCD1_VRD_F_RAW"] = 32768
    counts["NFEE_CCD1_VGD_RAW"] = 32768
    counts["NFEE_CCD2_VOD_E_RAW"] = 32768
    counts["NFEE_CCD2_VOD_F_RAW"] = 32768
    counts["NFEE_CCD2_VOG_RAW"] = 32768
    counts["NFEE_CCD2_VRD_E_RAW"] = 32768
    counts["NFEE_CCD2_VRD_F_RAW"] = 32768
    counts["NFEE_CCD2_VGD_RAW_RAW"] = 32768
    counts["NFEE_CCD3_VOD_E_RAW"] = 32768
    counts["NFEE_CCD3_VOD_F_RAW"] = 32768
    counts["NFEE_CCD3_VOG_RAW"] = 32768
    counts["NFEE_CCD3_VRD_E_RAW"] = 32768
    counts["NFEE_CCD3_VRD_F_RAW"] = 32768
    counts["NFEE_CCD3_VGD_RAW"] = 32768
    counts["NFEE_CCD4_VOD_E_RAW"] = 32768
    counts["NFEE_CCD4_VOD_F_RAW"] = 32768
    counts["NFEE_CCD4_VOG_RAW"] = 32768
    counts["NFEE_CCD4_VRD_E_RAW"] = 32768
    counts["NFEE_CCD4_VRD_F_RAW"] = 32768
    counts["NFEE_CCD4_VGD_RAW"] = 32768
    counts["NFEE_CCD1_VDD_RAW"] = 55483
    counts["NFEE_CCD2_VDD_RAW"] = 55469
    counts["NFEE_CCD3_VDD_RAW"] = 55497
    counts["NFEE_CCD4_VDD_RAW"] = 55494
    counts["NFEE_VCCD_RAW"] = 49844
    counts["NFEE_VRCLK_RAW"] = 31667
    counts["NFEE_VICLK_RAW"] = 31563
    counts["NFEE_5VB_NEG_RAW"] = 40199
    counts["NFEE_3V3B_RAW"] = 26370
    counts["NFEE_2V5A_RAW"] = 39618
    counts["NFEE_3V3D_RAW"] = 26279
    counts["NFEE_2V5D_RAW"] = 39696
    counts["NFEE_1V8D_RAW"] = 29158
    counts["NFEE_1V5D_RAW"] = 24242
    counts["NFEE_5VREF_RAW"] = 39625
    counts["NFEE_IG_HI_RAW"] = 52240

    counts["NFEE_VCCD_R_RAW"] = 0
    counts["NFEE_VCLK_R_RAW"] = 0
    counts["NFEE_VAN1_R_RAW"] = 0
    counts["NFEE_VAN2_R_RAW"] = 0
    counts["NFEE_VAN3_R_RAW"] = 0
    counts["NFEE_VDIG_RAW"] = 0

    # Supply Voltage calibration (Achel v1)

    yaml_location = Path(os.environ["PLATO_CONF_REPO_LOCATION"]) / "data" / "common" / "n-fee"\
        / "nfee_sensor_calibration_achel_v1.yaml"
    sensor_calibration = NavigableDict(Settings.load(filename=yaml_location, add_local_settings=False))
    sensor_calibration = sensor_calibration.supply_voltages

    supply_voltages = get_calibrated_supply_voltages(counts, sensor_calibration)

    expected_supply_voltages = {}
    expected_supply_voltages["NFEE_CCD1_VOD_E"] = 27.942
    expected_supply_voltages["NFEE_CCD1_VOD_F"] = 18.628
    expected_supply_voltages["NFEE_CCD1_VOG"] = 18.426
    expected_supply_voltages["NFEE_CCD1_VRD_E"] = 18.697
    expected_supply_voltages["NFEE_CCD1_VRD_F"] = 18.611
    expected_supply_voltages["NFEE_CCD1_VGD"] = 18.566
    expected_supply_voltages["NFEE_CCD2_VOD_E"] = 18.603
    expected_supply_voltages["NFEE_CCD2_VOD_F"] = 18.598
    expected_supply_voltages["NFEE_CCD2_VOG"] = 18.433
    expected_supply_voltages["NFEE_CCD2_VRD_E"] = 18.690
    expected_supply_voltages["NFEE_CCD2_VRD_F"] = 18.680
    expected_supply_voltages["NFEE_CCD2_VGD_RAW"] = 18.565
    expected_supply_voltages["NFEE_CCD3_VOD_E"] = 18.604
    expected_supply_voltages["NFEE_CCD3_VOD_F"] = 18.623
    expected_supply_voltages["NFEE_CCD3_VOG"] = 18.425
    expected_supply_voltages["NFEE_CCD3_VRD_E"] = 18.692
    expected_supply_voltages["NFEE_CCD3_VRD_F"] = 18.612
    expected_supply_voltages["NFEE_CCD3_VGD"] = 18.566
    expected_supply_voltages["NFEE_CCD4_VOD_E"] = 18.611
    expected_supply_voltages["NFEE_CCD4_VOD_F"] = 18.623
    expected_supply_voltages["NFEE_CCD4_VOG"] = 18.429
    expected_supply_voltages["NFEE_CCD4_VRD_E"] = 18.688
    expected_supply_voltages["NFEE_CCD4_VRD_F"] = 18.612
    expected_supply_voltages["NFEE_CCD4_VGD"] = 18.565
    expected_supply_voltages["NFEE_CCD1_VDD"] = 24.392
    expected_supply_voltages["NFEE_CCD2_VDD"] = 24.394
    expected_supply_voltages["NFEE_CCD3_VDD"] = 24.395
    expected_supply_voltages["NFEE_CCD4_VDD"] = 24.394
    expected_supply_voltages["NFEE_VCCD"] = 31.540
    expected_supply_voltages["NFEE_VRCLK"] = 9.930
    expected_supply_voltages["NFEE_VICLK"] = 9.930
    expected_supply_voltages["NFEE_5VB_NEG"] = -5.124
    expected_supply_voltages["NFEE_3V3B"] = 3.306
    expected_supply_voltages["NFEE_2V5A"] = 2.487
    expected_supply_voltages["NFEE_3V3D"] = 3.293
    expected_supply_voltages["NFEE_2V5D"] = 2.493
    expected_supply_voltages["NFEE_1V8D"] = 1.826
    expected_supply_voltages["NFEE_1V5D"] = 1.513
    expected_supply_voltages["NFEE_5VREF"] = 4.998
    expected_supply_voltages["NFEE_IG_HI"] = 9.912

    expected_supply_voltages["NFEE_VCCD_R"] = 0
    expected_supply_voltages["NFEE_VCLK_R"] = 0
    expected_supply_voltages["NFEE_VAN1_R"] = 0
    expected_supply_voltages["NFEE_VAN2_R"] = 0
    expected_supply_voltages["NFEE_VAN3_R"] = 0
    expected_supply_voltages["NFEE_VDIG"] = 0

    for sensor_name in sensor_calibration:
        assert math.isclose(supply_voltages[sensor_name], expected_supply_voltages[sensor_name], rel_tol=0.005)
