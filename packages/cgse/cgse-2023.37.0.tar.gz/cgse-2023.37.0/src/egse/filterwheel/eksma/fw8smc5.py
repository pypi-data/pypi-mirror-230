import logging

from prometheus_client import Gauge

from egse.control import ControlServer
from egse.protocol import CommandProtocol
from egse.command import ClientServerCommand
from egse.proxy import Proxy
from egse.settings import Settings
from egse.state import GlobalState
from egse.synoptics import SynopticsManagerProxy
from egse.zmq_ser import bind_address
from egse.system import format_datetime
from egse.filterwheel.eksma.fw8smc5_interface import Fw8Smc5Interface
from egse.filterwheel.eksma.fw8smc5_controller import Fw8Smc5Controller
from egse.filterwheel.eksma.fw8smc5_simulator import Fw8Smc5Simulator
from egse.zmq_ser import connect_address

logger = logging.getLogger(__name__)

FDIR_PREFIX = 400

DEVICE_SETTINGS = Settings.load(filename="fw8smc5.yaml")
CTRL_SETTINGS = Settings.load("Standa 8SMC5 Control Server")

gauge_position_0 = Gauge('GSRON_FW8SMC5_POS_0', 'wheel 0 position in encoder steps')
gauge_position_1 = Gauge('GSRON_FW8SMC5_POS_1', 'wheel 1 position in encoder steps')
gauge_relative_intensity = Gauge('GSRON_FW8SMC5_RI', 'filter attenuation as relative index')
gauge_fwc_fraction = Gauge('GSRON_FW8SMC5_FWC_FRACTION', 'FWC fraction')


class Fw8Smc5Command(ClientServerCommand):
    pass


class Fw8Smc5Protocol(CommandProtocol):

    def __init__(self, control_server: ControlServer):

        super().__init__()
        self.control_server = control_server

        self.fwc_calibration = GlobalState.setup.gse.ogse.calibration.fwc_calibration

        if Settings.simulation_mode():
            self.dev = Fw8Smc5Simulator()
        else:
            self.dev = Fw8Smc5Controller()

        self.load_commands(DEVICE_SETTINGS.Commands, Fw8Smc5Command, Fw8Smc5Interface)
        self.build_device_method_lookup_table(self.dev)

        self.synoptics = SynopticsManagerProxy()


    # move to parent class?
    def get_bind_address(self):
        return bind_address(
            self.control_server.get_communication_protocol(),
            self.control_server.get_commanding_port(),
        )


    def get_status(self):
        status_dict = super().get_status()
        status = {
            'RelativeIntensity': self.dev.get_relative_intensity(),
            'FullWellCapacity': self.dev.get_relative_intensity() / self.fwc_calibration,
            'FW1Position' : self.dev.get_position_steps(0),
            'FW2Position' : self.dev.get_position_steps(1)
        }
        status_dict['fw8smc5_status'] = status
        # need to get the channel from somewhere
        # status_dict['device_status'] = self.dev.get_status(channel)

        return status_dict


    def get_housekeeping(self) -> dict:
        result = dict()
        result["timestamp"] = format_datetime()

        try:
            result["GSRON_FW8SMC5_RI"] = self.dev.get_relative_intensity()
            result["GSRON_FW8SMC5_FWC_FRACTION"] = result["GSRON_FW8SMC5_RI"] / self.fwc_calibration
            # TODO Include FWC fraction in result

            # Send the HK acquired so far to the Synoptics Manager
            self.synoptics.store_th_synoptics(result)

            result["GSRON_FW8SMC5_POS_0"] = self.dev.get_position_steps(0)
            result["GSRON_FW8SMC5_POS_1"] = self.dev.get_position_steps(1)

        except Exception as exc:
            logger.warning(f'failed to get HK ({exc})')
            return result

        gauge_position_0.set(result[f"GSRON_FW8SMC5_POS_0"])
        gauge_position_1.set(result[f"GSRON_FW8SMC5_POS_1"])
        gauge_relative_intensity.set(result[f"GSRON_FW8SMC5_RI"])
        gauge_fwc_fraction.set(result["GSRON_FW8SMC5_FWC_FRACTION"])

        return result


class Fw8Smc5Proxy(Proxy, Fw8Smc5Interface):

    def __init__(self):
        super().__init__(
            connect_address(
                CTRL_SETTINGS.PROTOCOL, CTRL_SETTINGS.HOSTNAME, CTRL_SETTINGS.COMMANDING_PORT))
