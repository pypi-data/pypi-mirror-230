"""
This module define the FITS generation process.

The FITS generation process connects to the monitoring channel of the DPU control server and starts processing
HDF5 files as soon as they are available. The FITS generation can also be started off-line to process a list
of HDF5 files or to process a given Observation (OBSID).

"""
import glob
import logging
import multiprocessing
import os
import pickle
import threading
from datetime import timedelta, datetime
from enum import Enum
from pathlib import Path, PosixPath
from typing import List, Mapping

import click
import invoke
import natsort
import numpy as np
import persistqueue
import rich
import sys
import time
import zmq
from astropy.io import fits
from h5py import File
from h5py._hl.attrs import AttributeManager
from itertools import chain
from scipy.interpolate import interp1d

import egse
from egse import h5
from egse.config import find_file, find_files
from egse.control import time_in_ms
from egse.dpu import DPUMonitoring, get_expected_last_packet_flags
from egse.dpu.dpu_cs import is_dpu_cs_active
from egse.env import get_data_storage_location
from egse.exceptions import Abort
from egse.fee import convert_ccd_order_value
from egse.fee import n_fee_mode
from egse.fee.nfee import HousekeepingData
from egse.hk import get_housekeeping, HKError
from egse.obsid import ObservationIdentifier, LAB_SETUP_TEST, TEST_LAB, obsid_from_storage
from egse.reg import RegisterMap
from egse.settings import Settings
from egse.setup import load_setup, Setup
from egse.spw import SpaceWirePacket
from egse.state import GlobalState
from egse.storage import is_storage_manager_active
from egse.storage.persistence import FITS, HDF5
from egse.synoptics import ORIGIN as SYN_ORIGIN
from egse.synoptics import get_synoptics_table
from egse.system import time_since_epoch_1958, format_datetime, read_last_line
from egse.zmq_ser import bind_address, connect_address

LOGGER = logging.getLogger(__name__)

N_FEE_SETTINGS = Settings.load("N-FEE")
CCD_SETTINGS = Settings.load("CCD")
SITE = Settings.load("SITE")
CTRL_SETTINGS = Settings.load("FITS Generator Control Server")
STORAGE_SETTINGS = Settings.load("Storage Control Server")
DPU_SETTINGS = Settings.load("DPU")

TIMEOUT_RECV = 1.0  # seconds


def get_cycle_time(n_fee_state: Mapping, obsid=None, data_dir=None):
    """ Return the image cycle time.

    In the given N-FEE state parameters or register map, we check whether we are in internal or external sync:

        - Internal sync: Read the image cycle time from the given N-FEE state parameters or register map;
        - External sync: Get the image cycle time from the AEU (AWG2).  In case of off-line FITS generation (i.e. from
          the HDF5 files), the image cycle time (for the specified obsid) is taken from the AEU housekeeping (AWG2).
          In case of on-line FITS generation, the image cycle time is queried from the AEU AWG2.

    Args:
        - n_fee_state: N-FEE state parameters or register map.
        - obsid: Observation identifier for which the image cycle time is read from the AEU housekeeping.

    Returns: Image cycle time [s].
    """

    # Internal sync -> use sync period from the N-FEE state

    if n_fee_state["sync_sel"] == 1:
        return n_fee_state["int_sync_period"] / 1000.    # [ms] -> [s]

    # External sync -> use AEU sync pulses

    else:
        if obsid:
            try:
                return float(get_housekeeping("GAEU_EXT_CYCLE_TIME", obsid=obsid, data_dir=data_dir)[1])
            except HKError as exc:  # See GitHub issue #2025
                LOGGER.warning("No HK available for AWG2 (using default cycle time of 25s)", exc)
                return 25.0
        else:
            return None


def get_cgse_version(obsid=None, data_dir=None):
    """ Returns the version of the Common EGSE with which the FITS file was created.

    Args:
        - obsid: Observation identifier for which the version of the Common EGSE is read from the Configuration
                 Manager housekeeping.
    """

    try:
        return None if obsid is None else get_housekeeping("CM_CGSE_VERSION", obsid=obsid, data_dir=data_dir)[1]
    except HKError:
        return None


class FITSGenerator:

    def __init__(self):
        """ Generation of FITS files from HDF5 files with SpW packets.

        In a separate thread, the DPU monitoring puts the name of new HDF5 files with SpW packets in the queue.  The
        FITS generator accesses this queue (FIFO) and stores the information in a FITS file.

        When there is a change in crucial parameters, the current FITS file (if any) will be closed and a new one will
        be created as soon as data packet start coming in (when the N-FEE is in full-image or full-image pattern mode).
        """

        # Queue with the full path of the HDF5 files that still need to be processed.

        self.hdf5_filename_queue = persistqueue.Queue(f"{get_data_storage_location()}/{DPU_SETTINGS['HDF5_QUEUE']}")

        # Name of the FITS file currently being written
        # (None if the N-FEE is not in full-image mode or in full-image pattern mode)

        self.fits_images_filename = None
        self.fits_cube_filename = None

        # Name of the HDF5 file currently being processed

        self.hdf5_filename = None

        # The last obsid that was/is being processed

        self.last_processed_obsid = None

        # Keep track of what was the N-FEE mode and what were the crucial parameters at the previous long pulse
        # (When we have checked whether a change has been detected, these values will be overwritten with the new ones)

        self.ccd_mode_config = None
        self.v_start = None
        self.v_end = None
        self.h_end = None
        self.ccd_readout_order = None
        # self.sensor_sel = None
        self.rows_final_dump = None
        self.setup = GlobalState.setup
        self.sensor_sel_enum = self.setup.camera.fee.sensor_sel.enum
        self.camera_name = self.setup.camera.ID

        self.config_slicing_num_cycles = 0   # Configured slicing parameter
        self.processed_num_cycles = 0           # HDF5 files with image data processed for current FITS file

        # self._quit_event = multiprocessing.Event()

        self.keep_processing_queue = True

        # The DPU monitoring should populate the queue in a separate thread

        self.dpu_monitoring_thread = threading.Thread(target=self.fill_queue)
        self.dpu_monitoring_thread.daemon = True
        self.dpu_monitoring_thread.start()

        # Processing the content of the queue should be done in a separate thread

        self.process_queue_thread = threading.Thread(target=self.process_queue)
        self.process_queue_thread.daemon = True
        self.process_queue_thread.start()

    def fill_queue(self):
        """
        The DPU monitoring fills the queue.

        Each time an HDF5 file with SpW packets is closed, the DPU monitoring puts the full path of this file on the
        queue.
        """

        dpu_monitoring_timeout = 30  # seconds

        with DPUMonitoring() as dpu_monitoring:

            start_time = time.time()

            while self.keep_processing_queue:

                try:
                    hdf5_filename = dpu_monitoring.wait_for_hdf5_filename(retries=0, timeout=1.0)
                    self.hdf5_filename_queue.put(hdf5_filename)
                    start_time = time.time()
                except TimeoutError:
                    if time.time() - start_time > dpu_monitoring_timeout:
                        LOGGER.warning(f"DPU monitoring timeout, "
                                       f"no HDF5 filename received after {dpu_monitoring_timeout} seconds.")
                        start_time = time.time()

            LOGGER.info(f"Broke out of monitoring loop {self.keep_processing_queue=}.")

    def run(self):
        """ Process the content of the queue.

        When there is a filename in the queue, take it from the queue:

            - If there is a change in crucial parameters, close the current FITS file (if any).
            - If there is a change in crucial parameter and the N-FEE is in full-image mode or in full-image pattern
              mode, or the N-FEE goes to full-image mode or full-image pattern mode, a new FITS file will be created.
            - The content of the HDF5 files will be extracted and passed to the FITS persistence layer as SpW packets.
        """
        zcontext = zmq.Context.instance()

        monitoring_socket = zcontext.socket(zmq.PUB)
        monitoring_socket.bind(bind_address(CTRL_SETTINGS.PROTOCOL, CTRL_SETTINGS.MONITORING_PORT,))

        endpoint = bind_address(CTRL_SETTINGS.PROTOCOL, CTRL_SETTINGS.COMMANDING_PORT)
        commander = zcontext.socket(zmq.REP)
        commander.bind(endpoint)

        poller = zmq.Poller()
        poller.register(commander, zmq.POLLIN)

        last_time = time_in_ms()

        try:
            while True:

                if _check_commander_status(commander, poller):

                    self.keep_processing_queue = False
                    break

                if time_in_ms() - last_time >= 1000:
                    last_time = time_in_ms()

                    monitoring_info = {"hdf5": self.hdf5_filename,
                                       "fits": self.fits_cube_filename or self.fits_images_filename,
                                       "last obsid (being) processed": self.last_processed_obsid}
                    pickle_string = pickle.dumps(monitoring_info)
                    monitoring_socket.send(pickle_string)

        except KeyboardInterrupt:
            click.echo("KeyboardInterrupt caught!")

        self.keep_processing_queue = False

        # Clean up all open sockets and running threads

        poller.unregister(commander)

        LOGGER.info("Shutting down FITS generation")

        commander.close(linger=0)
        LOGGER.info("Commander closed.")

        monitoring_socket.close(linger=0)
        LOGGER.info("Monitoring socket closed.")

        # Check if the Monitoring and Processing Threads are finished
        # Since the default timeout on the DPU Monitoring is set to 30s for some reason, this may take some time

        LOGGER.info("Joining worker threads, this may take some time...")
        self.dpu_monitoring_thread.join()
        self.process_queue_thread.join()
        LOGGER.info("Worker threads terminated.")

        del self.hdf5_filename_queue
        LOGGER.info("HDF5 filename Queue deleted.")

        del zcontext

    def __del__(self):
        egse.logger.close_all_zmq_handlers()

        zmq.Context.instance().term()
        logging.getLogger().info("ZMQ Context terminated.")

    def process_queue(self):

        location = get_data_storage_location()

        syn_obsid = None

        while self.keep_processing_queue:

            # There is an HDF5 file ready for processing

            if not self.hdf5_filename_queue.empty():

                try:

                    # Get the first item in the queue (FIFO) and open it

                    item = self.hdf5_filename_queue.get()
                    # LOGGER.info(f"HFD5 filename Queue {item = }")
                    self.hdf5_filename = hdf5_filename = item[0]
                    self.hdf5_filename_queue.task_done()

                    LOGGER.info(f"Processing file {hdf5_filename}")

                    with h5.get_file(hdf5_filename, mode="r", locking=False) as hdf5_file:

                        LOGGER.info(f"Opened file {hdf5_filename}")

                        # Check whether there is data in the HDF5
                        # (if there is no data in the HDF5 file, nothing has to be done and you can go to the next file)

                        try:

                            # Slicing

                            try:
                                slicing_num_cycles = hdf5_file["dpu"].attrs["slicing_num_cycles"]
                                if slicing_num_cycles != self.config_slicing_num_cycles:
                                    LOGGER.debug(f"Slicing parameter changed: {self.config_slicing_num_cycles} "
                                                 f"-> {slicing_num_cycles}")
                                    self.close_fits()
                                    self.config_slicing_num_cycles = slicing_num_cycles
                            except KeyError:
                                self.config_slicing_num_cycles = 0
                                LOGGER.debug("No slicing")

                            # Obsid

                            try:
                                obsid = hdf5_file["obsid"][()].decode()
                                # LOGGER.info(f"OBSID from HDF5 file: {obsid = }")
                                obsid = ObservationIdentifier.create_from_string(obsid, order=LAB_SETUP_TEST)
                                # LOGGER.info(f"OBSID from string: {obsid = !s}")

                                self.last_processed_obsid = obsid_from_storage(
                                    obsid, data_dir=location, camera_name=self.camera_name)
                            except (KeyError, ValueError) as exc:
                                # KeyError: when no obsid is included in the HDF5 file
                                # ValueError: when the format of the obsid does not match LAB_SETUP_TEST
                                # Uncomment the following line when you need more debug info
                                # LOGGER.warning(f"Exception caught: {exc.__class__.__name__} - {exc}", exc_info=False)
                                obsid = None
                            except AttributeError as exc:
                                # AttributeError: when is this raised ??
                                LOGGER.warning(f"Exception caught: {exc.__class__.__name__} - {exc}", exc_info=False)
                                LOGGER.error(f"No data present for obsid {str(obsid)} in the obs folder, terminating ...")
                                self.keep_processing_queue = False
                                break

                            register_map = RegisterMap("N-FEE", memory_map=h5.get_data(hdf5_file["register"]))

                            # Loop over all groups in the current HDF5 file and check whether the "data" group is
                            # present

                            has_data = False

                            for group in h5.groups(hdf5_file):

                                if "data" in group.keys():

                                    has_data = True

                                    n_fee_state = group["data"].attrs

                                    # Check whether there is a change in crucial parameters or in the N-FEE mode

                                    if self.crucial_parameter_change(n_fee_state):

                                        self.close_fits()

                                    if in_data_acquisition_mode(n_fee_state):

                                        if self.fits_images_filename is None:

                                            # Start writing to a new FITS file

                                            self.fits_images_filename = construct_images_filename(
                                                hdf5_filename, obsid, location=location, camera_name=self.camera_name
                                            )

                                            ccd_readout_order = convert_ccd_order_value(self.ccd_readout_order)

                                            prep = {
                                                "v_start": self.v_start,
                                                "v_end": self.v_end,
                                                "h_end": self.h_end,
                                                "rows_final_dump": self.rows_final_dump,
                                                "ccd_mode_config": self.ccd_mode_config,
                                                "ccd_readout_order": ccd_readout_order,  # CCD numbering [1-4]
                                                "expected_last_packet_flags": get_expected_last_packet_flags(
                                                    n_fee_state, self.sensor_sel_enum),
                                                "obsid": str(obsid),
                                                "cycle_time": get_cycle_time(n_fee_state, obsid=obsid),
                                                "cgse_version": get_cgse_version(obsid=obsid),
                                                "setup": self.setup,
                                                "register_map": register_map,
                                            }

                                            persistence = FITS(self.fits_images_filename, prep)
                                            persistence.open()

                                        # See https://github.com/IvS-KULeuven/plato-common-egse/issues/901
                                        # timecode = group["timecode"]
                                        # spw_packet = SpaceWirePacket.create_packet(h5.get_data(timecode))

                                        timestamp = group["timecode"].attrs["timestamp"]
                                        persistence.create({"Timestamp": timestamp})

                                        data = group["data"]
                                        sorted_datasets = natsort.natsorted(data.items(), key=lambda x: x[0])

                                        persistence.expected_last_packet_flags = get_expected_last_packet_flags(
                                            n_fee_state, self.sensor_sel_enum)

                                        for identifier, dataset in sorted_datasets:

                                            spw_packet = SpaceWirePacket.create_packet(h5.get_data(dataset))
                                            persistence.create({f"SpW packet {identifier}": spw_packet})

                            if has_data:
                                self.processed_num_cycles += 1
                                syn_obsid = obsid

                                if self.config_slicing_num_cycles != 0 and \
                                        self.processed_num_cycles == self.config_slicing_num_cycles:
                                    self.close_fits()

                            else:

                                self.close_fits()
                                self.clear_crucial_parameters()

                            # When the previous HDF5 file still pertained to an observation and the current one doesn't,
                            # it means that the observation has just finished and all FITS files have been generated. It
                            # is only at this point that the synoptics can be included in the FITS headers.

                            if syn_obsid is not None and obsid is None:
                                LOGGER.info(f"Adding synoptics for {syn_obsid}")
                                add_synoptics(syn_obsid, fits_dir=location, syn_dir=location)
                                syn_obsid = None
                        except KeyError:
                            LOGGER.debug("KeyError occurred when accessing data in all groups of the HDF5 file.")

                except IndexError:
                    LOGGER.debug("Queue contained an emtpy entry")
                except RuntimeError as exc:
                    LOGGER.debug(f"Unable to open HDF5 file: {exc}")

    def clear_crucial_parameters(self):
        """ Clear the crucial parameters."""

        self.v_start = None
        self.v_end = None
        self.h_end = None
        self.rows_final_dump = None
        self.ccd_readout_order = None
        self.ccd_mode_config = None

    def close_fits(self):

        if self.fits_images_filename is not None:

            self.fits_cube_filename = construct_cube_filename(self.fits_images_filename)
            convert_to_cubes(self.fits_images_filename)
            self.fits_cube_filename = None

            # Stop writing to the current FITS file

            self.fits_images_filename = None

            # Reset the number of HDF5 files with image data processed for current FITS file

            self.processed_num_cycles = 0

    def crucial_parameter_change(self, n_fee_state: AttributeManager):
        """ Check for a change in crucial parameters.

        Crucial parameters are:

            - ccd_mode_config: readout mode;
            - v_start (int) and v_end(int): index of the first and the last row being transmitted;
            - h_end (int): index of the last serial readout of the readout register;
            - ccd_readout_order: CCDs that will be read out;
            # - sensor_sel: which  side(s) of the CCD(s) that will be read out;

        Args:
            - n_fee_stage: N-FEE stae parameters.

        Returns: True if a change in crucial parameters has been detected; False otherwise.
        """

        ccd_mode_config = n_fee_state["ccd_mode_config"]
        v_start = n_fee_state["v_start"]
        v_end = n_fee_state["v_end"]
        h_end = n_fee_state["h_end"]
        ccd_readout_order = n_fee_state["ccd_readout_order"]
        rows_final_dump = n_fee_state["n_final_dump"]

        crucial_parameter_change = False

        if v_start != self.v_start:

            LOGGER.info(f"Change in v_start: {self.v_start} -> {v_start}")

            self.v_start = v_start
            crucial_parameter_change = True

        if v_end != self.v_end:

            LOGGER.info(f"Change in v_end: {self.v_end} -> {v_end}")

            self.v_end = v_end
            crucial_parameter_change = True

        if h_end != self.h_end:

            LOGGER.info(f"Change in h_end: {self.h_end} -> {h_end}")

            self.h_end = h_end
            crucial_parameter_change = True

        if rows_final_dump != self.rows_final_dump:

            LOGGER.info(f"Change in rows_final_dump: {self.rows_final_dump} -> {rows_final_dump}")

            self.rows_final_dump = rows_final_dump
            crucial_parameter_change = True

        if ccd_readout_order != self.ccd_readout_order:

            LOGGER.info(f"Change in ccd_readout_order: {self.ccd_readout_order} -> {ccd_readout_order}")

            self.ccd_readout_order = ccd_readout_order
            crucial_parameter_change = True

        if ccd_mode_config != self.ccd_mode_config:

            LOGGER.info(f"Change in ccd_mode_config: {self.ccd_mode_config} -> {ccd_mode_config}")

            self.ccd_mode_config = ccd_mode_config
            crucial_parameter_change = True

        return crucial_parameter_change


def convert_to_cubes(filename):
    """ Conversion of level-1 FITS files to level-2 FITS files.

    After the conversion, the flat-structure FITS file is removed.

    Args:
        - filename: Full path of the level-1 FITS file.
    """

    cube_filename = construct_cube_filename(filename)
    LOGGER.info(f"Converting to {cube_filename}")
    fee_side = GlobalState.setup.camera.fee.ccd_sides.enum

    with fits.open(filename) as level1:

        primary_header = level1["PRIMARY"].header

        selected_ccds = np.unique(primary_header["CCD_READOUT_ORDER"][1:-1].split(", "))  # str
        side_is_present = {ccd: {fee_side.E: 0, fee_side.F: 0} for ccd in selected_ccds}

        has_serial_overscan = primary_header["H_END"] >= \
            CCD_SETTINGS.LENGTH_SERIAL_PRESCAN + CCD_SETTINGS.NUM_COLUMNS // 2
        has_parallel_overscan = primary_header["V_END"] >= CCD_SETTINGS.NUM_ROWS

        # We are going to calculate the relative time since the very first exposure in the FITS file.  We don't know
        # here which CCD side of which CCD came in first, so we determine the start time here.

        start_time = time_since_epoch_1958(format_datetime(precision=6, width=9))   # Now (data will certainly be older)
        date_obs = None

        for ccd_number in selected_ccds:

            for ccd_side in fee_side:

                try:

                    finetime = level1[f"IMAGE_{ccd_number}_{ccd_side.name[0]}", 0].header["FINETIME"]

                    if finetime < start_time:

                        start_time = finetime
                        date_obs = level1[f"IMAGE_{ccd_number}_{ccd_side.name[0]}", 0].header["DATE-OBS"]

                    side_is_present[ccd_number][ccd_side] = True

                except KeyError:

                    side_is_present[ccd_number][ccd_side] = False

        primary_hdu = fits.PrimaryHDU()
        primary_header["DATE-OBS"] = (date_obs, "Timestamp for 1st frame",)
        primary_header["FINETIME"] = (start_time, "Finetime representation of DATE-OBS",)
        primary_header["LEVEL"] = 2  # Cube structure
        primary_hdu.header = primary_header
        primary_hdu.writeto(cube_filename)

        for ccd_number in selected_ccds:

            for ccd_side in fee_side:

                if side_is_present[ccd_number][ccd_side]:

                    # Image

                    images = []
                    time_axis = np.array([])

                    exposure = 0

                    while True:

                        try:

                            slice = level1[f"IMAGE_{ccd_number}_{ccd_side.name[0]}", exposure]

                            time = time_since_epoch_1958(slice.header["DATE-OBS"])
                            time_axis = np.append(time_axis, time)

                            images.append(slice.data)

                            exposure += 1

                        except KeyError:

                            break

                    image_cube = np.stack(images)
                    del images

                    time_axis -= start_time
                    time_column = fits.Column("TIME", format="F", array=time_axis)
                    time_table = fits.BinTableHDU.from_columns([time_column])
                    time_table.header["EXTNAME"] = f"WCS-TAB_{ccd_number}_{ccd_side.name[0]}"

                    fits.append(cube_filename, time_table.data, time_table.header)
                    fits.append(filename, time_table.data, time_table.header)

                    image_cube_header = level1[f"IMAGE_{ccd_number}_{ccd_side.name[0]}", 0].header
                    image_cube_header["NAXIS"] = (3, f"Dimensionality of the image cube ({ccd_side.name[0]}-side)",)
                    image_cube_header["NAXIS3"] = exposure
                    image_cube_header["CRPIX3"] = 1
                    image_cube_header["CRVAL3"] = start_time
                    image_cube_header["CTYPE3"] = "TIMETAB"
                    image_cube_header["CUNIT3"] = "s"
                    image_cube_header["PS3_0"] = f"WCS-TAB_{ccd_number}_{ccd_side.name[0]}"
                    image_cube_header["PS3_1"] = "TIME"

                    fits.append(cube_filename, image_cube, image_cube_header)

                    # Serial pre-scan

                    serial_prescans = []

                    exposure = 0

                    while True:

                        try:

                            serial_prescans.append(level1[f"SPRE_{ccd_number}_{ccd_side.name[0]}", exposure].data)
                            exposure += 1

                        except KeyError:

                            break

                    serial_prescan_cube = np.stack(serial_prescans)
                    del serial_prescans

                    serial_prescan_cube_header = level1[f"SPRE_{ccd_number}_{ccd_side.name[0]}", 0].header
                    serial_prescan_cube_header["NAXIS"] = (3, f"Dimensionality of the serial pre-scan cube ({ccd_side.name[0]}-side)",)
                    serial_prescan_cube_header["NAXIS3"] = exposure
                    serial_prescan_cube_header["CRPIX3"] = 1
                    serial_prescan_cube_header["CRVAL3"] = start_time
                    serial_prescan_cube_header["CTYPE3"] = "TIMETAB"
                    serial_prescan_cube_header["CUNIT3"] = "s"
                    serial_prescan_cube_header["PS3_0"] = f"WCS-TAB_{ccd_number}_{ccd_side.name[0]}"
                    serial_prescan_cube_header["PS3_1"] = "TIME"

                    fits.append(cube_filename, serial_prescan_cube, serial_prescan_cube_header)

                    # Serial over-scan

                    if has_serial_overscan:

                        serial_overscans = []
                        exposure = 0

                        while True:

                            try:

                                serial_overscans.append(level1[f"SOVER_{ccd_number}_{ccd_side.name[0]}", exposure].data)
                                exposure += 1

                            except KeyError:

                                break

                        serial_overscan_cube = np.stack(serial_overscans)
                        del serial_overscans

                        serial_overscan_cube_header = level1[f"SOVER_{ccd_number}_{ccd_side.name[0]}", 0].header
                        serial_overscan_cube_header["NAXIS"] = (3, f"Dimensionality of the serial over-scan cube ({ccd_side.name[0]}-side)",)
                        serial_overscan_cube_header["NAXIS3"] = exposure
                        serial_overscan_cube_header["CRPIX3"] = 1
                        serial_overscan_cube_header["CRVAL3"] = start_time
                        serial_overscan_cube_header["CTYPE3"] = "TIMETAB"
                        serial_overscan_cube_header["CUNIT3"] = "s"
                        serial_overscan_cube_header["PS3_0"] = f"WCS-TAB_{ccd_number}_{ccd_side.name[0]}"
                        serial_overscan_cube_header["PS3_1"] = "TIME"

                        fits.append(cube_filename, serial_overscan_cube, serial_overscan_cube_header)

                    # Parallel over-scan

                    if has_parallel_overscan:

                        parallel_overscans = []
                        exposure = 0

                        while True:

                            try:

                                parallel_overscans.append(level1[f"POVER_{ccd_number}_{ccd_side.name[0]}", exposure].data)
                                exposure += 1

                            except KeyError:
                                break

                        parallel_overscan_cube = np.stack(parallel_overscans)
                        del parallel_overscans

                        parallel_overscan_cube_header = level1[f"POVER_{ccd_number}_{ccd_side.name[0]}", 0].header
                        parallel_overscan_cube_header["NAXIS"] = (3, f"Dimensionality of the parallel over-scan cube ({ccd_side.name[0]}-side)",)
                        parallel_overscan_cube_header["NAXIS3"] = exposure
                        parallel_overscan_cube_header["CRPIX3"] = 1
                        parallel_overscan_cube_header["CRVAL3"] = start_time
                        parallel_overscan_cube_header["CTYPE3"] = "TIMETAB"
                        parallel_overscan_cube_header["CUNIT3"] = "s"
                        parallel_overscan_cube_header["PS3_0"] = f"WCS-TAB_{ccd_number}_{ccd_side.name[0]}"
                        parallel_overscan_cube_header["PS3_1"] = "TIME"

                        fits.append(
                            cube_filename, parallel_overscan_cube, parallel_overscan_cube_header
                        )

    # Remove the level-1 FITS file

    LOGGER.info(f"Removing flat-structure FITS file {filename}")
    os.remove(filename)


def is_incomplete(hdf5_file: File):
    """ Check whether the given HDF5 file is incomplete.

    The HDF5 files are created at the start of a cycle. The register map and (if applicable) the format version are
    stored at this point.  If an observation starts "half way" a cycle, the register map will not be present.

    Args:
        - hdf5_file: HDF5 file.

    Returns: True if the given HDF5 file is incomplete (i.e. if the register map is not stored); False otherwise.
    """

    return "register" not in hdf5_file


def is_corrupt(hdf5_file: File):
    """ Check whether the given HDF5 file is corrupt.

    Args:
        - hdf5_file: HDF5 file.

    Returns: True if an error flag is set in one of the groups; False otherwise.
    """

    for count in range(4):

        if f"/{count}/hk" in hdf5_file:

            hk_packet = SpaceWirePacket.create_packet(hdf5_file[f"/{count}/hk"][...])
            error_flags = HousekeepingData(hk_packet.data)['error_flags']

            if error_flags:
                return True

    return False


def any_crucial_parameters_changed(prep: dict, n_fee_state: Mapping):
    """ Check whether there is a change in crucial parameters.

    Return True if any of the following parameters changed with respect to the revious check: v_start, v_end, h_end,
    rows_final_dump, ccd_mode_config, and ccd_readout_order.

    Args:
        - prep (dict): Current values for the crucial parameters.
        - n_fee_state: N-FEE state parameters or register map.

    Returns: True if any of the values have changed, False otherwise.
    """

    v_start = n_fee_state['v_start']
    v_end = n_fee_state['v_end']
    h_end = n_fee_state['h_end']
    rows_final_dump = n_fee_state['n_final_dump']
    ccd_mode_config = n_fee_state['ccd_mode_config']
    ccd_readout_order = n_fee_state['ccd_readout_order']
    ccd_readout_order = convert_ccd_order_value(ccd_readout_order)

    for x, y in dict(
        v_start=v_start, v_end=v_end, h_end=h_end, rows_final_dump=rows_final_dump,
        ccd_mode_config=ccd_mode_config, ccd_readout_order=ccd_readout_order,
    ).items():
        if prep.get(x) != y:
            LOGGER.debug(f"{x=}, {prep.get(x)=}, {y=}")
            return True

    return False


def in_data_acquisition_mode(n_fee_state: Mapping):
    """ Check whether the N-FEE is in data acquisition mode.

    Args:
           - n_fee_state: N-FEE state parameters or register map.

    Returns: True if the N-FEE is in imaging mode (full-image (pattern) mode, windowing (pattern) mode, or
             parallel/serial trap pumping mode (1/2)) and the digitised data is transferred to the N-DPU.
    """

    ccd_mode_config = n_fee_state["ccd_mode_config"]
    digitise_en = n_fee_state["digitise_en"]

    return ccd_mode_config in [n_fee_mode.FULL_IMAGE_MODE, n_fee_mode.FULL_IMAGE_PATTERN_MODE,
                               n_fee_mode.PARALLEL_TRAP_PUMPING_1_MODE, n_fee_mode.PARALLEL_TRAP_PUMPING_2_MODE,
                               n_fee_mode.SERIAL_TRAP_PUMPING_1_MODE, n_fee_mode.SERIAL_TRAP_PUMPING_2_MODE,
                               n_fee_mode.WINDOWING_PATTERN_MODE, n_fee_mode.WINDOWING_MODE] and digitise_en


def construct_cube_filename(fits_filename: str) -> str:
    """ Construct the filename for the level-2 FITS file.

    The level-2 FITS file will have the data arranged in cubes, rather than in a flat structure.

    Args:
        - fits_filename: Filename for the level-1 FITS file.  The level-1 FITS files has the data arranged in a flat
                         structure.

    Returns: Filename for the level-2 FITS file.
    """

    LOGGER.info(f"Construct cube filename from {fits_filename}")

    # LOGGER.info(f"Images: {'images' in fits_filename}")

    if "images" in fits_filename:
        return fits_filename.replace("images", "cube")

    else:
        prefix, suffix = str(fits_filename).rsplit('_', 1)
        return f"{prefix}_cube_{suffix}"


def construct_images_filename(hdf5_filename: PosixPath, obsid: ObservationIdentifier = None,
                              location=None, camera_name: str = None):
    """ Construct the filename for the level-1 FITS file.


    The level-1 FITS files has the data arranged in a flat structure.

    Args:
        - identifier (str): Identifier for the source of the data, this string is usually what is sent in the `origin`
                            of the item dictionary.
        - ext (str): File extension: this depends on the persistence class that is used for storing the data.
        - obsid (ObservationIdentifier): Unique identifier for the observation (LAB_SETUP_TEST).
        - use_counter: Indicates whether or not a counter should be included in the filename.
        - location: Folder (with /daily and /obs sub-folders) in which the FITS files should be written (in a
                    dedicated directory in the /obs folder). If not specified, the `PLATO_DATA_STORAGE_LOCATION`
                    environment variable will be used to construct the location..

    Returns: Full path to the file as a `PurePath`.
    """

    location = location or get_data_storage_location()

    if obsid is None:

        timestamp, site_id, _, _, counter = str.split(str.split(str(hdf5_filename), ".")[0], "_")
        fits_filename = f"{timestamp}_{site_id}_{N_FEE_SETTINGS.ORIGIN_CCD_DATA}_{counter}_images.{FITS.extension}"

        location += "/daily/"

        return str(Path(location) / timestamp / fits_filename)

    else:

        # Make sure that the FITS file ends up in the correct sub-folder
        #   - oldest data: TEST_LAB_SETUP
        #   - more recent data: TEST_LAB

        obsid = obsid_from_storage(obsid, data_dir=location, camera_name=camera_name)

        timestamp = str.split(str(hdf5_filename).split("/")[-1], "_")[0]
        location += "/obs/"

        if not os.path.isdir(f"{location}/{obsid}"):
            os.makedirs(f"{location}/{obsid}")
        location += f"{obsid}/"

        # Determine the filename

        pattern = f"{obsid}_{N_FEE_SETTINGS.ORIGIN_CCD_DATA}_*_{timestamp}_cube.{FITS.extension}"
        counter = get_fits_counter(location, pattern)

        fits_filename = f"{obsid}_{N_FEE_SETTINGS.ORIGIN_CCD_DATA}_{counter:05d}_{timestamp}_images.{FITS.extension}"

        return str(Path(location) / fits_filename)


def get_fits_counter(location, pattern):
    """ Determine counter for a new FITS file at the given location and with the given pattern.

    Args:
        - location: Location where the FITS file should be stored.
        - pattern: Pattern for the filename.

    Returns: Value of the next counter; 1 if no previous files were found or if an error occurred.
    """

    LOGGER.debug(f"Pattern: {pattern=}")
    LOGGER.debug(f"Location: {location=}")

    files = sorted(find_files(pattern=pattern, root=location))

    # No filenames found showing the given pattern -> start counting at 1

    LOGGER.debug(f"Number of matches: {len(files)=}")

    if len(files) == 0:
        return 1

    last_file = files[-1]

    counter = last_file.name.split("_")

    LOGGER.debug(f"{counter = }")

    try:

        # Observation files have the following pattern:
        #  <test ID>_<lab ID>_N-FEE_CCD_<counter>_<day YYYYmmdd>_cube.fits

        counter = int(counter[-3]) + 1
        LOGGER.debug(f"{counter = }")
        return counter

    except ValueError:

        LOGGER.warning("ValueError", exc_info=True)
        return 1


def create_fits_from_hdf5(files: List, location: str = None, setup: Setup = None):
    """ Off-line generation of FITS files from HDF5 files with SpW packets.

    When there is a change in crucial parameters, the current FITS file (if any) will be closed and a new one will be
    created as soon and HDF5 file with data content is encountered (when the N-FEE is in full-image or full-image
    pattern mode):

        - If there is a change in crucial parameters, close the current FITS file (if any).
        - If there is a change in crucial parameter and the N-FEE is in full-image mode or in full-image pattern
          mode, or the N-FEE goes to full-image mode or full-image pattern mode, a new FITS file will be created.
        - The content of the HDF5 files will be extracted and passed to the FITS persistence layer as SpW packets.

    In the older HDF5 files, only the register map is stored, which does not always reflect the actual N-FEE state.
    This is solved in the later version of the HDF5 files (format version >= 2.0).  In these files, the current N-FEE
    state is stored in each of the data groups.

    It's possible that the first file in the list is incomplete, because it was already created by the time the
    current observation started.  That file

    Args:
        - files: List of filenames of the HDF5 files to use to create the FITS file.
        - location: Folder (with /daily and /obs sub-folders) in which the FITS files should be written (in a
                    dedicated directory in the /obs folder). If not specified, the `PLATO_DATA_STORAGE_LOCATION`
                    environment variable will be used to construct the location.
        - setup: Setup to retrieve information from.
    """

    location = location or get_data_storage_location()

    # Loop over the filenames.  When you encounter an HDF5 file, check its format version.

    for filename in files:

        filename = Path(filename)

        if filename.suffix == f".{HDF5.extension}":

            try:

                with h5.get_file(filename, mode="r", locking=False) as hdf5_file:

                    # It happens that some of the HDF5 files are incomplete.  These should not be considered to determine
                    # whether the register map (original format version) or the N-FEE state (format version >= 2.0) to
                    # determine the state of the crucial parameters.

                    if is_incomplete(hdf5_file):    # or is_corrupt(hdf5_file):

                        files = files[1:]

                    else:

                        # The N-FEE state is stored in the data groups of the HDF5 files (format version >= 2.0)

                        if "versions" in hdf5_file:

                            version_attrs = hdf5_file["versions"]["format_version"].attrs

                            if version_attrs["major_version"] == 2:
                                create_fits_from_hdf5_nfee_state(files, location=location, setup=setup)
                                break

                            else:

                                version = f"{version_attrs['major_version']}.{version_attrs['minor_version']}"

                                raise AttributeError(f"HDF5 file format version {version} cannot be handled by the FITS generator")

                        # The register map is stored (globally) in the HDF5 files

                        else:
                            create_fits_from_hdf5_register_map(files, location=location, setup=setup)
                            break

            except RuntimeError as exc:
                LOGGER.debug(f"Unable to open HDF5 file: {exc}")


def create_fits_from_hdf5_register_map(files: List, location: str = None, setup: Setup = None):
    """ Off-line generation of FITS files from HDF5 files with SpW packets.

    When there is a change in crucial parameters, the current FITS file (if any) will be closed and a new one will be
    created as soon and HDF5 file with data content is encountered (when the N-FEE is in full-image or full-image
    pattern mode):

        - If there is a change in crucial parameters, close the current FITS file (if any).
        - If there is a change in crucial parameter and the N-FEE is in full-image mode or in full-image pattern
          mode, or the N-FEE goes to full-image mode or full-image pattern mode, a new FITS file will be created.
        - The content of the HDF5 files will be extracted and passed to the FITS persistence layer as SpW packets.

    In the given HDF5 files, only the register map is stored, which does not always reflect the actual N-FEE state. As
    a result not all data may be present in the generated FITS files (e.g. because the register map says the N-FEE is
    already in dump mode) or the data might be split over more FITS files than expected (e.g. because the v_start and
    v_end parameters are already / not yet changed in the register map but not in the N-FEE state).

    Note that this problem is solved in the later version of the HDF5 files (format version >= 2.0).

    Args:
        - files: List of filenames of the HDF5 files to use to create the FITS file.
        - location: Folder (with /daily and /obs sub-folders) in which the FITS files should be written (in a
                    dedicated directory in the /obs folder). If not specified, the `PLATO_DATA_STORAGE_LOCATION`
                    environment variable will be used to construct the location.
        - setup: Setup to retrieve information from.
    """
    setup = setup or GlobalState.setup

    location = location or get_data_storage_location()
    hdf5_file_root = Path(files[0]).parent.parent.parent
    sensor_sel_enum = setup.camera.fee.sensor_sel.enum
    camera_name = setup.camera.ID

    prep = {}
    fits_filename = None

    for filename in files:

        filename = Path(filename)

        if filename.suffix == '.hdf5':

            print(f"Processing {filename=!s}...")

            try:

                with h5.get_file(filename, mode="r", locking=False) as hdf5_file:

                    # if is_corrupt(hdf5_file):
                    #     LOGGER.warning(f"Skipping {filename} (corrupt)")
                    #
                    # else:

                    if 'register' not in hdf5_file:
                        LOGGER.warning(f"No register map found for {filename=!s}, continue with next file..")
                        continue  # next HDF5 file

                    register_map = RegisterMap("N-FEE", memory_map=h5.get_data(hdf5_file["register"]))

                    has_data = False

                    for group in h5.groups(hdf5_file):

                        if "data" in group.keys():

                            has_data = True

                            # Should a new FITS file be created?

                            if any_crucial_parameters_changed(prep, register_map):

                                if fits_filename:

                                    LOGGER.info(f"Creating a FITS CUBE file ...")
                                    convert_to_cubes(fits_filename)
                                    fits_filename = None

                            if in_data_acquisition_mode(register_map):

                                if fits_filename is None:

                                    LOGGER.info(f"A new FITS file will be created...")

                                    # Start writing to a new FITS file
                                    # Collect all information to sent to the FITS layer

                                    if "obsid" in hdf5_file:
                                        obsid = hdf5_file["obsid"][()].decode()
                                        obsid = ObservationIdentifier.create_from_string(obsid, order=LAB_SETUP_TEST)
                                    else:
                                        obsid = None

                                    fits_filename = construct_images_filename(
                                        filename, obsid, location=location, camera_name=camera_name
                                    )
                                    LOGGER.info(f"{fits_filename = !s}")

                                    ccd_readout_order = register_map['ccd_readout_order']
                                    ccd_readout_order = convert_ccd_order_value(ccd_readout_order)

                                    prep = {
                                        "v_start": register_map['v_start'],
                                        "v_end": register_map['v_end'],
                                        "h_end": register_map['h_end'],
                                        "rows_final_dump": register_map['n_final_dump'],
                                        "ccd_mode_config": register_map['ccd_mode_config'],
                                        "ccd_readout_order": ccd_readout_order,  # CCD numbering [1-4]
                                        "expected_last_packet_flags": get_expected_last_packet_flags(register_map,
                                                                                                     sensor_sel_enum),
                                        "obsid": str(obsid) if obsid is not None else None,
                                        "cycle_time": get_cycle_time(register_map, obsid=obsid, data_dir=hdf5_file_root),
                                        "cgse_version": get_cgse_version(obsid=obsid, data_dir=hdf5_file_root),
                                        "setup": setup,
                                        "register_map": register_map
                                    }

                                    persistence = FITS(str(fits_filename), prep)
                                    persistence.open()

                                # See https://github.com/IvS-KULeuven/plato-common-egse/issues/901
                                # timecode = group["timecode"]
                                # spw_packet = SpaceWirePacket.create_packet(h5.get_data(timecode))

                                timestamp = group["timecode"].attrs["timestamp"]
                                persistence.create({"Timestamp": timestamp})

                                data = group["data"]
                                sorted_datasets = natsort.natsorted(data.items(), key=lambda x: x[0])

                                persistence.expected_last_packet_flags = get_expected_last_packet_flags(register_map,
                                                                                                        sensor_sel_enum)

                                for identifier, dataset in sorted_datasets:

                                    spw_packet = SpaceWirePacket.create_packet(h5.get_data(dataset))
                                    # LOGGER.debug(f"{spw_packet.type = !s}")
                                    persistence.create({f"SpW packet {identifier}": spw_packet})

                    if not has_data:

                        if fits_filename:

                            LOGGER.info(f"Creating a FITS CUBE file ...")
                            convert_to_cubes(fits_filename)
                            fits_filename = None

                        prep = clear_crucial_parameters(prep)

            except RuntimeError as exc:
                LOGGER.debug(f"Unable to open HDF5 file: {exc}")
        else:
            print(f"Skipping {filename=}")

    try:
        if fits_filename:
            LOGGER.info(f"Creating a FITS CUBE file ...")
            convert_to_cubes(fits_filename)
    except OSError:
        # The last file in the list still contained data, so we reached the end of the list without creating a cube
        # FITS file yet
        pass


def create_fits_from_hdf5_nfee_state(files: List, location: str = None, setup: Setup = None):
    """ Off-line generation of FITS files from HDF5 files with SpW packets.

    When there is a change in crucial parameters, the current FITS file (if any) will be closed and a new one will be
    created as soon and HDF5 file with data content is encountered (when the N-FEE is in full-image or full-image
    pattern mode):

        - If there is a change in crucial parameters, close the current FITS file (if any).
        - If there is a change in crucial parameter and the N-FEE is in full-image mode or in full-image pattern
          mode, or the N-FEE goes to full-image mode or full-image pattern mode, a new FITS file will be created.
        - The content of the HDF5 files will be extracted and passed to the FITS persistence layer as SpW packets.

    In the given HDF5 files, the N-FEE state is saved in all data groups, reflecting the actual N-FEE state (i.e.
    solving the problem of the mismatch between the register map and the N-FEE state).

    Args:
        - files: List of filenames of the HDF5 files to use to create the FITS file.
        - location: Folder (with /daily and /obs sub-folders) in which the FITS files should be written (in a
                    dedicated directory in the /obs folder). If not specified, the `PLATO_DATA_STORAGE_LOCATION`
                    environment variable will be used to construct the location.
        - setup: Setup to retrieve information from.
    """
    setup = setup or GlobalState.setup

    location = location or get_data_storage_location()
    hdf5_file_root = Path(files[0]).parent.parent.parent
    sensor_sel_enum = setup.camera.fee.sensor_sel.enum
    camera_name = setup.camera.ID

    config_slicing_num_cycles = 0    # Configured slicing parameter
    processed_num_cycles = 0            # HDF5 files with image data processed for current FITS file

    prep = {}
    fits_filename = None

    for filename in files:

        filename = Path(filename)

        if filename.suffix == '.hdf5':

            print(f"Processing {filename=!s}...")

            try:

                with h5.get_file(filename, mode="r", locking=False) as hdf5_file:

                    # Slicing

                    try:
                        slicing_num_cycles = hdf5_file["dpu"].attrs["slicing_num_cycles"]
                        if slicing_num_cycles != config_slicing_num_cycles:
                            if fits_filename:
                                convert_to_cubes(fits_filename)
                                fits_filename = None
                            processed_num_cycles = 0
                            config_slicing_num_cycles = slicing_num_cycles
                    except KeyError:
                        config_slicing_num_cycles = 0

                    register_map = RegisterMap("N-FEE", memory_map=h5.get_data(hdf5_file["register"]))

                    # if is_corrupt(hdf5_file):
                    #     LOGGER.warning(f"Skipping {filename} (corrupt)")
                    #
                    # else:

                    has_data = False

                    for group in h5.groups(hdf5_file):

                        if "data" in group.keys():

                            has_data = True

                            n_fee_state = group["data"].attrs

                            # Should a new FITS file be created?

                            if any_crucial_parameters_changed(prep, n_fee_state):

                                if fits_filename:

                                    LOGGER.info(f"Creating a FITS CUBE file ...")
                                    convert_to_cubes(fits_filename)
                                    fits_filename = None
                                    processed_num_cycles = 0

                            if in_data_acquisition_mode(n_fee_state):

                                if fits_filename is None:

                                    LOGGER.info(f"A new FITS file will be created...")

                                    # Start writing to a new FITS file
                                    # Collect all information to sent to the FITS layer

                                    if "obsid" in hdf5_file:
                                        obsid = hdf5_file["obsid"][()].decode()
                                        obsid = ObservationIdentifier.create_from_string(obsid, order=LAB_SETUP_TEST)
                                    else:
                                        obsid = None

                                    fits_filename = construct_images_filename(
                                        filename, obsid, location=location, camera_name=camera_name
                                    )
                                    LOGGER.info(f"{fits_filename = !s}")

                                    ccd_readout_order = n_fee_state['ccd_readout_order']
                                    ccd_readout_order = convert_ccd_order_value(ccd_readout_order)

                                    prep = {
                                        "v_start": n_fee_state['v_start'],
                                        "v_end": n_fee_state['v_end'],
                                        "h_end": n_fee_state['h_end'],
                                        "rows_final_dump": n_fee_state['n_final_dump'],
                                        "ccd_mode_config": n_fee_state['ccd_mode_config'],
                                        "ccd_readout_order": ccd_readout_order,  # CCD numbering [1-4]
                                        "expected_last_packet_flags": get_expected_last_packet_flags(n_fee_state,
                                                                                                     sensor_sel_enum),
                                        "obsid": str(obsid) if obsid is not None else None,
                                        "cycle_time": get_cycle_time(n_fee_state, obsid=obsid, data_dir=hdf5_file_root),
                                        "cgse_version": get_cgse_version(obsid=obsid, data_dir=hdf5_file_root),
                                        "setup": setup,
                                        "register_map": register_map
                                    }

                                    persistence = FITS(str(fits_filename), prep)
                                    persistence.open()

                                # See https://github.com/IvS-KULeuven/plato-common-egse/issues/901
                                # timecode = group["timecode"]
                                # spw_packet = SpaceWirePacket.create_packet(h5.get_data(timecode))

                                timestamp = group["timecode"].attrs["timestamp"]
                                persistence.create({"Timestamp": timestamp})

                                data = group["data"]
                                sorted_datasets = natsort.natsorted(data.items(), key=lambda x: x[0])

                                persistence.expected_last_packet_flags = get_expected_last_packet_flags(n_fee_state,
                                                                                                        sensor_sel_enum)

                                for identifier, dataset in sorted_datasets:

                                    spw_packet = SpaceWirePacket.create_packet(h5.get_data(dataset))
                                    # LOGGER.debug(f"{spw_packet.type = !s}")
                                    persistence.create({f"SpW packet {identifier}": spw_packet})

                    if has_data:
                        processed_num_cycles += 1

                        if fits_filename and config_slicing_num_cycles != 0 \
                                and processed_num_cycles == config_slicing_num_cycles:
                            convert_to_cubes(fits_filename)
                            fits_filename = None
                            processed_num_cycles = 0
                    else:

                        if fits_filename:
                            LOGGER.info(f"Creating a FITS CUBE file ...")
                            convert_to_cubes(fits_filename)
                            fits_filename = None
                            processed_num_cycles = 0

                        prep = clear_crucial_parameters(prep)

            except RuntimeError as exc:
                LOGGER.debug(f"Unable to open HDF5 file: {exc}")
        else:
            print(f"skipping {filename=}")

    try:
        if fits_filename:
            LOGGER.info(f"Creating a FITS CUBE file ...")
            convert_to_cubes(fits_filename)
    except OSError:
        # The last file in the list still contained data, so we reached the end of the list without creating a cube
        # FITS file yet
        pass


def clear_crucial_parameters(prep: dict):
    """ Clear the crucial parameters from the given dictionary.

    Args:
        - prep: Dictionary with crucial parameters.

    Returns: Dictionary with the cleared crucial parameters.
    """

    prep["v_start"] = None
    prep["v_end"] = None
    prep["h_end"] = None
    prep["rows_final_dump"] = None
    prep["ccd_mode_config"] = None
    prep["ccd_readout_order"] = None

    return prep


class SynopticsFwdFill(tuple, Enum):
    """ Enumeration of the synoptics to forward fill.

    This is only applicable for the commanded source position.
    """

    # Source position (commanded)

    THETA_CMD = ("GSYN_CMD_THETA", "Commanded source position theta [deg]")
    PHI_CMD = ("GSYN_CMD_PHI", "Commanded source position phi [deg]")


class SynopticsInterp1d(tuple, Enum):
    """ Enumeration of the synoptics to linearly interpolate.

    This is only applicable for:
        - calibrated TCS temperatures;
        - calibrated N-FEE temperatures (TOU + CCDs + and board sensors);
        - selection of TH DAQ(s) temperatures;
        - OGSE attenuation (relative intensity + FWC fraction for the OGSE);
        - actual source position.
    """

    # TCS temperatures

    T_TRP1 = ("GSYN_TRP1", "Mean T for TOU TRP1 (TCS) [deg C]")
    T_TRP22 = ("GSYN_TRP22", "Mean T for FEE TRP22 (TCS) [deg C]")

    # TOU TRP PT1000 sensors (N-FEE)

    T_TRP5 = ("GSYN_TRP5", "Mean T for TRP5 (TOU baffle ring) [deg C]")
    T_TRP6 = ("GSYN_TRP6", "Mean T for TRP6 (FPA I/F) [deg C]")
    T_TRP8 = ("GSYN_TRP8", "Mean T for TRP8 (L3) [deg C]")
    T_TRP21 = ("GSYN_TRP21", "Mean T for TRP21 (TOU bipod +X bottom) [deg C]")
    T_TRP31 = ("GSYN_TRP31", "Mean T for TRP31 (TOU bipod -Y bottom) [deg C]")
    T_TRP41 = ("GSYN_TRP41", "Mean T for TRP41 (TOU bipod +Y bottom) [deg C]")

    # CCD PT100/PT1000 sensors (N-FEE)

    T_CCD1 = ("GSYN_CCD1", "Mean T for CCD1 [deg C]")
    T_CCD2 = ("GSYN_CCD2", "Mean T for CCD2 [deg C]")
    T_CCD3 = ("GSYN_CCD3", "Mean T for CCD3 [deg C]")
    T_CCD4 = ("GSYN_CCD4", "Mean T for CCD4 [deg C]")

    T_CCD1_AMB = ("GSYN_CCD1_AMB", "Mean T for CCD1 (ambient calibration) [deg C]")
    T_CCD2_AMB = ("GSYN_CCD2_AMB", "Mean T for CCD2 (ambient calibration) [deg C]")
    T_CCD3_AMB = ("GSYN_CCD3_AMB", "Mean T for CCD3 (ambient calibration) [deg C]")
    T_CCD4_AMB = ("GSYN_CCD4_AMB", "Mean T for CCD4 (ambient calibration) [deg C]")

    # Board sensors: type PT1000 (N-FEE)

    T_PCB1 = ("GSYN_NFEE_T_PCB1", "Mean T for board sensor PCB1 [deg C]")
    T_PCB2 = ("GSYN_NFEE_T_PCB2", "Mean T for board sensor PCB2 [deg C]")
    T_PCB3 = ("GSYN_NFEE_T_PCB3", "Mean T for board sensor PCB3 [deg C]")
    T_PCB4 = ("GSYN_NFEE_T_PCB4", "Mean T for board sensor PCB4 [deg C]")

    # Board sensors: type ISL71590

    T_ADC = ("GSYN_NFEE_T_ADC", "Mean ADC board T [deg C]")
    T_CDS = ("GSYN_NFEE_T_CDS", "Mean CDS board T [deg C]")
    T_ANALOG = ("GSYN_NFEE_T_ANALOG", "Mean analog board T [deg C]")
    T_SKYSHROUD = ("GSYN_SKYSHROUD", "Mean front shroud T [deg C]")
    T_TEB_TOU = ("GSYN_TEB_TOU", "Mean TEB TOU T [deg C]")
    T_TEB_FEE = ("GSYN_TEB_FEE", "Mean TEB FEE T [deg C]")

    # Temperatures from the TH DAQ

    T_TRP2 = ("GSYN_TRP2", "Mean T for TRP2 (MaRi bipod +X I/F) [deg C]")
    T_TRP3 = ("GSYN_TRP3", "Mean T for TRP3 (MaRi bipod -Y I/F) [deg C]")
    T_TRP4 = ("GSYN_TRP4", "Mean T for TRP4 (MaRi bipod +Y I/F) [deg C]")

    T_TRP7 = ("GSYN_TRP7", "Mean T for TRP7 (thermal strap) [deg C]")
    T_TRP10 = ("GSYN_TRP10", "Mean T for TRP10 (FPA) [deg C]")

    # OGSE attenuation

    OGATT = ("GSYN_OGSE_REL_INTENSITY", "Relative OGSE intensity")
    OGFWC = ("GSYN_OGSE_FWC_FRACTION", "OGSE FWC fraction")

    # Source position (actual)

    THETA = ("GSYN_ACT_THETA", "Actual source position theta [deg]")
    PHI = ("GSYN_ACT_PHI", "Actual source position phi [deg]")


class SynopticsLeaveGaps(tuple, Enum):
    """ Enumeration of the synoptics not to fill the gaps for.

    This is only applicable for the status of the shutter (open/closed).  Note that there is no shutter in CSL, so we
    indicate that the shutter is always open there.
    """

    OGSHTTR = ("GSYN_OGSE_SHUTTER_OPEN", "Is the shutter open?")


def get_fits_synoptics(obsid: str, data_dir=None) -> dict:
    """ Retrieve the synoptics that need to be included in the FITS files for the given observation.

    The synoptics that need to be included in the FITS files are represented by the following enumerations:

        - SynopticsFwdFill: Use forward filling for the gaps -> only at the beginning of the observation it is possible
          that there still are gaps (but it is unlikely that the data acquisition has already started then);
        - SynopticsInterp1d: Use linear interpolation to fill the gaps.  At the extremes, we use extrapolation;
        - SynopticsLeaveGaps: Don't fill the gaps.

    Args:
        - obsid: Observation identifier [TEST_LAB or TEST_LAB_SETUP].

    Returns: Dictionary with the synoptics that should go into the FITS files for the given observation.
    """

    synoptics_table = get_synoptics_table(obsid, data_dir=data_dir)

    # We keep the original timestamps (when filling the gaps)

    timestamps = synoptics_table["timestamp"].values
    for index in range(len(timestamps)):
        timestamps[index] = time_since_epoch_1958(timestamps[index])
    timestamps = timestamps.astype(float)

    synoptics = {"timestamps": timestamps}  # Don't forget to include the timestamps to the returned dictionary

    # Linear interpolation

    for syn_enum in SynopticsInterp1d:

        syn_name = syn_enum.value[0]

        if syn_name in synoptics_table:

            # We need to filter out the NaNs or the interpolation will not work

            values = synoptics_table[syn_name].values

            if len(values) > 0:
                selection = ~np.isnan(values)

                if np.any(selection):
                    selected_timestamps = timestamps[np.where(selection)]
                    selected_values = values[np.where(selection)]

                    if len(selected_timestamps) > 1:
                        interpolation = interp1d(selected_timestamps, selected_values, kind='linear',
                                                 fill_value='extrapolate')
                        synoptics[syn_enum] = interpolation(timestamps)

    # Forward fill

    for syn_enum in SynopticsFwdFill:

        syn_name = syn_enum.value[0]

        if syn_name in synoptics_table:
            synoptics[syn_enum] = synoptics_table[syn_name].ffill()

    # Leave the gaps in

    for syn_enum in SynopticsLeaveGaps:

        syn_name = syn_enum.value[0]

        if syn_name in synoptics_table:
            synoptics[syn_enum] = synoptics_table[syn_name]

    return synoptics


def add_synoptics(obsid: str, fits_dir: str, syn_dir: str):
    """ Add synoptics to the FITS headers for the given observation.

    When all FITS files have been produced for the given obsid, synoptics is added to the headers.  This is done in the
    following steps:
        - Determine which folder in the /obs directory comprises the HK and FITS files for the given obsid;
        - Read the synoptics for the given obsid (from said folder) into a pandas DataFrame;
        - Compose the list of FITS files for the given observation (from said folder);
        - For all of these FITS files, loop over the cubes it contains and:
                - Determine the time range covered by the cube;
                - Select the synoptics (from the pandas DataFrame) over that time range;
                - For the synoptical temperatures, source position (commanded + actual), and OGSE intensity: calculate
                  the average and add this to the header of the cube;
                - For the shutter: calculate the mean and add this to the header of the cube.

    Args:
        obsid: Observation identifier [TEST_LAB or TEST_LAB_SETUP]
        fits_dir: Directory (with /daily and /obs sub-folders) with the FITS files
        syn_dir: Directory (with /daily and /obs sub-folders) with the original synoptics files
    """

    fits_dir = fits_dir or get_data_storage_location()
    syn_dir = syn_dir or get_data_storage_location()
    fee_side = GlobalState.setup.camera.fee.ccd_sides.enum

    obsid = obsid_from_storage(obsid, data_dir=fits_dir)
    obs_dir = f"{fits_dir}/obs/{obsid}"  # Where the HK and FITS files are stored

    try:
        synoptics = get_fits_synoptics(obsid, data_dir=fits_dir)
    except FileNotFoundError:
        synoptics = get_fits_synoptics(obsid, data_dir=syn_dir)
    timestamps = synoptics["timestamps"]    # Timestamps of the synoptics -> compare with absolute time in FITS file

    # Compose the list of FITS files for the given obsid

    pattern = f"{obsid}_{N_FEE_SETTINGS.ORIGIN_CCD_DATA}_*_*_cube.fits"
    fits_filenames = sorted(find_files(pattern=pattern, root=obs_dir))

    # Loop over all FITS files (cubes) for the given obsid

    for fits_filename in fits_filenames:

        syn_info = {}

        # Loop over all image cubes

        with fits.open(fits_filename) as fits_file:

            start_time = fits_file["PRIMARY"].header["FINETIME"]

            # Loop over both sides of all CCDs (not all of them might be in -> hence the KeyError)

            for ccd_number in range(1, 5):

                for ccd_side in fee_side:

                    try:
                        # Absolute time = time at the start of the readout
                        #               = time at the end of the exposure
                        # -> Extract relative time from the WCS-TAB and add the DATE-OBS (which is the time of the
                        #    1st frame in the FITS file; all times in the WCS-TAB are relative to this)

                        wcs_table_name = f"WCS-TAB_{ccd_number}_{ccd_side.name[0]}"     # Holds relative time
                        absolute_time = np.array(fits_file[wcs_table_name].data["TIME"]) + start_time

                        # We don't care about the 1st frame of any CCD side, as the image is saturated anyway, and it is
                        # very difficult to determine the start of that exposure anyway
                        # -> Simplest solution: indicate that the synoptics is unknown for those frames
                        # For all other frames:
                        #       - Determine when the readout for the previous frame started -> start_previous_readout;
                        #       - Determine when the readout for the current frame started -> start_current_readout;
                        #       - For each synoptics parameter, gather the values acquired in the timespan
                        #         [start_previous_readout, start_current_readout]
                        #       - For the numerical values: take the mean (skipping the NaNs)
                        #       - For the boolean values (i.c. status of the shutter):
                        #               - Only NaN selected -> "U" (unknown)
                        #               - Both True & False selected (potentially also NaNs) -> "M" (mixed)
                        #               - Only True (potentially also NaNs) selected -> "T" (True = shutter open)
                        #               - Only False (potentially also NaNs) selected -> "F" (False = shutter closed)
                        #
                        # For each synoptical parameter, first determine all the values that need to be included in the
                        # current cube of the current FITS file (it is only when we have composed these arrays, that we
                        # can included them in a table in the FITS file)

                        fits_synoptics = {syn_enum: np.array([np.nan]) for syn_enum in chain(SynopticsFwdFill,
                                                                                             SynopticsInterp1d)}
                        fits_synoptics.update({syn_enum: np.array(["U"]) for syn_enum in SynopticsLeaveGaps})

                        for index in range(1, len(absolute_time)):

                            # Selection of the synoptics for the current frame: based on timestamps:
                            #   - Start (start_previous_readout): start of the readout of the previous exposure
                            #   - End (start_current_readout): start of the readout of the current exposure

                            start_previous_readout = absolute_time[index - 1]
                            start_current_readout = absolute_time[index]

                            selection = np.where(timestamps >= start_previous_readout) \
                                        and np.where(timestamps <= start_current_readout)[0]

                            # Average (skipping NaNs)

                            for syn_enum in chain(SynopticsFwdFill, SynopticsInterp1d):
                                try:
                                    selected_values = synoptics[syn_enum][selection]
                                    average_value = np.nanmean(selected_values)

                                    fits_synoptics[syn_enum] = np.append(fits_synoptics[syn_enum], average_value)
                                except (KeyError, AttributeError):
                                    fits_synoptics[syn_enum] = np.append(fits_synoptics[syn_enum], np.nan)

                            for syn_enum in SynopticsLeaveGaps:
                                try:
                                    selected_values = synoptics[syn_enum][selection].astype(float)
                                    selection = ~np.isnan(selected_values)

                                    if not np.any(selection):   # No data -> "U" (unknown)
                                        value = "U"
                                    else:   # Use "T" (True) / "F" (False) only when unique (otherwise: "M" (mixed))
                                        unique_values = np.unique(selected_values[selection])
                                        value = str(bool(unique_values[0]))[0] if len(unique_values) == 1 else "M"
                                    fits_synoptics[syn_enum] = np.append(fits_synoptics[syn_enum], value)
                                except (KeyError, AttributeError):    # "U" (unknown)
                                    fits_synoptics[syn_enum] = np.append(fits_synoptics[syn_enum], "U")

                            # At this point, we have for each synoptical parameter an array of the values that need to
                            # be included in the FITS file.  We now put all this information in a dedicated table and
                            # add it to the FITS file.

                            syn_columns = []

                            for syn_enum in chain(SynopticsFwdFill, SynopticsInterp1d, SynopticsLeaveGaps):
                                column_format = "A" if syn_enum == SynopticsLeaveGaps.OGSHTTR else "F"

                                syn_column = fits.Column(syn_enum.value[0], format=column_format,
                                                         array=fits_synoptics[syn_enum])
                                syn_columns.append(syn_column)

                            syn_table = fits.BinTableHDU.from_columns(syn_columns)
                            syn_table.header["EXTNAME"] = f"SYN-TAB_{ccd_number}_{ccd_side.name[0]}"

                            # merged_columns = wcs_table.columns + syn_table.columns
                            # merged_table = fits.BinTableHDU.from_columns(merged_columns)

                            syn_info[syn_table.header["EXTNAME"]] = (syn_table.data, syn_table.header)
                    except KeyError:
                        pass

        for data in syn_info.values():
            fits.append(str(fits_filename), data[0], data[1])

@click.group()
def cli():
    pass


@cli.command()
def start():
    multiprocessing.current_process().name = "fitsgen"

    # FIXME: Why is this line commented out?
    # start_http_server(CTRL_SETTINGS.METRICS_PORT)

    # The Storage Manager must be active (otherwise the HK cannot be stored)

    if not is_storage_manager_active():
        LOGGER.error("The Storage Manager is not running, start the core services before running the data acquisition.")
        return

    if not is_dpu_cs_active():
        LOGGER.critical("DPU Control Server must be running to be able to start the FITS generator.")
        return

    FITSGenerator().run()


@cli.command()
def start_bg():

    invoke.run("fitsgen start", disown=True)


@cli.command()
def stop():
    """Stop the FOV HK Control Server. """

    # In the while True loop in the start command, _should_stop needs to force a break from the loop.When this happens
    # (and also when a keyboard interrupt has been caught), the monitoring socket needs to be closed (this needs to be
    # done in the TH - specific implementation of _start).  Unregistering from the Storage Manager is done
    # automatically.

    response = send_request("quit")

    if response == "ACK":
        rich.print("FITS generation successfully terminated.")
    else:
        rich.print(f"[red] ERROR: {response}")


def _check_commander_status(commander, poller) -> bool:
    """ Check the status of the commander.

    Checks whether a command has been received by the given commander.

    Returns: True if a quit command was received; False otherwise.

    Args:
        - commander: Commanding socket for the FOV HK generation.
        - poller: Poller for the FOV HK generation.
    """

    socks = dict(poller.poll(timeout=5000))   # Timeout of 5s

    if commander in socks:
        pickle_string = commander.recv()
        command = pickle.loads(pickle_string)

        if command.lower() == "quit":

            commander.send(pickle.dumps("ACK"))
            return True

        if command.lower() == "status":
            response = dict(
                status="ACK",
                host=CTRL_SETTINGS.HOSTNAME,
                command_port=CTRL_SETTINGS.COMMANDING_PORT
            )
            commander.send(pickle.dumps(response))

        return False

    return False


@cli.command()
def status():
    """Print the status of the FITS Generation Control Server."""

    rich.print("FITS generation:")

    response = send_request("status")

    if response.get("status") == "ACK":
        rich.print("  Status: [green]active")
        rich.print(f"  Hostname: {response.get('host')}")
        rich.print(f"  Commanding port: {response.get('command_port')}")
    else:
        rich.print("  Status: [red]not active")

def send_request(command_request: str):
    """Sends a request to the FOV HK Control Server and waits for a response.

    Args:
        - command_request: Request.

    Returns: Response to the request.
    """

    ctx = zmq.Context().instance()
    endpoint = connect_address(CTRL_SETTINGS.PROTOCOL, CTRL_SETTINGS.HOSTNAME, CTRL_SETTINGS.COMMANDING_PORT)
    socket = ctx.socket(zmq.REQ)
    socket.connect(endpoint)

    socket.send(pickle.dumps(command_request))
    rlist, _, _ = zmq.select([socket], [], [], timeout=TIMEOUT_RECV)

    if socket in rlist:
        response = socket.recv()
        response = pickle.loads(response)
    else:
        response = {"error": "Receive from ZeroMQ socket timed out for FITS generation Control Server."}
    socket.close(linger=0)

    return response


@cli.command()
@click.argument('files', type=str, nargs=-1)
@click.option("--location", type=str, is_flag=False, default=None, help="Set the root folder for the output "
                                                                        "(i.e. folder with /daily and /obs)")
@click.option("--setup_id", type=int, is_flag=False, default=None, help="Setup ID")
@click.option("--site_id", type=str, is_flag=False, default=None, help="Site ID")
def from_hdf5(files, location=None, setup_id=None, site_id=None):
    """ Generate the FITS files for the given list of HDF5 files.

    Args:
        - files: List of HDF5 filenames.
        - setup_id: Identifier of the setup that should be used.  When not specified, the setup loading in the
                    Configuration Manager will be used to retrieve information from.
        - site_id: Identifier for the test site.
    """

    setup = get_offline_setup(site_id=site_id, setup_id=setup_id)
    location = location or get_data_storage_location()

    create_fits_from_hdf5(files, location=location, setup=setup)


@cli.command()
@click.argument('obsid', type=str)
@click.option("--input_dir", type=str, is_flag=False, default=None, help="Set the root folder for the input "
                                                                         "(i.e. folder with /daily and /obs)")
@click.option("--output_dir", type=str, is_flag=False, default=None, help="Set the root folder for the output "
                                                                          "(i.e. folder with /daily and /obs)")
@click.option("--setup_id", type=int, is_flag=False, default=None, help="Setup ID")
@click.option("--site_id", type=str, is_flag=False, default=None, help="Site ID")
def for_obsid(obsid, input_dir=None, output_dir=None, setup_id=None, site_id=None):
    """ Generate the FITS files for the given obsid.

    The setup that was loaded in the Configuration Manager during the given observation, will be used to retrieve
    information from.

    Args:
        - obsid: Observation identifier [TEST_LAB or TEST_LAB_SETUP].
        - location: Folder (with /daily and /obs sub-folders) in which the FITS files should be written (in a
                    dedicated directory in the /obs folder). If not specified, the `PLATO_DATA_STORAGE_LOCATION`
                    environment variable will be used to construct the location.
    """

    input_dir = input_dir or get_data_storage_location()    # Location of HDF5 files (under /daily)
    output_dir = output_dir or input_dir    # Location of the FITS files that will be generated (under /obs)

    obsid = obsid_from_storage(obsid, data_dir=input_dir)
    # Folder in the output /obs directory in which the FITS files will be stored (full path)
    output_obs_folder = Path(f"{output_dir}/obs/{obsid}")
    if not output_obs_folder.exists():      # If this directory doesn't exist yet, create it
        os.makedirs(output_obs_folder)

    setup = get_offline_setup(site_id=site_id, setup_id=setup_id)   # Setup (complete for the camera in question)

    hdf5_filenames = get_hdf5_filenames_for_obsid(obsid, data_dir=input_dir)    # HDF5 files to process

    # Create FITS files (flat structure -> cubes)
    create_fits_from_hdf5(hdf5_filenames, location=output_dir, setup=setup)

    # Add synoptics

    if find_file(f"{obsid_from_storage(obsid, data_dir=input_dir)}_{SYN_ORIGIN}_*.csv", root=output_obs_folder):
        # Synoptics have already been re-processed (located in the directory to which the FITS files will be stored)
        add_synoptics(obsid, fits_dir=output_dir, syn_dir=output_dir)
    else:
        # Use the original synoptics files
        add_synoptics(obsid, fits_dir=output_dir, syn_dir=input_dir)


def get_offline_setup(site_id: str = None, setup_id: int = None):
    """ Return setup to use for the off-line FITS generation.

    If the setup ID and site ID have been specified, the corresponding setup is used.  Otherwise, the setup that is
    currently loaded in the Configuration Manager is used.

    Args:
        site_id: Identifier of the testhouse
        setup_id: Identifier of the setup

    Returns:
        - Setup to use for the off-line FITS generation.
    """

    if setup_id is None:
        return GlobalState.setup
    else:
        site_id = site_id or SITE.ID
        return load_setup(setup_id=setup_id, site_id=site_id, from_disk=True)


def get_hdf5_filenames_for_obsid(obsid: str, data_dir: str = None) -> List:
    """ Return list of HDF5 filenames that contribute to the given obsid.

    The given obsid can be specified in either of these two formats: TEST_LAB or TEST_LAB_SETUP.  The obsid that is
    stored in the HDF5 files is of format LAB_SETUP_TEST.  In this method, we gather the list of HDF5 filenames for
    which the combination (TEST, SITE) matches with the (TEST, SITE) combination from the given obsid.  To do this, the
    list of relevant ODs is composed, based on the first and last timestamp in the DPU HK file (this file will always
    be present if data has been acquired).  Then all HDF5 files for these ODs are looped over and the obsid stored in
    there is compared with the given obsid.  In case of a match, the HDF5 filename is added to the list.

    Args:
        - obsid: Observation identifier [TEST_LAB or TEST_LAB_SETUP].
        - data_dir: Full path to the directory in which the data resides.  This is the folder with a sub-folder /daily,
                    in which the HDF5 files are stored.
    """

    data_dir = data_dir or get_data_storage_location()

    # Determine in which location (i.e. in the folder of which OD in the /daily sub-folder of the data directory)
    # the required HDF5 files are stored.  This sub-folder carries the OD [yyyymmdd] as name.

    od_list = get_od(obsid, data_dir)                # Obsid -> OD
    LOGGER.info(f"OD for obsid {obsid}: {od_list}")

    obs_hdf5_files = []

    for od in od_list:

        day_dir = Path(f"{data_dir}/daily/{od}")    # Sub-folder with the data for that OD

        daily_hdf5_filenames = glob.glob(str(day_dir / f"*.{HDF5.extension}"))

        for hdf5_filename in sorted(daily_hdf5_filenames):

            try:
                with h5.get_file(hdf5_filename, mode="r", locking=False) as hdf5_file:

                    if "/obsid" in hdf5_file:

                        hdf5_obsid = h5.get_data(hdf5_file["/obsid"]).item().decode()

                        if hdf5_obsid != "None":
                            hdf5_obsid = ObservationIdentifier.create_from_string(
                                hdf5_obsid, LAB_SETUP_TEST).create_id(order=TEST_LAB)      # TEST_LAB
                            if hdf5_obsid in str(obsid):
                                obs_hdf5_files.append(hdf5_filename)

            except OSError as exc:
                LOGGER.error(f"Couldn't open {hdf5_filename} ({exc=})")
            except RuntimeError as exc:
                LOGGER.debug(f"Unable to open HDF5 file: {exc}")

    return obs_hdf5_files


def get_od(obsid: str, data_dir: str = None):
    """ Return list of OD(s) for the given obsid.

    The given obsid can be specified in either of these two formats: TEST_LAB or TEST_LAB_SETUP. In this method, we
    determine during which OD(s) the given obsid was executed.  To do this, the first and last timestamp from the DPU HK
    file (this file will always be present if data has been acquired) are extracted.  This file resides in the folder of
    the given obsid in the /obs directory, with the name (i.e. obsid) in the format TEST_SITE_SETUP or TEST_SITE
    (depending on how old the observation is).  The obsid that is used in the filename follows the same pattern, so the
    given obsid must be converted to that format.

    Args:
         - obsid: Observation identifier [TEST_LAB or TEST_LAB_SETUP].
         - data_dir: Full path to the directory in which the data resides.  This is the folder with a sub-folder /daily,
                    in which the HDF5 files are stored.

    Returns: List of observation day [yyyymmdd].
    """

    data_dir = data_dir or get_data_storage_location()
    obsid = obsid_from_storage(obsid, data_dir=data_dir)     # Convert the obsid to the correct format
    obs_dir = f"{data_dir}/obs/{obsid}"

    try:
        filename = str(find_file(f"{obsid}_DPU_*.csv", root=obs_dir))

        od_start = datetime.strptime(filename.split("_")[-2], "%Y%m%d")         # First OD (from filename)
        od_end = datetime.strptime(read_last_line(filename)[:10], "%Y-%m-%d")   # Last OD (from last line)

        od = od_start
        delta = timedelta(days=1)
        od_list = []

        while od <= od_end:

            od_list.append(od.strftime("%Y%m%d"))

            od += delta

        return od_list
    except IndexError:
        raise Abort(f"DPU was not running during obsid {obsid}: no data could be acquired")


def get_obsid(od: str, index: int, day_dir: str) -> int:
    """ Return the obsid stored in the HDF5 file for the given OD and the given index.

    Args:
        - od: Observation day.
        - index: Index of the HDF5 file.
        - day_dir: Full path to the directory with the HDF5 files for the given OD.

    Returns: Obsid as stored in the HDF5 file for the given OD and the given index (LAB_SETUP_TEST).
    """

    if index == 0:  # For the first file, no index is used
        hdf5_filename = f"{day_dir}/{od}_{SITE.ID}_{N_FEE_SETTINGS.ORIGIN_SPW_DATA}.hdf5"
    else:
        hdf5_filename = f"{day_dir}/{od}_{SITE.ID}_{N_FEE_SETTINGS.ORIGIN_SPW_DATA}_{index:05d}.hdf5"

    with h5.get_file(hdf5_filename, mode="r", locking=False) as hdf5_file:
        try:
            return int(hdf5_file["obsid"][()].decode().split("_")[-1])
        except:
            return None


if __name__ == "__main__":

    sys.exit(cli())
