"""
This module defines the device classes to be used to connect to and control the TCS EGSE.
"""
import datetime
import itertools
import logging
import multiprocessing
import operator
from collections import namedtuple
from enum import IntEnum
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from prometheus_client import start_http_server
from rich.console import Console
from rich.table import Table

from egse.control import Failure
from egse.control import is_control_server_active
from egse.device import DeviceConnectionState
from egse.device import DeviceInterface
from egse.hk import read_conversion_dict
from egse.metrics import define_metrics
from egse.mixin import DynamicCommandMixin
from egse.mixin import ETX
from egse.mixin import add_etx
from egse.mixin import dynamic_command
from egse.proxy import DynamicProxy
from egse.settings import Settings
from egse.sockets import SocketInterface
from egse.storage import StorageProxy
from egse.storage import register_to_storage_manager
from egse.storage import unregister_from_storage_manager
from egse.storage.persistence import CSV
from egse.synoptics import SynopticsManagerProxy
from egse.system import SignalCatcher
from egse.system import format_datetime
from egse.tcs.tcs_devif import TCSEthernetInterface
from egse.zmq_ser import connect_address

logger = logging.getLogger(__name__)

TCS_SETTINGS = Settings.load("TCS Controller")
CTRL_SETTINGS = Settings.load("TCS Control Server")
DEVICE_SETTINGS = Settings.load(filename="tcs.yaml")

THIS_FILE_LOCATION = Path(__file__).parent

ORIGIN = "TCS-HK"

REMOTE_MODE_NOT_ACTIVE = 'not_allowed_remote_mode_not_active'

REQUEST_TIMEOUT = 10_000  # 10s timeout should be more than enough

HousekeepingValue = namedtuple("HousekeepingValue", "timestamp name value")


def decode_response(response: bytes) -> str:
    """Decodes the bytes object. Doesn't perform any other conversions on the response."""
    return response.decode()


def decode_and_strip_response(response: bytes) -> str:
    """Decodes the bytes object and strips off the last ETX character."""
    return response.decode().rstrip(ETX)


def process_request_remote_response(response: bytes) -> bool:
    """Returns True when the remote operation is active or could be activated."""
    return b"acknowledge_remote_operation" in response


def process_quit_remote_response(response: bytes) -> bool:
    """Returns True when the remote operation is inactive or could be inactivated."""
    return b"acknowledge_quit_remote_operation" in response


def process_is_remote_operation_response(response: bytes) -> bool:
    """Returns True when the remote operation is active or could be activated."""
    return b"remote_mode_active" in response


def process_is_task_running_response(response: bytes) -> Union[bool, Failure]:
    """
    Returns True when a task is running on the TCS EGSE.

    When an error occurred, a warning messages is logged and a Failure is returned.
    """
    is_task_running = process_get_housekeeping_value(response)
    if isinstance(is_task_running, Failure):
        return is_task_running
    elif is_task_running.value == 'tbd':
        return Failure("Cannot determine if task is running, TBD was returned.")
    else:
        return bool(int(is_task_running.value))


def process_commit_response(response: bytes):
    if b"erroneous" in response:
        logger.warning("The TCS EGSE commit has automatically corrected some of the "
                       "configuration parameters that were provided.")
    return decode_and_strip_response(response)


def expand_kwargs(kv_pairs: Dict):
    return " ".join(f"{k} {v}" for k, v in kv_pairs.items())


def process_error_response(response: bytes) -> List:

    data = response.decode().split('\x03')

    # Remove empty items from the list

    data = [x for x in data if x]

    data = [x for y in data for x in y.split('\r\n') if x]

    return data


def process_all_housekeeping(response: bytes) -> Union[List[List], Failure]:
    """
    Process the response from the TCS EGSE remote command `get_TM_All`.

    Args:
        response (bytes): contains the response from the TCS EGSE to the get_TM_All command.

    Returns:
        A nested list where the inner lists contain the name, timestamp and value of a housekeeping
        parameter. The list is sorted on the name.

        A Failure object is returned when the remote control mode is de-activated or when a
        communication error occurred.
    """

    data = response.decode().split('\x03')

    if "not_allowed_remote_mode_not_active" in data:
        msg = "Remote Control not active, no housekeeping values received."
        return Failure(msg)

    if len(data) != 2:
        msg = "Format error: no housekeeping value received."
        logger.error(msg)
        return Failure(msg)

    data = data[0].split('\r\n')
    data = [x.split('\t') for x in data]
    data = sorted(data, key=operator.itemgetter(0))

    return data


def process_get_housekeeping_value(response: bytes) -> Union[HousekeepingValue, Failure]:

    if b"remote_mode_not_active" in response:
        logger.warning("Requesting housekeeping value invalid, not in remote control mode.")
        return Failure("Requesting housekeeping value invalid, not in remote control mode.")
    if b"invalid_tm_item_id" in response:
        logger.warning("Invalid housekeeping parameter name.")
        return Failure("Invalid housekeeping parameter name.")
    data = response.decode().split('\x03')
    data = data[0].split('\t')
    return HousekeepingValue(*data)


def process_configuration(response: bytes) -> Union[Dict, Failure]:
    """
    Process the response to the get_configuration command. Processing in this context means to
    disentangle the returned string and split it up in parameter name, value pairs.

    Args:
        response (str): a string containing the response from the TCS EGSE

    Returns:
        A dictionary with the parameters names and their current values.
    """

    # The rest of this function parse and organise the configuration parameters
    # in a list of lists with [[name, value], [...]]

    tcs_conf = response.decode().split('\x03')

    # Remove empty items from the list. The list ends always with an empty item because
    # the response ends with the '\x03' EOT character.

    tcs_conf = [x for x in tcs_conf if x]

    if not tcs_conf:
        logger.info('No response received from the get_Conf command to TCS EGSE.')
        return {}

    # The last line is what we need, we assume there is only one line, but just to be sure...

    tcs_conf = tcs_conf[-1]

    if REMOTE_MODE_NOT_ACTIVE in tcs_conf:
        return Failure(
            "Remote mode is not active on the TCS EGSE, commanding is not possible, "
            "you can still retrieve telemetry."
        )

    # All configuration parameters are separated by '\r\n', and  the name and value
    # are separated by a '\t', so let's split them into a list of [value, name].

    tcs_conf = tcs_conf.split('\r\n')

    # The configuration parameters also contain the RTD parameters which is organised
    # differently, so we threat them differently and append them to the configuration
    # parameters again later.

    rtd_list = [x for x in tcs_conf if x.startswith("rtd_list") or x.startswith('\t')]
    rtd_list = [x.split('\t') for x in rtd_list]
    rtd_list = [x[1:] for x in rtd_list]
    rtd_list = [[f"{x[0]}_A_B_C_D_E_F", f"{x[1]}, {x[2]}, {x[3]}, {x[4]}, {x[5]}, {x[6]}"] for x in
                rtd_list]

    # Now process each of the 'normal' configuration parameters, and

    tcs_conf = [x for x in tcs_conf if not (x.startswith("rtd_list") or x.startswith('\t'))]
    tcs_conf = [x.split('\t') for x in tcs_conf if x]

    # add the RTD list back into the configuration parameters.

    tcs_conf.extend(rtd_list)

    # We want to sort the final list by name, this order will be preserved when we convert it
    # into a dictionary.

    tcs_conf = sorted(tcs_conf, key=operator.itemgetter(0))

    # Now convert the above list into a dictionary.

    tcs_conf = {k: v for k, v in tcs_conf}

    return tcs_conf


class OperatingMode(IntEnum):
    NORMAL = 0
    SAFE = 1
    DECONTAMINATION = 2
    CALIBRATION = 3
    EMC = 4
    SELF_TEST = 5
    EXTENDED = 6


class ClosedLoopMode(IntEnum):
    PI_ALG_1 = 0
    PI_ALG_2 = 1
    BANG_BANG_ALG_1 = 2
    BANG_BANG_ALG_2 = 3


class TCSError(Exception):
    """A TCS EGSE specific error."""

    pass


def is_tcs_cs_active(timeout: float = 2.0):
    """Check if the TCS Control Server is running.

    Args:
        timeout (float): timeout when waiting for a reply [seconds, default=0.5]
    Returns:
        True if the Storage Manager is running and replied with the expected answer.
    """

    endpoint = connect_address(
        CTRL_SETTINGS.PROTOCOL, CTRL_SETTINGS.HOSTNAME, CTRL_SETTINGS.COMMANDING_PORT
    )

    return is_control_server_active(endpoint, timeout)


def print_configuration():
    """
    This convenience function prints the configuration parameters in a table on your console.
    This function is for use in a REPL or Jupyter Notebook.
    """
    with TCSProxy() as tcs:
        tcs_conf = tcs.get_configuration()

    table = Table(title="Configuration")

    table.add_column("Name", justify="left", style="cyan", no_wrap=True)
    table.add_column("Value", justify="right", style="green")

    for name, value in sorted(tcs_conf.items()):
        table.add_row(name, value)

    console = Console()
    console.print(table)


def print_all_housekeeping():
    """
    This convenience function prints the last sampled housekeeping parameters in a table in your
    console. This function is for use in a REPL or Jupyter Notebook.

    Note that when no task is running most of the housekeeping parameters are not sampled and the
    values will be out-of-date. To make sure you have up-to-date values, run the task.
    """
    with TCSProxy() as tcs:
        hk = tcs.get_all_housekeeping()

    table = Table(title="All Telemetry")

    table.add_column("Date Time", justify="center", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta")
    table.add_column("Value", justify="right", style="green")

    for name, date, value in hk:
        table.add_row(name, date, value)

    console = Console()
    console.print(table)


def set_operating_mode(mode: str):

    with TCSProxy() as tcs:
        tcs.set_operating_mode(mode)
        tcs.commit()


class TCSInterface(DeviceInterface):
    """
    Interface definition for the TCSController, the TCSProxy and the TCSSimulator.
    """

    @dynamic_command(cmd_type="query", cmd_string="request_remote_operation",
                     process_cmd_string=add_etx, process_response=process_request_remote_response)
    def request_remote_operation(self) -> bool:
        """
        Activate the Remote Control Mode in the TCS EGSE.

        Returns:
            True, if Remote Control could be activated, False otherwise.
        """
        raise NotImplementedError

    @dynamic_command(cmd_type="query", cmd_string="quit_remote_operation",
                     process_cmd_string=add_etx, process_response=process_quit_remote_response)
    def quit_remote_operation(self) -> bool:
        """
        Command the TCS EGSE to end the Remote Control Mode. The TCS EGSE will continue with the
        ongoing task in Local Control Mode.

        Returns:
            True, if Remote Control mode could be de-activated, False otherwise.
        """
        raise NotImplementedError

    @dynamic_command(cmd_type="query", cmd_string="get_remote_status",
                     process_cmd_string=add_etx, process_response=process_is_remote_operation_response)
    def is_remote_operation_active(self) -> bool:
        """
        Check if Remote Control Mode is active in the TCS EGSE.

        Returns:
            True, if the command was acknowledged, False otherwise.
        """
        raise NotImplementedError

    @dynamic_command(cmd_type="query", cmd_string="get_tm task_is_running",
                     process_cmd_string=add_etx, process_response=process_is_task_running_response)
    def is_task_running(self) -> bool:
        """
        Query the TCS EGSE if a task is currently running.

        Returns:
            True, if a task is running, False otherwise.
        """
        raise NotImplementedError

    @dynamic_command(cmd_type="query", cmd_string="clear_popup",
                     process_cmd_string=add_etx, process_response=decode_and_strip_response)
    def clear_popup(self) -> str:
        """Clears the error/warning popup on the MMI. Returns an acknowledgement message."""
        raise NotImplementedError

    @dynamic_command(cmd_type="query", cmd_string="get_conf_all",
                     process_cmd_string=add_etx, process_response=process_configuration)
    def get_configuration(self) -> Dict:
        """Returns the last valid configuration as a dictionary."""
        raise NotImplementedError

    @dynamic_command(cmd_type="query", cmd_string="get_tm_all",
                     process_cmd_string=add_etx, process_response=process_all_housekeeping)
    def get_all_housekeeping(self) -> List[List[str]]:
        """
        Returns the last housekeeping data sampled by the TCS EGSE.

        Returns:
            A list of lists, where the inner list contains the parameter name, the sampling time,
              and the parameter value, in that order. All these values are returned as strings.
        """
        raise NotImplementedError

    @dynamic_command(cmd_type="query", cmd_string="get_tm ${hk_id}",
                     process_cmd_string=add_etx, process_response=process_get_housekeeping_value)
    def get_housekeeping_value(self, hk_id: str) -> Optional[HousekeepingValue]:
        """Returns the last updated value for the housekeeping parameter.

        The returned value is a namedtuple with the following fields:

          * timestamp: a string in the format 'YYYY/mm/dd HH:MM:SS.%f UTC'
          * name: the name of the requested housekeeping value
          * value: as a string

        """
        raise NotImplementedError

    @dynamic_command(cmd_type="query", cmd_string="set_parameter operation_mode ${mode}",
                     process_cmd_string=add_etx, process_response=decode_and_strip_response)
    def set_operating_mode(self, mode: Union[str, int]) -> str:
        """
        Define the operating mode of the task to be started.

        The mode can either be an integer or the text value of:
          0. normal
          1. safe
          2. decontamination|de-icing
          3. calibration
          4. EMC
          5. self-test
          6. extended

        Args:
            mode (str, int): the required mode as defined above.

        Returns:
            No response.
        """
        raise NotImplementedError

    @dynamic_command(cmd_type="query", cmd_string="set_parameter ${name} ${value}",
                     process_cmd_string=add_etx, process_response=decode_and_strip_response)
    def set_parameter(self, name: str, value: Any) -> str:
        """
        Set the parameter in the configuration.

        These parameters will be stored on a temporary buffer and will only be applied
        after the commit command is sent.
        """
        raise NotImplementedError

    @dynamic_command(cmd_type="query", cmd_string="set_parameter ${kwargs}",
                     process_cmd_string=add_etx, process_kwargs=expand_kwargs,
                     process_response=decode_and_strip_response)
    def set_parameters(self, **kwargs) -> str:
        """
        Set the given parameters in the configuration.

        The parameters are provided as a dictionary

        These parameters will be stored on a temporary buffer and will only be applied
        after the commit command is sent.
        """
        raise NotImplementedError

    @dynamic_command(cmd_type="query", cmd_string="commit_config",
                     process_cmd_string=add_etx, process_response=process_commit_response)
    def commit(self) -> str:
        """
        Enables all received configuration parameters, check the parameters and
        saves them to the TCS local configuration file. If a parameter that was
        previously sent and is not in accordance to the range and resolution allowed,
        it will be coerced to the nearest value allowed. In this latter case, a Warning
        message will be logged.
        """
        raise NotImplementedError

    @dynamic_command(cmd_type="query", cmd_string="discard_config",
                     process_cmd_string=add_etx, process_response=decode_and_strip_response)
    def discard(self) -> str:
        """
        Discards all received configuration parameters sent without commit command.
        """
        raise NotImplementedError

    @dynamic_command(
        cmd_type="query",
        cmd_string="upload_rtd_parameters ${sn}_${r0}_${a}_${b}_${c}",
        process_cmd_string=add_etx)
    def upload_callendar_vandusen_rtd_parameters(self, sn, r0, a, b, c):
        """
        Uploads the Callendar Van-Dussen parameters.

        The 'sn' argument is the 'serial number' or identifier for this set of parameters.

        Values of R0, A, B and C constants for 3th order polynomial equation
        calibration curves.

        These parameters are required for 2 wire RTDs.
        """
        raise NotImplementedError

    @dynamic_command(
        cmd_type="query",
        cmd_string="upload_rtd_parameters ${sn}_${a}_${b}_${c}_${d}_${e}_${f}",
        process_cmd_string=add_etx)
    def upload_polynomial_rtd_parameters(self, sn, a, b, c, d, e, f):
        """
        Uploads the 5th order polynomial calibration parameters.

        The 'sn' argument is the 'serial number' or identifier for this set of parameters.

        Values of A, B, C, D, E, F constants for 5th order polynomial equation
        calibration curves.

        These parameters are required for 4 wire RTDs.
        """
        raise NotImplementedError

    @dynamic_command(cmd_type="query", cmd_string="set_rtd_parameters ${rtd_id} ${sn}",
                     process_cmd_string=add_etx)
    def set_rtd_parameters(self, rtd_id, sn):
        """
        Applies a previously uploaded set of RTD parameters, identified by the
        serial number (<sn>), to a given RTD channel (<rtd_id>).

        RTD parameters can be uploaded with the functions:

        * upload_callendar_vandusen_rtd_parameters()
        * upload_polynomial_rtd_parameters()

        """
        raise NotImplementedError

    @dynamic_command(cmd_type="query", cmd_string="run_task",
                     process_cmd_string=add_etx, process_response=decode_and_strip_response)
    def run_task(self) -> str:
        """
        Stores previously sent configuration parameters and runs the task.
        """
        raise NotImplementedError

    @dynamic_command(cmd_type="query", cmd_string="stop_task",
                     process_cmd_string=add_etx, process_response=decode_and_strip_response)
    def stop_task(self) -> str:
        """
        Stops the current running task (test, self-test, etc).
        """
        raise NotImplementedError

    @dynamic_command(cmd_type="query", cmd_string="get_error",
                     process_cmd_string=add_etx, process_response=process_error_response)
    def get_error(self) -> List:
        """
        Returns a list of the active occurred errors.
        """
        raise NotImplementedError


class TCSParameterNaming:
    """Defines the mapping between TCS EGSE device names and the CGSE names."""
    def __init__(self, origin: str):
        # The hk_names_mapping is a dictionary that maps the original device telemetry parameter
        # names to the correct device names as defined in the CGSE. The keys in the mapping are
        # the original device name, the values are the CGSE corrected names.

        self.hk_names_mapping = read_conversion_dict(storage_mnemonic=origin, use_site=False)

    def get_all_cgse_names(self):
        """Returns the correct CGSE housekeeping parameter names."""
        return self.hk_names_mapping.values()

    def get_cgse_name(self, device_name: str):
        """
        Returns the CGSE name corresponding to the given device name.
        If no CGSE name exists, the device name is returned.
        """
        return self.hk_names_mapping.get(device_name, device_name)


class TCSTelemetryMetrics:
    """Defines the metrics for the TCS EGSE that are maintained by the TCSTelemetry class."""
    def __init__(self):
        self.hk_metrics = define_metrics(origin=ORIGIN, dashboard="TCS_TRP_MON")
        self.hk_metrics_status = define_metrics(origin=ORIGIN, dashboard="TCS_STATUS_MON")

    def update_metrics(self, name: str, value: str):
        """Update the TCS metric parameter with the given value."""
        if name in self.hk_metrics:
            self.hk_metrics[name].set(float(value))
        elif name in self.hk_metrics_status:
            if '.' in value:
                self.hk_metrics_status[name].set(float(value))
            else:
                self.hk_metrics_status[name].set(int(value))


class TCSTelemetry(multiprocessing.Process):
    def __init__(self,
                 command_queue: multiprocessing.Queue,
                 response_queue: multiprocessing.Queue):
        super().__init__()
        self._command_q = command_queue
        self._response_q = response_queue
        self._column_names = None
        self._housekeeping = {}
        self._killer = None
        self._metrics: TCSTelemetryMetrics = None
        self._hk_names: TCSParameterNaming = None

    def run(self):

        # The TCS Telemetry runs in a different process and since ZeroMQ Sockets are not
        # thread/process safe, we have to recreate the ZeroMQHandler attached to the egse.logger
        # in this process.

        import egse.logger
        egse.logger.replace_zmq_handler()

        self._killer = SignalCatcher()

        # Device naming is different from CGSE naming, the conversion is handled in the
        # TCSParameterNaming class.

        self._hk_names = TCSParameterNaming(origin=ORIGIN)

        # Metrics must be defined only when the sub-process already exists, otherwise a TypeError
        # will be raised, indicating that a thread lock cannot be pickled

        self._metrics = TCSTelemetryMetrics()

        # These are only 61 of the telemetry parameters of the TCS EGSE. It is not possible to know
        # all the parameters beforehand since they are only published when changed. So, eventually,
        # more HK parameters will be available, but the CSV implementation does not allow to add
        # them after the file creation. In the TCS CSV the corrected CGSE naming is used.

        self._column_names = list(self._hk_names.get_all_cgse_names())

        # Prepend the timestamp (_ts) for each of the telemetry parameters.
        # Start with a reference timestamp

        self._column_names = list(
            (
                "timestamp",
                *itertools.chain.from_iterable((f"{x}_ts", x) for x in self._column_names)
            )
        )

        # The HTTP server is usually started from the control server, only in this case, the
        # metrics will be updated from this process and the server has to be started from here.

        start_http_server(CTRL_SETTINGS.METRICS_PORT)

        with SocketInterface(hostname=TCS_SETTINGS.HOSTNAME, port=TCS_SETTINGS.TELEMETRY_PORT) \
                as socket, StorageProxy() as storage:

            register_to_storage_manager(origin=CTRL_SETTINGS.STORAGE_TM_MNEMONIC,
                                        persistence_class=CSV,
                                        prep={"mode": "a", "column_names": self._column_names})
            while True:
                data = socket.read()
                self.process_telemetry(data)
                # logger.info(f"{data=}")
                # logger.info(f"{self._housekeeping=}")
                # logger.info(f"{self._housekeeping.keys()}")
                storage.save(
                    {
                        "origin": CTRL_SETTINGS.STORAGE_TM_MNEMONIC,
                        "data": self._housekeeping,
                    }
                )

                with SynopticsManagerProxy() as synoptics:
                    synoptics.store_common_synoptics(
                        dict(**self._housekeeping))

                if self._killer.term_signal_received:
                    break

            unregister_from_storage_manager(origin=CTRL_SETTINGS.STORAGE_TM_MNEMONIC)

    def process_telemetry(self, data: bytes):
        """
        Process the housekeeping telemetry that was received from the TCS EGSE.

        Args:
            data (str): a string containing the telemetry from the TCS EGSE.

        Returns:
            A dictionary where the key is the housekeeping parameter name and the value is a list
            containing the timestamp, name, and value of the housekeeping parameter. Only the last
            sample in kept in the dictionary.
        """

        self._housekeeping["timestamp"] = format_datetime()

        data = data.decode().split('\x03')
        data = [x for x in data if x]
        if not data:
            logger.warning("Format error: no new housekeeping values received.")
            return
        data = data[0].split('\r\n')
        data = [x.split('\t') for x in data]

        # We do not need to sort by timestamp since the data is already sorted by time.
        # data = sorted(data, key=operator.itemgetter(0))  # sort by date

        # We noticed that the telemetry transmission is not fail safe and sometimes data is missing
        # from the stream. That will result in an IndexError because one or more fields are missing.
        # When the date is incomplete due to transmission errors and cannot be parsed, a ValueError
        # is raised and silently ignored here.

        name = value = "not-yet-set"
        for x in data:
            try:
                date = convert_date(x[0])
                # replace name with the CGSE mnemonic from the TM dictionary
                name = self._hk_names.get_cgse_name(x[1])
                value = x[2]  # extract_value(x[1], x[2])
                self._housekeeping[f"{name}_ts"] = date
                self._housekeeping[name] = value
                self._metrics.update_metrics(name, value)
            except (IndexError, ValueError) as exc:
                logger.info(f"{exc=!s} for {name=}, {value=}")


def convert_date(date: str):
    """
    Convert the datetime string that is sent by the TCS EGSE to a format that is used by the CGSE.

    Args:
        date (str): datetime as "YYYY/MM/DD HH:MM:SS.ms UTC"

    Returns:
        A date string in the format "DD.MM.YYYY HH:MM:SS"

    Raises:
        ValueError when the date string can not be parsed.
    """
    try:
        dt = datetime.datetime.strptime(date, "%Y/%m/%d %H:%M:%S.%f utc")
        return format_datetime(dt)
    except ValueError as exc:
        logger.warning(f"Could not process date: {date=}, {exc=}")
        raise


class TCSController(TCSInterface, DynamicCommandMixin):
    """
    The constructor sets the connection parameters but there is no attempt to connect
    to the controller. Make sure that you explicitly use the `tcs.connect()` and `tcs.disconnect()`
    commands before communicating with the TCS EGSE.

    The controller can also be used as a context manager, in which case the `connect()`
    and `disconnect()` methods should not be called:

        with TCSController() as tcs:
            tcs.get_configuration()

    """

    def __init__(self, hostname=TCS_SETTINGS.HOSTNAME, port=TCS_SETTINGS.COMMANDING_PORT):
        """
        Opens a TCP/IP socket connection with the TCS EGSE Hardware Controller.

        Args:
            hostname (str): the IP address or fully qualified hostname of the TCS hardware
            controller. The default is defined in the `settings.yaml` configuration file.

            port (int): the IP port number to connect to, by default set in the `settings.yaml`
            configuration file.

        Raises:
            TCSError: when the connection could not be established for some reason.
        """

        super().__init__()

        logger.debug(f"Initializing TCSController with hostname={hostname} on port={port}")

        try:
            self.transport = self.tcs = TCSEthernetInterface(hostname, port)
        except TCSError as exc:
            logger.warning(
                f"TCSError: Couldn't establish connection with the TCS EGSE Hardware "
                f"Controller: ({exc})"
            )

    def is_simulator(self):
        return False

    def is_connected(self):
        return self.tcs.is_connected()

    def connect(self):
        try:
            self.tcs.connect()
        except TCSError as exc:
            logger.warning(f"TCSError caught: Couldn't establish connection ({exc})")
            raise ConnectionError("Couldn't establish a connection with the TCS EGSE.") from exc

        self.notify_observers(DeviceConnectionState.DEVICE_CONNECTED)

    def disconnect(self):
        try:
            self.tcs.disconnect()
        except TCSError as exc:
            raise ConnectionError("Couldn't disconnect from TCS EGSE.") from exc

        self.notify_observers(DeviceConnectionState.DEVICE_NOT_CONNECTED)

    def reconnect(self):
        if self.is_connected():
            self.disconnect()
        self.connect()


class TCSSimulator(TCSInterface):
    """
    Use the tcs_sim process instead of this class!
    """
    pass


class TCSProxy(DynamicProxy, TCSInterface):
    """
    The TCSProxy class is used to connect to the control server and send commands to the
    TCS EGSE remotely.
    """

    def __init__(
        self,
        protocol=CTRL_SETTINGS.PROTOCOL,
        hostname=CTRL_SETTINGS.HOSTNAME,
        port=CTRL_SETTINGS.COMMANDING_PORT,
        timeout=REQUEST_TIMEOUT
    ):
        """
        Args:
            protocol: the transport protocol [default is taken from settings file]
            hostname: location of the control server (IP address) [default is taken from settings
            file]
            port: TCP port on which the control server is listening for commands [default is
            taken from settings file]
        """
        super().__init__(connect_address(protocol, hostname, port), timeout=timeout)


def process_data(data: str) -> List[List[str]]:
    """
    Process the response from the TCS EGSE periodic telemetry.

    The output list may contains the same parameter several times.
    Args:
        data (str): a string containg the periodic telemetry sent out by the TCS EGSE.

    Returns:
        A nested list where the inner lists contain the name, timestamp and value of a telemetry
        parameter. The list is not sorted, but left in the order that they had in the response
        string.
    """

    data = data.split('\x03')
    data = [x for y in data for x in y.split('\r\n') if x]
    data = [x.split('\t') for x in data]

    # make sure the nested list is [name, date, value]
    data = [[x[1], x[0], x[2]] for x in data]

    return data
