import logging

from prometheus_client import Gauge

from egse.control import ControlServer
from egse.command import ClientServerCommand
from egse.protocol import CommandProtocol
from egse.proxy import Proxy
from egse.settings import Settings
from egse.zmq_ser import bind_address
from egse.system import format_datetime
from egse.vacuum.pfeiffer.acp40_interface import Acp40Interface
from egse.vacuum.pfeiffer.acp40_controller import Acp40Controller
from egse.vacuum.pfeiffer.acp40_simulator import Acp40Simulator
from egse.zmq_ser import connect_address
from egse.serialdevice import SerialTimeoutException, SerialException
logger = logging.getLogger(__name__)

DEVICE_SETTINGS = Settings.load(filename="acp40.yaml")
CTRL_SETTINGS = Settings.load("Pfeiffer ACP40 Control Server")
SITE_ID = Settings.load("SITE").ID

gauge_status = Gauge('GSRON_ACP40_STATUS', 'device status word')
gauge_faults = Gauge('GSRON_ACP40_FAULTS', 'device faults word')


class Acp40Command(ClientServerCommand):
    pass


class Acp40Protocol(CommandProtocol):

    def __init__(self, control_server: ControlServer):

        super().__init__()
        self.control_server = control_server

        if Settings.simulation_mode():
            self.dev = Acp40Simulator()
        else:
            self.dev = Acp40Controller()

        self.load_commands(DEVICE_SETTINGS.Commands, Acp40Command, Acp40Interface)
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
        result["timestamp"] = format_datetime()
        
        try:
            status_list = self.dev.get_device_status().split(',')

            result[f"GSRON_ACP40_STATUS"] = status_list[0]
            result[f"GSRON_ACP40_FAULTS"] = status_list[1]

            gauge_status.set(result[f"GSRON_ACP40_STATUS"])
            gauge_faults.set(result[f"GSRON_ACP40_FAULTS"])
        except Exception as e:
            logger.warning(f"An exception was raised by the serial device: {e}")
            self.dev.reconnect()
        return result


class Acp40Proxy(Proxy, Acp40Interface):

    def __init__(self):
        super().__init__(
            connect_address(
                CTRL_SETTINGS.PROTOCOL, CTRL_SETTINGS.HOSTNAME, CTRL_SETTINGS.COMMANDING_PORT))
