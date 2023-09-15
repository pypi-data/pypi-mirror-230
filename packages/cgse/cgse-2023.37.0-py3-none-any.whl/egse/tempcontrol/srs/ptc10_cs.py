import argparse
import click
import logging
import sys

import zmq

from egse.control import ControlServer
from egse.tempcontrol.srs.ptc10 import ptc10Proxy
from egse.tempcontrol.srs.ptc10_protocol import ptc10Protocol
from egse.settings import Settings
from egse.zmq_ser import connect_address
from egse.control import is_control_server_active

logger = logging.getLogger(__name__)

CTRL_SETTINGS = Settings.load("SRS PTC10 Control Server")


def is_ptc10_cs_active(timeout: float = 0.5):
    """Check if the DAQ6510 Control Server is running.

    Args:
        timeout (float): timeout when waiting for a reply [seconds, default=0.5]
    Returns:
        True if the control server is running and replied with the expected answer.
    """

    endpoint = connect_address(
        CTRL_SETTINGS.PROTOCOL, CTRL_SETTINGS.HOSTNAME, CTRL_SETTINGS.COMMANDING_PORT
    )

    return is_control_server_active(endpoint, timeout)


class ptc10ControlServer(ControlServer):
    """
    ptc10ControlServer - Command and monitor the PTC10 Temp Controllers.
    This class works as a command and monitoring server to control the Temp Controller remotely.
    The sever binds to the following ZeroMQ sockets:
    * a REQ-REP socket that can be used as a command server. Any client can connect and
      send a command to the Temp controller.
    * a PUB-SUP socket that serves as a monitoring server. It will send out Temp status
      information to all the connected clients every DELAY seconds.
    """

    def __init__(self):
        super().__init__()

        self.device_protocol = ptc10Protocol(self)

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
            return "DAS-PTC10-EMPTY"


@click.group()
def cli():
    pass


@cli.command()
@click.option("--simulator", "--sim", is_flag=True, help="Start the PTC10 Temp Simulator as the backend.")
def start(simulator):
    """Start the PTC10 Temp Control Server."""

    if simulator:

        Settings.set_simulation_mode(True)

    try:

        controller = ptc10ControlServer()
        controller.serve()

    except KeyboardInterrupt:

        print("Shutdown requested...exiting")

    except SystemExit as exit_code:

        print("System Exit with code {}.".format(exit_code))
        sys.exit(exit_code)

    except Exception:

        logger.exception("Cannot start the PTC10 Temp Control Server")

        # The above line does exactly the same as the traceback, but on the logger
        # import traceback
        # traceback.print_exc(file=sys.stdout)

    return 0


@cli.command()
def stop():
    """Send a 'quit_server' command to the PTC10 Temp Control Server."""

    with ptc10Proxy() as proxy:

        sp = proxy.get_service_proxy()
        sp.quit_server()


if __name__ == "__main__":

    sys.exit(cli())
