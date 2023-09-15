"""
The HUBER SMC9300 control server connects to the HUBER Hardware Controller.

Start the control server from the terminal as follows:

    $ smc9300_cs start-bg

or when you don't have the device available, start the control server in simulator mode. That
will make the control server connect to a device software simulator:

    $ smc9300_cs start --sim

Please note that software simulators are intended for simple test purposes and will not simulate
all device behavior correctly, e.g. timing, error conditions, etc.

"""

import logging
import multiprocessing

import rich

from egse.control import is_control_server_active
from egse.zmq_ser import connect_address

multiprocessing.current_process().name = "smc9300_cs"

import sys

import click
import invoke
import zmq
from prometheus_client import start_http_server

from egse.control import ControlServer
from egse.settings import Settings
from egse.stages.huber.smc9300 import HuberSMC9300Proxy
from egse.stages.huber.smc9300_protocol import HuberSMC9300Protocol

logger = logging.getLogger(__name__)

CTRL_SETTINGS = Settings.load("Huber Control Server")


class HuberSMC9300ControlServer(ControlServer):
    """
    HuberSMC9300ControlServer - Command and monitor the HUBER hardware stages.

    This class works as a command and monitoring server to control the HUBER stages remotely.

    The sever binds to the following ZeroMQ sockets:

    * a REQ-REP socket that can be used as a command server. Any client can connect and
      send a command to the Huber hardware controller.

    * a PUB-SUP socket that serves as a monitoring server. It will send out HUBER status
      information to all the connected clients every DELAY seconds.

    """

    def __init__(self):
        super().__init__()

        self.device_protocol = HuberSMC9300Protocol(self)

        self.logger.info(f"Binding ZeroMQ socket to {self.device_protocol.get_bind_address()}")

        self.device_protocol.bind(self.dev_ctrl_cmd_sock)

        self.poller.register(self.dev_ctrl_cmd_sock, zmq.POLLIN)

        self.set_delay(CTRL_SETTINGS.ST_DELAY)
        self.set_hk_delay(CTRL_SETTINGS.HK_DELAY)

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
            return "SMC9300"

    def before_serve(self):
        start_http_server(CTRL_SETTINGS.METRICS_PORT)


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--simulator", "--sim", is_flag=True, help="Start the Huber Stages Simulator as the backend."
)
def start(simulator):
    """Start the Huber SMC9300 Stages Control Server."""

    if simulator:

        Settings.set_simulation_mode(True)

    try:

        controller = HuberSMC9300ControlServer()
        controller.serve()

    except KeyboardInterrupt:

        print("Shutdown requested...exiting")

    except SystemExit as exit_code:

        print("System Exit with code {}.".format(exit_code))
        sys.exit(exit_code)

    except Exception:

        logger.exception("Cannot start the Huber SMC9300 Stages Control Server")

    return 0


@cli.command()
@click.option("--simulator", "--sim", is_flag=True,
              help="Start the Huber SMC9300 Simulator as the backend.")
def start_bg(simulator):
    """Start the Huber SMC9300 Stages Control Server in the background."""
    sim = "--simulator" if simulator else ""
    invoke.run(f"smc9300_cs start {sim}", disown=True)


@cli.command()
def stop():
    """Send a 'quit_server' command to the Huber SMC9300 Stages Control Server."""

    with HuberSMC9300Proxy() as proxy:

        sp = proxy.get_service_proxy()
        sp.quit_server()

@cli.command()
def status():
    """Request status information from the Control Server."""

    protocol = CTRL_SETTINGS.PROTOCOL
    hostname = CTRL_SETTINGS.HOSTNAME
    port = CTRL_SETTINGS.COMMANDING_PORT

    endpoint = connect_address(protocol, hostname, port)

    if is_control_server_active(endpoint):
        rich.print(f"HUBER Stages: [green]active")
        with HuberSMC9300Proxy() as stages:
            sim = stages.is_simulator()
            connected = stages.is_connected()
            ip = stages.get_ip_address()
            rich.print(f"mode: {'simulator' if sim else 'device'}{' not' if not connected else ''} connected")
            rich.print(f"hostname: {ip}")
    else:
        rich.print(f"HUBER Stages: [red]not active")


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG, format=Settings.LOG_FORMAT_FULL)

    sys.exit(cli())
