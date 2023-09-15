#!/usr/bin/env python3
import argparse
import logging
import sys
import click

import zmq
from prometheus_client import start_http_server

import multiprocessing


from egse.control import ControlServer
from egse.settings import Settings
from egse.zmq_ser import connect_address
from egse.tempcontrol.digalox.digalox  import DigaloxInterface, DigaloxProxy
from egse.tempcontrol.digalox.digalox_protocol import DigaloxProtocol

logging.basicConfig(level=logging.DEBUG, format=Settings.LOG_FORMAT_FULL)

logger = logging.getLogger('__name__')

CTRL_SETTINGS = Settings.load("Digalox LN2 level monitor Control Server")


class DigaloxControlServer(ControlServer):

    def __init__(self):
        super().__init__()

        self.device_protocol = DigaloxProtocol(self)

        logger.debug(f'Binding ZeroMQ socket to {self.device_protocol.get_bind_address()}')

        self.device_protocol.bind(self.dev_ctrl_cmd_sock)

        self.poller.register(self.dev_ctrl_cmd_sock, zmq.POLLIN)

        self.set_hk_delay(CTRL_SETTINGS.DELAY)

    def get_communication_protocol(self):
        return CTRL_SETTINGS.PROTOCOL

    def get_commanding_port(self):
        return CTRL_SETTINGS['COMMANDING_PORT']

    def get_service_port(self):
        return CTRL_SETTINGS['SERVICE_PORT']

    def get_monitoring_port(self):
        return CTRL_SETTINGS['MONITORING_PORT']

    def get_storage_mnemonic(self):
        try:
            return CTRL_SETTINGS['STORAGE_MNEMONIC']
        except:
            return f'Digalox'

    def before_serve(self):
        start_http_server(CTRL_SETTINGS['METRICS_PORT'])


@click.group()
def cli():
    pass


@cli.command()
@click.option("--simulator", "--sim", is_flag=True, help="Start the Digalox Simulator as the backend.")
def start(simulator):
    """Start the BeagleBone Control Server."""

    if simulator:
        Settings.set_simulation_mode(True)
    try:
        logger.debug(f'Starting Digalox LN2 level monitor Control Server')
        
        multiprocessing.current_process().name = "digalox"

        control_server = DigaloxControlServer()
        control_server.serve()

    except KeyboardInterrupt:
        logger.info("Shutdown requested...exiting")

    except SystemExit as exit_code:
        logger.info("System Exit with code {}.".format(exit_code))
        sys.exit(exit_code)

    except Exception:

        logger.exception("Cannot start the Digalox LN2 level monitor Control Server")
        # The above line does exactly the same as the traceback, but on the logger
        # import traceback
        # traceback.print_exc(file=sys.stdout)

    return 0


@cli.command()
def stop(index):
    """Send a 'quit_server' command to the Control Server."""

    with DigaloxProxy(index) as proxy:

        sp = proxy.get_service_proxy()
        sp.quit_server()


if __name__ == "__main__":

    sys.exit(cli())
