import pandas
from math import isnan
from egse.hk import read_conversion_dict
from egse.fee.n_fee_hk import ORIGIN

filename = "/Users/sara/work/Instrumentation/Plato/data/PLATO-MSSL-PL-FI-0063_1.1_N-FEE_PFM_HK_Calibrations_File.xlsx"


def print_temperature_calibration(filename: str):
    table = pandas.read_excel(filename, sheet_name="HK & DAC Calibrations",
                              usecols="B, E, F, I, J",
                              names=["mssl_names", "gain1", "offset1", "gain2", "offset2"])

    mssl_names = table["mssl_names"]
    gain1 = table["gain1"]
    offset1 = table["offset1"]
    gain2 = table["gain2"]
    offset2 = table["offset2"]

    hk_name_mapping = read_conversion_dict(ORIGIN, use_site=False)

    for index in range(len(mssl_names)):
        mssl_name = mssl_names[index]

        if isinstance(mssl_name, str) and "[" in mssl_name and "]" in mssl_name:
            mssl_name = mssl_name.split("[")[0]
            egse_name = hk_name_mapping[mssl_name]

            is_temperature_calibration = "_T_" in egse_name or "TRP" in egse_name
            if is_temperature_calibration:
                print(f"\t{egse_name} ({mssl_name}):")
                # print(gain1[index], offset1[index])

                if "TSENSE" in mssl_name:
                    print(f"\t\tcounts_to_temperature_gain: {gain1[index]}")
                    print(f"\tcounts_to_temperature_offset: {offset1[index]}")

                else:
                    print(f"\t\tcounts_to_resistance_gain: {gain2[index]}")
                    print(f"\t\toffset: {offset2[index]}")
                    print(f"\t\tresistance_to_temperature:")

                    if "CCD" in mssl_name:
                        print(f"\t\t\tmethod: polynomial")
                        print(f"\t\t\ttemperature_to_resistance_coefficients: XXX")
                    else:
                        print(f"\t\t\tmethod: callendar_van_dusen")
                        print(f"\t\t\tstandard: EN60751")
                        print(f"\t\t\tref_resistance: 1000")


def print_supply_voltage_calibration(filename: str):
    table = pandas.read_excel(filename, sheet_name="HK & DAC Calibrations",
                              usecols="B, T, U, E, F",
                              names=["mssl_names", "gain1", "offset1", "gain2", "offset2"])

    mssl_names = table["mssl_names"]
    gain1 = table["gain1"]
    offset1 = table["offset1"]
    gain2 = table["gain2"]
    offset2 = table["offset2"]

    hk_name_mapping = read_conversion_dict(ORIGIN, use_site=False)

    for index in range(len(mssl_names)):
        mssl_name = mssl_names[index]

        if isinstance(mssl_name, str) and "[" in mssl_name and "]" in mssl_name:
            mssl_name = mssl_name.split("[")[0]
            egse_name = hk_name_mapping[mssl_name]

            is_temperature_calibration = "_T_" in egse_name or "TRP" in egse_name
            if not is_temperature_calibration:
                print(f"\t{egse_name}:")

                if not isnan(gain1[index]) and not isnan(offset1[index]):
                    print(f"\t\tgain: {gain1[index]}")
                    print(f"\t\toffset: {offset1[index]}")
                elif not isnan(gain2[index]) and not isnan(offset2[index]):
                    print(f"\t\tgain: {gain2[index]}")
                    print(f"\t\toffset: {offset2[index]}")


def print_n_fee_calibration(filename):
    print("temperatures:")
    # TODO Print sub-sections
    print_temperature_calibration(filename)

    print("")

    print("supply_voltages:")
    print_supply_voltage_calibration(filename)
