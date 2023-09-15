import argparse
import click
import logging
import sys
import rich
import zmq

import multiprocessing
multiprocessing.current_process().name = "lsci_cs"

from egse.control import ControlServer
from egse.control import is_control_server_active
from egse.settings import Settings
from egse.tempcontrol.lakeshore.lsci import LakeShoreProxy
from egse.tempcontrol.lakeshore.lsci_protocol import LakeShoreProtocol
from prometheus_client import start_http_server
from egse.zmq_ser import connect_address

logging.basicConfig(level=logging.DEBUG, format=Settings.LOG_FORMAT_FULL)
logger = logging.getLogger("LSCI CS")

CTRL_SETTINGS = Settings.load("LakeShore Control Server")




def is_lsci_cs_active(timeout: float = 0.5):
    """Check if the LSCI Control Server is running.

    Args:
        timeout (float): timeout when waiting for a reply [seconds, default=0.5]
    Returns:
        True if the control server is running and replied with the expected answer.
    """

    endpoint = connect_address(
        CTRL_SETTINGS.PROTOCOL, CTRL_SETTINGS.HOSTNAME, CTRL_SETTINGS.COMMANDING_PORT
    )

    return is_control_server_active(endpoint, timeout)


class LakeShoreControlServer(ControlServer):
    """
    LakeShoreControlServer - Command and monitor the LakeShore Temperature Controllers.

    This class works as a command and monitoring server to control the LakeShore Controller.

    The sever binds to the following ZeroMQ sockets:

    * a REQ-REP socket that can be used as a command server. Any client can connect and
      send a command to the LakeShore controller.

    * a PUB-SUP socket that serves as a monitoring server. It will send out LakeShore status
      information to all the connected clients every DELAY seconds.

    """

    def __init__(self, index):
        self.index = index
        self.name = "LS_"+str(index)
        print(index)
        super().__init__()
        self.device_protocol = LakeShoreProtocol(self, self.index)

        logger.debug(f"Binding ZeroMQ socket to {self.device_protocol.get_bind_address()}")

        self.device_protocol.bind(self.dev_ctrl_cmd_sock)

        self.poller.register(self.dev_ctrl_cmd_sock, zmq.POLLIN)

    def get_communication_protocol(self):
        return CTRL_SETTINGS.PROTOCOL

    def get_commanding_port(self):
        return CTRL_SETTINGS[self.name]['COMMANDING_PORT']

    def get_service_port(self):
        return CTRL_SETTINGS[self.name]['SERVICE_PORT']

    def get_monitoring_port(self):
        return CTRL_SETTINGS[self.name]['MONITORING_PORT']
    
    def get_storage_mnemonic(self):
        try:
            return CTRL_SETTINGS[self.name]['STORAGE_MNEMONIC']
        except AttributeError:
            return f'LSCI_{self.index}'
    def before_serve(self):
        start_http_server(CTRL_SETTINGS[self.name]['METRICS_PORT'])

    def after_serve(self):
        self.device_protocol.synoptics.disconnect_cs()

@click.group()
def cli():
    pass


@cli.command()
@click.option("--simulator", "--sim", is_flag=True, help="Start the Lakeshore LSCI Simulator as the backend.")
@click.argument('index', type=click.IntRange(1, 3))
def start(simulator,index):
    """Start the LakeShore LSCI Control Server."""

    if simulator:

        Settings.set_simulation_mode(True)

    try:
        logger.debug(f'Starting LakeShore {index} Control Server')
        multiprocessing.current_process().name = f"lsci_cs_{index}"

        controller = LakeShoreControlServer(index)
        controller.serve()

    except KeyboardInterrupt:

        logger.exception("Shutdown requested...exiting")

    except SystemExit as exit_code:

        logger.exception("System Exit with code {}.".format(exit_code))
        sys.exit(exit_code)

    except Exception:

        logger.exception("Cannot start the LakeShore LSCI Control Server")

        # The above line does exactly the same as the traceback, but on the logger
        # import traceback
        # traceback.print_exc(file=sys.stdout)

    return 0


@cli.command()
@click.argument('index', type=click.IntRange(1, 3))
def stop(index):
    """Send a 'quit_server' command to the LakeShore LSCI Control Server."""

    with LakeShoreProxy(index) as proxy:

        sp = proxy.get_service_proxy()
        sp.quit_server()

@cli.command()
@click.argument('index', type=click.IntRange(1, 3))
def status(index):
    """Request status information from the Control Server."""
    name = "LS_"+str(index)
    protocol = CTRL_SETTINGS.PROTOCOL
    hostname = CTRL_SETTINGS.HOSTNAME
    port = CTRL_SETTINGS[name]['COMMANDING_PORT']

    endpoint = connect_address(protocol, hostname, port)

    if is_control_server_active(endpoint):
        rich.print(f"LSCI {index} CS: [green]active")
        with LakeShoreProxy(index) as lsci:
            sim = lsci.is_simulator()
            connected = lsci.is_connected()
            ip = lsci.get_ip_address()
            rich.print(f"mode: {'simulator' if sim else 'device'}{' not' if not connected else ''} connected")
            rich.print(f"hostname: {ip}")
    else:
        rich.print(f"LSCI {index} CS: [red]not active")




if __name__ == "__main__":

    sys.exit(cli())
