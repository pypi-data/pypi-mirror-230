import glob
import logging
import os.path
from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd
from pandas._libs.parsers import EmptyDataError
from pandas.errors import ParserError

from egse import h5
from egse.config import find_file
from egse.dpu.fitsgen import get_hdf5_filenames_for_obsid, get_od, create_fits_from_hdf5, add_synoptics
from egse.fee.n_fee_hk import ORIGIN as N_FEE_ORIGIN
from egse.fee.n_fee_hk import ORIGIN as ORIGIN_NFEE_HK
from egse.fee.n_fee_hk import get_calibrated_supply_voltages, get_calibrated_temperatures
from egse.fee.nfee import HousekeepingData
from egse.fov import ORIGIN as FOV_ORIGIN
from egse.hk import read_conversion_dict
from egse.obsid import ObservationIdentifier, obsid_from_storage
from egse.settings import Settings
from egse.setup import NavigableDict, Setup
from egse.spw import SpaceWirePacket
from egse.storage import HDF5
from egse.storage.persistence import CSV
from egse.synoptics import ORIGIN as SYN_ORIGIN
from egse.synoptics import read_hk_info as read_syn_info
from egse.tcs.tcs import ORIGIN as TCS_ORIGIN

LOGGER = logging.getLogger(__name__)

# sensor_cal_filename = "/Users/sara/work/Instrumentation/Plato/softwareDevelopment/plato-cgse-conf/data/nfee_sensor_calibration_em_v3.yaml"
# sensor_cal = NavigableDict(Settings.load(filename=sensor_cal_filename))#, add_local_settings=False))
# data_dir = "/STER/platodata/SRON/plato-data"
# site = "SRON"


# def reprocess_campaign(od_start: str, od_end: str, sensor_cal: NavigableDict, archive_dir: str, fixed_archive_dir: str,
#                        reprocessed_archive_dir: str):
#     """ Re-process the daily data in the given timespan.
#
#     Args:
#         - od_start:
#         - od_end
#         - archive_dir: Folder (with sub-folders /daily and /obs) in which the HK files are stored.
#         - fixed_archive_dir: Folder (with sub-folders /daily and /obs) in which the fixed HK files are stored.
#         - reprocessed_archive_dir: Folder (with sub-folders /daily and /obs) in which the re-processed files will be
#                                    stored.
#     """
#
#     delta = timedelta(days=1)
#     date_end = datetime.strptime(od_end, "%Y%m%d")  # The last OD to re-process [YYYYMMDD]
#     date = datetime.strptime(od_start, "%Y%m%d")    # The first OD to re-process [YYYYMMDD]
#
#     # Re-process the daily N-FEE HK (from the HDF5 files) + synoptics
#
#     while date <= date_end:
#
#         od = date.strftime("%Y%m%d")    # Current OD [YYYYMMDD]
#         # day_dir = Path(f"{archive_dir}/daily/{od}")  # Sub-folder with the data for the given OD
#
#         reprocess_od(od, sensor_cal, archive_dir, fixed_archive_dir, reprocessed_archive_dir)
#
#         date += delta


def reprocess_od(od: str, site: str, setup: Setup, archive_dir: str, fixed_archive_dir: str,
                 reprocessed_archive_dir: str):
    """ Re-processing for the given OD.

    This re-processing consists of the following steps:
        - Re-processing the N-FEE HK from the HDF5 files;
        - Re-processing the synoptics from the contributing (and potentially fixed) HK files.

    Args:
        - od: Observation day in the format YYYYMMDD.
        - site: Site ID (CSL/CSL1/CSL2/SRON/IAS/INTA).
        - setup: Setup from which to read all calibration information.
        - archive_dir: Folder (with sub-folders /daily and /obs) in which the HK files are stored.
        - fixed_archive_dir: Folder (with sub-folders /daily and /obs) in which the fixed HK files are stored.
        - reprocessed_archive_dir: Folder (with sub-folders /daily and /obs) in which the re-processed synoptics file
                                   will be stored.
    """

    fee_calibration = setup.camera.fee.calibration

    reprocess_daily_n_fee_hk(od, site, fee_calibration, archive_dir, reprocessed_archive_dir)       # N-FEE HK
    reprocess_daily_synoptics(od, site, archive_dir, fixed_archive_dir, reprocessed_archive_dir)    # Synoptics


def reprocess_obsid(obsid: Union[str, int, ObservationIdentifier], site: str, setup: Setup, archive_dir: str,
                    fixed_archive_dir: str, reprocessed_archive_dir: str):
    """ Re-processing for the given obsid.

    This re-processing consists of the following steps:
        - Re-processing the N-FEE HK from the HDF5 files;
        - Re-processing the synoptics from the contributing (and potentially fixed HK files);
        - Re-processing the FITS files from the HDF5 files and (re-processed) synoptics.

    Args:
        - obsid: Observation identifier.
        - site: Site ID (CSL/CSL1/CSL2/SRON/IAS/INTA).
        - setup: Setup from which to read all calibration information.
        - archive_dir: Folder (with sub-folders /daily and /obs) in which the HK files are stored.
        - fixed_archive_dir: Folder (with sub-folders /daily and /obs) in which the fixed HK files are stored.
        - reprocessed_archive_dir: Folder (with sub-folders /daily and /obs) in which the re-processed synoptics file
                                   will be stored.
    """

    fee_calibration = setup.camera.fee.calibration

    reprocess_obs_n_fee_hk(obsid, fee_calibration, archive_dir, reprocessed_archive_dir)            # N-FEE HK
    reprocess_obs_synoptics(obsid, site, archive_dir, fixed_archive_dir, reprocessed_archive_dir)   # Synoptics

    reprocess_ccd_data(obsid, archive_dir, reprocessed_archive_dir, setup)                          # FITS files


def reprocess_daily_n_fee_hk(od: str, site: str, fee_calibration: NavigableDict, archive_dir: str,
                             reprocessed_archive_dir: str):
    """ Re-processing the N-FEE HK for the given OD.

    The procedure is as follows:
        - Read the N-FEE HK information from the TM dictionary.  This comprises the name conversion from the original
          name (used by the N-FEE itself and in the HDF5 files) to the conventional name starting with "NFEE", and the
          calibration information for the supply voltages and temperatures.
        - Determine the filename for the N-FEE HK for the given OD.
        - Determine the list of HDF5 filenames acquired during the given OD.
        - Determine the column names to use in the new N-FEE HK file and create a new N-FEE HK file with these.
        - Loop over all these HDF5 files.  For each of them, read the uncalibrated values and apply the calibration,
          according to the given calibration information.  Then append the raw and calibrated values to the N-FEE HK
          file.

    Args:
        - od: Observation day in the format YYYYMMDD.
        - site: Site ID (CSL/CSL1/CSL2/SRON/IAS/INTA).
        - fee_calibration: Calibration data for the N-FEE HK.
        - archive_dir: Folder (with sub-folders /daily and /obs) in which the HDF5 files are stored.
        - reprocessed_archive_dir: Folder (with sub-folders /daily and /obs) in which the re-processed N-FEE HK files
                                   will be stored.
    """

    archive_od_dir = f"{archive_dir}/daily/{od}"
    reprocessed_archive_od_dir = f"{reprocessed_archive_dir}/daily/{od}"

    # Compose the list of HDF5 filenames for the given OD
    # If there are no HDF5 files, exit with a proper log message

    hdf5_filenames = glob.glob(f"{archive_od_dir}/*.{HDF5.extension}")
    if len(hdf5_filenames) == 0:
        LOGGER.info(f"No HDF5 files found in {archive_od_dir}")
        return

    # Use the same filename for the N-FEE HK as before, but store it in the re-processed archive now
    # (don't touch the old N-FEE HK file)

    n_fee_hk_filename = f"{reprocessed_archive_od_dir}/{od}_{site}_{N_FEE_ORIGIN}.{CSV.extension}"

    _reprocess_n_fee_hk(hdf5_filenames, n_fee_hk_filename, fee_calibration, reprocessed_archive_od_dir)


def reprocess_obs_n_fee_hk(obsid: Union[str, int, ObservationIdentifier], fee_calibration: NavigableDict,
                           archive_dir: str, reprocessed_archive_dir: str):
    """ Re-processing the synoptics for the given obsid.

    The procedure is as follows:
        - Read the N-FEE HK information from the TM dictionary.  This comprises the name conversion from the original
          name (used by the N-FEE itself and in the HDF5 files) to the conventional name starting with "NFEE", and the
          calibration information for the supply voltages and temperatures.
        - Determine the filename for the N-FEE HK for the given obsid.
        - Determine the list of HDF5 filenames acquired during the given obsid.
        - Determine the column names to use in the new N-FEE HK file and create a new N-FEE HK file with these.
        - Loop over all these HDF5 files.  For each of them, read the uncalibrated values and apply the calibration,
          according to the given calibration information.  Then append the raw and calibrated values to the N-FEE HK
          file.

    Args:
        - obsid: Observation identifier.
        - site: Site ID (CSL/CSL1/CSL2/SRON/IAS/INTA).
        - fee_calibration: Calibration data for the N-FEE HK.
        - archive_dir: Folder (with sub-folders /daily and /obs) in which the HDF5 files are stored.
        - reprocessed_archive_dir: Folder (with sub-folders /daily and /obs) in which the re-processed N-FEE HK files
                                   will be stored.
    """

    obsid = obsid_from_storage(obsid, archive_dir)

    archive_obsid_dir = f"{archive_dir}/obs/{obsid}"
    reprocessed_archive_obsid_dir = f"{reprocessed_archive_dir}/obs/{obsid}"

    # Compose the list of HDF5 filenames for the given obsid
    # If there are no HDF5 files, exit with a proper log message

    hdf5_filenames = get_hdf5_filenames_for_obsid(obsid, data_dir=archive_dir)
    if len(hdf5_filenames) == 0:
        LOGGER.info(f"No HDF5 files found for obsid {obsid}")
        return

    # Use the same filename for the N-FEE HK as before, but store it in the re-processed archive now
    # (don't touch the old N-FEE HK file)

    pattern = f"{obsid}_{N_FEE_ORIGIN}_*_*.csv"
    n_fee_hk_filename = find_file(pattern, root=archive_obsid_dir)
    if n_fee_hk_filename is None:
        od = get_od(obsid, archive_dir)[0]
        n_fee_hk_filename = f"{reprocessed_archive_obsid_dir}/{obsid}_{N_FEE_ORIGIN}_{od}.{CSV.extension}"
    else:
        n_fee_hk_filename = f"{reprocessed_archive_obsid_dir}/{n_fee_hk_filename.stem}.{CSV.extension}"

    _reprocess_n_fee_hk(hdf5_filenames, n_fee_hk_filename, fee_calibration, reprocessed_archive_obsid_dir)


def _reprocess_n_fee_hk(hdf5_filenames, n_fee_hk_filename: str, fee_calibration: NavigableDict):
    """ Re-processing the N-FEE HK.

    The procedure is as follows for the "hk" dataset in all groups of the given list of HDF5 files:
        - Extract the raw values from the SpW packets;
        - Re-name the extracted parameters to the corresponding synoptical name;
        - Apply the calibration for the supply voltages and temperatures;
        - Append a row to the N-FEE HK file with the raw and calibrated values.

    Args:
        - hdf5_filenames: Filenames of the HDF5 files containing the raw N-FEE HK.
        - n_fee_hk_filename: Filename for the re-processed N-FEE HK file.
        - fee_calibration: Calibration data for the N-FEE HK.
    """

    hk_names_mapping = read_conversion_dict(ORIGIN_NFEE_HK, use_site=False)

    supply_voltage_calibration = fee_calibration.supply_voltages
    temperature_calibration = fee_calibration.temperatures

    # name_conversion, n_fee_supply_voltage_cal = read_n_fee_hk_info()
    column_names = ["timestamp", *list(hk_names_mapping.values())]

    with CSV(filename=n_fee_hk_filename, prep={"column_names": column_names, "mode": 'w'}) as csv:

        for hdf5_filename in hdf5_filenames:

            with h5.get_file(hdf5_filename, mode="r") as hdf5_file:

                try:

                    for group in h5.groups(hdf5_file):

                        # Read the HK from the HDF5 groups and rename them

                        if "hk" in group:

                            # Create a dictionary in which we will gather all the raw and calibrated data for the
                            # timestamp in the current group of the current HDF5 file

                            values = {"timestamp": group["timecode"].attrs["timestamp"]}

                            hk_packet = SpaceWirePacket.create_packet(h5.get_data(group["hk"]))
                            hk_data = HousekeepingData(hk_packet.data)

                            for orig_name in hk_data:
                                try:
                                    new_name = hk_names_mapping[orig_name]
                                    values[new_name] = hk_data[orig_name]
                                except KeyError:
                                    pass

                            # Apply the correct calibration

                            calibrated_supply_voltages = get_calibrated_supply_voltages(values,
                                                                                        supply_voltage_calibration)
                            values.update(calibrated_supply_voltages)
                            calibrated_temperatures = get_calibrated_temperatures(values, temperature_calibration)
                            values.update(calibrated_temperatures)

                            # Store the new N-FEE HK

                            csv.create(values)
                except RuntimeError as exc:
                    LOGGER.warning(f"Problem occurred when reading HK from {hdf5_filename} ({exc}).  Skipping...")


def reprocess_daily_synoptics(od: str, site: str, archive_dir: str, fixed_archive_dir: str,
                              reprocessed_archive_dir: str):
    """ Re-processing the N-FEE HK for the given OD.

    The procedure is as follows:
        - Compose a list of HK files contributing to the synoptics.
        - Read those files one by one and concatenate them.
        - Sort the concatenated tables in order of ascending timestamp.
        - Store only the relevant columns in the synoptics file.

    Args:
        - od: Observation day in the format YYYYMMDD.
        - site: Site ID (CSL/CSL1/CSL2/SRON/IAS/INTA).
        - archive_dir: Folder (with sub-folders /daily and /obs) in which the HDF5 files are stored.
        - fixed_archive_dir: Folder (with sub-folders /daily and /obs) in which the fixed HK files are stored.
        - reprocessed_archive_dir: Folder (with sub-folders /daily and /obs) in which the re-processed N-FEE HK files
                                   will be stored.
    """

    archive_day_dir = f"{archive_dir}/daily/{od}"
    fixed_archive_day_dir = f"{fixed_archive_dir}/daily/{od}"
    reprocessed_archive_day_dir = f"{reprocessed_archive_dir}/daily/{od}"

    # Determine the filename for the HK that contribute to the synoptics
    #       - At this point, the N-FEE HK is re-processed already
    #       - Most of the other HK will be stored in the original archive, but some of it may be fixed (for some reason)

    syn_input_filenames = get_syn_input_filenames_od(od, site, archive_day_dir, fixed_archive_day_dir,
                                                     reprocessed_archive_day_dir)

    if len(syn_input_filenames) == 0:
        LOGGER.info(f"No HK files contributing the synoptics found in {archive_day_dir} nor {fixed_archive_day_dir}")
        return

    synoptics_filename = f"{reprocessed_archive_day_dir}/{od}_{site}_{SYN_ORIGIN}.{CSV.extension}"
    _reprocess_synoptics(syn_input_filenames, synoptics_filename)


def reprocess_obs_synoptics(obsid: Union[str, int, ObservationIdentifier], site: str, archive_dir: str,
                            fixed_archive_dir: str, reprocessed_archive_dir: str):
    """ Re-processing the N-FEE HK for the given obsid.

    The procedure is as follows:
        - Compose a list of HK files contributing to the synoptics.
        - Read those files one by one and concatenate them.
        - Sort the concatenated tables in order of ascending timestamp.
        - Store only the relevant columns in the synoptics file.

    Args:
        - obsid: Observation identifier.
        - site: Site ID (CSL/CSL1/CSL2/SRON/IAS/INTA).
        - archive_dir: Folder (with sub-folders /daily and /obs) in which the HDF5 files are stored.
        - fixed_archive_dir: Folder (with sub-folders /daily and /obs) in which the fixed HK files are stored.
        - reprocessed_archive_dir: Folder (with sub-folders /daily and /obs) in which the re-processed synoptics files
                                   will be stored.
        """

    obsid = obsid_from_storage(obsid, archive_dir)

    archive_obs_dir = f"{archive_dir}/obs/{obsid}"
    fixed_archive_obs_dir = f"{fixed_archive_dir}/obs/{obsid}"
    reprocessed_archive_obs_dir = f"{reprocessed_archive_dir}/obs/{obsid}"

    # Determine the filename for the HK that contribute to the synoptics
    #       - At this point, the N-FEE HK is re-processed already
    #       - Most of the other HK will be stored in the original archive, but some of it may be fixed (for some reason)

    syn_input_filenames = get_syn_input_filename_obs(obsid, site, archive_obs_dir, fixed_archive_obs_dir,
                                                     reprocessed_archive_obs_dir)

    if len(syn_input_filenames) == 0:
        LOGGER.info(f"No HK files contributing the synoptics found in {archive_obs_dir} nor {fixed_archive_obs_dir}")
        return

    pattern = f"{obsid}_{SYN_ORIGIN}_*_*.csv"
    synoptics_filename = find_file(pattern, root=archive_obs_dir)

    if not os.path.exists(f"{reprocessed_archive_obs_dir}"):
        os.makedirs(f"{reprocessed_archive_obs_dir}/{obsid}")

    if synoptics_filename is None:
        od = get_od(obsid, archive_dir)[0]
        synoptics_filename = f"{reprocessed_archive_obs_dir}/{obsid}_{SYN_ORIGIN}_{od}.{CSV.extension}"
    else:
        synoptics_filename = f"{reprocessed_archive_obs_dir}/{synoptics_filename.stem}.{CSV.extension}"

    _reprocess_synoptics(syn_input_filenames, synoptics_filename)


def _reprocess_synoptics(syn_input_filenames, synoptics_filename: str):
    """ Re-processing the synoptics.

    The procedure is as follows:
        - Compose a list of HK files contributing to the synoptics.
        - Read those files one by one and concatenate them.
        - Sort the concatenated tables in order of ascending timestamp.
        - Store only the relevant columns in the synoptics file.

    Args:
        - syn_input_filenames: Filenames of the HK files contributing to the synoptics.
        - synoptics_filename: Filename for the re-processed synoptics file.
    """

    syn_names, original_name_egse, original_name_th = read_syn_info()

    # Concatenate the content of all contributing HK files

    concatenated_hk = pd.DataFrame()

    for syn_input_filename in syn_input_filenames:
        try:
            syn_input_file = pd.read_csv(syn_input_filename)

            concatenated_hk = concatenated_hk.append(syn_input_file)
        except (ParserError, EmptyDataError) as exc:
            LOGGER.warning(f"Problem with the content of {syn_input_file} ({exc}).  "
                           f"The file is either empty or poorly formatted.  Skipping...")

    # Sort according to ascending timestamp

    concatenated_hk = concatenated_hk.sort_values(by=['timestamp'])

    # Convert the HK names to synoptical names (starting with "GSYN_")

    concatenated_hk = concatenated_hk.rename(columns=original_name_egse)
    concatenated_hk = concatenated_hk.rename(columns=original_name_th)

    # # Fill NaNs
    #
    # concatenated_hk = concatenated_hk.fillna(method="ffill")
    # # concatenated_hk = concatenated_hk.fillna(method="bfill")    # This is only relevant for the first few seconds

    available_syn_names = np.delete(syn_names, np.where(syn_names == "timestamp"))
    missing_syn_names = np.array([])

    for syn_name in available_syn_names:
        if syn_name not in concatenated_hk:
            available_syn_names = np.delete(available_syn_names, np.where(available_syn_names == syn_name))
            missing_syn_names = np.append(missing_syn_names, syn_name)

    # For numerical columns, use the mean; for boolean columns, use any (unless they are all NaN)

    # agg_dict = {syn_name: np.mean for syn_name in available_syn_names}
    #
    # def any_func(arr):
    #     if arr.isnull().values.all():
    #         return float('nan')
    #     return any(arr)
    #
    # def mean_func(arr):
    #     if arr.isnull().values.all():
    #         return float('nan')
    #     return np.nanmean(arr)
    #
    # agg_dict = {syn_name: mean_func for syn_name in available_syn_names}
    #
    # agg_dict["GSYN_OGSE_LAMP_ON"] = any_func
    # agg_dict["GSYN_OGSE_LASER_ON"] = any_func
    # agg_dict["GSYN_OGSE_SHUTTER_OPEN"] = any_func
    #
    # concatenated_hk = concatenated_hk.groupby("timestamp").agg(agg_dict)

    num_rows = len(concatenated_hk.index)
    for missing_syn_name in missing_syn_names:
        concatenated_hk[missing_syn_name] = [float('nan')] * num_rows

    concatenated_hk.to_csv(synoptics_filename, columns=syn_names, index=False)


def get_syn_input_filenames_od(od: str, site: str, archive_day_dir: str, fixed_archive_day_dir: str,
                               reprocessed_archive_day_dir: str):
    """ Return list of filenames for the HK files contributing to the synoptics of the given TH for the given OD.

    Returns: List of filenames for the HK files contributing to the synoptics of the given TH.

    Args:
        - od: Observation day in the format YYYYMMDD.
        - site: Site ID (CSL/CSL1/CSL2/SRON/IAS/INTA).
        - archive_day_dir: Folder in which the HK files are stored for the given OD.
        - fixed_archive_day_dir: Folder in which the fixed HK files are stored for the given OD.
        - reprocessed_archive_day_dir: Folder in which the re-processed synoptics file will be stored for the given OD.
    """

    syn_input_origins = get_syn_input_origins(site)
    return get_syn_input_filenames_from_origins_od(syn_input_origins, od, site, archive_day_dir, fixed_archive_day_dir,
                                                   reprocessed_archive_day_dir)


def get_syn_input_filename_obs(obsid: str, site: str, archive_obs_dir: str, fixed_archive_obs_dir: str,
                               reprocessed_archive_obs_dir: str):
    """ Return list of filenames for the HK files contributing to the synoptics of the given TH for the given obsid.

    Returns: List of filenames for the HK files contributing to the synoptics of the given TH.

    Args:
        - obsid: Observation identifier.
        - site: Site ID (CSL/CSL1/CSL2/SRON/IAS/INTA).
        - archive_obs_dir: Folder in which the HK files are stored for the given obsid.
        - fixed_archive_obs_dir: Folder in which the fixed HK files are stored for the given obsid.
        - reprocessed_archive_obs_dir: Folder in which the re-processed synoptics file will be stored for the given
                                       obsid.
    """

    syn_input_origins = get_syn_input_origins(site)
    return get_syn_input_filenames_from_origins_obs(syn_input_origins, obsid, archive_obs_dir,
                                                    fixed_archive_obs_dir, reprocessed_archive_obs_dir)


def get_syn_input_origins(site: str):
    """ Return list of storage mnemonics for the HK files contributing to the synoptics at the given TH.

    Returns: List of storage mnemonics for the HK files contributing to the synoptics at the given TH.
    """

    # Non-TH-specific HK files:
    #   - N-FEE HK (potentially re-processed)
    #   - FOV HK

    common_syn_input_origins = [N_FEE_ORIGIN, FOV_ORIGIN]

    # TH-specific HK files

    sitehash = {
        "CSL": csl_get_syn_input_origins,
        "CSL1": csl_get_syn_input_origins,
        "CSL2": csl_get_syn_input_origins,
        "IAS": ias_get_syn_input_origins,
        "INTA": inta_get_syn_input_origins,
        "SRON": sron_get_syn_input_origins,
    }

    th_syn_input_origins = sitehash[site]()

    return [*common_syn_input_origins, *th_syn_input_origins]


def csl_get_syn_input_origins():
    """ Return list of storage mnemonics for the HK files contributing to the synoptics specifically for CSL.

    Returns: List of storage mnemonics for the HK files contributing to the synoptics specifically for CSL.
    """

    return ["OGSE"]
        #[Settings.load("OGSE Control Server").STORAGE_MNEMONIC]


def sron_get_syn_input_origins():
    """ Return list of storage mnemonics for the HK files contributing to the synoptics specifically for SRON.

    Returns: List of storage mnemonics for the HK files contributing to the synoptics specifically for SRON.
    """

    return [TCS_ORIGIN,
            Settings.load("BeagleBone Lamp Control Server").STORAGE_MNEMONIC,
            Settings.load("Thorlabs PM100 Control Server").STORAGE_MNEMONIC,
            Settings.load("Standa 8SMC5 Control Server").STORAGE_MNEMONIC,
            Settings.load("Thorlabs SC10 Control Server").STORAGE_MNEMONIC,
            Settings.load("Agilent 34970 Control Server").DAQ0["STORAGE_MNEMONIC"],
            Settings.load("Agilent 34970 Control Server").DAQ1["STORAGE_MNEMONIC"],
            Settings.load("Agilent 34972 Control Server").DAQ0["STORAGE_MNEMONIC"],
            Settings.load("Agilent 34972 Control Server").DAQ1["STORAGE_MNEMONIC"]]


def ias_get_syn_input_origins():
    """ Return list of storage mnemonics for the HK files contributing to the synoptics specifically for IAS.

    Returns: List of storage mnemonics for the HK files contributing to the synoptics specifically for IAS.
    """

    return [TCS_ORIGIN,
            f"DAS-{Settings.load('Keithley Control Server').STORAGE_MNEMONIC}",
            f"DAS-{Settings.load('SRS PTC10 Control Server').STORAGE_MNEMONIC}",
            Settings.load("Lamp EQ99 Control Server").STORAGE_MNEMONIC,
            Settings.load("Thorlabs PM100 Control Server").STORAGE_MNEMONIC,
            "KSC101"]


def inta_get_syn_input_origins():
    """ Return list of storage mnemonics for the HK files contributing to the synoptics specifically for INTA.

    Returns: List of storage mnemonics for the HK files contributing to the synoptics specifically for INTA.
    """

    # return [TCS_ORIGIN,
    #         ]
    raise NotImplementedError


def get_syn_input_filenames_from_origins_od(origins: list, od: str, site: str, archive_day_dir: str,
                                            fixed_archive_day_dir: str, reprocessed_archive_day_dir: str):
    """
    Return list of filenames for the given OD for the given list of origins.

    Returns: List of filenames for the given OD for the given list of origins.

    Args:
        - origins: List of storage mnemonics for the HK files contributing to the synoptics at the given TH.
        - od: Observation day in the format YYYYMMDD.
        - site: Site ID (CSL/CSL1/CSL2/SRON/IAS/INTA).
        - archive_day_dir: Folder in which the HK files are stored for the given OD.
        - fixed_archive_day_dir: Folder in which the fixed HK files are stored for the given OD.
        - reprocessed_archive_day_dir: Folder in which the re-processed synoptics file will be stored for the given OD.
    """

    filenames = []

    for origin in origins:

        filename = f"{od}_{site}_{origin}.{CSV.extension}"

        # The N-FEE HK must be re-processed already

        if origin == N_FEE_ORIGIN:
            if Path(f"{reprocessed_archive_day_dir}/{filename}").is_file():
                filenames.append(f"{reprocessed_archive_day_dir}/{filename}")
            else:
                LOGGER.debug(f"No re-processed N-FEE HK available in {reprocessed_archive_day_dir}")

        # For all other HK: first check whether there is a fixed version.  If there is one, use that; otherwise, use
        # the original version from the archive (if that is available).

        else:

            if Path(f"{fixed_archive_day_dir}/{filename}").is_file():
                filenames.append(f"{fixed_archive_day_dir}/{filename}")
                LOGGER.debug(f"Using the fixed HK for {origin}")
            elif Path(f"{archive_day_dir}/{filename}").is_file():
                filenames.append(f"{archive_day_dir}/{filename}")
                LOGGER.debug(f"Using the originally archived HK for {origin}")
            else:
                LOGGER.debug(f"No HK file available for {origin}, neither in {fixed_archive_day_dir} nor "
                             f"{archive_day_dir}")

    return filenames


def get_syn_input_filenames_from_origins_obs(origins: list, obsid: str, archive_obs_dir: str,
                                             fixed_archive_obs_dir: str, reprocessed_archive_obs_dir: str):
    """ Return list of filenames for the given obsid for the given list of origins.

    Returns: List of filenames for the given obsid for the given list of origins.

    Args:
        - origins: List of storage mnemonics for the HK files contributing to the synoptics at the given TH.
        - obsid: Observation identifier.
        - archive_obs_dir: Folder in which the HK files are stored for the given obsid.
        - fixed_archive_obs_dir: Folder in which the fixed HK files are stored for the given obsid.
        - reprocessed_archive_obs_dir: Folder in which the re-processed synoptics file will be stored for the given
                                       obsid.
    """

    filenames = []

    for origin in origins:

        pattern = f"{obsid}_{origin}_*_*.{CSV.extension}"
        filename = find_file(pattern, root=reprocessed_archive_obs_dir)

        if filename is None:

            filename = find_file(pattern, root=fixed_archive_obs_dir)

            if filename is None:
                filename = find_file(pattern, root=archive_obs_dir)

                if filename is None:
                    LOGGER.debug(f"No HK file available for {origin}, neither in {fixed_archive_obs_dir} nor "
                                 f"{archive_obs_dir}")
                else:
                    filenames.append(f"{archive_obs_dir}/{filename}")
                    LOGGER.debug(f"Using the originally archived HK for {origin}")
            else:
                filenames.append(f"{fixed_archive_obs_dir}/{filename.stem}.{CSV.extension}")
                LOGGER.debug(f"Using the fixed HK for {origin}")

        else:
            filenames.append(f"{fixed_archive_obs_dir}/{filename.stem}.{CSV.extension}")
            LOGGER.debug(f"Using the re-processed HK for {origin}")

    return filenames


def reprocess_ccd_data(obsid: str, archive_dir: str, reprocessed_archive_dir: str, setup: Setup):
    """ Re-processing of the CCD data for the given obsid.

    Args:
        - obsid: Observation identifier.
        - archive_dir: Folder (with sub-folders /daily and /obs) in which the HDF5 and HK files are stored.
        - fixed_archive_dir: Folder (with sub-folders /daily and /obs) in which the fixed HK files are stored.
        - reprocessed_archive_dir: Folder (with sub-folders /daily and /obs) in which the re-processed files will be
                                   stored.
    """

    hdf5_filenames = get_hdf5_filenames_for_obsid(obsid, data_dir=archive_dir)
    create_fits_from_hdf5(hdf5_filenames, location=reprocessed_archive_dir, setup=setup)
    add_synoptics(obsid, data_dir=reprocessed_archive_dir)
