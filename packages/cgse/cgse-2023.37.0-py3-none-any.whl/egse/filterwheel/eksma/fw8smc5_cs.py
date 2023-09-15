import logging

import click
import rich
import sys
import zmq
from prometheus_client import start_http_server

from egse.control import ControlServer, is_control_server_active
from egse.filterwheel.eksma.fw8smc5 import Fw8Smc5Protocol, Fw8Smc5Proxy
from egse.settings import Settings
from egse.zmq_ser import connect_address

logging.basicConfig(level=logging.DEBUG, format=Settings.LOG_FORMAT_FULL)

logger = logging.getLogger(__name__)

CTRL_SETTINGS = Settings.load("Standa 8SMC5 Control Server")


class Fw8Smc5ControlServer(ControlServer):
    """
    Fw8Smc5ControlServer - Command and monitor the 8SMC5 turbo pump.
    This class works as a command and monitoring server to control the device remotely.
    The sever binds to the following ZeroMQ sockets:
    * a REP socket that can be used as a command server. Any client can connect and
      send a command to the Lamp controller.
    * a PUB socket that serves as a monitoring server. It will send out Lamp status
      information to all the connected clients every DELAY seconds.
    """

    def __init__(self):
        super().__init__()

        self.device_protocol = Fw8Smc5Protocol(self)

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
            return "8SMC5"

    def before_serve(self):
        start_http_server(CTRL_SETTINGS.METRICS_PORT)

    def after_serve(self):
        self.device_protocol.synoptics.disconnect_cs()


@click.group()
def cli():
    pass


@cli.command()
@click.option("--simulator", "--sim", is_flag=True, help="Start the 8SMC5 Simulator as the backend.")
def start(simulator):
    """Start the 8SMC5 Control Server."""

    if simulator:
        Settings.set_simulation_mode(True)
    try:
        controller = Fw8Smc5ControlServer()
        controller.serve()

    except KeyboardInterrupt:
        print("Shutdown requested...exiting")

    except SystemExit as exit_code:
        print("System Exit with code {}.".format(exit_code))
        sys.exit(exit_code)

    except Exception:

        logger.exception("Cannot start the 8SMC5 Control Server")
        # The above line does exactly the same as the traceback, but on the logger
        # import traceback
        # traceback.print_exc(file=sys.stdout)

    return 0


@cli.command()
def stop():
    """Send a 'quit_server' command to the Control Server."""

    with Fw8Smc5Proxy() as proxy:

        sp = proxy.get_service_proxy()
        sp.quit_server()


@cli.command()
def status():
    """Send a 'quit_server' command to the FW8 SMC5 filterwheel."""

    rich.print("FW8SMC5 filterwheel:")

    protocol = CTRL_SETTINGS.PROTOCOL
    hostname = CTRL_SETTINGS.HOSTNAME
    port = CTRL_SETTINGS.COMMANDING_PORT

    endpoint = connect_address(protocol, hostname, port)

    if is_control_server_active(endpoint):
        rich.print(f"  Status: [green]active")

        with Fw8Smc5Proxy() as filterwheel:
            rich.print(f"  Hostname: {filterwheel.get_ip_address()}")
            rich.print(f"  Monitoring port: {filterwheel.get_monitoring_port()}")
            rich.print(f"  Commanding port: {filterwheel.get_commanding_port()}")
            rich.print(f"  Service port: {filterwheel.get_service_port()}")
            sim = filterwheel.is_simulator()
            connected = filterwheel.is_connected()
            rich.print(f"mode: {'simulator' if sim else 'device'}{' not' if not connected else ''} connected")

    else:
        rich.print(f"  Status: [red]inactive")


if __name__ == "__main__":

    sys.exit(cli())
