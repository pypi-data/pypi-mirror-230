"""
The Control Server that connects to the PLATO TCS EGSE Hardware Controller.

Start the control server from the terminal as follows:

```bash
$ tcs_cs start
```
or when you don't have the device available, start the control server in simulator mode. That
will make the control server connect to a device software simulator:
```bash
$ tcs_cs start --sim
```
When you need to kill or stop the TCS control server, sue the stop command:
```bash
$ tcs_cs stop
```
Please note that software simulators are intended for simple test purposes and will not simulate
all device behavior correctly, e.g. timing, error conditions, etc.

"""
import logging
import multiprocessing
import sys
import time

from prometheus_client import start_http_server

multiprocessing.current_process().name = "tcs_cs"

import click
import invoke
import rich
import zmq

from egse.control import ControlServer
from egse.control import is_control_server_active
from egse.settings import Settings
from egse.tcs.tcs import TCSProxy
from egse.tcs.tcs import is_tcs_cs_active
from egse.tcs.tcs_protocol import TCSProtocol
from egse.zmq_ser import connect_address


logger = logging.getLogger(__name__)

CTRL_SETTINGS = Settings.load("TCS Control Server")


def is_tcs_cs_active(timeout: float = 2.0):
    """
    Checks whether the TCS EGSE Control Server is running.

    Args:
        timeout (float): Timeout when waiting for a reply [seconds, default=2.0]

    Returns:
        True if the TCS EGSE CS is running and replied with the expected answer.
    """

    endpoint = connect_address(
        CTRL_SETTINGS.PROTOCOL, CTRL_SETTINGS.HOSTNAME, CTRL_SETTINGS.COMMANDING_PORT
    )

    return is_control_server_active(endpoint, timeout)


class TCSControlServer(ControlServer):
    """TCSControlServer - Command and monitor the TCS EGSE hardware.

    This class works as a command and monitoring server to control the TCS EGSE.
    This control server shall be used as the single point access for controlling the hardware
    device. Monitoring access should be done preferably through this control server also.

    The sever binds to the following ZeroMQ sockets:

    * a REQ-REP socket that can be used as a command server. Any client can connect and
      send a command to the TCS EGSE.

    * a PUB-SUP socket that serves as a monitoring server. It will send out TCS EGSE status
      information to all the connected clients every TBD seconds.

    """

    def __init__(self):
        super().__init__()

        self.device_protocol = TCSProtocol(self)

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

    def get_metrics_port(self):
        return CTRL_SETTINGS.METRICS_PORT

    def get_storage_mnemonic(self):
        try:
            return CTRL_SETTINGS.STORAGE_MNEMONIC
        except AttributeError:
            return "TCS"

    def before_serve(self):
        start_http_server(CTRL_SETTINGS.CS_METRICS_PORT)


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--simulator", "--sim", is_flag=True, help="Start the TCS EGSE Simulator as the backend."
)
def start(simulator):
    """Start the TCS EGSE Control Server."""

    if simulator:
        Settings.set_simulation_mode(True)

    try:
        controller = TCSControlServer()
        controller.serve()
    except KeyboardInterrupt:
        print("Shutdown requested...exiting")
    except SystemExit as exit_code:
        print(f"System Exit with code {exit_code}.")
        sys.exit(exit_code)
    except Exception as exc:
        logger.exception(f"Cannot start the TCS EGSE Control Server: {exc}")

    time.sleep(3.0)  # Give the process and sub-process (TCSTelemetry) time to start

    return 0


@cli.command()
def start_bg():
    """Start the TCS EGSE Control Server in the background."""
    invoke.run("tcs_cs start", disown=True)


@cli.command()
def stop():
    """Send a 'quit_server' command to the TCS EGSE Control Server."""

    if not is_tcs_cs_active():
        rich.print("[red]I couldn't find the TCS Control Server, no action taken.")
        return

    with TCSProxy() as proxy:

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
        rich.print("TCS CS: [green]active")
        with TCSProxy() as tcs:
            sim = tcs.is_simulator()
            connected = tcs.is_connected()
            ip = tcs.get_ip_address()
            rich.print(f"mode: {'simulator' if sim else 'device'}"
                       f"{' not' if not connected else ''} connected")
            rich.print(f"hostname: {ip}")
    else:
        rich.print('TCS CS: [red]not active')


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG, format=Settings.LOG_FORMAT_FULL)

    sys.exit(cli())
