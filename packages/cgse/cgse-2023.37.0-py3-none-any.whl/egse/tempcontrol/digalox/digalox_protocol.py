import logging

from prometheus_client import Gauge

from egse.protocol import CommandProtocol
from egse.settings import Settings
from egse.setup import get_setup

from egse.system import format_datetime

from egse.tempcontrol.digalox.digalox import DigaloxController, DigaloxInterface, DigaloxSimulator, DigaloxCommand
from egse.zmq_ser import bind_address

logger = logging.getLogger(__name__)

COMMAND_SETTINGS = Settings.load(filename='digalox.yaml')


class DigaloxProtocol(CommandProtocol):
    def __init__(self, control_server):

        super().__init__()

        self.control_server = control_server
        self.cs_storage_mnemonic = self.control_server.get_storage_mnemonic()

        if Settings.simulation_mode():
            self.digalox = DigaloxSimulator()
        else:
            self.digalox = DigaloxController()

        self.load_commands(COMMAND_SETTINGS.Commands, DigaloxCommand, DigaloxInterface)

        self.build_device_method_lookup_table(self.digalox)
        
        self.ln2_gauge = Gauge('GSRON_DIGALOX_LN2_LEVEL', '')


    def get_bind_address(self):
        return bind_address(self.control_server.get_communication_protocol(),
                            self.control_server.get_commanding_port())

    def get_status(self):
        return super().get_status()


    def get_housekeeping(self) -> dict:

        hk_dict = {'timestamp': format_datetime()}

        hk_dict['GSRON_DIGALOX_LN2_LEVEL'] = self.digalox.get_value()
        
        self.ln2_gauge.set(hk_dict['GSRON_DIGALOX_LN2_LEVEL'])
        
        return hk_dict