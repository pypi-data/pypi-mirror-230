import logging
import multiprocessing
import sys
from pathlib import Path

from PyQt5.QtWidgets import QApplication
import click
import zmq
from prometheus_client import start_http_server

from egse.settings import Settings
from egse.control import ControlServer
from egse.system import replace_environment_variable
from egse.fdir.fdir_remote import FdirRemoteProtocol, FdirRemoteProxy

logger = logging.getLogger(__name__)

CTRL_SETTINGS = Settings.load("FDIR Remote Control Server")


class FdirRemoteControlServer(ControlServer):


    def __init__(self):
        super().__init__()
        self.device_protocol = FdirRemoteProtocol(self)
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
            return "FR"

    def before_serve(self):
        start_http_server(CTRL_SETTINGS.METRICS_PORT)


@click.group()
def cli():
    pass


@cli.command()
def start():
    """ Starts the FDIR Control Server. """

    multiprocessing.current_process().name = "fdir_remote_cs"

    try:
        control_server = FdirRemoteControlServer()
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
    with FdirRemoteProxy() as fm:
        sp = fm.get_service_proxy()
        sp.quit_server()


@cli.command()
def status():
    """Print the status of the control server."""
    pass


if __name__ == "__main__":

    sys.exit(cli())
