import logging

from prometheus_client import Gauge

from egse.control import ControlServer
from egse.command import ClientServerCommand
from egse.protocol import CommandProtocol
# from egse.fdir.fdir_manager import FdirManagerProxy
from egse.proxy import Proxy
from egse.settings import Settings
from egse.zmq_ser import bind_address
from egse.system import format_datetime
from egse.stages.arun.smd3_interface import Smd3Interface
from egse.stages.arun.smd3_controller import Smd3Controller, EFLAGS, SFLAGS
from egse.stages.arun.smd3_simulator import Smd3Simulator
from egse.zmq_ser import connect_address

logger = logging.getLogger(__name__)

FDIR_PREFIX = 200

DEVICE_SETTINGS = Settings.load(filename="smd3.yaml")
CTRL_SETTINGS = Settings.load("Arun SMD3 Control Server")
SITE_ID = Settings.load("SITE").ID


class Smd3Command(ClientServerCommand):
    pass


class Smd3Protocol(CommandProtocol):

    def __init__(self, control_server: ControlServer):

        super().__init__()
        self.control_server = control_server

        if Settings.simulation_mode():
            self.dev = Smd3Simulator()
        else:
            self.dev = Smd3Controller()

        self.gauge_absolute_position_steps   = Gauge('GSRON_SMD3_ABS_POS_STEPS', '')
        self.gauge_absolute_position_mm      = Gauge('GSRON_SMD3_ABS_POS_MM', '')
        self.gauge_motor_temperature         = Gauge('GSRON_SMD3_MOTOR_TEMP', '')
        self.gauge_mask_in_fov               = Gauge("GSRON_SMD3_MASK_IN_FOV", '')
        self.gauge_status = []
        self.gauge_errors = []

        for _, x in enumerate(EFLAGS):
            self.gauge_errors.append(Gauge(f'GSRON_SMD3_E_{EFLAGS[x]}', ''))

        for _, x in enumerate(SFLAGS):
            self.gauge_status.append(Gauge(f'GSRON_SMD3_S_{SFLAGS[x]}', ''))
                
        
        self.load_commands(DEVICE_SETTINGS.Commands, Smd3Command, Smd3Interface)
        self.build_device_method_lookup_table(self.dev)


    # move to parent class?
    def get_bind_address(self):
        return bind_address(
            self.control_server.get_communication_protocol(),
            self.control_server.get_commanding_port(),
        )


    def get_status(self):
        status_dict = super().get_status()
        status_dict['hartmann_status'] = self.dev.mask_in_fov()
        return status_dict


    def get_housekeeping(self) -> dict:
        result = dict()
        result["timestamp"] = format_datetime()

        # get values from device
        try:
            _, _, result["GSRON_SMD3_ABS_POS_STEPS"]    = self.dev.actual_position()
            result["GSRON_SMD3_ABS_POS_MM"]             = self.dev.actual_position_mm()
            result["GSRON_SMD3_STATUS"], \
            result["GSRON_SMD3_ERRORS"], \
            result["GSRON_SMD3_MOTOR_TEMP"]             = self.dev.get_temperature()
            result['GSRON_SMD3_MASK_IN_FOV']            = self.dev.mask_in_fov()
        except Exception as exc:
            logger.warning(f'failed to get HK ({exc})')
            return result

        for y, x in enumerate(EFLAGS):
            self.gauge_errors[y].set((int(result["GSRON_SMD3_ERRORS"], 0) >> x) & 0b1)

        for y, x in enumerate(SFLAGS):
            self.gauge_status[y].set((int(result["GSRON_SMD3_STATUS"], 0) >> x) & 0b1)

        # update prometheus
        self.gauge_absolute_position_steps.set(result["GSRON_SMD3_ABS_POS_STEPS"])
        self.gauge_absolute_position_mm.set(result["GSRON_SMD3_ABS_POS_MM"])
        self.gauge_motor_temperature.set(result["GSRON_SMD3_MOTOR_TEMP"])
        self.gauge_mask_in_fov.set(result['GSRON_SMD3_MASK_IN_FOV'])

        return result


class Smd3Proxy(Proxy, Smd3Interface):

    def __init__(self):
        super().__init__(
            connect_address(
                CTRL_SETTINGS.PROTOCOL, CTRL_SETTINGS.HOSTNAME, CTRL_SETTINGS.COMMANDING_PORT))
