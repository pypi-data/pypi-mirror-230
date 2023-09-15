import logging
import os
from pathlib import Path

import numpy as np
import pandas

from egse.command import ClientServerCommand
from egse.config import find_file
from egse.control import ControlServer
from egse.control import Failure
from egse.control import is_control_server_active
from egse.decorators import dynamic_interface
from egse.env import get_data_storage_location
from egse.hk import TmDictionaryColumns
from egse.metrics import define_metrics
from egse.obsid import obsid_from_storage
from egse.protocol import CommandProtocol
from egse.proxy import Proxy
from egse.settings import Settings
from egse.state import GlobalState
from egse.storage import StorageProxy
from egse.storage import is_storage_manager_active
from egse.storage import register_to_storage_manager
from egse.storage.persistence import CSV
from egse.system import format_datetime
from egse.zmq_ser import bind_address
from egse.zmq_ser import connect_address

logger = logging.getLogger(__name__)

ORIGIN = "SYN-HK"
CTRL_SETTINGS = Settings.load("Synoptics Manager Control Server")
COMMAND_SETTINGS = Settings.load(filename="syn.yaml")
SITE_ID = Settings.load("SITE").ID


def is_synoptics_manager_active(timeout: float = 0.5):
    """Check if the Synoptics Manager is running.

    Returns:
        True if the Synoptics Manager is running and replied with the expected answer.
    """

    endpoint = connect_address(
        CTRL_SETTINGS.PROTOCOL, CTRL_SETTINGS.HOSTNAME, CTRL_SETTINGS.COMMANDING_PORT
    )

    return is_control_server_active(endpoint, timeout)


class SynopticsManagerProtocol(CommandProtocol):

    """
    Command Protocol for Synoptics Management.
    """

    def __init__(self, control_server: ControlServer):
        """Initialisation of a new Protocol for Synoptics Management.

        The initialisation of this Protocol consists of the following steps:

            - create a Controller to which the given Control Server should send commands;
            - load the commands;
            - build a look-up table for the commands.

        Args:
            - control_server: Control Server via which commands should be sent
                              to the Controller.
        """

        super().__init__()

        # Control Server for Synoptics Management

        self.control_server = control_server

        # Create a new Controller for Synoptics Management

        self.controller = SynopticsManagerController()

        # Load the commands (for commanding of the Synoptics Manager Controller) from the
        # YAML file into a dictionary, stored in the Synoptics Manager Protocol

        self.load_commands(
            COMMAND_SETTINGS.Commands, SynopticsManagerCommand, SynopticsManagerController)

        # Build a look-up table for the methods

        self.build_device_method_lookup_table(self.controller)

    def get_bind_address(self):
        """Returns the address to bind a socket to.

        This bind address is a properly formatted URL, based on the communication protocol and
        the commanding port.

        Returns:
            - Properly formatted URL to bind a socket to.
        """

        return bind_address(
            self.control_server.get_communication_protocol(),
            self.control_server.get_commanding_port(),
        )

    def get_status(self) -> dict:
        """Returns the status information for the Control Server."""

        return super().get_status()

    def get_housekeeping(self) -> dict:
        """Returns the housekeeping data for the Control Server.

        This housekeeping data is returns in the form of a dictionary that contains the following
        information about the Control Server for Synoptics Management:

            - timestamp (str): string representation of the current datetime.

        Returns:
            - Dictionary with housekeeping data for the Control Server for Synoptics Management.
        """

        return {"timestamp": format_datetime()}


class SynopticsManagerCommand(ClientServerCommand):

    """
    Command (client-server) for Synoptics Management.
    """

    pass


class SynopticsManagerInterface:

    @dynamic_interface
    def store_common_synoptics(self, common_synoptics: dict):
        """ Store the given non-testhouse-specific synoptics.

        Args:
            - common_synoptics: Non-testhouse-specific synoptics.
        """

        raise NotImplementedError

    @dynamic_interface
    def store_th_synoptics(self, th_synoptics: dict):
        """ Store the given testhouse-specific synoptics.

        Args:
            - th_synoptics: Testhouse-specific synoptics.
        """

        raise NotImplementedError


class SynopticsManagerController(SynopticsManagerInterface):

    """
    Controller for Synoptics Management.
    """

    def __init__(self):
        """Initialisation for the Synoptics Manager Controller.
        """

        # Storage Manager must be active

        if not is_storage_manager_active():

            logger.error("No Storage Manager available!!!!")

        # Register to storage

        self.syn_names = read_all_syn_names()
        self.register_to_storage()

        self.hk_info_read = False
        self.original_name_egse, self.original_name_th = None, None

        self.synoptics_metrics = None

    def read_hk_info(self):
        self.syn_names, self.original_name_egse, self.original_name_th = read_hk_info()
        self.synoptics_metrics = define_metrics(ORIGIN)

        self.hk_info_read = True

    def register_to_storage(self):
        """ Register the Synoptics Manager to the storage.

        The Storage Manager will take care of producing daily files and duplicate the information during observations.
        """

        register_to_storage_manager(ORIGIN, CSV, prep=dict(mode='a', column_names=list(self.syn_names)))

    def store_common_synoptics(self, common_hk: dict):
        """ Store the given non-TH-specific calibrated device housekeeping as synoptics.

        Args:
            - common_hk: Non-TH-specific HK that needs to be included in the synoptics.
        """

        if not self.hk_info_read:
            self.read_hk_info()

        common_synoptics = {}

        for hk_name, cal_value in common_hk.items():

            try:
                syn_name = self.original_name_egse[hk_name]
                common_synoptics[syn_name] = cal_value

                self.store_metrics(syn_name, cal_value)
            except KeyError:
                # do add the timestamp although it's not in the tm-dictionary
                if hk_name == "timestamp":
                    common_synoptics[hk_name] = cal_value

        self.store_synoptics(common_synoptics)

    def store_th_synoptics(self, th_hk: dict):
        """ Store the given TH-specific calibrated device housekeeping as synoptics.

        Args:
            - th_hk: TH-specific HK that needs to be included in the synoptics.
        """

        if not self.hk_info_read:
            self.read_hk_info()

        th_synoptics = {}

        for hk_name, cal_value in th_hk.items():

            try:
                syn_name = self.original_name_th[hk_name]
                th_synoptics[syn_name] = cal_value

                self.store_metrics(syn_name, cal_value)
            except KeyError:
                # do add the timestamp although it's not in the tm-dictionary
                if hk_name == "timestamp":
                    th_synoptics[hk_name] = cal_value

        self.store_synoptics(th_synoptics)

    def store_synoptics(self, synoptics: dict):
        """ Store the given synoptics."""

        logger.log(0, "Sending synoptics to storage manager.")

        try:

            with StorageProxy() as storage:

                response = storage.save({"origin": ORIGIN, "data": synoptics})

                if isinstance(response, Failure):
                    logger.warning(f"Couldn't save synoptics to the Storage Manager: {synoptics}, "
                                   f"cause: {response.cause}")

        except ConnectionError as exc:
            logger.warning(f"Couldn't connect to the Storage Manager to store synoptics: {exc}")

    def store_metrics(self, name: str, value):
        """ Store the given synoptical parameter in the metrics.

        Args:
            - name: Name of the synoptical parameter and its metrics.
            - value: Value to store in the given metrics.
        """

        if not self.hk_info_read:
            self.read_hk_info()

        try:
            self.synoptics_metrics[name].set(value)
        except KeyError:
            logger.debug(f"Cannot store synoptics metrics: {name} is not a synoptical parameter")


def read_hk_info() -> (dict, dict):
    """ Read the table with the HK information, i.e. the TM dictionary.

    Returns:
        - List with the name of the timestamp and synoptics
        - Dictionary with the original name at the TH you are currently at
        - Dictionary with the original name from the EGSE (not TH-specific)
    """

    hk_info_table = GlobalState.setup.telemetry.dictionary

    syn_selection = np.where(hk_info_table[TmDictionaryColumns.STORAGE_MNEMONIC].values == ORIGIN)
    syn_names = hk_info_table[TmDictionaryColumns.CORRECT_HK_NAMES].values[syn_selection]
    original_name_egse = hk_info_table[TmDictionaryColumns.ORIGINAL_EGSE_HK_NAMES].values[syn_selection]

    original_name_egse = dict(zip(original_name_egse, syn_names))
    original_name_egse = {k: original_name_egse[k] for k in original_name_egse if isinstance(k, str)}

    try:

        original_name_th = hk_info_table[f"Origin of synoptics at {SITE_ID}"].values[syn_selection]
        original_name_th = dict(zip(original_name_th, syn_names))
        original_name_th = {k: original_name_th[k] for k in original_name_th if isinstance(k, str)}

    except (NameError, KeyError):

        logger.warning(f"No TH-specific HK for {SITE_ID}")
        original_name_th = {}

    # Add the timestamp as a column in the Synoptic table

    syn_names = np.concatenate((["timestamp"], syn_names))

    return syn_names, original_name_egse, original_name_th


def read_all_syn_names():
    """ Return all synoptical names that have been used so far.

    Not all camera models will use the same synoptics: this is defined in the TM dictionary that is mentioned in the
    setup.  Since the Synoptical Manager is a core process, it will be started before a setup is loaded, so it cannot
    determine the names of the columns of its HK file from there. However, at start-up, the column names need to be
    known, for the registration to the Storage Manager.

    The work-around is to read the synoptical names from all TM dictionaries that have been used to far, and use those.

    Returns: Synoptical names used for all camera models so far.
    """

    tm_location_dir = Path(os.environ["PLATO_CONF_REPO_LOCATION"]) / "data" / "common" / "telemetry"
    tm_filenames = os.listdir(tm_location_dir)

    all_syn_names = np.array([])

    for tm_filename in tm_filenames:
        if tm_filename.endswith(".csv"):
            tm_filepath = tm_location_dir / tm_filename
            hk_info_table = pandas.read_csv(tm_filepath, sep=";")

            syn_selection = np.where(hk_info_table[TmDictionaryColumns.STORAGE_MNEMONIC].values == ORIGIN)
            syn_names = hk_info_table[TmDictionaryColumns.CORRECT_HK_NAMES].values[syn_selection]

            all_syn_names = np.append(all_syn_names, syn_names)

    all_syn_names = np.unique(all_syn_names)
    
    return np.concatenate((["timestamp"], all_syn_names))


class SynopticsManagerProxy(Proxy, SynopticsManagerInterface):
    """
    Proxy for Synoptics Management, used to connect to the Synoptics Manager Control Server and
    send commands remotely.
    """

    def __init__(
        self,
        protocol=CTRL_SETTINGS.PROTOCOL,
        hostname=CTRL_SETTINGS.HOSTNAME,
        port=CTRL_SETTINGS.COMMANDING_PORT,
    ):
        """Initialisation of a new Proxy for Synoptics Management.

        If no connection details (transport protocol, hostname, and port) are not provided,
        these are taken from the settings file.

        Args:
            protocol: Transport protocol [default is taken from settings file].
            hostname: Location of the control server (IP address)
                [default is taken from the settings file].
            port: TCP port on which the Control Server is listening for commands
                [default is taken from the settings file].
        """

        super().__init__(connect_address(protocol, hostname, port))


def get_synoptics_table(obsid: str, data_dir=None):
    """
    Read and return the synoptics table for the given obsid as a pandas DataFrame.

    Args:
        obsid: Observation identifier [TEST_LAB or TEST_LAB_SETUP].
        data_dir: Folder (with sub-folders /daily and /obs) in which the data files are stored. If this argument is not
            provided, the data_dir will be determined from the environment variable PLATO_DATA_STORAGE_LOCATION.

    Returns:
        Synoptics table for the given obsid as a pandas DataFrame.
    """

    data_dir = data_dir or get_data_storage_location()

    obsid = obsid_from_storage(obsid, data_dir=data_dir)
    obs_dir = f"{data_dir}/obs/{obsid}"  # Where the synoptics file is stored

    # Read the synoptics for the given obsid

    pattern = f"{obsid}_{ORIGIN}_*.csv"
    synoptics_filename = str(find_file(pattern, root=obs_dir))

    synoptics_table = pandas.read_csv(synoptics_filename, sep=",")

    # Sort by timestamps

    synoptics_table = synoptics_table.sort_values(by="timestamp")

    return synoptics_table
