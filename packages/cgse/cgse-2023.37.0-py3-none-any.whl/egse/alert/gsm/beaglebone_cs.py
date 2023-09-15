# Control server for the BeagleBone Black heater controller

import click
import logging
import sys

import zmq
from prometheus_client import start_http_server

from egse.control import ControlServer
from egse.settings import Settings
from egse.alert.gsm.beaglebone_protocol import BeagleboneProtocol
from egse.alert.gsm.beaglebone import BeagleboneProxy

logging.basicConfig(level=logging.DEBUG, format=Settings.LOG_FORMAT_FULL)

logger = logging.getLogger('BeagleBone GSM')

CTRL_SETTINGS = Settings.load("BeagleBone GSM Control Server")


class BeagleBoneControlServer(ControlServer):

    def __init__(self):
        super().__init__()

        self.device_protocol = BeagleboneProtocol(self)

        self.logger.debug(f'Binding ZeroMQ socket to {self.device_protocol.get_bind_address()}')

        self.device_protocol.bind(self.dev_ctrl_cmd_sock)

        self.poller.register(self.dev_ctrl_cmd_sock, zmq.POLLIN)

        self.set_hk_delay(10)


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
        except:
            return 'BB_GSM'

    def before_serve(self):
        start_http_server(CTRL_SETTINGS.METRICS_PORT)
        
    def after_serve(self):
        self.device_protocol.beaglebone.beaglebone._dev_gpio.close()


@click.group()
def cli():
    pass


@cli.command()
@click.option("--simulator", "--sim", is_flag=True, help="Start the BeagleBone Simulator as the backend.")
def start(simulator):
    """Start the BeagleBone Control Server."""

    if simulator:
        Settings.set_simulation_mode(True)
    try:
        control_server = BeagleBoneControlServer()
        control_server.serve()

    except KeyboardInterrupt:
        logger.info("Shutdown requested...exiting")

    except SystemExit as exit_code:
        logger.info("System Exit with code {}.".format(exit_code))
        sys.exit(exit_code)

    except Exception:

        logger.exception("Cannot start the BeagleBone Control Server")
        # The above line does exactly the same as the traceback, but on the logger
        # import traceback
        # traceback.print_exc(file=sys.stdout)

    return 0


@cli.command()
def stop():
    """Send a 'quit_server' command to the Control Server."""

    with BeagleboneProxy() as proxy:

        sp = proxy.get_service_proxy()
        sp.quit_server()


if __name__ == "__main__":

    sys.exit(cli())
