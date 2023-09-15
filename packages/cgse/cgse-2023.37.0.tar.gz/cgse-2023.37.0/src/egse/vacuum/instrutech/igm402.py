import logging

from prometheus_client import Gauge

from egse.control import ControlServer
from egse.command import ClientServerCommand
from egse.protocol import CommandProtocol
from egse.proxy import Proxy
from egse.settings import Settings
from egse.setup import get_setup
from egse.zmq_ser import bind_address
from egse.system import format_datetime
from egse.vacuum.instrutech.igm402_interface import Igm402Interface
from egse.vacuum.instrutech.igm402_controller import Igm402Controller
from egse.vacuum.instrutech.igm402_simulator import Igm402Simulator
from egse.zmq_ser import connect_address


LOGGER = logging.getLogger(__name__)

CTRL_SETTINGS = Settings.load("InstruTech IGM402 Control Server")
DEVICE_SETTINGS = Settings.load(filename="igm402.yaml")


gauge_ion_gauge_pressure = Gauge('GSRON_IGM402_IG_P', '')
gauge_cg_pressure_1 = Gauge('GSRON_IGM402_CG_P_1', '')
gauge_cg_pressure_2 = Gauge('GSRON_IGM402_CG_P_2', '')


class Igm402Command(ClientServerCommand):
    pass


class Igm402Protocol(CommandProtocol):

    def __init__(self, control_server: ControlServer):

        super().__init__()
        self.control_server = control_server

        if Settings.simulation_mode():
            self.dev = Igm402Simulator()
        else:
            self.dev = Igm402Controller()

        self.load_commands(DEVICE_SETTINGS.Commands, Igm402Command, Igm402Interface)
        self.build_device_method_lookup_table(self.dev)

        # Get calibration from setup
        self.setup = get_setup()


    # move to parent class?
    def get_bind_address(self):
        return bind_address(
            self.control_server.get_communication_protocol(),
            self.control_server.get_commanding_port(),
        )


    def get_status(self):
        status_dict = super().get_status()

        return status_dict


    def get_housekeeping(self) -> dict:
        result = dict()
        result["timestamp"] = format_datetime()
        result["GSRON_IGM402_IG_P"] = self.dev.get_ion_gauge_pressure()
        result["GSRON_IGM402_CG_P_1"] = self.dev.get_cgn_pressure(1)
        result["GSRON_IGM402_CG_P_2"] = self.dev.get_cgn_pressure(2)

        gauge_ion_gauge_pressure.set(result["GSRON_IGM402_IG_P"])
        gauge_cg_pressure_1.set(result["GSRON_IGM402_CG_P_1"])
        gauge_cg_pressure_2.set(result["GSRON_IGM402_CG_P_2"])

        # Select the IG current based on the pressure
        if result["GSRON_IGM402_IG_P"] < self.setup.gse.igm402.calibration.enable_4ma_pressure:
            self.dev.set_emission_current(1) # Set to 4ma.
        else:
            self.dev.set_emission_current(0) # Set to 100uA.

        return result


class Igm402Proxy(Proxy, Igm402Interface):

    def __init__(self):
        super().__init__(
            connect_address(
                CTRL_SETTINGS.PROTOCOL, CTRL_SETTINGS.HOSTNAME, CTRL_SETTINGS.COMMANDING_PORT))
