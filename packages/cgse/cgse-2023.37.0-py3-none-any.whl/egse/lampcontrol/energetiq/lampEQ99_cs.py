
import click
import logging
import sys
import zmq

from egse.control import ControlServer
from egse.settings import Settings
from egse.lampcontrol.energetiq.lampEQ99 import LampEQ99Proxy
from egse.lampcontrol.energetiq.lampEQ99_protocol import LampEQ99Protocol
from prometheus_client import start_http_server


logger = logging.getLogger(__name__)

# Restrict the logging output for the following loggers.

# Note that, in production, the logging level for the different loggers can be changed with a
# service command `set_logging_level(logger_name, level)`.

logger_levels = [
    ("egse.protocol", logging.INFO),
    ("egse.command", logging.INFO),
    ("egse.settings", logging.INFO),
]

for name, level in logger_levels:
    logger = logging.getLogger(name)
    logger.setLevel(level)

CTRL_SETTINGS = Settings.load("Lamp EQ99 Control Server")


class LampControlServer(ControlServer):
    """
    LampControlServer - Command and monitor the Lamp EQ99 Controllers.
    This class works as a command and monitoring server to control the Lamp Controller remotely.
    The sever binds to the following ZeroMQ sockets:
    * a REQ-REP socket that can be used as a command server. Any client can connect and
      send a command to the Lamp controller.
    * a PUB-SUP socket that serves as a monitoring server. It will send out Lamp status
      information to all the connected clients every DELAY seconds.
    """

    def __init__(self):
        super().__init__()

        self.device_protocol = LampEQ99Protocol(self)

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
            return "EQ99"

    def before_serve(self):
        start_http_server(CTRL_SETTINGS.METRICS_PORT)

@click.group()
def cli():
    pass


@cli.command()
@click.option("--simulator", "--sim", is_flag=True, help="Start the EQ99 Lamp Simulator as the backend.")
def start(simulator):
    """Start the EQ99 Lamp Control Server."""

    if simulator:

        Settings.set_simulation_mode(True)

    try:

        controller = LampControlServer()
        controller.serve()

    except KeyboardInterrupt:

        print("Shutdown requested...exiting")

    except SystemExit as exit_code:

        print("System Exit with code {}.".format(exit_code))
        sys.exit(exit_code)

    except Exception:

        logger.exception("Cannot start the EQ99 Lamp Control Server")

        # The above line does exactly the same as the traceback, but on the logger
        # import traceback
        # traceback.print_exc(file=sys.stdout)

    return 0


@cli.command()
def stop():
    """Send a 'quit_server' command to the EQ99 Lamp Control Server."""

    with LampEQ99Proxy() as proxy:

        sp = proxy.get_service_proxy()
        sp.quit_server()


if __name__ == "__main__":

    sys.exit(cli())
