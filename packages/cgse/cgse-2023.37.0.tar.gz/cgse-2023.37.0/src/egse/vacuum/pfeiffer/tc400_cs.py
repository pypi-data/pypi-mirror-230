import click
import logging
import sys

import zmq
from prometheus_client import start_http_server

from egse.control import ControlServer
from egse.settings import Settings
from egse.vacuum.pfeiffer.tc400 import Tc400Protocol, Tc400Proxy


logging.basicConfig(level=logging.DEBUG, format=Settings.LOG_FORMAT_FULL)

logger = logging.getLogger(__name__)

CTRL_SETTINGS = Settings.load("Pfeiffer TC400 Control Server")


class Tc400ControlServer(ControlServer):
    """
    Tc400ControlServer - Command and monitor the Tc400 roots pump controller.
    This class works as a command and monitoring server to control the device remotely.
    The sever binds to the following ZeroMQ sockets:
    * a REP socket that can be used as a command server. Any client can connect and
      send a command to the Lamp controller.
    * a PUB socket that serves as a monitoring server. It will send out Lamp status
      information to all the connected clients every DELAY seconds.
    """

    def __init__(self):
        super().__init__()

        self.device_protocol = Tc400Protocol(self)

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
            return "TC400"

    def before_serve(self):
        start_http_server(CTRL_SETTINGS.METRICS_PORT)


@click.group()
def cli():
    pass


@cli.command()
@click.option("--simulator", "--sim", is_flag=True, help="Start the TC400 Simulator as the backend.")
def start(simulator):
    """Start the TC400 Control Server."""

    if simulator:
        Settings.set_simulation_mode(True)
    try:
        controller = Tc400ControlServer()
        controller.serve()

    except KeyboardInterrupt:
        print("Shutdown requested...exiting")

    except SystemExit as exit_code:
        print("System Exit with code {}.".format(exit_code))
        sys.exit(exit_code)

    except Exception:

        logger.exception("Cannot start the TC400 Control Server")
        # The above line does exactly the same as the traceback, but on the logger
        # import traceback
        # traceback.print_exc(file=sys.stdout)

    return 0


@cli.command()
def stop():
    """Send a 'quit_server' command to the TC400 Control Server."""

    with Tc400Proxy() as proxy:

        sp = proxy.get_service_proxy()
        sp.quit_server()


if __name__ == "__main__":

    sys.exit(cli())
