import logging
import multiprocessing
import sys
from pathlib import Path

import click
import zmq
from prometheus_client import start_http_server

from egse.settings import Settings
from egse.control import ControlServer
from egse.system import replace_environment_variable
from egse.fdir.fdir_manager import FdirManagerProtocol, FdirManagerProxy

logger = logging.getLogger(__name__)

CTRL_SETTINGS = Settings.load("FDIR Manager Control Server")


class FdirManagerControlServer(ControlServer):
    """ The FDIR Manager Control Server is the centralized point of emergency mitigation.
        In response to an FDIR signal from anywhere in the CGSE, this CS will terminate all running
        control scripts and subsequently run a predefined recovery script. Terminating control
        scripts on other hosts is done through a FDIR Remote CS, running on the other host(s).

        The following functionality is provided:

        * (de-)registering control scripts
        * receiving FDIR codes
        * automated killing of operational scripts
        * automated running of recovery scripts
        * handling priority between FDIR codes
        * monitoring of the FDIR CS state
    """

    def __init__(self):
        super().__init__()

        self.device_protocol = FdirManagerProtocol(self)
        self.logger.debug(f"Binding ZeroMQ socket to {self.device_protocol.get_bind_address()}")
        self.device_protocol.bind(self.dev_ctrl_cmd_sock)
        self.poller.register(self.dev_ctrl_cmd_sock, zmq.POLLIN)

    def get_communication_protocol(self):
        return CTRL_SETTINGS.PROTOCOL

    def get_commanding_port(self):
        return CTRL_SETTINGS.COMMANDING_PORT

    def get_service_port(self):
        return CTRL_SETTINGS.SERVICE_PORT

    def get_monitoring_port(self):
        return CTRL_SETTINGS.MONITORING_PORT

    def get_storage_mnemonic(self):
        try:
            return CTRL_SETTINGS.STORAGE_MNEMONIC
        except AttributeError:
            return "FM"

    def before_serve(self):
        start_http_server(CTRL_SETTINGS.METRICS_PORT)


@click.group()
def cli():
    pass


@cli.command()
def start():
    """ Starts the FDIR Control Server. """

    multiprocessing.current_process().name = "fdir_manager_cs"

    try:
        check_prerequisites()
    except RuntimeError as exc:
        print(exc)
        logger.error(exc)
        return 0

    try:
        control_server = FdirManagerControlServer()
        control_server.serve()
    except KeyboardInterrupt:
        print("Shutdown requested...exiting")
    except SystemExit as exit_code:
        print("System Exit with code {}.".format(exit_code))
        sys.exit(exit_code)
    except Exception:
        import traceback

        traceback.print_exc(file=sys.stdout)

    return 0


@cli.command()
def stop():
    """Send a 'quit_server' command to the Configuration Manager."""
    with FdirManagerProxy() as fm:
        sp = fm.get_service_proxy()
        sp.quit_server()


@cli.command()
def status():
    """Print the status of the control server."""
    pass


def check_prerequisites():
    """ Checks if the recovery script location is defined and valid.

        Raises:
            RuntimeError.
    """

    location = CTRL_SETTINGS.RECOVERY_SCRIPT_LOCATION
    location = replace_environment_variable(location)

    if not location:
        raise RuntimeError(
            "The environment variable referenced in the Settings.yaml file for the "
            "RECOVERY_SCRIPT_LOCATION of the FDIR control server does not exist, please set "
            "the environment variable."
        )

    location = Path(location)

    if not location.exists():
        raise RuntimeError(
            f"The directory {location} does not exist, provide a valid location for "
            f"recovery scripts."
        )

    logger.debug(f"recovery script location = {location}")

    location = CTRL_SETTINGS.LOGGING_LOCATION
    location = replace_environment_variable(location)

    if not location:
        raise RuntimeError(
            "The environment variable referenced in the Settings.yaml file for the "
            "LOGGING_LOCATION of the FDIR control server does not exist, please set "
            "the environment variable."
        )

    location = Path(location)

    if not location.exists():
        raise RuntimeError(
            f"The directory {location} does not exist, provide a valid location for "
            f"the log output of recovery scripts."
        )

    logger.debug(f"FDIR recovery script logging location = {location}")


if __name__ == "__main__":

    sys.exit(cli())
