import datetime
import logging
import multiprocessing
from typing import List

from egse.command import ClientServerCommand
from egse.control import ControlServer
from egse.control import Failure
from egse.device import DeviceConnectionState
from egse.device import DeviceTimeoutError
from egse.metrics import define_metrics
from egse.protocol import DynamicCommandProtocol
from egse.settings import Settings
from egse.system import format_datetime
from egse.tcs.tcs import TCSController
from egse.tcs.tcs import TCSParameterNaming
from egse.tcs.tcs import TCSSimulator
from egse.tcs.tcs import TCSTelemetry

MODULE_LOGGER = logging.getLogger(__name__)

CTRL_SETTINGS = Settings.load("TCS Control Server")
PUNA_SETTINGS = Settings.load(filename="tcs.yaml")


class TCSCommand(ClientServerCommand):
    def get_cmd_string(self, *args, **kwargs) -> str:
        out = super().get_cmd_string(*args, **kwargs)
        return out + chr(3)  # end the string with the ASCII character EOT


class TCSMetrics:
    """Defines the metrics for the TCS EGSE that are maintained by the TCSProtocol class."""
    def __init__(self, origin: str, dashboard: str):
        self.metrics = define_metrics(origin=origin, dashboard=dashboard)

    def __contains__(self, item):
        return self.metrics.__contains__(item)

    def names(self):
        return self.metrics.keys()

    def update_metrics(self, name: str, value: str):
        """Update the TCS metric parameter with the given value."""
        if name in self.metrics:
            self.metrics[name].set(float(value))


class TCSProtocol(DynamicCommandProtocol):
    def __init__(self, control_server: ControlServer):
        super().__init__(control_server)

        # Read the configuration metrics from the tm-dictionary

        self._metrics = TCSMetrics(origin=control_server.get_storage_mnemonic(),
                                   dashboard="TCS_CONFIGURATION_MON")

        # Device naming is different from CGSE naming, the conversion is handled in the
        # TCSParameterNaming class.

        self._hk_names = TCSParameterNaming(origin=control_server.get_storage_mnemonic())

        # Set up two queue's to communicate with the TCS Telemetry Process.
        # The command queue is joinable because the Controller needs to wait for a response in
        # the response queue.

        self.command_queue = multiprocessing.Queue()
        self.response_queue = multiprocessing.Queue()

        # Start a separate Process to handle the TCS EGSE Telemetry

        self.processor = TCSTelemetry(self.command_queue, self.response_queue)
        self.processor.name = "tcs.telemetry"
        self.processor.start()

        self.device = TCSSimulator() if Settings.simulation_mode() else TCSController()

        try:
            self.device.connect()
        except (ConnectionError, DeviceTimeoutError) as exc:
            MODULE_LOGGER.warning(
                f"Couldn't establish a connection to the TCS EGSE ({exc}).")

        self._dt_of_last_error = datetime.datetime.now(tz=datetime.timezone.utc)

    def quit(self):
        self.processor.terminate()

    def get_device(self):
        return self.device

    def get_status(self):

        status = super().get_status()

        # TODO (rik): add status information for the monitoring service here

        if self.state == DeviceConnectionState.DEVICE_CONNECTED or Settings.simulation_mode():
            # Collect status information here
            pass

        return status

    def get_housekeeping(self) -> dict:

        self.log_new_errors()

        result = {"timestamp": format_datetime()}

        # Put in NaN as a default value, this will be updated with the actual real values
        # when the TCS EGSE is in remote control mode and the configuration can be obtained.
        # This 'initialisation' is also needed because the column names are determined when
        # the TCS EGSE is not in remote control mode.

        result.update(
            {name: float('nan') for name in self._metrics.names()}
        )

        # if self.state == DeviceConnectionState.DEVICE_CONNECTED:
        #     # Collect housekeeping information here
        #     pass

        configuration = self.device.get_configuration()

        if isinstance(configuration, Failure):
            [self._metrics.update_metrics(name, 'nan') for name in self._metrics.names()]
            return result

        # update the housekeeping table with the actual values for the Storage

        result.update(
            {
                self._hk_names.get_cgse_name(name): value
                for name, value in configuration.items()
                if self._hk_names.get_cgse_name(name) in self._metrics
            }
        )

        # update the recorded metrics for Prometheus/Grafana

        for name, value in configuration.items():
            self._metrics.update_metrics(self._hk_names.get_cgse_name(name), value)

        return result

    def log_new_errors(self):

        errors = new_errors = None
        try:
            errors = self.device.get_error()
            new_errors = self._extract_last_error(errors)
            for error in new_errors:
                MODULE_LOGGER.error(f"TCS EGSE: {error}")
        except Exception as exc:
            MODULE_LOGGER.error(f"Exception caught: {exc=}")
            MODULE_LOGGER.debug(f"{errors=}")
            MODULE_LOGGER.debug(f"{new_errors=}")

    def _extract_last_error(self, errors: List):

        new_errors = []

        for error_msg in errors:
            if 'remote_mode_not_active' in error_msg:
                MODULE_LOGGER.warning("TCS EGSE: Remote mode is not active")
                break
            if 'no errors' in error_msg:
                break
            dt_error_str, *_, msg = error_msg.split('\t')
            dt_error = datetime.datetime.strptime(dt_error_str, "%Y/%m/%d %H:%M:%S.%f UTC")
            dt_error = dt_error.replace(tzinfo=datetime.timezone.utc)
            if dt_error > self._dt_of_last_error:
                new_errors.append((format_datetime(dt_error), msg))

        self._dt_of_last_error = datetime.datetime.now(tz=datetime.timezone.utc)

        return new_errors
