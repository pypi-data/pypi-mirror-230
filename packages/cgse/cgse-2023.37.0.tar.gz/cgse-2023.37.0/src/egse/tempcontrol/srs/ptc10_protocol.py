from egse.control import ControlServer
# from egse.metrics import define_metrics
from egse.synoptics import SynopticsManagerProxy
from egse.tempcontrol.srs.ptc10 import ptc10Controller, ptc10Simulator, ptc10Interface
from egse.tempcontrol.srs.ptc10_devif import ptc10Command

from egse.protocol import CommandProtocol
from egse.settings import Settings
from egse.system import format_datetime
from egse.zmq_ser import bind_address

COMMAND_SETTINGS = Settings.load(filename="ptc10.yaml")


class ptc10Protocol(CommandProtocol):
    def __init__(self, control_server: ControlServer):
        super().__init__()
        self.control_server = control_server

        if Settings.simulation_mode():
            self.temp = ptc10Simulator()
        else:
            self.temp = ptc10Controller()

        self.load_commands(
            COMMAND_SETTINGS.Commands, ptc10Command, ptc10Interface
        )

        self.build_device_method_lookup_table(self.temp)

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
