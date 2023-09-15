# import glob
# import os
#
# from egse import h5
# from egse.dpu.fitsgen import in_data_acquisition_mode
# import natsort
#
# from egse.dpu.hdf5_ui import GroupPropertiesModel
# from egse.dpu.hdf5_viewer import ndarray_to_str
# from egse.spw import DataPacket
# # from camtest import start_observation, end_observation
# from egse.storage import HDF5
# from egse.state import GlobalState
# import rich
#
#
#
# # # def test_fitsgen():
# # #
#     from camtest import *
#
#
#
# setup = GlobalState.setup
#
#     from camtest.commanding import dpu
#
#     execute(dpu.set_slicing, num_cycles=2)
#
#     n_fee_parameters = dict(
#         num_cycles=5,
#         row_start=2000,
#         row_end=3500,
#         rows_final_dump=4510,
#         ccd_order=[2, 2, 2, 2],
#         ccd_side="E",
#         exposure_time=0.276140
#     )
#
#     execute(dpu.n_cam_partial_int_sync, **n_fee_parameters) # 309
#
#     from astropy.io import fits
#     filename = "/STER/platodata/SRON/plato-data/obs/02088_SRON_00041/02088_SRON_00041_N-FEE_CCD_20211128_205907_cube_00001.fits"    # Doesn't work
#     filename = "/STER/platodata/IAS/data/IAS/obs/00227_IAS/00227_IAS_N-FEE_CCD_00001_20220624_cube.fits"    # Does work
#
#
#
#     # filename = "/STER/platodata/IAS/archive/IAS/obs/00698_IAS/00698_IAS_N-FEE_CCD_00002_20220801_cube.fits"
#
#     # filename = "/Users/sara/work/Instrumentation/Plato/cgse/data/storage/obs/00424_CSL/00424_CSL_N-FEE_CCD_00002_20220603_cube.fits"
#     # filename = "/Users/sara/work/Instrumentation/Plato/cgse/data/storage/obs/00421_SRON/00421_SRON_N-FEE_CCD_00001_20220426_cube.fits"
#     # filename = "/STER/platodata/SRON/plato-data/obs/03054_SRON/03054_SRON_N-FEE_CCD_00107_20220224_cube.fits"
#
#     filename = "/STER/platodata/IAS/data/IAS/obs/00547_IAS/00547_IAS_N-FEE_CCD_00002_20220720_cube.fits"
#     with fits.open(filename) as hdu:
#         hdu.info()
#         # rich.print(hdu["PRIMARY"].header)
# #
# # #     start_observation("FITS generation test")
# # #     dpu.n_cam_partial_int_sync(**n_fee_parameters)
# # #     dpu.n_cam_partial_int_sync(**n_fee_parameters)
# # #     end_observation()
# # #
# # #     from astropy.io import fits
# # #
# # #     # filename = f"/Users/sara/work/Instrumentation/Plato/cgse/data/storage/obs/{filename}"
# # #     filename = "00314_CSL_00082_N-FEE_CCD_20211005_114146_cube_00001.fits"
# # #     # filename = "00315_CSL_00082_N-FEE_CCD_20211005_114620_00001.fits"
# # #     # filename = "00316_CSL_00082_N-FEE_CCD_20211005_115620_00001.fits"
# # #     # filename = "00320_CSL_00082_N-FEE_CCD_20211005_123444_00001.fits"
# # #     filename = "00323_CSL_00082_N-FEE_CCD_20211005_130719_00001.fits"
# # #     filename = "00323_CSL_00082_N-FEE_CCD_20211005_130719_cube_00001.fits"
# # #
# # #
# # #     filename = "00847_CSL_00086_N-FEE_CCD_20211011_133546_cube_00001.fits"
# # #     filename = f"/STER/platodata/CSL/obs/{filename}"
# # #     # filename = f"/Users/sara/work/Instrumentation/Plato/cgse/data/storage/obs/{filename}"
# # #
# # #     with fits.open(filename) as hdul:
# # #         hdul.info()
# #
# #
# # hdf5_filename = "/Users/sara/847/newfits/00813_CSL_00086_N-FEE_SPW_20211007_085422_00001.hdf5"
# # hdf5_file = h5.get_file(hdf5_filename)
# #
# # for group in h5.groups(hdf5_file):
# #
# #     if "data" in group.keys():
# #
# #         print(f"Data: {group.keys()}")
# #
# #         n_fee_state = group["data"].attrs
# #
# #         is_in_data_acquisition_mode = in_data_acquisition_mode(n_fee_state)
# #         print(f"In data acquisition mode: {is_in_data_acquisition_mode}")
# #
# #         data = group["data"]
# #         sorted_datasets = natsort.natsorted(data.items(), key=lambda x: x[0])
# #
# #         expected_id = 0
# #         for identifier, dataset in sorted_datasets:
# #             # print(f"Identifier: {identifier}")
# #             if int(identifier) != expected_id:
# #                 print(f"Identifier order problem: {identifier} vs {expected_id}")
# #             expected_id += 1
# #             # spw_packet = SpaceWirePacket.create_packet(h5.get_data(dataset))
# #             # persistence.create({f"SpW packet {identifier}": spw_packet})
# #
# # hdf5_file.close()
# #
# #
# # from egse.dpu.fitsgen import create_fits_from_hdf5
# #
# # # 2441: 20220126_SRON_N-FEE_SPW_03025.hdf5’ ⟶ ‘20220126_SRON_N-FEE_SPW_03557.hdf5
# #
# # hdf5_filenames = []
# # location = "/STER/platodata/SRON/plato-data/daily/20220126"
# #
# # for hdf5_index in range(3025, 3557+1):
# #
# #     hdf5_filenames.append(f"{location}/20220126_SRON_N-FEE_SPW_{hdf5_index:05d}.hdf5")
# #
# # create_fits_from_hdf5(hdf5_filenames)
# #
# #
# # # 2423: ‘20220125_SRON_N-FEE_SPW_01087.hdf5’ ⟶ ‘20220125_SRON_N-FEE_SPW_02401.hdf5’
# #
# # hdf5_filenames = []
# # location = "/STER/platodata/SRON/plato-data/daily/20220125"
# #
# # for hdf5_index in range(1087, 2401+1):
# #
# #     hdf5_filenames.append(f"{location}/20220125_SRON_N-FEE_SPW_{hdf5_index:05d}.hdf5")
# #
# # create_fits_from_hdf5(hdf5_filenames)
# #
# #
# #
# #
# # # 2442: ‘20220126_SRON_N-FEE_SPW_03698.hdf5’ ⟶ ‘20220126_SRON_N-FEE_SPW_05106.hdf5’
# #
# # hdf5_filenames = []
# # location = "/STER/platodata/SRON/plato-data/daily/20220126"
# #
# # for hdf5_index in range(3698, 5106+1):
# #
# #     hdf5_filenames.append(f"{location}/20220126_SRON_N-FEE_SPW_{hdf5_index:05d}.hdf5")
# #
# # create_fits_from_hdf5(hdf5_filenames)
# #
# # # 2408: ‘20220124_SRON_N-FEE_SPW_00146.hdf5’ ⟶ ‘20220124_SRON_N-FEE_SPW_00292.hdf5’
# # # (the last file is corrupt!)
# #
# # hdf5_filenames = []
# # location = "/STER/platodata/SRON/plato-data/daily/20220124"
# #
# # for hdf5_index in range(146, 292+1):
# #
# #     hdf5_filenames.append(f"{location}/20220124_SRON_N-FEE_SPW_{hdf5_index:05d}.hdf5")
# #
# # create_fits_from_hdf5(hdf5_filenames)
# #
# #
# # filename = "/Users/sara/work/Instrumentation/Plato/cgse/data/storage/daily/20220126/20220126_CSL_N-FEE_SPW_00186.hdf5"
# # hdf5_file = h5.get_file(filename, mode="r")
# #
# # for group in h5.groups(hdf5_file):
# #
# #     if "data" in group.keys():
# #
# #         print(group["data"].attrs["sensor_sel"])
# #
# # hdf5_file.close()
# #
# # hdf5_filename = "/Users/sara/work/Instrumentation/Plato/cgse/data/storage/daily/20220128/20220128_CSL_N-FEE_SPW_00771.hdf5"
# # hdf5_file = h5.get_file(hdf5_filename, mode="r")
# # if "obsid" in hdf5_file:
# #     obsid = hdf5_file["obsid"][()].decode()
# # hdf5_file.close()
# #
# #
# #
# # # from camtest import *
# # # from egse.dpu.fitsgen import create_fits_from_hdf5
# # #
# # # setup = load_setup
# # #
# # # # 2614: ‘20220201_SRON_N-FEE_SPW_20949.hdf5’ ⟶ ‘20220201_SRON_N-FEE_SPW_20965.hdf5’
# # # # (the last file is corrupt!)
# # #
# # # hdf5_filenames = []
# # # location = "/STER/platodata/SRON/plato-data/daily/20220201"
# # #
# # # for hdf5_index in range(20949, 20965+1):
# # #
# # #     hdf5_filenames.append(f"{location}/20220201_SRON_N-FEE_SPW_{hdf5_index:05d}.hdf5")
# # #
# # # create_fits_from_hdf5(hdf5_filenames)
# # #
# # #
# # # #########
# # #
# # # from camtest import *
# # # from egse.dpu.fitsgen import create_fits_from_hdf5
# # # import os
# # #
# # # setup = load_setup()
# #
# # os.environ["PLATO_DATA_STORAGE_LOCATION"] = "/STER/platodata/SRON/plato-data"
# #
# # # 2612: ‘20220201_SRON_N-FEE_SPW_20840.hdf5’ ⟶ ‘20220201_SRON_N-FEE_SPW_20855.hdf5’
# # # (the last file is corrupt!)
# #
# # hdf5_filenames = []
# # location = "/STER/platodata/SRON/plato-data/daily/20220201"
# #
# # for hdf5_index in range(20840, 20855+1):
# #
# #     hdf5_filenames.append(f"{location}/20220201_SRON_N-FEE_SPW_{hdf5_index:05d}.hdf5")
# #
# # create_fits_from_hdf5(hdf5_filenames)
# #
# #
# # # 2615: ‘20220201_SRON_N-FEE_SPW_20982.hdf5’ ⟶ ‘20220201_SRON_N-FEE_SPW_21094.hdf5’
# # # (the last file is corrupt!)
# #
# # hdf5_filenames = []
# # location = "/STER/platodata/SRON/plato-data/daily/20220201"
# #
# # for hdf5_index in range(20982, 21094+1):
# #
# #     hdf5_filenames.append(f"{location}/20220201_SRON_N-FEE_SPW_{hdf5_index:05d}.hdf5")
# #
# # create_fits_from_hdf5(hdf5_filenames)
# #
# #
# # # 2620: ‘20220202_SRON_N-FEE_SPW_01102.hdf5’ ⟶ ‘20220202_SRON_N-FEE_SPW_02074.hdf5’
# # # (the last file is corrupt!)
# #
# # hdf5_filenames = []
# # location = "/STER/platodata/SRON/plato-data/daily/20220202"
# #
# # for hdf5_index in range(1102, 2074+1):
# #
# #     hdf5_filenames.append(f"{location}/20220202_SRON_N-FEE_SPW_{hdf5_index:05d}.hdf5")
# #
# # create_fits_from_hdf5(hdf5_filenames)
# #
# #
# #
# #
# #
# #
# # # 2623: ‘20220202_SRON_N-FEE_SPW_02207.hdf5’ ⟶ ‘20220202_SRON_N-FEE_SPW_02766.hdf5’
# # # (the last file is corrupt!)
# #
# # hdf5_filenames = []
# # location = "/STER/platodata/SRON/plato-data/daily/20220202"
# #
# # for hdf5_index in range(2207, 2766+1):
# #
# #     hdf5_filenames.append(f"{location}/20220202_SRON_N-FEE_SPW_{hdf5_index:05d}.hdf5")
# #
# # create_fits_from_hdf5(hdf5_filenames)
# #
# #
# # from egse.dpu.fitsgen import get_hdf5_filenames_for_obsid
# #
# # os.environ["PLATO_DATA_STORAGE_LOCATION"] = "/STER/platodata/SRON/plato-data"
# # # for_obsid("02620_SRON")
# #
# # hdf5_filenames = get_hdf5_filenames_for_obsid("02620_SRON", data_dir="/STER/platodata/SRON/plato-data")
# # create_fits_from_hdf5(hdf5_filenames)
# #
# # filename = "/STER/platodata/SRON/plato-data/obs/02607_SRON/02607_SRON_N-FEE_CCD_00002_20220201_cube.fits"
# #
# # from astropy.io import fits
# # filename = "/STER/platodata/SRON/plato-data/obs/02607_SRON/02607_SRON_N-FEE_CCD_00002_20220201_cube.fits"
# #
# # filename = "/Users/sara/work/Instrumentation/Plato/cgse/data/storage/SRON_00043_02156/SRON_00043_02156_N-FEE_CCD_20211201_cube_00001.fits"
# # from astropy.wcs import WCS
# # f = fits.open(filename)
# #
# #
# # h = f[2].header
# # # h["CTYPE3"] = "VOPT"
# # # h.pop("CUNIT3")
# # w = WCS(h, f)
# #
# # #
# # # w = WCS(f[1].header)
# # # w = WCS(f[2].header, fix=True)
# #
# # h.pop("CRPIX3")
# # h.pop("CRVAL3")
# #
# #
# # h.pop("PS3_0")  # "WCS-TAB_3_E"
# # h.pop("PS3_1")  # "WCS-TIME"
# # h.pop("CTYPE3")  # "TIME-TAB"
# #
# # h["PS3_0a"] = "WCS-TAB_3_E"
# # h["PS3_1a"] = "TIME"
# # # h["CTYPE3"] = "TIME-TAB"
# #
# # w = WCS(h, f)
# # w.pixel_to_world_values(0,-3852,2)
# # f.close()
# #
# #
# #
# # # 2623: ‘20220202_SRON_N-FEE_SPW_02207.hdf5’ ⟶ ‘20220202_SRON_N-FEE_SPW_03284.hdf5’
# # # (the last file is corrupt!)
# #
# # hdf5_filenames = []
# #
# # location = "/STER/platodata/SRON/plato-data/daily/20220202"
# #
# # for hdf5_index in range(2723, 3284+1):
# #
# #     hdf5_filenames.append(f"{location}/20220202_SRON_N-FEE_SPW_{hdf5_index:05d}.hdf5")
# #
# # create_fits_from_hdf5(hdf5_filenames)
# #
# # time_axis = [0., 6.24216413, 12.50460601]
# # index_axis = [0, 1, 2]
# # index_column = fits.Column("INDEX", format="E", array=index_axis)
# # time_column = fits.Column("TIME", format="F", array=time_axis)
# #
# # coldefs = fits.ColDefs([index_column, time_column])
# # hdu = fits.BinTableHDU.from_columns(coldefs)
# #
# #
# # time_table = fits.BinTableHDU.from_columns([time_column], nrows=0)
# # time_table.header["EXTNAME"] = f"WCS-TAB_{3}_{'E'}"
# #
# # time_table.data
# #
# #
# # from rich.progress import track
# # import time
# # for index in track(range(10), description=f"Checking {10} files"):
# #     print("Test")
# #     # time.sleep(3)
# #
# #
# # filename = "/Users/sara/test-16bit.fits"
# #
# # primary_hdu = fits.PrimaryHDU()
# # primary_hdu.writeto(filename)
# #
# # import numpy as np
# # image = np.array([[0, 65535], [0, 65535]], dtype=np.uint16)
# # image_header = fits.Header()
# # image_header["SIMPLE"] = "T"
# # image_header["BITPIX"] = 16
# # image_header["BZERO"] = 32768
# # fits.append(filename, image, image_header)
# # fits.append(filename, image, image_header)
# # with fits.open(filename) as f:
# #     f.info()
# #
# #     print((f[1].data))
# #     print(f[1].header)
# #
# # f = fits.open(filename)
# #
# # stripped_filename = "/Users/sara/tab-fits3.fits"
# #
# # primary_hdu = f[0].writeto(stripped_filename)
# # data = f[2].data[:2]
# # header = f[2].header
# # header["NAXIS1"] = 2
# # fits.append(stripped_filename, data, header)
# #
# # time_axis = np.array([0.1, 6.24216413])
# # time_column = fits.Column("TIME", format="F", array=time_axis)
# # time_table = fits.BinTableHDU.from_columns([time_column])
# # time_table.header["EXTNAME"] = "WCS-TAB_3_E"
# # fits.append(stripped_filename, time_table.data, time_table.header)
# #
# # f.close()
# # f = fits.open(stripped_filename)
# # f.info()
# #
# # w = WCS(f[1].header)
# #
# # f.close()
# # # fits.append(stripped_filename, f[2].data, f[2].header)
# # # fits.append(stripped_filename, f[1].data, f[1].header)
# #
# # hdul = fits.open(stripped_filename)
# # wcs = WCS(hdul[1].header)
# #
# # header = f[2].header
# # # header.pop("PS3_0")
# # header.pop("CTYPE3")
# # wcs = WCS(header, naxis=2)
# #
# #
# #
# # hdf5_filenames = []
# # location = "/STER/platodata/SRON/plato-data/daily/20220211"
# #
# # for hdf5_index in range(16409, 17595+1):
# #
# #     hdf5_filenames.append(f"{location}/20220211_SRON_N-FEE_SPW_{hdf5_index:05d}.hdf5")
# #
# # # create_fits_from_hdf5(hdf5_filenames, setup=setup)
# #
# #
# # from egse.visitedpositions import visit_field_angles
# # import numpy as np
# #
# # vtheta = np.array([1.,3.,7.,10.,13.,16., 16.5,17.,17.5,17.7,17.9, 18.,18.2,18.4,18.6,18.8, 18.88,18.95,19.0])
# # vphi = np.array([-135, 135, 45, -45])
# #
# # for theta in vtheta:
# #     for phi in vphi[0:1]:
# #         visit_field_angles(theta, phi)
# #
# #
# # filename = "/STER/platodata/SRON/plato-data/obs/03024_SRON/03024_SRON_N-FEE_CCD_00001_20220223_cube.fits"
# #
# #
# # with fits.open(filename) as f:
# #     f.info()
# #
# #
# # # Normal dark
# #
# # filename_sat = "/STER/platodata/SRON/plato-data/obs/03054_SRON/03054_SRON_N-FEE_CCD_00003_20220224_cube.fits"
# #
# # with fits.open(filename_sat) as f:
# #     f.info()
# #
# # filename_sat1 = "/STER/platodata/SRON/plato-data/obs/03054_SRON/03054_SRON_N-FEE_CCD_00078_20220224_cube.fits"
# # filename_sat2 = "/STER/platodata/SRON/plato-data/obs/03054_SRON/03054_SRON_N-FEE_CCD_00079_20220224_cube.fits"
# # filename_sat3 = "/STER/platodata/SRON/plato-data/obs/03054_SRON/03054_SRON_N-FEE_CCD_00080_20220224_cube.fits"
# #
# # with fits.open(filename_sat1) as f:
# #     f.info()
# #
# # with fits.open(filename_sat2) as f:
# #     f.info()
# #
# # with fits.open(filename_sat3) as f:
# #     f.info()
# from egse.fee import fee_side
# import numpy as np
# from astropy.io import fits
#
# from egse.system import time_since_epoch_1958
#
# fits_filename = "/STER/platodata/SRON/plato-data/obs/02915_SRON/02915_SRON_N-FEE_CCD_00001_20220211_cube.fits"
# fits_file = fits.open(fits_filename)
#
# absolute_time = {}
# # start_time = time_since_epoch_1958(fits_file["PRIMARY"].header["DATE-OBS"])   # TODO
# start_time = 0
#
# for ccd_number in range(1, 5):
#
#     for ccd_side in fee_side:
#
#         try:
#             absolute_time[f"{ccd_number}{ccd_side.name[0]}"] = \
#                 np.array(fits_file[f"WCS-TAB_{ccd_number}_{fee_side(ccd_side).name[0]}"].data["TIME"]) + start_time
#         except KeyError:
#             pass
#
# # Lost data should be replaced by dummy frame (with NaNs)
#
#
# # Duration: time between subsequent readouts of the same side of the same CCD
# # TODO What should we do with the last or only frame?
#
# filename = "/STER/platodata/SRON/plato-data/obs/03054_SRON/03054_SRON_N-FEE_CCD_00107_20220224_cube.fits"
# fits_file = fits.open(filename)
# fits_file.info()
# data = fits_file[12].data
# print(np.min(data), np.max(data))
# fits_file.close()
#
#
# from egse.fee.n_fee_hk import get_calibrated_ccd_temperatures
# from egse.settings import Settings
# from egse.setup import NavigableDict
#
# sensor_cal_filename = "/Users/sara/work/Instrumentation/Plato/softwareDevelopment/plato-cgse-conf/data/nfee_sensor_calibration_em_v3.yaml"
# sensor_cal = NavigableDict(Settings.load(filename=sensor_cal_filename))#, add_local_settings=False))
#
# # 09.02.22 18:15
#
# current_data = {
#     "NFEE_T_CCD2_RAW": 3338,
#     "NFEE_T_CCD3_RAW": 3297,
#     "NFEE_T_CCD4_RAW": 3283,
#     "NFEE_T_CCD1_RAW": 3337
# }
#
# calibrated_ccd_temperatures = get_calibrated_ccd_temperatures(current_data, sensor_cal)
# print(f"Calibrated temperatures for 09.02.22 18:15 (degCelsius):")
# for key, item in calibrated_ccd_temperatures.items():
#     print(f"- {key}: {item}")
#
#
# # 07.02.22 17:00
#
# current_data = {
#     "NFEE_T_CCD2_RAW": 3526,
#     "NFEE_T_CCD3_RAW": 3482,
#     "NFEE_T_CCD4_RAW": 3469,
#     "NFEE_T_CCD1_RAW": 3525
# }
#
# calibrated_ccd_temperatures = get_calibrated_ccd_temperatures(current_data, sensor_cal)
# print(f"Calibrated temperatures for 07.02.22 17:00 (degCelsius):")
# for key, item in calibrated_ccd_temperatures.items():
#     print(f"- {key}: {item}")
#
# # 03.02.22 19:20
#
# current_data = {
#     "NFEE_T_CCD2_RAW": 3709,
#     "NFEE_T_CCD3_RAW": 3669,
#     "NFEE_T_CCD4_RAW": 3648,
#     "NFEE_T_CCD1_RAW": 3706
# }
#
# calibrated_ccd_temperatures = get_calibrated_ccd_temperatures(current_data, sensor_cal)
# print(f"Calibrated temperatures for 03.02.22 19:20 (degCelsius):")
# for key, item in calibrated_ccd_temperatures.items():
#     print(f"- {key}: {item}")
#
# # filename1 = "/Users/sara/Downloads/20220607_IAS_N-FEE_SPW_00036.hdf5"
# # filename2 = "/Users/sara/Downloads/20220607_IAS_N-FEE_SPW_00037.hdf5"
# # filename3 = "/Users/sara/Downloads/20220607_IAS_N-FEE_SPW_00038.hdf5"
# # filename4 = "/Users/sara/Downloads/20220607_IAS_N-FEE_SPW_00039.hdf5"
#
# filename1 = "/STER/platodata/IAS/archive/IAS/daily/20220420/20220420_IAS_N-FEE_SPW_00119.hdf5"
# filename2 = "/STER/platodata/IAS/archive/IAS/daily/20220420/20220420_IAS_N-FEE_SPW_00120.hdf5"
# filename3 = "/STER/platodata/IAS/archive/IAS/daily/20220420/20220420_IAS_N-FEE_SPW_00121.hdf5"
# # filename2 = "/Users/sara/Downloads/20220607_IAS_N-FEE_SPW_00037.hdf5"
# # filename3 = "/Users/sara/Downloads/20220607_IAS_N-FEE_SPW_00038.hdf5"
# # filename4 = "/Users/sara/Downloads/20220607_IAS_N-FEE_SPW_00039.hdf5"
# #
# # # filename1 = "/STER/platodata/IAS/data/IAS/daily20220607_IAS_N-FEE_SPW_00036.hdf5"
# # # filename2 = "/STER/platodata/IAS/data/IAS/daily/20220607_IAS_N-FEE_SPW_00037.hdf5"
# #
# # hdf5_filenames = [filename1, filename2, filename3, filename4]
# # from camtest import load_setup
# # from egse.dpu.fitsgen import *
# # setup = load_setup(53)
# #
# # create_fits_from_hdf5(hdf5_filenames, setup=setup)
# # add_synoptics(obsid)
# #
# # fits_filename = "/Users/sara/work/Instrumentation/Plato/cgse/data/storage/obs/IAS_00067/IAS_00067_N-FEE_CCD_00004_20220607_cube.fits"
#
# from camtest import *
# from egse.dpu.fitsgen import *
# setup = GlobalState.setup
# location = "/STER/platodata/IAS/archive/IAS/"
# # f"{obsid:05d}"
#
# obsid = "00171_IAS"
# for_obsid(obsid, location=location)
#
# # hdf5_filenames = get_hdf5_filenames_for_obsid(obsid, data_dir=location)
# # setup = get_setup_for_obsid(obsid, data_dir=location)
# #
# # create_fits_from_hdf5(hdf5_filenames, location=location, setup=setup)
# # add_synoptics(obsid, data_dir=location)
#
# #
# # from persistqueue import Queue
# # hdf5_filename_queue = Queue("/Users/sara/hdf5_queue")
#
# # hdf5_filename = hdf5_filename_queue.get()[0]
#
# from camtest import GlobalState
# from egse.setup import submit_setup
#
# setup = GlobalState.setup
#
# ccd_id = {"0b00": "CCD3", "0b01": "CCD4", "0b10": "CCD1", "0b11": "CCD2"}
# ccd_numbering = {
#     "CCD_BIN_TO_ID": [3, 4, 1, 2],
#     "CCD_BIN_TO_IDX": [2, 3, 0, 1],
#     "CCD_ID_TO_BIN": [0, "0b10", "0b11", "0b00", "0b01"],
#     "CCD_IDX_TO_BIN": ["0b10", "0b11", "0b00", "0b01"],
#     "DEFAULT_CCD_READOUT_ORDER": "0b01001110",
#     "CCD_ID": ccd_id
# }
#
# setup.camera.fee.calibration = "yaml//../../common/n-fee/nfee_sensor_calibration_em_v3.yaml"
# setup.camera.fee["register_map"] = "yaml//../../common/n-fee/nfee_register_em_v2.yaml"
# setup.camera.fee["hk_map"] = "yaml//../../common/n-fee/nfee_hk_em_v2.yaml"
# setup.camera.fee["ccd_numbering"] = ccd_numbering
#
# setup = submit_setup(setup, "Updated CCD numbering for EM")
#
#
#
# l = ["0", "0b10", "0b11", "0b00", "0b01"]
# # l = [1, 2, 3, 4]
# if isinstance(l, list):
#     line = "["
#     for el in l:
#         # if isinstance(el, str) and el.startswith("0b"):
#         #     line = f"{line}{el}, "
#         #     print(line)
#         # else:
#         line = f"{line}{el}, "
#     line = f"{line[:-2]}]"
#     print(line)
#
#
# from camtest import GlobalState
# setup = GlobalState.setup
# print(setup)
# gse = dict(setup.gse)
# gse.pop("tcs")
# setup.gse = gse
# print(setup.gse.tcs)
#
# setup = submit_setup(setup, "Removed TCS block")
#
#
#
#
#
#
# from camtest import GlobalState
# from egse.setup import submit_setup
#
# setup = GlobalState.setup
#
#
# print(setup.gse.aeu.awg2)
#
# print(setup.gse.aeu.awg2.calibration.n_cam_sync_data)
#
# setup.gse.aeu.awg2.calibration.n_cam_sync_data.A = "SyncData//(A | 25.00 | ArbDataFile//(N_CCD_READ_25) | ArbDataFile//(SVM_SYNC_CCD_READ_25) | 0.006667)"
# setup.gse.aeu.awg2.calibration.n_cam_sync_data.B = "SyncData//(B | 31.25 | ArbDataFile//(N_CCD_READ_31_25) | ArbDataFile//(SVM_SYNC_CCD_READ_31_25) | 0.016)"
# setup.gse.aeu.awg2.calibration.n_cam_sync_data.C = "SyncData//(C | 37.50 | ArbDataFile//(N_CCD_READ_37_50) | ArbDataFile//(SVM_SYNC_CCD_READ_37_50) | 0.006667)"
# setup.gse.aeu.awg2.calibration.n_cam_sync_data.D = "SyncData//(D | 43.75 | ArbDataFile//(N_CCD_READ_43_75) | ArbDataFile//(SVM_SYNC_CCD_READ_43_75) | 0.0114286)"
# setup.gse.aeu.awg2.calibration.n_cam_sync_data.E = "SyncData//(E | 50.00 | ArbDataFile//(N_CCD_READ_50) | ArbDataFile//(SVM_SYNC_CCD_READ_50) | 0.006667)"
#
# print(setup.gse.aeu.awg2.calibration.n_cam_sync_data)
#
# setup = submit_setup(setup, "Using short sync pulses of 200ms (instead of 150ms)")
#
#
#
# from egse.dpu.fitsgen import get_hdf5_filenames_for_obsid
# from egse.state import GlobalState
# from egse import h5
# from rich.console import Console
# from rich.table import Table
#
# obsid = "00170_IAS"
# obs_hdf5_files = get_hdf5_filenames_for_obsid(obsid, "/STER/platodata/IAS/data/IAS")
# ccd_bin_to_id = GlobalState.setup.camera.fee.ccd_numbering.CCD_BIN_TO_ID
#
# table = Table(title=f"Report for obsid {obsid}")
# table.add_column("HDF5 file")
# table.add_column("Group", no_wrap=True)
# table.add_column("CCD number", no_wrap=True)
# table.add_column("CCD side", no_wrap=True)
# table.add_column("Command", no_wrap=False)
#
# for hdf5_filename in obs_hdf5_files:
#
#     try:
#         with h5.get_file(hdf5_filename, mode="r", locking=False) as hdf5_file:
#             hdf5_index = int(hdf5_filename.split("_")[-1].split(".")[0])
#             print(hdf5_index)
#
#             for index in range(0, 4):
#                 try:
#                     group = hdf5_file[str(index)]
#
#                     # Data
#
#                     has_e_side = False
#                     has_f_side = False
#
#                     try:
#                         data = group["data"]
#
#
#                         for packet_index in range(2):
#                             packet_type = DataPacket(data[str(packet_index)]).type
#                             ccd_number = ccd_bin_to_id[packet_type.ccd_number]
#                             ccd_side = packet_type.ccd_side
#                             if ccd_side == 1:
#                                 has_e_side = True
#                             else:
#                                 has_f_side = True
#                         if has_e_side and has_f_side:
#                             table.add_row(str(hdf5_index), str(index), str(ccd_number), "both", "")
#                         elif has_e_side:
#                             table.add_row(str(hdf5_index), str(index), str(ccd_number), "E", "")
#                         elif has_f_side:
#                             table.add_row(str(hdf5_index), str(index), str(ccd_number), "F", "")
#                     except KeyError:
#                         pass    # No data
#
#                     # Command
#
#                     try:
#                         commands = group["commands"]
#
#                         for command_index in range(len(commands)):
#                             command = commands[str(command_index)][()]
#                             table.add_row(str(hdf5_index), str(index), "", "", f"{command_index}: {command}")
#                     except KeyError:
#                         pass  # No commands sent
#
#                 except KeyError:
#                     pass    # Internal sync
#     except OSError as exc:
#         print("OS error")
#     except RuntimeError as exc:
#         print("Runtime error")
#     table.add_row(None, None, None, None)
#
# console = Console(width=300)
# console.print(table)
#
#
#
# from rich.console import Console
# from rich.table import Table
# from rich.progress import Progress, track, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn, \
#     TimeRemainingColumn, SpinnerColumn, TimeElapsedColumn
# import time
#
# console = Console(record=True)
# with Progress(
#         SpinnerColumn(),
#         # *Progress.get_default_columns(),
#         # TimeElapsedColumn(),
#         console=console,
#         transient=False,
# ) as progress:
#     task1 = progress.add_task("[red]Downloading", total=10)
#     while not progress.finished:
#         progress.update(task1, advance=1)
#         time.sleep(0.5)