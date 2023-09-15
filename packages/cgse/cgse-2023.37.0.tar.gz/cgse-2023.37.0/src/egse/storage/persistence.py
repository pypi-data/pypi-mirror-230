"""
This module handles the persistence storage for the Common-EGSE.
"""
import csv
import logging
import os
import re
import sqlite3
import warnings
from abc import ABC
from abc import abstractmethod
from math import cos
from math import radians
from math import sin
from pathlib import Path
from sqlite3 import Connection
from typing import Optional
from typing import Union

import h5py
import natsort
import numpy as np
from astropy.io import fits
from astropy.io.ascii.cparser import AstropyWarning

from egse.fee import n_fee_mode
from egse.fee.nfee import HousekeepingData
from egse.settings import Settings
from egse.setup import Setup
from egse.setup import SetupError
from egse.spw import DataDataPacket
from egse.spw import DataPacket
from egse.spw import DataPacketType
from egse.spw import HousekeepingPacket
from egse.spw import OverscanDataPacket
from egse.spw import PacketType
from egse.spw import TimecodePacket
from egse.state import GlobalState
from egse.system import read_last_line
from egse.system import time_since_epoch_1958

logger = logging.getLogger(__name__)

FOV_SETTINGS = Settings.load("Field-Of-View")
CCD_SETTINGS = Settings.load("CCD")
INT_SYNC_TIMING_OFFSET = 0.4   # See https://github.com/IvS-KULeuven/plato-common-egse/issues/2475

try:
    _ = os.environ["PLATO_CAMERA_IS_EM"]
    PLATO_CAMERA_IS_EM = True if _.capitalize() in ("1", "True", "Yes") else 0
except KeyError:
    PLATO_CAMERA_IS_EM = False



class PersistenceLayer(ABC):
    """The Persistence Layer implements the CRUD paradigm for storing data."""

    extension = "no_ext"
    """The file extension to use for this persistence type."""

    @abstractmethod
    def open(self, mode=None):
        """Opens the resource."""
        raise NotImplementedError("Persistence layers must implement the open method")

    @abstractmethod
    def close(self):
        """Closes the resource."""
        raise NotImplementedError("Persistence layers must implement the close method")

    @abstractmethod
    def exists(self):
        """Does the resource exists."""
        raise NotImplementedError("Persistence layers must implement the exists method")

    @abstractmethod
    def create(self, data):
        """Creates an entry in the persistence store."""
        raise NotImplementedError("Persistence layers must implement a create method")

    @abstractmethod
    def read(self, select=None):
        """Returns a list of all entries in the persistence store.

        The list can be filtered based on a selection from the `select` argument which
        should be a Callable object.

        Args:
            select (Callable): a filter function to narrow down the list of all entries.
        Returns:
            A list or generator for all entries in the persistence store.
        """
        raise NotImplementedError("Persistence layers must implement a read method")

    @abstractmethod
    def update(self, idx, data):
        """Updates the entry for index `idx` in the persistence store."""
        raise NotImplementedError("Persistence layers must implement an update method")

    @abstractmethod
    def delete(self, idx):
        """Deletes the entry for index `idx` from the persistence store."""
        raise NotImplementedError("Persistence layers must implement a delete method")

    @abstractmethod
    def get_filepath(self):
        """If this persistence class is file based, return its file path, otherwise return None."""
        raise NotImplementedError("Persistence layers must implement a get_filepath method")


class FITSPersistenceError(Exception):
    """ Error for the FITS persistence layer."""

    pass


class MissingSpWPacketsError(Exception):
    """ Error when the SpW data for a frame in an HDF5 file is incomplete."""

    pass


class FITS(PersistenceLayer):
    """ Persistence layer that saves (image) data in a FITS file."""

    extension = "fits"

    warnings.simplefilter('ignore', category=AstropyWarning)

    def __init__(self, filename: str, prep: dict):
        """ Initialisation of the FITS persistence layer.

        This consists of the following steps:

            - Initialise the filepath (for the given filename);
            - Fetch the register map from the DPU;
            - Read all necessary data from that register map:
                - Which CCD(s) will be read;
                - Which side(s) of the CCD(s) will be read (E = left; F = right);
                - Which rows and columns will be transmitted;
                - How can we know whether all information has been received for a particular exposure;
            - Initialisation of the (1D) arrays in which the received data will be stored;
            - Initialisation of basic headers for the image, serial pre-scan(s), serial over-scan(s), and parallel
              over-scan for any exposure.

        Assumed is that the crucial parameters in the register map (N-FEE mode, v_start, v_end, h_end) will stay the
        same throughout data acquisition and assembly of the FITS file.  It is not explicitly checked whether this is
        indeed the case.

        All information (image data, serial pre-scan, serial over-scan, and parallel over-scan) will be stored in the
        same FITS file.  If the data of multiple CCDs would be transmitted, it is all stored in the same FITS file.  The
        extension name will indicate which kind of data it contains (image data, serial pre-scan, serial over-scan, or
        parallel over-scan), for which CCD.  In case of the serial scan maps, the extension will also indicate which
        CCD side it applies to.

        Args:
             - filename: Name of the output FITS file.
             - prep: Dictionary with the following information:
                    * v_start (int) and v_end(int): index of the first and the last row being transmitted;
                    * h_end (int): index of the last serial readout of the readout register;
                    * rows_final_dump:
                    * ccd_mode_config (egse.fee.n_fee_mode): readout mode;
                    * ccd_readout_order (List[int]): CCDs that will be read out;
                    * expected_last_packet_flags (List[bool]): expected last packet flags;
                    * obsid: observation identifier;
                    * cycle_time: image cycle time [s];
                    * cgse_version: version of the Common EGSE;
                    * setup: setup;
                    * register_map: FEE register map;
                    * vgd: configured VGD;
                    * in case of windowing mode or windowing pattern mode: dictionary with one window list for each CCD.
        """

        self.fee_side = GlobalState.setup.camera.fee.ccd_sides.enum

        self._filepath = Path(filename)

        # Which side(s) of which CCD(s) will be transmitted?
        # (initialise the data arrays for each of these)

        self.ccd_readout_order = prep["ccd_readout_order"]  # CCD numbering [1-4]
        self.selected_ccds = np.unique(self.ccd_readout_order)
        logger.debug(f"Selected CCDs: {self.selected_ccds}")

        self.data_arrays = {}
        self.init_data_arrays()

        self.frame_number = {ccd: {self.fee_side.LEFT_SIDE: 0, self.fee_side.RIGHT_SIDE: 0} for ccd in self.selected_ccds}
        self.timestamp = None
        self.finetime = None

        # How can you know whether or not all data for a given CCD has been received?
        # (this depends on whether or not there is parallel over-scan data and on which CCD side(s) will be transmitted)

        self.expected_last_packet_flags = prep["expected_last_packet_flags"]                    # To be received
        self.received_last_packet_flags = {ccd: [False] * 4 for ccd in self.selected_ccds}      # Actually received

        logger.debug(f"Init last packets flag: {self.received_last_packet_flags}")

        # Readout mode

        self.ccd_mode_config = prep["ccd_mode_config"]
        self.is_windowing_mode = self.check_readout_mode()

        # if self.is_windowing_mode:
        #
        #     self.windows = self.init_window_list(prep["window_list"])

        # Define the values of the WCS keywords


        self.v_start = prep["v_start"]                              # First transmitted row
        self.v_end = prep["v_end"]                                  # Last transmitted row
        self.h_end = prep["h_end"]                                  # Last transmitted column
        self.rows_final_dump = prep["rows_final_dump"]              # Number of rows to be dumped after readout
        self.cycle_time = prep["cycle_time"]                        # Image cycle time [s]
        self.cgse_version = prep["cgse_version"]                    # Version of the Common EGSE
        self.obsid = prep["obsid"]

        self.register_map = prep["register_map"]                    # Register map

        # Read information from the setup

        self.setup: Setup = prep["setup"]

        self.site_name = self.setup["site_id"]           # Site ID
        self.setup_id = self.setup.get_id()              # Setup ID
        self.camera_id = self.setup.camera.get("ID")     # Camera ID (None if not present in the setup)

        self.readout_time = self.calculate_readout_time(self.setup)      # Readout time [s]
        try:
            self.exposure_time = self.cycle_time - self.readout_time    # Exposure time [s]
        except TypeError:
            # Image cycle time is unknown (None)
            self.exposure_time = None

        self.has_serial_overscan = self.h_end >= CCD_SETTINGS.LENGTH_SERIAL_PRESCAN + CCD_SETTINGS.NUM_COLUMNS / 2
        self.has_parallel_overscan = self.v_end >= CCD_SETTINGS.NUM_ROWS

        # Create basic WCS
        # (part of the information can only be determined when the data is assembled)

        self.image_header = self.create_base_image_wcs()
        self.serial_prescan_header = self.create_base_serial_prescan_wcs()
        self.serial_overscan_header = self.create_base_serial_overscan_wcs()
        self.parallel_overscan_header = self.create_base_parallel_overscan_wcs()

        self.is_fits_file_open = False

    def calculate_readout_time(self, setup: Setup):
        """ Calculate the readout time.

        The readout time consists of:

            - clearout for the rows up to v_start;
            - reading (i.e. parallel transfer of the row + serial transfer of all its pixels up to h_end) rows v_start
              to v_end;
            - dumping rows_final_dump.

        Returns: Readout time for the requested part of a single CCD side [s].
        """

        time_row_parallel = setup.camera.fee.time_row_parallel
        time_row_clearout = setup.camera.fee.time_row_clearout
        time_pixel_readout = setup.camera.fee.time_pixel_readout

        time_read_rows = (self.v_end - self.v_start + 1) * (time_row_parallel + (self.h_end + 1) * time_pixel_readout)
        time_dump_rows = (self.v_start + self.rows_final_dump) * time_row_clearout

        return time_read_rows + time_dump_rows

    def get_vgd(self):
        """ Extract the VGD voltage from the register map.

        Return: Configured VGD voltage [V].
        """

        vgd_19 = self.register_map[('reg_19_config', 'ccd_vgd_config')]
        vgd_20 = self.register_map[('reg_20_config', 'ccd_vgd_config')]

        return ((vgd_20 << 4) + vgd_19) / 1000 * 5.983

    def get_ccd2_vrd(self):
        """
        Extract the VRD voltage for CCD2 from the register map.

        NOTE: Use this function only for the FM cameras.

        Return: Configured VRD voltage.
        """
        vrd_18 = self.register_map[('reg_18_config', 'ccd2_vrd_config')]
        vrd_19 = self.register_map[('reg_19_config', 'ccd2_vrd_config')]

        return int(f'0x{vrd_19:x}{vrd_18:x}', 16)


    def get_ccd3_vrd(self):
        """
        Extract the VRD voltage for CCD3 from the register map.

        NOTE: Use this function only for the EM camera.

        Return: Configured VRD voltage.
        """
        vrd_18 = self.register_map[('reg_18_config', 'ccd3_vrd_config')]
        vrd_19 = self.register_map[('reg_19_config', 'ccd3_vrd_config')]

        return int(f'0x{vrd_19:x}{vrd_18:x}', 16)


    def init_data_arrays(self):
        """ Initialise data arrays in which the data content of the SpW packets will be dumped.

        At this point, we have already determined which side(s) of which CCD(s) will be read out.  For each of them,
        a placeholder will be foreseen in a dedicated dictionary.  The structure of this dictionary is the following,
        in case both sides of all CCDs will be read:

            data_arrays[fee_side.LEFT_SIDE][1] # left side of CCD1
            data_arrays[fee_side.LEFT_SIDE][2] # left side of CCD2
            data_arrays[fee_side.LEFT_SIDE][3] # left side of CCD3
            data_arrays[fee_side.LEFT_SIDE][4] # left side of CCD4
            data_arrays[fee_side.RIGHT_SIDE][1] # right side of CCD1
            data_arrays[fee_side.RIGHT_SIDE][2] # right side of CCD2
            data_arrays[fee_side.RIGHT_SIDE][3] # right side of CCD3
            data_arrays[fee_side.RIGHT_SIDE][4] # right side of CCD4

        In case not all CCDs will be read out and/or only one side, placeholders will only be foreseen for the relevant
        CCD data.

        Returns: Dictionary with placeholders for the data arrays of the selected CCD sides.
        """

        left_side_arrays = {ccd: np.array([], dtype=np.uint16) for ccd in self.selected_ccds}
        self.data_arrays[self.fee_side.LEFT_SIDE] = left_side_arrays

        right_side_arrays = {ccd: np.array([], dtype=np.uint16) for ccd in self.selected_ccds}
        self.data_arrays[self.fee_side.RIGHT_SIDE] = right_side_arrays

    def clear_for_next_exposure(self, ccd_number: int, ccd_side):
        """ Indicate that no data has been received yet for the next exposure of the given CCD.

        At the end of an exposure, when the data have been assembled and written to FITS:

            - clear the data arrays for the next exposure;
            - indicate that the last packet has not been received yet for the next exposure;
            - clear the timestamp for the next exposure.

        Args:
            - ccd_number: CCD identifier (1/2/3/4).
            - ccd_side: CCD side from which the last received data originates.
        """

        for ccd_side in self.fee_side:
            self.clear_data_arrays(ccd_number, ccd_side)

        self.clear_last_packet_received(ccd_number)

    def clear_data_arrays(self, ccd_number: int, ccd_side):
        """ Clear the data arrays for the given CCD.

        At the end of an exposure, when the data have been assembled and written to FITS, the data arrays must be
        cleared for the next exposure.

        Args:
            - ccd_number: CCD identifier (1/2/3/4).
        """

        self.data_arrays[ccd_side][ccd_number] = np.array([], dtype=np.uint16)

    def clear_last_packet_received(self, ccd_number: int):
        """ Clear the information about the last packet being received for the given CCD.

        At the end of an exposure, when the data have been assembled and written to FITS, it must be indicated that the
        last packet has not been received for the next exposure for the given CCD.

        Args:
            - ccd_number: CCD identifier (1/2/3/4).
        """

        self.received_last_packet_flags[ccd_number] = [False for el in self.received_last_packet_flags[ccd_number]]

    # def get_data_array(self, ccd_number: int, ccd_side: fee_side):
    #     """ Return the data array for the given side of the given CCD.
    #
    #     In this array all SpW data concerning the serial pre-scan, image, serial over-scan, and parallel over-scan
    #     will be dumped (in 1D).  If the last data packet has been received, the different parts will be extracted and
    #     written to FITS.
    #
    #     Args:
    #         - ccd_number: CCD identifier (1/2/3/4).
    #         - ccd_side: CCD side.
    #
    #     Returns: Data array for the given side of the given CCD.
    #     """
    #
    #     return self.data_arrays[ccd_side][ccd_number]

    def check_readout_mode(self):
        """ For now only checks whether the N-FEE is in the correct mode, i.e. full-image (pattern) mode.

        In the future, if deemed necessary, windowing (pattern) mode may be implemented as well.
        """

        if self.ccd_mode_config in [n_fee_mode.FULL_IMAGE_MODE, n_fee_mode.FULL_IMAGE_PATTERN_MODE,
                                    n_fee_mode.PARALLEL_TRAP_PUMPING_1_MODE, n_fee_mode.PARALLEL_TRAP_PUMPING_2_MODE,
                                    n_fee_mode.SERIAL_TRAP_PUMPING_1_MODE, n_fee_mode.SERIAL_TRAP_PUMPING_2_MODE]:

            return False

        if self.ccd_mode_config in [n_fee_mode.WINDOWING_PATTERN_MODE, n_fee_mode.WINDOWING_MODE]:

            return True

        else:

            raise FITSPersistenceError("Construction of FITS files from SpW packets only implemented for full-image "
                                       "(pattern) mode, windowing (pattern) mode, and parallel/serial trap pumping 1/2 "
                                       "mode")

    # def init_window_list(self, window_list: dict):
    #     """ Compile the window list.
    #
    #     For each of the CCDs that will be read out, execute the following steps:
    #
    #         - For each of the CCD sides that will be transmitted, identify which pixels in the compound 2D array (i.e.
    #           in which the image and the scan maps are still glued together) will be transmitted.  Store their index
    #           in the corresponding 1D array in a dictionary.
    #         - Store the pixel coordinates of the lower left corner of the window (in the CCD reference frame) of all
    #           windows in the image area.
    #     """
    #
    #     window_indices = {ccd_side: {} for ccd_side in self.selected_ccd_side}
    #
    #     for ccd_number in self.selected_ccds:
    #
    #         # Get the window information for the current CCD
    #
    #         ccd_window_list_obj: WindowList = window_list[ccd_number]
    #         ccd_window_list = ccd_window_list_obj.get_window_list()     # Ordered set of windows
    #         ccd_window_num_columns, ccd_window_num_rows = ccd_window_list_obj.get_window_size()     # Window size
    #
    #         ccd_window_x_array = np.array([])
    #         ccd_window_y_array = np.array([])
    #
    #         ccd_window_indices = {ccd_side: np.array([]) for ccd_side in self.selected_ccd_side}
    #
    #         for (x_window, y_window, ccd_side_window) in ccd_window_list:
    #
    #             # Calculate the index in the 1D array
    #
    #             for row in range(y_window, y_window + ccd_window_num_rows + 1):
    #
    #                 for column in range(x_window, x_window + ccd_window_num_columns + 1):
    #
    #                     index = row * (self.v_end - self.v_start + 1) + column
    #                     ccd_window_indices[ccd_side_window] = np.append(ccd_window_indices[ccd_side_window], index)
    #
    #             # Store the coordinates of the lower left corner of the windows in the CCD reference frame
    #             # (only for the windows in the image area)
    #
    #             x_to_append = x_window - CCD_SETTINGS.LENGTH_SERIAL_PRESCAN
    #
    #             # TODO Should we check that the window is on the image area?
    #
    #             if ccd_side_window == fee_side.F_SIDE:
    #
    #                 x_to_append = CCD_SETTINGS.NUM_COLUMNS / 2 - 1 - x_to_append
    #
    #                 if fee_side.E_SIDE in self.selected_ccd_side:
    #
    #                     x_to_append += CCD_SETTINGS.NUM_COLUMNS / 2
    #
    #             ccd_window_x_array = np.append(ccd_window_x_array, x_to_append)
    #             ccd_window_y_array = np.append(ccd_window_y_array, y_window)
    #
    #         for ccd_side in self.selected_ccd_side:
    #
    #             window_indices[ccd_side][ccd_number] = np.sort(np.unique(ccd_window_indices[ccd_side]))
    #
    #         rows = fits.Column("Rows", format="I", array=ccd_window_y_array)
    #         columns = fits.Column("Columns", format="I", array=ccd_window_x_array)
    #         table = fits.BinTableHDU.from_columns([rows, columns])
    #         table.header["EXTNAME"] = f"Windows"
    #         table.header["EXTVER"] = ccd_number
    #         table.header["CCD_ID"] = (ccd_number, "CCD identifier",)
    #
    #         # TODO
    #
    #         # fits.append(table)
    #
    #         # with fits.open(self._filepath, mode="append") as hdul:
    #         #
    #         #     hdul.append(table)
    #
    #     return window_indices

    def create_primary_header(self):
        """ Creates the primary header (i.e. the header of the primary HDU).

        This contains information that is specific for the camera.
        """

        primary_header = fits.PrimaryHDU().header

        primary_header["LEVEL"] = 1     # Flat structure

        primary_header["V_START"] = (self.v_start, "Index of 1st row that is transmitted (counting starts at 0)")
        primary_header["V_END"] = (self.v_end, "Index of last row that is transmitted (counting starts at 0)")
        primary_header["H_END"] = (self.h_end, "Number of serial register transfers")
        primary_header["ROWS_FINAL_DUMP"] = (self.rows_final_dump, "Number of rows for clearout after readout")
        primary_header["READ_MODE"] = (n_fee_mode(self.ccd_mode_config).name, "N-FEE operating mode")

        primary_header["CI_WIDTH"] = (self.register_map["charge_injection_width"],
                                      "Number of rows in each charge injection region")
        primary_header["CI_GAP"] = (self.register_map["charge_injection_gap"],
                                    "Number of rows between charge injection regions")
        primary_header["PARALLEL_TOI_PERIOD"] = (self.register_map["parallel_toi_period"],
                                                 "Duration of a parallel  overlap period (TOI) [us]")
        primary_header["PARALLEL_CLK_OVERLAP"] = (self.register_map["parallel_clk_overlap"],
                                                  "Extra parallel clock overlap [us]")
        primary_header["CI_EN"] = (self.register_map["charge_injection_width"],
                                   "Charge injection enabled (1) / disabled (0)")
        primary_header["TRI_LEVEL_CLK_EN"] = (self.register_map["tri_level_clk_en"],
                                              "Generating bi-level parallel clocks (0) / tri-level parallel clocks (1)")
        primary_header["IMG_CLK_DIR"] = (self.register_map["img_clk_dir"],
                                         "Generating reverse parallel clocks (1) / normal forward parallel clocks (0)")
        primary_header["REG_CLK_DIR"] = (self.register_map["reg_clk_dir"],
                                         "Generating reverse serial clocks (1) / normal forward serial clocks (0)")
        primary_header["PACKET_SIZE"] = (self.register_map["packet_size"],
                                         "Packet size = load bytes + 10 (header bytes)")

        primary_header["TRAP_PUMP_DWELL_CTR"] = (self.register_map["Trap_Pumping_Dwell_counter"],
                                                 "Dwell timer for trap pumping [ns]")
        primary_header["SENSOR_SEL"] = (self.register_map["sensor_sel"], "CCD port data transmission selection control")
        primary_header["SYNC_SEL"] = (self.register_map["sync_sel"], "Internal (1) / external (0) sync")
        primary_header["DIGITISE_EN"] = (self.register_map["digitise_en"],
                                         "Digitised data transferred to the N-DPU (1) or not (0) during image mode")
        primary_header["DG_EN"] = (self.register_map["DG_en"], "Dump gate high (1) / low (0)")
        primary_header["CCD_READ_EN"] = (self.register_map["ccd_read_en"], "CCD readout enabled (1) / disabled (0)")
        primary_header["CONV_DLY"] = (self.register_map["conv_dly"],
                                      "Delay value from rising edge of CCD_R_EF_DRV (where ADC convert pulse "
                                      "is generated) [ns]")
        primary_header["HIGH_PRECISION_HK_EN"] = (self.register_map["High_precision_HK_en"],
                                                  "Sending high-precision HK (1) / pixel data (0)")

        primary_header["CCD_VOD"] = (self.register_map["ccd_vod_config"], "Configured VOD")

        primary_header["CCD1_VRD"] = (self.register_map["ccd1_vrd_config"], "Configured VRD for CCD1")
        if PLATO_CAMERA_IS_EM:
            primary_header["CCD2_VRD"] = (self.register_map["ccd2_vrd_config"], "Configured VRD for CCD2")
            primary_header["CCD3_VRD"] = (self.get_ccd3_vrd(), "Configured VRD for CCD3")
        else:
            primary_header["CCD2_VRD"] = (self.get_ccd2_vrd(), "Configured VRD for CCD2")
            primary_header["CCD3_VRD"] = (self.register_map["ccd3_vrd_config"], "Configured VRD for CCD3")

        primary_header["CCD4_VRD"] = (self.register_map["ccd4_vrd_config"], "Configured VRD for CCD4")
        primary_header["CCD_VOG"] = (self.register_map["ccd_vog_config"], "Configured VOG")
        primary_header["CCD_VGD"] = (self.get_vgd(), "Configured VGD [V]")
        primary_header["CCD_IG_HI"] = (self.register_map["ccd_ig_hi_config"], "Configured IG-high")
        primary_header["CCD_IG_LO"] = (self.register_map["ccd_ig_lo_config"], "Configured IG-high")
        primary_header["TRK_HLD_HI"] = (self.register_map["trk_hld_hi"], "Track and hold high")
        primary_header["TRK_HLD_LO"] = (self.register_map["trk_hld_lo"], "Track and hold low")
        primary_header["CONT_RST_ON"] = (self.register_map["cont_rst_on"],
                                         "When 1, FPGA generates continuous reset clock during readout")
        if not PLATO_CAMERA_IS_EM:
            primary_header["CONT_CDSCLP_ON"] = (self.register_map["cont_cdsclp_on"],
                                                "When 1, FPGA generates continuous CDS clamp during readout")
            primary_header["CONT_ROWCLP_ON"] = (self.register_map["cont_rowclp_on"],
                                                "When 1, FPGA generates continuous row clamp during readout")
        primary_header["R_CFG1"] = (self.register_map["r_cfg1"], "Clock cycle for Rph3-low, Rph1-high")
        primary_header["R_CFG2"] = (self.register_map["r_cfg2"], "Clock cycle for Rph1-low, Rph2-high")
        primary_header["CDSCLP_LO"] = (self.register_map["cdsclp_lo"], "Clock cycle for cdsclp low")
        if not PLATO_CAMERA_IS_EM:
            primary_header["ADC_PWRDN_EN"] = (self.register_map["adc_pwrdn_en"],
                                              "ADC power-down enabled (0) / disabled (1)")
            primary_header["CDSCLP_HI"] = (self.register_map["cdsclp_hi"], "Clock cycle for cdsclp high")
            primary_header["ROWCLP_HI"] = (self.register_map["rowclp_hi"], "Clock cycle for rowclp high")
            primary_header["ROWCLP_LO"] = (self.register_map["rowclp_lo"], "Clock cycle for rowclp low")
        # primary_header["SURFACE_INV_CTR"] = (self.register_map["Surface_Inversion_counter"],
        #                                      "Surface inversion counter")
        primary_header["READOUT_PAUSE_CTR"] = (self.register_map["Readout_pause_counter"], "Readout pause counter")
        primary_header["TRAP_PUMP_SHUFFLE_CTR"] = (self.register_map["Trap_Pumping_Shuffle_counter"],
                                                   "Trap pumping shuffle counter")

        # primary_header["FOCALLEN"] = (FOV_SETTINGS["FOCAL_LENGTH"], "Focal length [mm]")

        # Additional keywords

        primary_header["TELESCOP"] = "PLATO"
        if self.camera_id:
            primary_header["INSTRUME"] = (self.camera_id, "Camera ID")
        primary_header["SITENAME"] = (self.site_name, "Name of the test site")
        primary_header["SETUP"] = (self.setup_id, "Setup ID")
        primary_header["CCD_READOUT_ORDER"] = (str(self.ccd_readout_order), "Transmitted CCDs")
        primary_header["CYCLETIME"] = (self.cycle_time, "Image cycle time [s]")
        primary_header["READTIME"] = (self.readout_time,
                                      "Time needed to read out the requested part for a single CCD side [s]")

        if self.register_map["sync_sel"] == 1:  # See https://github.com/IvS-KULeuven/plato-common-egse/issues/2475
            primary_header["READPERIOD"] = (self.cycle_time + INT_SYNC_TIMING_OFFSET, "Time between frames [s] "
                                                                                       "(internal sync)")
            texp_cmd = self.cycle_time - self.readout_time
            primary_header["TEXP_CMD"] = (texp_cmd, "Commanded exposure time [s] (internal sync)")
            primary_header["TEXP_EFF"] = (texp_cmd + INT_SYNC_TIMING_OFFSET, "Effective exposure time [s] (internal "
                                                                              "sync)")

        primary_header["CGSE"] = (self.cgse_version, "Version of the Common EGSE")

        logger.info(f"Obsid in FITS persistence layer: {self.obsid}")

        if self.obsid is not None:

            logger.debug(f"{self.obsid = }")

            primary_header["OBSID"] = (self.obsid, "Observation identifier")

        primary_header["PRE_SC_N"] = (CCD_SETTINGS.LENGTH_SERIAL_PRESCAN,
                                      "Number of pixels/columns in the serial pre-scan")
        primary_header["OVR_SC_N"] = (max(0, self.h_end + 1
                                          - CCD_SETTINGS.LENGTH_SERIAL_PRESCAN - CCD_SETTINGS.NUM_COLUMNS // 2),
                                      "Number of virtual pixels / columns in the serial over-scan")
        primary_header["OVR_SC_R"] = (max(0, self.v_end + 1 - CCD_SETTINGS.NUM_ROWS),
                                      "Number of rows in the parallel over-scan")
        primary_header["IMG_REPR"] = ("FOV_IMG", "Right CCD side flipped w.r.t. readout direction")

        return primary_header

    def create_base_image_wcs(self):
        """ Create a basic FITS header for the image.

        Not all information can be filled out at this point (i.c. extension, CCD identifier, number of columns,
        rotation, reference pixel).  This will be done at the moment the serial pre-scan will be written to file.

        Note that, if both CCD sides will be transmitted, the image of both sides will be glued together (the E-side
        must be flipped horizontally first).  If only the E-side will be transmitted, its image must be flipped
        horizontally.

        Returns: Basic FITS header for the image.
        """

        image_header = fits.ImageHDU().header

        # Make sure the data is saved as 16-bit

        image_header["BITPIX"] = 16
        image_header["BZERO"] = 32768

        # Dimensionality

        num_rows = min(CCD_SETTINGS["NUM_ROWS"] - 1, self.v_end) - self.v_start + 1

        image_header["NAXIS"] = (2, "Dimensionality of the image",)
        image_header["NAXIS2"] = (num_rows, "Number of rows in the image",)


        # Focal length (this is needed for the conversion to field angles)

        image_header["FOCALLEN"] = (FOV_SETTINGS["FOCAL_LENGTH"], "Focal length [mm]",) # TODO

        # Linear coordinate transformation from sub-field to focal-plane coordinates

        image_header["ctype1"] = ("LINEAR", "Linear coordinate transformation",)
        image_header["ctype2"] = ("LINEAR", "Linear coordinate transformation",)

        # Focal-plane coordinates are expressed in mm

        image_header["CUNIT1"] = ("MM", "Target unit in the column direction (mm)",)
        image_header["CUNIT2"] = ("MM", "Target unit in the row direction (mm)",)

        # Pixel size

        cdelt = CCD_SETTINGS["PIXEL_SIZE"] / 1000.0  # Pixel size [mm]
        image_header["CDELT1"] = (cdelt, "Pixel size in the x-direction [mm]",)
        image_header["CDELT2"] = (cdelt, "Pixel size in the y-direction [mm]",)

        # Additional keywords

        # image_header["TELESCOP"] = (setup["camera_id"], "Camera ID")
        # image_header["INSTRUME"] = (setup["camera_id"], "Camera ID")

        image_header["TELESCOP"] = "PLATO"
        if self.camera_id:
            image_header["INSTRUME"] = (self.camera_id, "Camera ID")
        image_header["SITENAME"] = (self.site_name, "Name of the test site")
        image_header["SETUP"] = (self.setup_id, "Setup ID")
        if self.obsid is not None:
            image_header["OBSID"] = (self.obsid, "Observation identifier")

        return image_header

    def create_base_serial_prescan_wcs(self):
        """ Create a basic FITS header for the serial pre-scan.

        Not all information can be filled out at this point (i.c. extension, CCD identifier).  This will be
        done at the moment the serial pre-scan will be written to file.

        Note that, if both CCD sides will be transmitted, you will end up having to serial pre-scan maps per exposures
        (one for each side).

        Returns: Basic FITS header for the serial pre-scan.
        """

        serial_prescan_wcs = fits.ImageHDU().header

        # Make sure the data is saved as 16-bit

        serial_prescan_wcs["BITPIX"] = 16
        serial_prescan_wcs["BZERO"] = 32768

        # Dimensionality

        num_rows = self.v_end - self.v_start + 1
        num_columns = CCD_SETTINGS.LENGTH_SERIAL_PRESCAN

        serial_prescan_wcs["NAXIS"] = (2, "Dimensionality of the serial pre-scan",)
        serial_prescan_wcs["NAXIS1"] = (num_columns, "Number of columns in the serial pre-scan",)
        serial_prescan_wcs["NAXIS2"] = (num_rows, "Number of rows in the serial pre-scan",)

        serial_prescan_wcs["TELESCOP"] = "PLATO"
        if self.camera_id:
            serial_prescan_wcs["INSTRUME"] = (self.camera_id, "Camera ID")
        serial_prescan_wcs["SITENAME"] = (self.site_name, "Name of the test site")
        serial_prescan_wcs["SETUP"] = (self.setup_id, "Setup ID")
        if self.obsid is not None:
            serial_prescan_wcs["OBSID"] = (self.obsid, "Observation identifier")

        return serial_prescan_wcs

    def create_base_serial_overscan_wcs(self):
        """ Create a basic FITS header for the serial over-scan.

        Not all information can be filled out at this point (i.c. extension, CCD identifier).  This will be
        done at the moment the serial over-scan will be written to file.

        Note that, if both CCD sides will be transmitted, you will end up having to serial over-scan maps per exposures
        (one for each side).

        Returns: Basic FITS header for the serial over-scan.
        """

        serial_overscan_wcs = fits.ImageHDU().header

        # Make sure the data is saved as 16-bit

        serial_overscan_wcs["BITPIX"] = 16
        serial_overscan_wcs["BZERO"] = 32768

        # Dimensionality

        num_rows = self.v_end - self.v_start + 1
        num_columns = self.v_end + 1 - CCD_SETTINGS.LENGTH_SERIAL_PRESCAN - CCD_SETTINGS.NUM_COLUMNS / 2

        serial_overscan_wcs["NAXIS"] = (2, "Dimensionality of the serial over-scan",)
        serial_overscan_wcs["NAXIS1"] = (num_columns, "Number of columns in the serial over-scan",)
        serial_overscan_wcs["NAXIS2"] = (num_rows, "Number of rows in the serial over-scan",)

        # Site name

        serial_overscan_wcs["TELESCOP"] = "PLATO"
        if self.camera_id:
            serial_overscan_wcs["INSTRUME"] = (self.camera_id, "Camera ID")
        serial_overscan_wcs["SITENAME"] = (self.site_name, "Name of the test site")
        serial_overscan_wcs["SETUP"] = (self.setup_id, "Setup ID")
        if self.obsid is not None:
            serial_overscan_wcs["OBSID"] = (self.obsid, "Observation identifier")

        return serial_overscan_wcs

    def create_base_parallel_overscan_wcs(self):
        """ Create a basic FITS header for the parallel over-scan.

        Not all information can be filled out at this point (i.c. extension, CCD identifier, number of columns).  This
        will be done at the moment the parallel over-scan will be written to file.

        Note that, if both CCD sides will be transmitted, the parallel over-scan of both sides will be glued together
        (the E-side must be flipped horizontally first).  If only the E-side will be transmitted, its parallel
        over-scan must be flipped horizontally.

        Returns: Basic FITS header for the parallel over-scan.
        """

        parallel_overscan_wcs = fits.ImageHDU().header

        # Make sure the data is saved as 16-bit

        parallel_overscan_wcs["BITPIX"] = 16
        parallel_overscan_wcs["BZERO"] = 32768

        # Dimensionality

        num_rows_parallel_overscan = max(0, self.v_end - CCD_SETTINGS.NUM_ROWS + 1)

        parallel_overscan_wcs["NAXIS"] = (2, "Dimensionality of the parallel over-scan",)
        parallel_overscan_wcs["NAXIS2"] = (num_rows_parallel_overscan, "Number of rows in the parallel over-scan",)

        # Site name

        parallel_overscan_wcs["TELESCOP"] = "PLATO"
        if self.camera_id:
            parallel_overscan_wcs["INSTRUME"] = (self.camera_id, "Camera ID")
        parallel_overscan_wcs["SITENAME"] = (self.site_name, "Name of the test site")
        parallel_overscan_wcs["SETUP"] = (self.setup_id, "Setup ID")
        if self.obsid is not None:
            parallel_overscan_wcs["OBSID"] = (self.obsid, "Observation identifier")

        return parallel_overscan_wcs

    def open(self, mode=None):

        primary_header = self.create_primary_header()

        # The primary HDU contains only this header and no image data

        primary_hdu = fits.PrimaryHDU()
        primary_hdu.header = primary_header

        # The FITS file is created.  If the filename is already in use, and exception
        # will be thrown.

        primary_hdu.writeto(self._filepath)

        self.is_fits_file_open = True

    def close(self):
        """Closes the resource."""

        self.is_fits_file_open = False

    def exists(self):

        return self._filepath.exists()

    def create(self, data: dict):
        """Add the given data to the FITS file.

        The given data is a stream of SpW packets, only part of which contains information should go in the FITS file:

            - Image (and over-scan) data contain the transmitted readout of the CCD(s);
            - Timecode and housekeeping packets are not needed for this purpose.
        """

        for key, spw_packet in data.items():

            # if isinstance(spw_packet, TimecodePacket):
            #
            #     self.timestamp = spw_packet.

            if key == "Timestamp":

                self.timestamp = spw_packet
                self.finetime = time_since_epoch_1958(self.timestamp)

            elif isinstance(spw_packet, DataPacket):

                try:
                    ccd_bin_to_id = self.setup.camera.fee.ccd_numbering.CCD_BIN_TO_ID
                except AttributeError:
                    raise SetupError("No entry in the setup for camera.fee.ccd_numbering.CCD_BIN_TO_ID")
                spw_packet_data_type = spw_packet.type
                ccd_number = ccd_bin_to_id[spw_packet_data_type.ccd_number] # 1-4
                ccd_side = self.fee_side(spw_packet_data_type.ccd_side)
                data_array = spw_packet.data_as_ndarray

                self.data_arrays[ccd_side][ccd_number] = np.append(self.data_arrays[ccd_side][ccd_number], data_array)

                # If all data has been received for the current exposure of this CCD, the following steps must be
                # performed:
                #   - re-shape the 1D data arrays to 2D data arrays;
                #   - extract the different pieces of the 2D data arrays (image + scan maps);
                #   - for the F-side: flip the image and parallel over-scan horizontally;
                #   - if both CCD sides are transmitted, stitch them together (for the image and parallel
                #     over-scan);
                #   - update the WCS of the different regions;
                #   - add to the FITS file.

                if self.is_all_data_received(spw_packet_data_type, ccd_number, ccd_side):

                    # Write the information to FITS

                    for ccd_side in self.fee_side:

                        try:
                            if self.data_arrays[ccd_side][ccd_number].size > 0:
                                self.assemble_slice(ccd_number, ccd_side)
                                self.frame_number[ccd_number][ccd_side] += 1
                        except MissingSpWPacketsError as exc:
                            logger.info(exc)

                    # Get ready for the next exposure

                    self.clear_for_next_exposure(ccd_number, ccd_side)

    def is_all_data_received(self, spw_packet_data_type: DataPacketType, ccd_number: int, ccd_side):
        """ Check if all data has been received for the current exposure.

        Args:
            - spw_packet_data_type: Last received data packet type.
            - ccd_number: CCD from which the last received data originates (1-4).
            - ccd_side: CCD side from which the last received data originates.

        Returns: True if all data for the current exposure has been received; False otherwise.
        """

        from egse.dpu import got_all_last_packets

        if spw_packet_data_type.last_packet:

            packet_type = spw_packet_data_type.packet_type

            if packet_type == PacketType.DATA_PACKET:

                if ccd_side == self.fee_side.E_SIDE:

                    self.received_last_packet_flags[ccd_number][0] = True

                elif ccd_side == self.fee_side.F_SIDE:

                    self.received_last_packet_flags[ccd_number][1] = True

            elif packet_type == PacketType.OVERSCAN_DATA:

                if ccd_side == self.fee_side.E_SIDE:

                    self.received_last_packet_flags[ccd_number][2] = True

                elif ccd_side == self.fee_side.F_SIDE:

                    self.received_last_packet_flags[ccd_number][3] = True

        return got_all_last_packets(self.received_last_packet_flags[ccd_number], self.expected_last_packet_flags)

    def got_all_last_packets(self, ccd_number: int, ccd_side):
        """ Check whether all the expected last-packet  flags have been seen for the given CCD side.

        Args:
            - ccd_number: CCD from which the last received data originates (1-4).
            - ccd_side: CCD side from which the last received data originates.

        Returns: True if the actual and the expected last-packet flags match for the given CCD side of the given CCD;
                 False otherwise.
        """

        received_last_packet_flags = self.received_last_packet_flags[ccd_number]

        if ccd_side == self.fee_side.E_SIDE:

            return received_last_packet_flags[0] == self.expected_last_packet_flags[0] \
                   and received_last_packet_flags[2] == self.expected_last_packet_flags[2]

        elif ccd_side == self.fee_side.F_SIDE:

            return received_last_packet_flags[1] == self.expected_last_packet_flags[1] \
                   and received_last_packet_flags[3] == self.expected_last_packet_flags[3]

        return False

    def assemble_slice(self, ccd_number: int, ccd_side):
        """ Assemble the data for the given CCD and write it to FITS.

        Args:
            - ccd_number: CCD identifier (1/2/3/4).
        """

        # Windowing (pattern) mode

        if self.is_windowing_mode:

            # self.assemble_slice_windowing_mode(ccd_number, ccd_side)
            pass

        # Full-image (pattern) mode

        else:

            self.assemble_slice_full_image_mode(ccd_number, ccd_side)

    # def assemble_slice_windowing_mode(self, ccd_number: int):
    #     """ Assemble the data for the given CCD and write it to FITS, for windowing mode or windowing pattern mode.
    #
    #     This consists of the following steps:
    #
    #         - Create a 1D array, filled with NaNs, exactly big enough to fit the image and scan maps;
    #         - Insert the data that was acquired (i.e. coming from the windows);
    #         - Convert the 1D data arrays to a 2D data array, in which the image and the scan maps are still glued
    #           together (do this for each transmitted CCD side);
    #         - Extract for each transmitted CCD side the different regions from the 2D array (image, serial pre-scan,
    #           serial over-scan, and parallel over-scan);
    #         - Append the serial pre-scan of the transmitted CCD side(s) to the FITS file (after completing its header);
    #         - Append the serial over-scan of the transmitted CCD side(s) to the FITS file (after completing its header),
    #           if present;
    #         - In case the F-side is transmitted, flips its image and parallel over-scan horizontally;
    #         - In case both sides are transmitted, stitch the two sides together for the image and the parallel
    #           over-scan;
    #         - Append the parallel over-scan to the FITS file (after completing its header), if present;
    #         - Append the image to the FITS file (after completing its header).
    #
    #     Args:
    #         - ccd_number: CCD identifier (1/2/3/4).
    #     """
    #
    #     num_rows = self.v_end - self.v_start + 1
    #     num_columns = self.h_end + 1
    #
    #     num_rows_image = min(CCD_SETTINGS.NUM_ROWS - 1, self.v_end) - self.v_start + 1
    #     num_rows_parallel_overscan = max(0, num_rows - num_rows_image)
    #
    #     image = np.array([]).reshape(num_rows_image, 0)
    #     parallel_overscan = np.array([]).reshape(num_rows_parallel_overscan, 0)
    #
    #     for ccd_side in fee_side:
    #
    #         if ccd_side in self.data_arrays:
    #
    #             data_array = np.array([float("nan")] * (num_rows * num_columns))
    #             data_array[self.windows[ccd_side][ccd_number]] = self.data_arrays[ccd_side][ccd_number]
    #
    #             side_image, side_serial_prescan, side_serial_overscan, side_parallel_overscan = \
    #                 self.extract_full_image_mode(data_array)
    #
    #             # Serial pre-scan
    #
    #             self.append_serial_prescan(side_serial_prescan, ccd_number, ccd_side)
    #
    #             # Serial over-scan
    #
    #             if self.has_serial_overscan:
    #
    #                 self.append_serial_overscan(side_serial_overscan, ccd_number, ccd_side)
    #
    #             # For the F-side, the image and parallel over-scan must be flipped horizontally
    #
    #             if ccd_side == fee_side.F_SIDE:
    #
    #                 side_image, side_parallel_overscan = self.flip_f_side_full_image_mode(side_image,
    #                                                                                       side_parallel_overscan)
    #
    #             # Image (the part that is on this side)
    #
    #             image = np.hstack([image, side_image])
    #
    #             # Parallel over-scan (the part that is on this side)
    #
    #             if self.has_parallel_overscan:
    #
    #                 parallel_overscan = np.hstack([parallel_overscan, side_parallel_overscan])
    #
    #     # Parallel over-scan
    #
    #     if self.has_parallel_overscan:
    #
    #         self.append_parallel_overscan(parallel_overscan, ccd_number)
    #
    #     # Image
    #
    #     self.append_image(image, ccd_number)

    def assemble_slice_full_image_mode(self, ccd_number: int, ccd_side):
        """ Assemble the data for the given CCD and write it to FITS, for full-image mode or full-image pattern mode.

        This consists of the following steps:

            - Convert the 1D data arrays to a 2D data array, in which the image and the scan maps are still glued
              together (do this for each transmitted CCD side);
            - Extract for each transmitted CCD side the different regions from the 2D array (image, serial pre-scan,
              serial over-scan, and parallel over-scan);
            - Append the serial pre-scan of the transmitted CCD side(s) to the FITS file (after completing its header);
            - Append the serial over-scan of the transmitted CCD side(s) to the FITS file (after completing its header),
              if present;
            - In case the F-side is transmitted, flips its image and parallel over-scan horizontally;
            - In case both sides are transmitted, stitch the two sides together for the image and the parallel
              over-scan;
            - Append the parallel over-scan to the FITS file (after completing its header), if present;
            - Append the image to the FITS file (after completing its header).

        Args:
            - ccd_number: CCD identifier (1/2/3/4).
        """

        num_rows = self.v_end - self.v_start + 1
        num_columns = self.h_end + 1

        # Re-shape the 1D array to a 2D array and extract the image and scan maps

        try:
            data_array = np.reshape(self.data_arrays[ccd_side][ccd_number], (num_rows, num_columns))    # 1D -> 2D
        except ValueError as exc:
            raise MissingSpWPacketsError(f"Incomplete SpW data for frame {self.frame_number[ccd_number][ccd_side]} "
                                         f"for the {ccd_side.name[0]}-side off CCD{ccd_number}.  Check the DPU "
                                         f"Processing logs for more information.") from exc
        side_image, side_serial_prescan, side_serial_overscan, side_parallel_overscan = \
            self.extract_full_image_mode(data_array)

        # Serial pre-scan

        self.append_serial_prescan(side_serial_prescan, ccd_number, ccd_side)

        # Serial over-scan

        if self.has_serial_overscan:

            self.append_serial_overscan(side_serial_overscan, ccd_number, ccd_side)

        # Parallel over-scan

        if self.has_parallel_overscan:

            self.append_parallel_overscan(side_parallel_overscan, ccd_number, ccd_side)

        # Image

        self.append_image(side_image, ccd_number, ccd_side)

    def extract_full_image_mode(self, data_array):
        """Extract the image and scan maps from the given data array.

        For the F-side, the image and parallel over-scan still have to be flipped horizontally.

        Args:
            - data_array: 2D array in which the image data and scan maps are still glued together.

        Returns:
            - Image data;
            - Serial pre-scan;
            - Serial over-scan;
            - Parallel over-scan.
        """

        # Calculate the following indices:
        #   - Column index of the first transmitted image column;
        #   - Column index of the last transmitted image column + 1 (if the serial over-scan is transmitted, this will
        #     be the column index of the first transmitted serial over-scan column);
        #   - Row index of the last transmitted image row + 1 (if the parallel over-scan is transmitted, this will be
        #     the row index of the first transmitted parallel over-scan row).

        start_column_image = CCD_SETTINGS.LENGTH_SERIAL_PRESCAN
        end_column_image_plus_1 = min(CCD_SETTINGS.LENGTH_SERIAL_PRESCAN + CCD_SETTINGS.NUM_COLUMNS // 2, self.h_end + 1)
        end_row_image_plus_1 = min(CCD_SETTINGS.NUM_ROWS - 1, self.v_end) - self.v_start + 1

        # Serial pre-scan (all rows, but only the first couple of rows)

        serial_prescan = data_array[:, 0: start_column_image]

        # Serial over-scan (all rows, omit the columns from the serial pre-scan and the serial over-scan)

        if self.has_serial_overscan:

            serial_overscan = data_array[:, end_column_image_plus_1:]

        else:

            serial_overscan = None

        # Image (omit the rows from the parallel over-scan
        # and the columns from the serial pre-scan and the serial over-scan)

        image = data_array[0: end_row_image_plus_1, start_column_image: end_column_image_plus_1]

        # Parallel over-scan

        if self.has_parallel_overscan:

            parallel_overscan = data_array[end_row_image_plus_1:, start_column_image: end_column_image_plus_1]

        else:

            parallel_overscan = None

        return image, serial_prescan, serial_overscan, parallel_overscan

    def append_serial_prescan(self, serial_prescan, ccd_number: int, ccd_side: str):
        """ Append the given serial pre-scan to the FITS file (after completing its header).

        Args:
            - serial_prescan: Serial pre-scan.
            - ccd_number: CCD identifier.
            - ccd_side: CCD side.
        """

        extension = f"SPRE_{ccd_number}_{self.fee_side(ccd_side).name[0]}"
        self.serial_prescan_header["EXTNAME"] = extension
        self.serial_prescan_header["EXTVER"] = self.frame_number[ccd_number][ccd_side]
        self.serial_prescan_header["CCD_ID"] = (ccd_number, "CCD identifier",)
        self.serial_prescan_header["SENSOR_SEL"] = (self.fee_side(ccd_side).name[0], "CCD side")
        self.serial_prescan_header["DATE-OBS"] = (self.timestamp, "Timestamp for 1st frame",)
        self.serial_prescan_header["FINETIME"] = (self.finetime, "Finetime representation of DATE-OBS",)

        if ccd_side in [self.fee_side.RIGHT_SIDE.name, self.fee_side.RIGHT_SIDE]:
            serial_prescan = np.fliplr(serial_prescan)

        fits.append(str(self._filepath), serial_prescan, self.serial_prescan_header)

    def append_serial_overscan(self, serial_overscan, ccd_number: int, ccd_side: str):
        """ Append the given serial over-scan to the FITS file (after completing its header).

        Args:
            - serial_overscan: Serial over-scan.
            - ccd_number: CCD identifier.
            - ccd_side: CCD side.
        """

        extension = f"SOVER_{ccd_number}_{self.fee_side(ccd_side).name[0]}"
        self.serial_overscan_header["EXTNAME"] = extension
        self.serial_overscan_header["EXTVER"] = self.frame_number[ccd_number][ccd_side]
        self.serial_overscan_header["CCD_ID"] = (ccd_number, "CCD identifier",)
        self.serial_overscan_header["SENSOR_SEL"] = (self.fee_side(ccd_side).name[0], "CCD side")
        self.serial_overscan_header["NAXIS1"] = (serial_overscan.shape[1], "Number of columns in the serial over-scan",)
        self.serial_overscan_header["DATE-OBS"] = (self.timestamp, "Timestamp for 1st frame",)
        self.serial_overscan_header["FINETIME"] = (self.finetime, "Finetime representation of DATE-OBS")

        if ccd_side in [self.fee_side.RIGHT_SIDE.name, self.fee_side.RIGHT_SIDE]:
            serial_overscan = np.fliplr(serial_overscan)

        fits.append(str(self._filepath), serial_overscan, self.serial_overscan_header)

    def append_parallel_overscan(self, parallel_overscan, ccd_number: int, ccd_side: str):
        """ Append the given parallel over-scan to the FITS file (after completing its header).

        Args:
            - parallel_overscan: Parallel over-scan.
            - ccd_number: CCD identifier.
            - ccd_side: CCD side.
        """

        extension = f"POVER_{ccd_number}_{self.fee_side(ccd_side).name[0]}"
        self.parallel_overscan_header["EXTNAME"] = extension
        self.parallel_overscan_header["EXTVER"] = self.frame_number[ccd_number][ccd_side]
        self.parallel_overscan_header["CCD_ID"] = (ccd_number, "CCD identifier",)
        self.parallel_overscan_header["SENSOR_SEL"] = (self.fee_side(ccd_side).name[0], "CCD side")
        self.parallel_overscan_header["NAXIS1"] = (parallel_overscan.shape[1],
                                                   "Number of columns in the parallel over-scan",)
        self.parallel_overscan_header["DATE-OBS"] = (self.timestamp, "Timestamp for 1st frame",)
        self.parallel_overscan_header["FINETIME"] = (self.finetime, "Finetime representation of DATE-OBS",)

        if ccd_side in [self.fee_side.RIGHT_SIDE.name, self.fee_side.RIGHT_SIDE]:
            parallel_overscan = np.fliplr(parallel_overscan)

        fits.append(str(self._filepath), parallel_overscan, self.parallel_overscan_header)

    def append_image(self, image, ccd_number: int, ccd_side: str):
        """ Append the given image to the FITS file (after completing its header).

        Args:
            - image: Image.
            - ccd_number: CCD identifier (1/2/3/4).
            - ccd_side: CCD side.
        """

        extension = f"IMAGE_{ccd_number}_{self.fee_side(ccd_side).name[0]}"
        self.image_header["EXTNAME"] = extension
        self.image_header["EXTVER"] = self.frame_number[ccd_number][ccd_side]
        self.image_header["CCD_ID"] = (ccd_number, "CCD identifier",)
        self.image_header["SENSOR_SEL"] = (self.fee_side(ccd_side).name[0], "CCD side")
        self.image_header["NAXIS1"] = (image.shape[1], "Number of columns in the image",)

        ccd_orientation_degrees = CCD_SETTINGS.ORIENTATION[ccd_number - 1]
        ccd_orientation_radians = radians(ccd_orientation_degrees)

        self.image_header["CROTA2"] = (ccd_orientation_degrees, "CCD orientation angle [degrees]",)

        cdelt = CCD_SETTINGS["PIXEL_SIZE"] / 1000.0  # Pixel size [mm]

        self.image_header["CD1_1"] = (cdelt * cos(ccd_orientation_radians),
                                      "Pixel size x cos(CCD orientation angle)",)
        self.image_header["CD1_2"] = (-cdelt * sin(ccd_orientation_radians),
                                      "-Pixel size x sin(CCD orientation angle)",)
        self.image_header["CD2_1"] = (cdelt * sin(ccd_orientation_radians),
                                      "Pixel size x sin(CCD orientation angle)",)
        self.image_header["CD2_2"] = (cdelt * cos(ccd_orientation_radians),
                                      "Pixel size x cos(CCD orientation angle)",)

        zeropoint_x, zeropoint_y = -np.array(CCD_SETTINGS.ZEROPOINT)
        crval1 = zeropoint_x * cos(ccd_orientation_radians) - zeropoint_y * sin(ccd_orientation_radians)
        crval2 = zeropoint_x * sin(ccd_orientation_radians) + zeropoint_y * cos(ccd_orientation_radians)

        self.image_header["CRVAL1"] = (crval1, "FP x-coordinate of the CCD origin [mm]",)
        self.image_header["CRVAL2"] = (crval2, "FP y-coordinate of the CCD origin [mm]",)

        self.image_header["CRPIX2"] = (-self.v_start,
                                       "CCD origin row wrt 1st transmitted row",)

        if ccd_side in [self.fee_side.LEFT_SIDE.name, self.fee_side.LEFT_SIDE]:
            self.image_header["CRPIX1"] = (0, "CCD origin column wrt lower left corner",)

        if ccd_side in [self.fee_side.RIGHT_SIDE.name, self.fee_side.RIGHT_SIDE]:
            image = np.fliplr(image)
            self.image_header["CRPIX1"] = (-CCD_SETTINGS.NUM_ROWS + image.shape[1],
                                           "CCD origin column wrt lower left corner")

        self.image_header["DATE-OBS"] = (self.timestamp, "Timestamp for 1st frame",)
        self.image_header["FINETIME"] = (self.finetime, "Finetime representation of DATE-OBS",)

        fits.append(str(self._filepath), image, self.image_header)

    def read(self, select=None):
        """Returns a list of all entries in the persistence store.

        The list can be filtered based on a selection from the `select` argument which
        should be a Callable object.

        Args:
            - select (Callable): a filter function to narrow down the list of all entries.

        Returns: List or generator for all entries in the persistence store.
        """
        raise NotImplementedError("Persistence layers must implement a read method")

    def update(self, idx, data):

        pass

    def delete(self, idx):

        logger.warning("The delete functionality is not implemented for the CSV persistence layer.")

    def get_filepath(self):

        return self._filepath


class HDF5(PersistenceLayer):
    extension = "hdf5"

    def __init__(self, filename, prep: dict = None):
        """
        The `prep` argument needs at least the following mandatory key:value pairs:

          * mode: the mode used for opening the file [default is 'r']

        """
        # logger.debug(f"{h5py.version.hdf5_version=}")
        self._filepath = Path(filename)
        self._mode = prep.get("mode") or "r"
        self._h5file: Optional[h5py.File] = None

    def __enter__(self):
        self.open(mode=self._mode)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self, mode=None):
        self._mode = mode or self._mode
        logger.debug(f"Opening file {self._filepath} in mode '{self._mode}'")
        self._h5file = h5py.File(self._filepath, mode=self._mode)

        # File "h5py/h5f.pyx", line 554, in h5py.h5f.FileID.start_swmr_write
        # RuntimeError: Unable to start swmr writing (file superblock version - should be at least 3)
        # self._h5file.swmr_mode = True

    def close(self):
        self._h5file.close()

    def exists(self):
        return self._filepath.exists()

    def create(self, data):
        """
        Store the given data in the HDF5 file. The data argument shall be a dictionary where the
        keys represent the group where the data shall be saved, and the value is the data to be
        saved. When the key ends with ":ATTRS", then the value is a list of attributes to that
        group. Values can be of different type and are processed if needed.

        An example data argument:

            {
                "/10/timecode": tc_packet,
                "/10/timecode:ATTRS": [("timestamp", timestamp)],
                "/10/command/": f"{command.__name__}, {args=}",
                "/10/register/": self.register_map.get_memory_map_as_ndarray()
            }

        The example saves a Timecode packet in the group "/10/timecode" and attaches a timestamp
        as an attribute called "timestamp" to the same group. It then adds a command string in
        the "/10/command" group and finally adds a register memory map (an np.ndarray) in the group
        "/10/register".

        Args:
            data (dict): a dictionary containing the data that needs to be saved.

        Returns:
            None.
        """
        for key, value in data.items():
            if key.endswith(":ATTRS"):
                a_key = key.split(":")[0]
                for k, v in value:
                    self._h5file[a_key].attrs[k] = v
            if isinstance(value, TimecodePacket):
                self._h5file[key] = value.timecode
            if isinstance(value, HousekeepingPacket):
                self._h5file[key] = value.packet_as_ndarray
            if isinstance(value, HousekeepingData):
                self._h5file[key] = value.data_as_ndarray
            if isinstance(value, DataDataPacket):
                self._h5file[key] = value.packet_as_ndarray
            if isinstance(value, OverscanDataPacket):
                self._h5file[key] = value.packet_as_ndarray
            if isinstance(value, (str, bytearray, np.ndarray)):

                # if we save a command, put it into a 'commands' group.
                # This is a special case that is the result of issue #1461

                if 'command' in key:
                    idx = key.split('/')[1]
                    if idx in self._h5file and 'commands' in self._h5file[idx]:
                        last_idx = int(sorted(self._h5file[f"/{idx}/commands"].keys())[-1])
                        key = f"/{idx}/commands/{last_idx+1}"
                    else:
                        key = f"/{idx}/commands/0"

                self._h5file[key] = value

    def read(self, select=None):
        """
        Read information or data from the HDF5 file.

        The `select` argument can contain the following information:

        * the string 'number_of_groups': request to determine the number of top groups in
          the HDF5 file.
        * the string 'last_top_group': request the name/key of the last item in the top group.
                The last item is the last element of the list of keys, sorted with natural order.

        Args:
            select (str or dict): specify which information should be read

        Returns:
            When 'number_of_groups', return an integer, when 'last_top_group' return a string.
        """
        if select == "number_of_groups":
            return len(self._h5file.keys())
        if select == "last_top_group":
            keys = self._h5file.keys()

            logger.debug(f"{self._h5file.filename}: {keys=}")

            return 0 if len(keys) == 0 else natsort.natsorted(keys)[-1]

            # This following lines is a longer version of the previous two lines, keep them for
            # debugging because I had problems and not yet sure what is the cause...

            # sorted_keys = natsort.natsorted(keys)
            # logger.debug(f"{self._h5file.filename}: {sorted_keys=}")
            # key = sorted_keys[-1]
            # logger.debug(f"{key=}")
            # return key

    def update(self, idx, data):

        pass

    def delete(self, idx):
        pass

    def get_filepath(self):
        return self._filepath


# class FITS(PersistenceLayer):
#
#     """
#     Persistence layer that saves (image) data in a FITS file.  The images in the FITS file
#     represent exposures of potentially different windows / sub-fields, which may even be
#     located on different CCDs (but always of the same camera).  The images are organised in
#     FITS extensions, to represent the different windows.  We assume that the images that
#     belong to the same extension, have the same WCS (i.e. the map the same pixels on the same
#     CCD), exposure time, etc.
#     """
#
#     extension = "fits"
#
#     def __init__(self, filename, prep: dict = None):
#
#         """
#         Initialisation of the filepath, the array to keep track of the represented windows,
#         and the base header with the information that is common to all images.
#
#         :param filename: Name of the output FITS file.
#         """
#
#         self._filepath = Path(filename)
#
#         # This array will be used to keep track of how many (different) windows are being
#         # represented in the FITS file (this will be stored in the "NWINDOWS" keyword
#         # in the header of the primary HDU)
#
#         self.windows = np.array([])
#
#         # Most of the information in the header will be the same for all images / windows.  This
#         # will be stored in the "base header".
#
#         self.create_base_header()
#
#     def create_base_header(self):
#
#         """
#         Creates a FITS header with the information that is common to all images of all windows. The
#         header of the non-primary HDUs (i.e. for the images) will build further on this one.
#         """
#
#         self._base_header = fits.Header()
#
#         self._base_header["SIMPLE"] = "T"
#
#         # Dimensionality of the sub-field
#
#         self._base_header["NAXIS"] = (2, "Dimensionality of the sub-field")
#
#         # Focal length (this is needed for the conversion to field angles)
#
#         self._base_header["FOCALLEN"] = (FOV_SETTINGS["FOCAL_LENGTH"], "Focal length [mm]")
#
#         # Linear coordinate transformation from sub-field to focal-plane coordinates
#
#         self._base_header["ctype1"] = ("LINEAR", "Linear coordinate transformation")
#         self._base_header["ctype2"] = ("LINEAR", "Linear coordinate transformation")
#
#         # Focal-plane coordinates are expressed in mm
#
#         self._base_header["CUNIT1"] = ("MM", "Target unit in the column direction (mm)")
#         self._base_header["CUNIT2"] = ("MM", "Target unit in the row direction (mm)")
#
#         # Pixel size
#
#         cdelt = CCD_SETTINGS["PIXEL_SIZE"] / 1000.0  # Pixel size [µm]
#         self._base_header["CDELT1"] = (cdelt, "Pixel size in the x-direction [micron]")
#         self._base_header["CDELT2"] = (cdelt, "Pixel size in the y-direction [micron]")
#
#         # Additional keywords
#
#         self._base_header["TELESCOP"] = (setup["camera_id"], "Camera ID")
#         self._base_header["INSTRUME"] = (setup["camera_id"], "Camera ID")
#         self._base_header["SITENAME"] = (setup["site_id"], "Name of the test site")
#
#         # self._base_header["DATE-LOC"] = (
#         #     datetime.datetime.now.strftime("%Y-%m-%d %H:%M:%S"),
#         #     "Local time of observation"
#         # )
#
#     def open(self, mode=None):
#
#         """
#         Creates the FITS file and writes the header to the primary HDU (Header Data Unit).
#         """
#
#         # Create a FITS header that contains the information that is the same for all images
#         # of all windows.  This will be used as the header of the primary HDU.
#
#         primary_header = self.create_primary_header()
#
#         # The primary HDU contains only this header and no image data
#
#         primary_hdu = fits.PrimaryHDU()
#         primary_hdu.header = primary_header
#
#         # The FITS file is created.  If the filename is already in use, and exception
#         # will be thrown.
#
#         primary_hdu.writeto(self._filepath)
#
#     def create_primary_header(self):
#
#         """
#         Creates the primary header (i.e. the header of the primary HDU).  This contains information
#         that is specific for the camera.
#         """
#
#         primary_header = fits.Header()
#
#         primary_header["SIMPLE"] = "T"
#
#         # Focal length [mm] (this is needed for the conversion to field angles)
#
#         primary_header["FOCALLEN"] = (FOV_SETTINGS["FOCAL_LENGTH"], "Focal length [mm]")
#
#         # Additional keywords
#
#         primary_header["TELESCOP"] = (setup["camera_id"], "Camera ID")
#         primary_header["INSTRUME"] = (setup["camera_id"], "Camera ID")
#         primary_header["SITENAME"] = (setup["site_id"], "Name of the test site")
#
#         # Number of windows
#
#         primary_header["NWINDOWS"] = (0, "Number of windows")
#
#         return primary_header
#
#     def exists(self):
#         return self._filepath.exists()
#
#     def create(self, data):
#
#         """
#         Adds the given data to the FITS file.  This acts as a new exposure for this specific
#         window.  We assume that the images that  belong to the same extension, have the same
#         WCS (i.e. the map the same pixels on the same CCD), exposure time, etc.
#
#         :param data: Dictionary containing the image data and the information concerning
#                      the window over which it was acquired.  This is organised in the following
#                      fashion:
#                         - "image": 2D numpy array with the image data;
#                         - "window": index of the window;
#                         - "zeropoint": pair (x, y) with the sub-field zeropoint [mm];
#                         - "exposure_time" exposure time [s];
#                         - "ccd": CCD code (1/2/3/4)
#         """
#
#         image = data["image"]
#         window_index = data["window"]
#         subfield_zeropoint = data["zeropoint"]  # (x, y) [mm]
#         exposure_time = data["exposure_time"]
#         ccd_code = data["ccd"]
#
#         # Copy + extend the primary header
#
#         header = self.create_header(
#             image, window_index, subfield_zeropoint, exposure_time, ccd_code
#         )
#
#         # Add this image (i.e. exposure) to the FITS file.  It will end up in the
#         # extension, dedicated to the window for which is was acquired (via the
#         # "EXTNAME" keyword in the header).
#
#         fits.append(self._filepath, image, header)
#
#         # Keep track of how many windows are stored in the FITS file
#
#         self.windows = np.append(self.windows, window_index)
#         self.windows = np.unique(self.windows)
#         fits.setval(self._filepath, "NWINDOWS", value=len(self.windows))
#
#     def create_header(self, image, window_index, subfield_zeropoint, exposure_time, ccd_code):
#
#         """
#         Creates a FITS header for the given images.  The base header is copied and information,
#         specific for the given image, is added.
#
#         :param image: 2D numpy array with the image data.
#
#         :param window_index: Window for which the given image data represents a new exposure
#                              (which should be added to the FITS file).
#
#         :param subfield_zeropoint: Pair (x, y) with the sub-field zeropoint [mm].
#
#         :param exposure_time: Exposure time [s].
#
#         :param ccd_code: CCD code (1/2/3/4).
#         """
#
#         from egse.coordinates import ccd_to_focal_plane_coordinates
#
#         header = self._base_header.copy()
#
#         # Dimensions of the sub-field
#
#         header["NAXIS1"] = (image.shape[1], "Number of columns in the sub-field")
#         header["NAXIS2"] = (image.shape[0], "Number of rows in the sub-field")
#
#         # CCD origin + corresponding focal-plane coordinates
#
#         # For the CCD origin, we know the coordinates in the source coordinate sytem
#         # (i.e. the sub-field reference frame), from the sub-field zeropoint, and
#         # can calculate the coordinates in the target coordinate system (i.e. in the
#         # focal-plane reference frame).  Hence, we use the CCD origin to be the
#         # reference point of the coordinate transformation (from the sub-field
#         # reference frame to the focal-plane reference frame):
#         #   - the coordinates of the reference point in the source reference frame
#         #     (i.e. in the sub-field reference frame) need to go in the CRPIXi
#         #     keywords;
#         #   - the coordinates of the reference point in the target reference frame
#         #     (i.e. in the focal-plane reference frame) need to go in the CRVALi
#         #     keywords.
#
#         header["CRPIX1"] = (-subfield_zeropoint[0], "Sub-field column of the CCD origin [pixels]")
#         header["CRPIX2"] = (-subfield_zeropoint[1], "Sub-field row of the CCD origin [pixels]")
#
#         crval1, crval2 = ccd_to_focal_plane_coordinates(0, 0, ccd_code)
#
#         header["CRVAL1"] = (crval1, "FP x-coordinate of the CCD origin [mm]")
#         header["CRVAL2"] = (crval2, "FP y-coordinate of the CCD origin [mm]")
#
#         # Pixel size
#
#         cdelt = CCD_SETTINGS["PIXEL_SIZE"] / 1000.0  # Pixel size [µm]
#
#         # Orientation angle of the CCD
#
#         self._base_header["crota2"] = (
#             CCD_SETTINGS["ORIENTATION"][ccd_code - 1],
#             "CCD orientation angle [degrees]",
#         )
#
#         ccd_orientation_angle_radians = math.radians(CCD_SETTINGS["ORIENTATION"][ccd_code - 1])
#         self._base_header["cd1_1"] = (
#             cdelt * math.cos(ccd_orientation_angle_radians),
#             "Pixel size x cos(CCD orientation angle)",
#         )
#         self._base_header["cd1_2"] = (
#             -cdelt * math.sin(ccd_orientation_angle_radians),
#             "-Pixel size x sin(CCD orientation angle)",
#         )
#         self._base_header["cd2_1"] = (
#             cdelt * math.sin(ccd_orientation_angle_radians),
#             "Pixel size x sin(CCD orientation angle)",
#         )
#         self._base_header["cd2_2"] = (
#             cdelt * math.cos(ccd_orientation_angle_radians),
#             "Pixel size x cos(CCD orientation angle)",
#         )
#
#         # Additional keywords
#
#         header["TELESCOP"] = (setup["camera_id"], "Camera ID")
#         header["INSTRUME"] = (setup["camera_id"], "Camera ID")
#         header["SITENAME"] = (setup["site_id"], "Name of the test site")
#         header["EXPOSURE"] = (exposure_time, "Exposure time [s]")
#         # header["DATE-LOC"] = (
#         #     datetime.datetime.now.strftime("%Y-%m-%d %H:%M:%S"),
#         #     "Local time of observation"
#         # )
#         header["CCDNAME"] = (ccd_code, "CCD code")
#
#         # Using this keyword, the image will end up in the correct extension
#
#         header["EXTNAME"] = "WINDOW" + str(window_index)
#
#         return header
#
#     def update(self, idx, data):
#
#         """
#         Replaces a specific exposure of a specific window by the given image (the header
#         is preserved).  We assume that the images that belong to the same extension, have
#         the same WCS (i.e. the map the same pixels on the same CCD), exposure time, etc.
#
#         :param idx: Number of the exposure for which the image data has to be updated.
#
#         :param data: Dictionary containing the image data and the information concerning
#                      the window over which it was acquired.  This is organised in the following
#                      fashion:
#                         - "image": 2D numpy array with the image data;
#                         - "window": index of the window;
#                         (- "zeropoint": pair (x, y) with the sub-field zeropoint [mm];)
#                         (- "exposure_time" exposure time [s];)
#                         (- "ccd": CCD code (1/2/3/4))
#         """
#
#         image = data["image"]
#         window_index = data["window"]
#
#         extension = "WINDOW" + str(window_index)
#
#         fits.update(self._filepath, image, extension, idx)
#
#     def close(self):
#
#         """
#         Closing the FITS file is not implemented here, because all write methods do this
#         automatically.
#         """
#
#         logger.warning("The close functionality is not implemented for the FITS persistence layer.")
#
#     def read(self, select=None):
#
#         """
#         Reads the FITS file, yielding the HDUs, based on the given selection filter.
#
#         :param select: Selection filter.  Currently not used yet.
#         """
#
#         def generator_function():
#
#             with fits.open(self._filepath) as open_file:
#
#                 for data in open_file:
#
#                     yield data
#
#         return generator_function()
#
#     def delete(self, idx):
#
#         """
#         Deleting individual exposures is not implemented here.
#         """
#
#         logger.warning(
#             "The delete functionality is not implemented for the FITS persistence layer."
#         )

def parts(data, delimiter=",", quote_char='"', keep_quote_char=False):
    compos = []
    part = ''
    skip = False
    for character in data:
        if (
            character == delimiter
            and skip
            or character not in [delimiter, quote_char]
        ):
            part += character
        elif character == delimiter:
            compos.append(part)
            part = ''
        else:
            skip = not skip
            if keep_quote_char: part += character
    if part:
        compos.append(part)

    return compos


# TODO:
#  it might be useful to remember the last 10 or 100 lines and have a dedicated read
#  function that returns these line quickly without the need to open the file.


class CSV1(PersistenceLayer):
    """A Persistence Layer that saves data in a CSV file.

    This class uses a custom implementation.
    """

    extension = "csv"

    def __init__(self, filename, prep: dict = None):
        """
        The `prep` argument is a dictionary that contains information to initialise this
        persistence layer. The CSV uses the following:

        * column_names: a list or tuple with the names of the column headers
        * mode: the mode in which the file shall be opened

        Args:
            filename: a str or Path that represents the name of the file
            prep (dict): preparation information to initialise the persistence layer
        """
        prep = prep or {}
        self._filepath = Path(filename)
        self._column_names = prep.get("column_names") or []
        self._mode = prep.get("mode") or "r"
        self._quote_char = prep.get("quote_char") or "|"
        self._delimiter = prep.get("delimiter") or ","
        self._fd = None
        self._regex = re.compile(rf"\\.|[{re.escape(self._quote_char)}{re.escape(self._delimiter)}']", re.DOTALL)

    def is_open(self):
        # we don't want to expose the file descriptor
        return bool(self._fd)

    def open(self, mode=None):
        """Opens the CSV file and writes the header if column_names are provided."""
        self._mode = mode or self._mode
        logger.debug(f"Opening file {self._filepath} in mode '{self._mode}'")
        self._fd = self._filepath.open(mode=self._mode)
        if self._column_names and self._mode == "w":
            self._fd.write(",".join(self._column_names))
            self._fd.write("\n")
        return self

    def close(self):
        logger.debug(f"Closing file {self._filepath}")
        self._fd.close()
        self._fd = None

    def exists(self):
        return self._filepath.exists()

    def __enter__(self):
        # Only open the file when not opened before. Remember if the file was open.
        self._context_fd = self._fd
        return self if self._fd else self.open(mode=self._mode)

    def __exit__(self, exc_type, exc_val, exc_tb):
        # only close the file if it was opened by the context manager
        self._context_fd or self.close()
        # propagate any exception to the caller, i.e. don't return True
        # return True

    def create(self, data):
        """Write a line in the CSV file with the given numbers separated by commas.

        The `data` argument can be a list or a tuple in which case the numbers are just joined
        to form a comma separated line. The `data` argument can also be a `dict`, in which
        case the column_names are used to order the values from the dictionary.
        The keys in the dictionary shall match the entries in the column_names.

        Args:
            data: the input data to create the line
        Raises:
            IOError when the CSV file was not opened before.
        """

        def quote(value):
            if self._delimiter in value:
                return f"{self._quote_char}{value}{self._quote_char}"
            else:
                return value

        if self._fd:
            if isinstance(data, (list, tuple)):

                data = self._delimiter.join([quote(str(x)) for x in data])

            elif isinstance(data, dict):

                if not self._column_names:
                    logger.error("Cannot write ordered dictionary data, no column names provided.")
                    return

                # Extract the values from the dictionary and sort them according to the column_names

                data_list = [(k, v) for k, v in data.items()]
                sorted_data_list = sorted(data_list, key=lambda x: self._column_names.index(x[0]))
                data = self._delimiter.join([quote(str(x[1])) for x in sorted_data_list])

            self._fd.write(data)
            data.endswith("\n") or self._fd.write("\n")
            self._fd.flush()
        else:
            raise IOError(
                "You try to write to a file which has not been opened yet, "
                "first call the open method or use the context manager."
            )

    def read(self, select=None):
        def generator_function():
            while True:
                line = self._fd.readline().rstrip()
                if line:
                    yield parts(line, self._delimiter, self._quote_char)
                else:
                    break

        return generator_function()

    def update(self, line_no, data):
        logger.warning("The update functionality is not implemented for the CSV persistence layer.")

    def delete(self, line_no):
        logger.warning("The delete functionality is not implemented for the CSV persistence layer.")

    def get_filepath(self):
        return self._filepath


class CSV2(PersistenceLayer):
    """A Persistence Layer that saves data in a CSV file."""

    extension = "csv"

    def __init__(self, filename, prep: dict = None):
        """
        The `prep` argument is a dictionary that contains information to initialise this
        persistence layer. The CSV initialisation uses the following:

        * column_names: a list or tuple with the names of the column headers
        * mode: the mode in which the file shall be opened

        Args:
            filename: a str or Path that represents the name of the file
            prep (dict): preparation information to initialise the persistence layer
        """
        prep = prep or {}
        self._filepath = Path(filename)
        self._column_names = prep.get("column_names") or []
        self._mode = prep.get("mode") or "r"
        self._quote_char = prep.get("quote_char") or "|"
        self._delimiter = prep.get("delimiter") or ","
        self._fd = None

    def __enter__(self):
        self._context_fd = self._fd
        return self if self._fd else self.open(mode=self._mode)

    def __exit__(self, exc_type, exc_val, exc_tb):
        # only close the file if it was opened by the context manager
        self._context_fd or self.close()
        # propagate any exception to the caller, i.e. don't return True
        # return True

    def exists(self):
        return self._filepath.exists()

    def is_open(self):
        # we don't want to expose the file descriptor
        return bool(self._fd)

    def open(self, mode=None):
        """Opens the CSV file and writes the header if column_names are provided."""
        self._mode = mode or self._mode
        logger.debug(f"Opening file {self._filepath} in mode '{self._mode}'")
        self._fd = self._filepath.open(mode=self._mode)
        if self._column_names and self._mode == "w":
            writer = csv.DictWriter(self._fd, fieldnames=self._column_names)
            writer.writeheader()
        return self

    def close(self):
        logger.debug(f"Closing file {self._filepath}")
        self._fd.close()
        self._fd = None

    def create(self, data):
        """Write a line in the CSV file.

        The `data` argument can be a list or a tuple in which case the numbers are just joined
        to form a comma separated line. The `data` argument can also be a `dict`, in which
        case the column_names is used to order the values from the dictionary.
        The keys in the dictionary shall match the entries in the column_names, but if there are
        extra keys in the dictionary, they will be silently ignored.

        Args:
            data: the input data to create the line
        Raises:
            IOError when the CSV file was not opened before.
        """
        if not self._fd:
            raise IOError(
                "You try to write to a file which has not been opened yet, "
                "first call the open method or use the context manager."
            )
        if isinstance(data, (list, tuple)):
            writer = csv.writer(
                self._fd,
                delimiter=self._delimiter,
                quotechar=self._quote_char, quoting=csv.QUOTE_MINIMAL,
            )
            writer.writerow(data)
        elif isinstance(data, dict):
            if not self._column_names:
                logger.error("Cannot write ordered dictionary data, no column names provided.")
                return

            writer = csv.DictWriter(
                self._fd,
                fieldnames=self._column_names, extrasaction="ignore",
                delimiter=self._delimiter,
                quotechar=self._quote_char, quoting=csv.QUOTE_MINIMAL,
            )
            writer.writerow(data)
        else:
            self._fd.write(data)
            data.endswith("\n") or self._fd.write("\n")

        self._fd.flush()

    def read(self, select=None):
        csv_reader = csv.reader(self._fd, delimiter=self._delimiter, quotechar=self._quote_char)

        def generator_function():
            if self._column_names:
                yield next(csv_reader)

            for line in csv_reader:
                yield line

        return generator_function()

    def update(self, line_no, data):
        logger.warning("The update functionality is not implemented for the CSV persistence layer.")

    def delete(self, line_no):
        logger.warning("The delete functionality is not implemented for the CSV persistence layer.")

    def get_filepath(self):
        return self._filepath


class TXT(PersistenceLayer):

    extension = "txt"

    def __init__(self, filename, prep: dict = None):
        """
        The `prep` argument is a dictionary that contains information to initialise this
        persistence layer. The TXT initialisation uses the following:

        * mode: the mode in which the file shall be opened
        * ending: a character sequence that is used to end the write action
        * header: a header text that will be written when opening the file

        Args:
            filename: a str or Path that represents the name of the file
            prep (dict): preparation information to initialise the persistence layer
        """
        prep = prep or {}
        self._filepath = Path(filename)
        self._mode = prep.get("mode") or "r"
        self._ending = prep.get("ending") or ""
        self._header = prep.get("header") or ""
        self._fd = None

    def open(self, mode=None):
        """Opens the TXT file."""
        self._mode = mode or self._mode
        logger.debug(f"Opening file {self._filepath} in mode '{self._mode}'")
        self._fd = self._filepath.open(mode=self._mode)
        if self._header and self._mode == "w":
            self.create(self._header)
        return self

    def close(self):
        logger.debug(f"Closing file {self._filepath}")
        self._fd.close()
        self._fd = None

    def exists(self):
        return self._filepath.exists()

    def __enter__(self):
        self._context_fd = self._fd
        return self if self._fd else self.open(mode=self._mode)

    def __exit__(self, exc_type, exc_val, exc_tb):
        # only close the file if it was opened by the context manager
        self._context_fd or self.close()
        return True

    def create(self, data):
        data_str = str(data)
        logger.log(5, f"Writing data: {data_str[:min(80, len(data_str))]}...")
        if self._fd:
            self._fd.write(str(data))
            self._fd.write(self._ending)
            self._fd.flush()
        else:
            raise IOError(
                "You try to write to a file which has not been opened yet, "
                "first call the open method or use the context manager."
            )

    def read(self, select=None):
        """Read lines form the file.

        The `select` argument can take the following values:

        * `select == "last_line"`: return the last line of the file as a string
        * `select == ("contains", <string>)`: returns all the files that contain `<string>`
        * `select == ("startswith", <string>)`: return all line that start with `<string>`

        Args:
            select (str or dict): defines a selection / filter for reading the lines
        Returns:
            A list of lines from the file or the last line as a string.
        """
        if select == "last_line":
            return read_last_line(self._filepath, max_line_length=4096)

        result = []

        if isinstance(select, tuple):
            if select[0] == "contains":
                with self._filepath.open(mode="r") as fd:
                    for line in fd:
                        if select[1] in line:
                            result.append(line.rstrip())
            elif select[0] == "startswith":
                with self._filepath.open(mode="r") as fd:
                    for line in fd:
                        if line.startswith(select[1]):
                            result.append(line.rstrip())
            return result

        with self._filepath.open("r") as fd:
            result = [line.rstrip() for line in fd]

        return result

    def update(self, idx, data):
        logger.warning("The update functionality is not implemented for the TXT persistence layer.")

    def delete(self, idx):
        logger.warning("The delete functionality is not implemented for the TXT persistence layer.")

    def get_filepath(self):
        return self._filepath


class SQLite(PersistenceLayer):

    extension = "sqlite3"

    def __init__(self, filename: Union[str, Path], prep: dict = None):
        self._filepath = Path(filename).with_suffix(f".{self.extension}")
        self._prep = prep
        self._connection: Optional[Connection] = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self, mode=None):
        self._connection = sqlite3.connect(self._filepath)

    def close(self):
        self._connection.close()

    def exists(self):
        return self._filepath.exists()

    def _execute(self, statement, values=None):
        with self._connection:
            cursor = self._connection.cursor()
            cursor.execute(statement, values or [])
            return cursor

    def create_table(self, table_name, columns):
        columns_with_types = [
            f'{column_name} {data_type}'
            for column_name, data_type in columns.items()
        ]
        self._execute(
            f"""CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns_with_types)});"""
        )

    def drop_table(self, table_name):
        self._execute(f"DROP TABLE {table_name};")

    def add_to_table(self, table_name, data):
        placeholders = ', '.join('?' * len(data))
        column_names = ', '.join(data.keys())
        column_values = tuple(data.values())

        self._execute(
            f"""INSERT INTO {table_name} ({column_names}) VALUES ({placeholders}); """,
            column_values,
        )

    def select_from_table(self, table_name: str, criteria: dict = None, order_by=None):
        criteria = criteria or {}

        query = f"SELECT * FROM {table_name}"

        if criteria:
            placeholders = [f'{column} = ?' for column in criteria.keys()]
            select_criteria = ' AND '.join(placeholders)
            query += f' WHERE {select_criteria}'

        if order_by:
            query += f' ORDER BY {order_by}'

        return self._execute(
            query,
            tuple(criteria.values()),
        )

    def delete_from_table(self, table_name, criteria):
        placeholders = [f'{column} = ?' for column in criteria.keys()]
        delete_criteria = ' AND '.join(placeholders)

        self._execute(
            f"""DELETE FROM {table_name} WHERE {delete_criteria}; """, tuple(criteria.values()),
        )

    def update_table(self, table_name, criteria, data):
        update_placeholders = [f'{column} = ?' for column in criteria.keys()]
        update_criteria = ' AND '.join(update_placeholders)
        data_placeholders = ', '.join(f'{key} = ?' for key in data.keys())

        values = tuple(data.values()) + tuple(criteria.values())

        self._execute(
            f"""UPDATE {table_name} SET {data_placeholders} WHERE {update_criteria};""",
            values,
        )

    def create(self, data):
        # Should call add_to_table()
        pass

    def read(self, select=None):
        # Should call select_from_table()
        pass

    def update(self, idx, data):
        # Should call update_table()
        pass

    def delete(self, idx):
        # Should call delete_from_table
        pass

    def get_filepath(self):
        return self._filepath


CSV = CSV2
