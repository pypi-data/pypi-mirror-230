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
from egse.vacuum.keller.leo3_interface import Leo3Interface
from egse.vacuum.keller.leo3_controller import Leo3Controller
from egse.vacuum.keller.leo3_controller import Leo3Simulator
from egse.zmq_ser import connect_address


LOGGER = logging.getLogger(__name__)

CTRL_SETTINGS = Settings.load("KELLER Leo3 Control Server")
DEVICE_SETTINGS = Settings.load(filename="leo3.yaml")

class Leo3Command(ClientServerCommand):
    pass


class Leo3Protocol(CommandProtocol):

    def __init__(self, control_server: ControlServer):

        super().__init__()
        self.control_server = control_server

        if Settings.simulation_mode():
            self.dev = Leo3Simulator()
        else:
            self.dev = Leo3Controller()

        self.load_commands(DEVICE_SETTINGS.Commands, Leo3Command, Leo3Interface)
        self.build_device_method_lookup_table(self.dev)

        self.addresses = [1, 2, 3, 4, 5, 6]

        self.gauge_pressures         = []
        self.gauge_temperatures      = []
        self.gauge_status             = []
        
        self.invalid_result = [False] * 6
        
        for address in self.addresses:
            self.gauge_pressures      += [Gauge(f'GSRON_LEO3_{address}_P', '')]
            self.gauge_temperatures   += [Gauge(f'GSRON_LEO3_{address}_T', '')]
            self.gauge_status          += [Gauge(f'GSRON_LEO3_{address}_STAT', '')]
            try:
                self.dev.initialize(address)
            except Exception as exc:
                LOGGER.info(f"Could not initialize kellerBus {address}: {exc}")
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
        
        for idx, address in enumerate(self.addresses):
            try:
                result[f"GSRON_LEO3_{address}_P"], _ = self.dev.get_pressure(address)
                result[f"GSRON_LEO3_{address}_T"], result[f'GSRON_LEO3_{address}_STAT'] = self.dev.get_temperature(address)            
            except Exception as exc:
                result[f"GSRON_LEO3_{address}_P"]    = 0
                result[f"GSRON_LEO3_{address}_T"], result[f"GSRON_LEO3_{address}_STAT"] = 0, 0

                if not self.invalid_result[idx]:
                    self.invalid_result[idx] = True
                    LOGGER.warning(f"Unable to get HK for KellerBus {address}: {exc}")
            else:
                self.invalid_result[idx] = False
            finally:
                self.gauge_pressures[idx].set(result[f"GSRON_LEO3_{address}_P"])
                self.gauge_temperatures[idx].set(result[f"GSRON_LEO3_{address}_T"])
                self.gauge_status[idx].set(result[f'GSRON_LEO3_{address}_STAT'])
            
        return result


class Leo3Proxy(Proxy, Leo3Interface):
    def __init__(self):
        super().__init__(
            connect_address(
                CTRL_SETTINGS.PROTOCOL, CTRL_SETTINGS.HOSTNAME, CTRL_SETTINGS.COMMANDING_PORT))
