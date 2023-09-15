import logging

import click
import rich
import sys
import zmq
from prometheus_client import start_http_server

from egse.control import ControlServer, is_control_server_active
from egse.filterwheel.eksma.fw8smc4 import FilterWheel8SMC4Proxy
from egse.filterwheel.eksma.fw8smc4_protocol import FilterWheel8SMC4Protocol
from egse.settings import Settings
from egse.zmq_ser import connect_address

logger = logging.getLogger("egse.filterwheel.eksma.fw8smc4_cs")

CTRL_SETTINGS = Settings.load("Filter Wheel 8SMC4 Control Server")


class FilterWheelControlServer(ControlServer):
    """
    FilterwheelControlServer - Command and monitor the Filter Wheel 8SMC4 Controller.
    This class works as a command and monitoring server to control the Shutter Controller remotely.
    The sever binds to the following ZeroMQ sockets:
    * a REQ-REP socket that can be used as a command server. Any client can connect and
      send a command to the Thorlabs controller.
    * a PUB-SUP socket that serves as a monitoring server. It will send out Eksma status
      information to all the connected clients every DELAY seconds.
    """

    def __init__(self):
        super().__init__()

        self.device_protocol = FilterWheel8SMC4Protocol(self)

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
            return "FW8SMC4"

    def before_serve(self):
        start_http_server(CTRL_SETTINGS.METRICS_PORT)

    def after_serve(self):
        self.device_protocol.synoptics.disconnect_cs()

@click.group()
def cli():
    pass


@cli.command()
@click.option("--simulator", "--sim", is_flag=True, help="Start the Eksma 8SMC4 Filterwheel Simulator as the backend.")
def start(simulator):
    """Start the Eksma 8SMC4 Filterwheel Control Server."""

    if simulator:

        Settings.set_simulation_mode(True)

    try:

        controller = FilterWheelControlServer()
        controller.serve()

    except KeyboardInterrupt:

        print("Shutdown requested...exiting")

    except SystemExit as exit_code:

        print("System Exit with code {}.".format(exit_code))
        sys.exit(exit_code)

    except Exception:

        logger.exception("Cannot start the Eksma 8SMC4 Filterwheel Control Server")

        # The above line does exactly the same as the traceback, but on the logger
        # import traceback
        # traceback.print_exc(file=sys.stdout)

    return 0


@cli.command()
def stop():
    """Send a 'quit_server' command to the Eksma Filterwheel Control Server."""

    with FilterWheel8SMC4Proxy() as proxy:

        sp = proxy.get_service_proxy()
        sp.quit_server()


@cli.command()
def status():
    """Send a 'quit_server' command to the FW8SMC4 filterwheel."""

    rich.print("FW8SMC4 filterwheel:")

    protocol = CTRL_SETTINGS.PROTOCOL
    hostname = CTRL_SETTINGS.HOSTNAME
    port = CTRL_SETTINGS.COMMANDING_PORT

    endpoint = connect_address(protocol, hostname, port)

    if is_control_server_active(endpoint):
        rich.print(f"  Status: [green]active")

        with FilterWheel8SMC4Proxy() as filterwheel:
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
