import logging
import datetime


from egse.control import ControlServer
from egse.ni.alarms.cdaq9375 import cdaq9375Controller, cdaq9375Simulator, cdaq9375Interface
from egse.ni.alarms.cdaq9375_devif import cdaq9375Command

from egse.protocol import CommandProtocol
from egse.device import DeviceConnectionState
from egse.settings import Settings
from egse.system import format_datetime
from egse.zmq_ser import bind_address

COMMAND_SETTINGS = Settings.load(filename="cdaq9375.yaml")
logger = logging.getLogger(__name__)



class cdaq9375Protocol(CommandProtocol):
    def __init__(self, control_server: ControlServer):
        super().__init__()
        self.control_server = control_server

        if Settings.simulation_mode():
            self.cdaq = cdaq9375Simulator()
        else:
            self.cdaq = cdaq9375Controller()

        self.load_commands(
            COMMAND_SETTINGS.Commands, cdaq9375Command, cdaq9375Interface
        )

        self.build_device_method_lookup_table(self.cdaq)

    def get_bind_address(self):
        return bind_address(
            self.control_server.get_communication_protocol(),
            self.control_server.get_commanding_port(),
        )

    def get_status(self):
        return super().get_status()

    def get_housekeeping(self) -> dict:

        result = dict()
        return result