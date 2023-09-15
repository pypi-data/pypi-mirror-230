import logging

from prometheus_client import Gauge

from egse.control import ControlServer
from egse.command import ClientServerCommand
from egse.protocol import CommandProtocol
from egse.proxy import Proxy
from egse.settings import Settings
from egse.zmq_ser import bind_address
from egse.system import format_datetime
from egse.zmq_ser import connect_address

from egse.vacuum.mks.evision_interface import EvisionInterface
from egse.vacuum.mks.evision_devif     import EvisionDriver
from egse.vacuum.mks.evision_simulator import EvisionSimulator

logger = logging.getLogger(__name__)

DEVICE_SETTINGS = Settings.load(filename="evision.yaml")
CTRL_SETTINGS = Settings.load("MKS E-Vision RGA Control Server")


class EvisionCommand(ClientServerCommand):
    pass


class EvisionProtocol(CommandProtocol):

    def __init__(self, control_server: ControlServer):

        super().__init__()
        self.control_server = control_server

        if Settings.simulation_mode():
            self.dev = EvisionSimulator()
        else:
            self.dev = EvisionDriver()

        self.load_commands(DEVICE_SETTINGS.Commands, EvisionCommand, EvisionInterface)
        self.build_device_method_lookup_table(self.dev)
        
        self.dev.control_sensor()
        self.dev.filament_status()
        self.dev.rga_status()
        
        self.massreading_gauges = [Gauge(f'GSRON_EVISION_MASSREADING_{i}', '') for i in range(0, 200)]

    # move to parent class?
    def get_bind_address(self):
        return bind_address(
            self.control_server.get_communication_protocol(),
            self.control_server.get_commanding_port(),
        )


    def get_status(self):
        status_dict = super().get_status()
        
        status_dict['ScanStatus']         = self.dev.get_scan_status()
        status_dict['RGAStatus']          = self.dev.get_rga_status()
        status_dict['FilamentStatus']     = self.dev.get_filament_status()
        status_dict['MassReading']      = self.dev.get_mass_reading()
        return status_dict


    def get_housekeeping(self) -> dict:
        result = dict()
        result["timestamp"] = format_datetime()
        
        for i in range(0, 200):
            column_name = f'GSRON_EVISION_MASSREADING_{i}'
            
            result[column_name] = self.dev.get_mass_reading()[i]
            
            self.massreading_gauges[i].set(self.dev.get_mass_reading()[i])
        
        return result


class EvisionProxy(Proxy, EvisionInterface):

    def __init__(self):
        super().__init__(
            connect_address(
                CTRL_SETTINGS.PROTOCOL, CTRL_SETTINGS.HOSTNAME, CTRL_SETTINGS.COMMANDING_PORT))
