"""
This module provides dummy implementation for classes of the Commanding chain.
"""
import logging
import sys

import click
import zmq

from egse.control import ControlServer
from egse.device import DeviceTransport
from egse.mixin import DynamicCommandMixin
from egse.mixin import dynamic_command
from egse.protocol import DynamicCommandProtocol
from egse.proxy import DynamicProxy
from egse.settings import Settings
from egse.system import AttributeDict
from egse.system import format_datetime
from egse.zmq_ser import bind_address
from egse.zmq_ser import connect_address

logging.basicConfig(level=logging.DEBUG, format=Settings.LOG_FORMAT_FULL)
logger = logging.getLogger("egse.dyndummy")

# We use AttributeDict here to define the settings, because that is how the Settings.load() returns
# settings loaded from a YAML file.

ctrl_settings = AttributeDict(
    {
        'HOSTNAME': 'localhost',
        'COMMANDING_PORT': 5553,
        'SERVICE_PORT': 5554,
        'MONITORING_PORT': 5555,
        'PROTOCOL': 'tcp'
    }
)


class DummyDeviceInterface(DeviceTransport):
    def __init__(self):
        self._read_counter = 0
        self._write_counter = 0
        self._trans_counter = 0

    def read(self) -> bytes:
        self._read_counter += 1
        logger.info(f"executing read() – [read count = {self._read_counter}]")
        return f"read count = {self._read_counter}".encode()

    def trans(self, command: str) -> bytes:
        self._trans_counter += 1
        logger.info(f"executing trans('{command}') – [trans count = {self._trans_counter}]")

        self.write(command)
        self.read()

        return f"trans count = {self._trans_counter}".encode()

    def write(self, command: str):
        self._write_counter += 1
        logger.info(f"executing write('{command}') – [write count = {self._write_counter}]")


class DummyInterface:
    @dynamic_command(cmd_type="query", cmd_string="INFO?")
    def info(self) -> str:
        """Return an info string from the device."""
        raise NotImplementedError

    @dynamic_command(cmd_type='transaction', cmd_string="RESPONSE:${msg}")
    def response(self, msg: str) -> str:
        """Return a response to the message sent."""
        raise NotImplementedError


class DummyController(DummyInterface, DynamicCommandMixin):
    def __init__(self):
        self.transport = DummyDeviceInterface()
        super().__init__()


class DummyProtocol(DynamicCommandProtocol):

    def __init__(self, control_server: ControlServer):
        super().__init__(control_server)
        self.control_server = control_server

        self.device_controller = DummyController()

    def get_device(self):
        return self.device_controller

    def get_bind_address(self):
        return bind_address(self.control_server.get_communication_protocol(), self.control_server.get_commanding_port())

    def get_status(self):
        return super().get_status()

    def get_housekeeping(self) -> dict:
        return {
            'timestamp': format_datetime(),
        }


class DummyControlServer(ControlServer):
    """
    DummyControlServer - Command and monitor dummy device controllers.

    The sever binds to the following ZeroMQ sockets:

    * a REQ-REP socket that can be used as a command server. Any client can connect and
      send a command to the dummy device controller.

    * a PUB-SUP socket that serves as a monitoring server. It will send out status
      information to all the connected clients every DELAY seconds.

    """

    def __init__(self):
        super().__init__()

        self.device_protocol = DummyProtocol(self)

        self.logger.info(f"Binding ZeroMQ socket to {self.device_protocol.get_bind_address()}")

        self.device_protocol.bind(self.dev_ctrl_cmd_sock)

        self.poller.register(self.dev_ctrl_cmd_sock, zmq.POLLIN)

    def get_communication_protocol(self):
        return 'tcp'

    def get_commanding_port(self):
        return ctrl_settings.COMMANDING_PORT

    def get_service_port(self):
        return ctrl_settings.SERVICE_PORT

    def get_monitoring_port(self):
        return ctrl_settings.MONITORING_PORT


class DummyProxy(DynamicProxy, DummyInterface):
    def __init__(self,
                 protocol=ctrl_settings.PROTOCOL, hostname=ctrl_settings.HOSTNAME, port=ctrl_settings.COMMANDING_PORT):
        """
        Args:
            protocol: the transport protocol [default is taken from settings file]
            hostname: location of the control server (IP address) [default is taken from settings file]
            port: TCP port on which the control server is listening for commands [default is taken from settings file]
        """
        super().__init__(connect_address(protocol, hostname, port))


@click.group()
def cli():
    pass


@cli.command()
def control_server():
    """Start the dummy control server on localhost."""
    from egse.dyndummy import DummyControlServer

    try:
        control_server = DummyControlServer()
        control_server.serve()
    except KeyboardInterrupt:
        print("Shutdown requested...exiting")
    except SystemExit as exit_code:
        print(f"System Exit with code ({exit_code})")
        sys.exit(exit_code)
    except Exception:
        import traceback
        traceback.print_exc(file=sys.stdout)


if __name__ == "__main__":
    cli()
