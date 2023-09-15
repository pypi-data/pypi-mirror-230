import logging

from prometheus_client import Gauge

from egse.control import ControlServer
from egse.command import ClientServerCommand
from egse.protocol import CommandProtocol
from egse.proxy import Proxy
from egse.settings import Settings
from egse.synoptics import SynopticsManagerProxy
from egse.zmq_ser import bind_address
from egse.system import format_datetime
from egse.shutter.thorlabs.sc10_interface import Sc10Interface
from egse.shutter.thorlabs.sc10_controller import Sc10Controller
from egse.shutter.thorlabs.sc10_simulator import Sc10Simulator
from egse.zmq_ser import connect_address


LOGGER = logging.getLogger(__name__)

DEVICE_SETTINGS = Settings.load(filename="sc10.yaml")
CTRL_SETTINGS = Settings.load("Thorlabs SC10 Control Server")

SITE_ID = Settings.load("SITE").ID

gauge_enable = Gauge(f'G{SITE_ID}_SC10_ENABLE', '')


class Sc10Command(ClientServerCommand):
    pass


class Sc10Protocol(CommandProtocol):

    def __init__(self, control_server: ControlServer):

        super().__init__()
        self.control_server = control_server

        if Settings.simulation_mode():
            self.dev = Sc10Simulator()
        else:
            self.dev = Sc10Controller()

        self.load_commands(DEVICE_SETTINGS.Commands, Sc10Command, Sc10Interface)
        self.build_device_method_lookup_table(self.dev)


    # move to parent class?
    def get_bind_address(self):
        return bind_address(
            self.control_server.get_communication_protocol(),
            self.control_server.get_commanding_port(),
        )


    def get_status(self):
        status_dict = super().get_status()
        status_dict['shutter_state'] = self.dev.get_enable()
        return status_dict

    def get_housekeeping(self) -> dict:

        result = dict()
        result["timestamp"] = format_datetime()

        result[f"G{SITE_ID}_SC10_ENABLE"] = self.dev.get_enable()

        with SynopticsManagerProxy() as synoptics:
            synoptics.store_th_synoptics(result)

        gauge_enable.set(result[f"G{SITE_ID}_SC10_ENABLE"])

        return result


class Sc10Proxy(Proxy, Sc10Interface):

    def __init__(self):
        super().__init__(
            connect_address(
                CTRL_SETTINGS.PROTOCOL, CTRL_SETTINGS.HOSTNAME, CTRL_SETTINGS.COMMANDING_PORT))
