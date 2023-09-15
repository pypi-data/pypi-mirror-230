"""
The Control Server that connects to the Gimbal Hardware Controller.

Start the control server from the terminal as follows:

    $ gimbal_cs start-bg

or when you don't have the device available, start the control server in simulator mode. That
will make the control server connect to a device software simulator:

    $ gimbal_cs start --sim

Please note that software simulators are intended for simple test purposes and will not simulate
all device behavior correctly, e.g. timing, error conditions, etc.

"""
import logging

if __name__ != "__main__":
    import multiprocessing
    multiprocessing.current_process().name = "gimbal_cs"

import sys

import click
import invoke
import rich
import zmq

from egse.control import is_control_server_active
from egse.zmq_ser import connect_address

from prometheus_client import start_http_server

from egse.control import ControlServer
from egse.gimbal.symetrie.gimbal import GimbalProxy
from egse.gimbal.symetrie.gimbal_protocol import GimbalProtocol
from egse.settings import Settings

logger = logging.getLogger(__name__)

CTRL_SETTINGS = Settings.load("Gimbal Control Server")


class GimbalControlServer(ControlServer):
    """GimbalControlServer - Command and monitor the Gimbal hardware.

    This class works as a command and monitoring server to control the Symétrie Gimbal.
    This control server shall be used as the single point access for controlling the hardware
    device. Monitoring access should be done preferably through this control server also,
    but can be done with a direct connection through the GimbalController if needed.

    The sever binds to the following ZeroMQ sockets:

    * a REQ-REP socket that can be used as a command server. Any client can connect and
      send a command to the Gimbal.

    * a PUB-SUP socket that serves as a monitoring server. It will send out Gimbal status
      information to all the connected clients every five seconds.

    """

    def __init__(self):
        super().__init__()

        self.device_protocol = GimbalProtocol(self)

        self.logger.info(f"Binding ZeroMQ socket to {self.device_protocol.get_bind_address()}")

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
            return "GIMBAL"

    def before_serve(self):
        start_http_server(CTRL_SETTINGS.METRICS_PORT)
    

@click.group()
def cli():
    pass


@cli.command()
@click.option("--simulator", "--sim", is_flag=True,
              help="Start the Gimbal Simulator as the backend.")
def start(simulator):
    """Start the Gimbal Control Server."""

    if simulator:

        Settings.set_simulation_mode(True)

    try:

        controller = GimbalControlServer()
        controller.serve()

    except KeyboardInterrupt:

        print("Shutdown requested...exiting")

    except SystemExit as exit_code:

        print("System Exit with code {}.".format(exit_code))
        sys.exit(exit_code)

    except Exception:

        logger.exception("Cannot start the Gimbal Control Server")

        # The above line does exactly the same as the traceback, but on the logger
        # import traceback
        # traceback.print_exc(file=sys.stdout)

    return 0


@cli.command()
@click.option("--simulator", "--sim", is_flag=True,
              help="Start the Gimbal Simulator as the backend.")
def start_bg(simulator):
    """Start the Gimbal Control Server in the background."""
    sim = "--simulator" if simulator else ""
    invoke.run(f"gimbal_cs start {sim}", disown=True)


@cli.command()
def stop():
    """Send a 'quit_server' command to the Gimbal Control Server."""

    try:
        with GimbalProxy() as proxy:
            sp = proxy.get_service_proxy()
            sp.quit_server()
    except ConnectionError:
        rich.print("[red]Couldn't connect to 'gimbal_cs', process probably not running. ")


@cli.command()
def status():
    """Request status information from the Control Server."""

    protocol = CTRL_SETTINGS.PROTOCOL
    hostname = CTRL_SETTINGS.HOSTNAME
    port = CTRL_SETTINGS.COMMANDING_PORT

    endpoint = connect_address(protocol, hostname, port)

    if is_control_server_active(endpoint):
        rich.print(f"Gimbal: [green]active")
        with GimbalProxy() as gimbal:
            sim = gimbal.is_simulator()
            connected = gimbal.is_connected()
            ip = gimbal.get_ip_address()
            rich.print(f"mode: {'simulator' if sim else 'device'}{' not' if not connected else ''} connected")
            rich.print(f"hostname: {ip}")
    else:
        rich.print(f"Gimbal: [red]not active")


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG, format=Settings.LOG_FORMAT_FULL)

    sys.exit(cli())
