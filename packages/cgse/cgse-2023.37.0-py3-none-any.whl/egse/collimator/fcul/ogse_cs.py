"""
This module defines the control server for the OGSE.
"""
import logging
import multiprocessing
import sys

multiprocessing.current_process().name = "ogse_cs"

import click
import invoke
import zmq
from prometheus_client import start_http_server

from egse.collimator.fcul.ogse import OGSEProxy
from egse.collimator.fcul.ogse_protocol import OGSEProtocol
from egse.control import ControlServer
from egse.control import is_control_server_active
from egse.settings import Settings
from egse.zmq_ser import connect_address

# Use explicit name here otherwise the logger will probably be called __main__

logger = logging.getLogger("egse.collimator.fcul.ogse_cs")

CTRL_SETTINGS = Settings.load("OGSE Control Server")


class OGSEControlServer(ControlServer):
    def __init__(self):
        super().__init__()

        self.device_protocol = OGSEProtocol(self)

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
            return "OGSE"

    def before_serve(self):
        start_http_server(CTRL_SETTINGS.METRICS_PORT)


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--simulator", "--sim", is_flag=True, help="Start the OGSE Simulator as the backend."
)
def start(simulator):
    """
    Starts the OGSE Control Server (ogse_cs). The ogse_cs is a device server which handles the
    commanding of the OGSE at CSL.
    """

    if simulator:
        Settings.set_simulation_mode(True)

    try:
        control_server = OGSEControlServer()
        control_server.serve()
    except KeyboardInterrupt:
        print("Shutdown requested...exiting")
    except SystemExit as exit_code:
        print(f"System Exit with code {exit_code}.")
        sys.exit(exit_code)
    except (Exception, ) as exc:  # ignore: too broad exception clause
        logger.error(f"Caught Exception: {exc}", exc_info=True)

        # import traceback
        # traceback.print_exc(file=sys.stdout)

    return 0


@cli.command()
@click.option(
    "--simulator", "--sim", is_flag=True, help="Start the OGSE Simulator as the backend."
)
def start_bg(simulator):
    """Start the OGSE Control Server in the background."""
    sim = "--simulator" if simulator else ""
    invoke.run(f"ogse_cs start {sim}", disown=True)


@cli.command()
def stop():
    """Send a 'quit_server' command to the OGSE Control Server."""
    import rich

    if is_control_server_active(connect_address(CTRL_SETTINGS.PROTOCOL,
                                                CTRL_SETTINGS.HOSTNAME,
                                                CTRL_SETTINGS.COMMANDING_PORT)):
        with OGSEProxy() as ogse:
            sp = ogse.get_service_proxy()
            sp.quit_server()
    else:
        rich.print("[red]OGSE Control Server is not replying, check if the server is running.")


@cli.command()
def status():
    """Print the status of the control server."""

    from rich import print

    print('OGSE Control Server:')

    if is_control_server_active(connect_address(CTRL_SETTINGS.PROTOCOL,
                                                CTRL_SETTINGS.HOSTNAME,
                                                CTRL_SETTINGS.COMMANDING_PORT)):
        print('  Status: [green]active')
        with OGSEProxy() as ogse:
            try:
                print(f"  Version: {ogse.version()}")
            except AttributeError:
                print('  Version: [red]UNKNOWN')

            print(f"  Hostname: {ogse.get_ip_address()}")
            print(f"  Monitoring port: {ogse.get_monitoring_port()}")
            print(f"  Commanding port: {ogse.get_commanding_port()}")
            print(f"  Service port: {ogse.get_service_port()}")
    else:
        print('  Status: [red]not active')


if __name__ == "__main__":

    sys.exit(cli())
