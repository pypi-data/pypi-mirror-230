import logging

from prometheus_client import Gauge

from egse.control import ControlServer
from egse.protocol import CommandProtocol
from egse.settings import Settings
from egse.alert.gsm.beaglebone import BeagleboneController
from egse.alert.gsm.beaglebone import BeagleboneInterface
from egse.alert.gsm.beaglebone import BeagleboneSimulator
from egse.alert.gsm.beaglebone_devif import BeagleboneCommand
from egse.system import format_datetime
from egse.zmq_ser import bind_address

COMMAND_SETTINGS = Settings.load(filename='beaglebone.yaml')

logger = logging.getLogger(__name__)


class BeagleboneProtocol(CommandProtocol):
    def __init__(self, control_server:ControlServer):
        super().__init__()
        self.control_server = control_server

        if Settings.simulation_mode():
            self.beaglebone = BeagleboneSimulator()
        else:
            self.beaglebone = BeagleboneController()

        self.load_commands(COMMAND_SETTINGS.Commands, BeagleboneCommand, BeagleboneInterface)

        self.build_device_method_lookup_table(self.beaglebone)

    def get_bind_address(self):
        return bind_address(self.control_server.get_communication_protocol(),
                            self.control_server.get_commanding_port())

    def get_status(self):
        return super().get_status()

    def get_housekeeping(self) -> dict:

        hk_dict = {'timestamp': format_datetime()}
        
        self.beaglebone.toggle_watchdog()
        # logger.info("Send a pulse to the watchdog")

        return hk_dict
