import logging

from prometheus_client import Gauge

from egse.control import ControlServer
from egse.protocol import CommandProtocol
from egse.proxy import Proxy
from egse.settings import Settings
from egse.zmq_ser import bind_address
from egse.system import format_datetime
# from egse.fdir.fdir_manager import FdirManagerProxy
from egse.vacuum.pfeiffer.tc400_interface import Tc400Command, Tc400Interface
from egse.vacuum.pfeiffer.tc400_controller import Tc400Controller
from egse.vacuum.pfeiffer.tc400_simulator import Tc400Simulator
from egse.zmq_ser import connect_address

LOGGER = logging.getLogger(__name__)

DEVICE_SETTINGS = Settings.load(filename="tc400.yaml")
CTRL_SETTINGS = Settings.load("Pfeiffer TC400 Control Server")

gauge_active_speed = Gauge('GSRON_TC400_ACT_SPEED', 'active pump speed')
gauge_drive_power = Gauge('GSRON_TC400_POWER', 'pump power')
gauge_motor_temperature = Gauge('GSRON_TC400_MOTOR_TEMP', 'motor temperature')
gauge_last_error = Gauge('GSRON_TC400_LAST_ERROR', 'last encountered error')


class Tc400Protocol(CommandProtocol):

    def __init__(self, control_server: ControlServer):

        super().__init__()
        self.control_server = control_server

        if Settings.simulation_mode():
            self.dev = Tc400Simulator()
        else:
            self.dev = Tc400Controller()

        self.load_commands(DEVICE_SETTINGS.Commands, Tc400Command, Tc400Interface)

        self.build_device_method_lookup_table(self.dev)


    # move to parent class?
    def get_bind_address(self):
        return bind_address(
            self.control_server.get_communication_protocol(),
            self.control_server.get_commanding_port(),
        )


    def get_status(self):
        status_dict = super().get_status()

        # need to get the channel from somewhere
        # status_dict['device_status'] = self.dev.get_status(channel)

        return status_dict


    def get_housekeeping(self) -> dict:
        result = dict()
        prev_err = None
        result["timestamp"] = format_datetime()

        try:
            result[f"GSRON_TC400_LAST_ERROR"] = self.dev.get_last_error()
            result[f"GSRON_TC400_ACT_SPEED"] = self.dev.get_active_speed()
            result[f"GSRON_TC400_POWER"] = self.dev.get_drive_power()
            result[f"GSRON_TC400_MOTOR_TEMP"] = self.dev.get_motor_temperature()
        except Exception as e:
            LOGGER.warning(f'failed to get HK ({e})')

            # with FdirManagerProxy() as fdir:
            #     fdir_code = 100010
            #     fdir.signal_fdir(fdir_code)
            #     LOGGER.warning(f'asserted fdir signal: {fdir_code}')

            return result

        # if prev_err is not result[f"G{SITE_ID}_TC400_LAST_ERROR"]:
        #     LOGGER.info(f"Device has raised an error flag: {result[f"G{SITE_ID}_TC400_LAST_ERROR"]}")
        #     with FdirManagerProxy() as fdir:
        #         fdir_code = 1010
        #         fdir.signal_fdir(fdir_code)
        #         LOGGER.warning(f'asserted fdir signal: {fdir_code}')

        prev_err = result['GSRON_TC400_LAST_ERROR']

        gauge_active_speed.set(result[f"GSRON_TC400_ACT_SPEED"])
        gauge_drive_power.set(result[f"GSRON_TC400_POWER"])
        gauge_motor_temperature.set(result[f"GSRON_TC400_MOTOR_TEMP"])
        gauge_last_error.set(result[f'GSRON_TC400_LAST_ERROR'])

        return result


class Tc400Proxy(Proxy, Tc400Interface):

    def __init__(self):
        super().__init__(
            connect_address(
                CTRL_SETTINGS.PROTOCOL, CTRL_SETTINGS.HOSTNAME, CTRL_SETTINGS.COMMANDING_PORT))

    def connect_cs(self):
        try:
            super().connect_cs()
        except Exception:
            with FdirManagerProxy() as fdir:
                fdir_code = 10010
                fdir.signal_fdir(fdir_code)
                LOGGER.warning(f'asserted fdir signal: {fdir_code}')
