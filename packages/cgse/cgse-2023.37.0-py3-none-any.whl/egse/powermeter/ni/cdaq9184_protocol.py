import logging
import datetime


from egse.control import ControlServer
from egse.powermeter.ni.cdaq9184 import cdaq9184Controller, cdaq9184Simulator, cdaq9184Interface
from egse.powermeter.ni.cdaq9184_devif import cdaq9184Command

from egse.protocol import CommandProtocol
from egse.device import DeviceConnectionState
from egse.settings import Settings
from egse.system import format_datetime
from egse.zmq_ser import bind_address

COMMAND_SETTINGS = Settings.load(filename="cdaq9184.yaml")
logger = logging.getLogger(__name__)



class cdaq9184Protocol(CommandProtocol):
    def __init__(self, control_server: ControlServer):
        super().__init__()
        self.control_server = control_server

        if Settings.simulation_mode():
            self.cdaq = cdaq9184Simulator()
        else:
            self.cdaq = cdaq9184Controller()

        self.load_commands(
            COMMAND_SETTINGS.Commands, cdaq9184Command, cdaq9184Interface
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