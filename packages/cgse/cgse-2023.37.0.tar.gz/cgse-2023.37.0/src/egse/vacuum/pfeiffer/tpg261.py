import logging

from prometheus_client import Gauge

from egse.control import ControlServer
from egse.protocol import CommandProtocol
from egse.proxy import Proxy
from egse.settings import Settings
from egse.zmq_ser import bind_address
from egse.system import format_datetime
# from egse.fdir.fdir_manager import FdirManagerProxy
from egse.vacuum.pfeiffer.tpg261_interface import Tpg261Command, Tpg261Interface
from egse.vacuum.pfeiffer.tpg261_controller import Tpg261Controller
from egse.vacuum.pfeiffer.tpg261_simulator import Tpg261Simulator
from egse.zmq_ser import connect_address

LOGGER = logging.getLogger(__name__)

DEVICE_SETTINGS = Settings.load(filename="tpg261.yaml")
CTRL_SETTINGS = Settings.load("Pfeiffer TPG261 Control Server")

class Tpg261Protocol(CommandProtocol):

    gauge_pressure_1 = Gauge('GSRON_TPG261_P_1', '')
    gauge_errors     = Gauge('GSRON_TPG261_ERR', '')
    
    def __init__(self, control_server: ControlServer):

        super().__init__()
        self.control_server = control_server

        if Settings.simulation_mode():
            self.dev = Tpg261Simulator()
        else:
            self.dev = Tpg261Controller()

        self.load_commands(DEVICE_SETTINGS.Commands, Tpg261Command, Tpg261Interface)

        self.build_device_method_lookup_table(self.dev)


    # move to parent class?
    def get_bind_address(self):
        return bind_address(
            self.control_server.get_communication_protocol(),
            self.control_server.get_commanding_port(),
        )


    def get_status(self):
        status_dict = super().get_status()

        status_dict['P1'] = self.dev.pressure_1

        return status_dict


    def get_housekeeping(self) -> dict:
        result = dict()
        result["timestamp"] = format_datetime()
        try:
            self.dev.pressure_1 = self.dev.get_gauge_pressure()
            result['GSRON_TPG261_P_1'] = self.dev.pressure_1
            result['GSRON_TPG261_ERR'] = self.dev.get_errors()
        except Exception as e:
            LOGGER.warning(f'Failed to get HK: {e}')
            return result
        
        self.gauge_pressure_1.set(result['GSRON_TPG261_P_1'])
        self.gauge_errors.set(result['GSRON_TPG261_ERR'])
        
        return result



class Tpg261Proxy(Proxy, Tpg261Interface):

    def __init__(self):
        super().__init__(
            connect_address(
                CTRL_SETTINGS.PROTOCOL, CTRL_SETTINGS.HOSTNAME, CTRL_SETTINGS.COMMANDING_PORT))
