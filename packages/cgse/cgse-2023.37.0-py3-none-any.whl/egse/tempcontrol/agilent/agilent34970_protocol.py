import logging

from prometheus_client import Gauge

from egse.protocol import CommandProtocol
from egse.settings import Settings
from egse.setup import get_setup
from egse.confman import ConfigurationManagerProxy
# from egse.fdir.fdir_manager import FdirManagerProxy
from egse.state import GlobalState
from egse.synoptics import SynopticsManagerProxy
from egse.tempcontrol.agilent.agilent34970 import Agilent34970Controller
from egse.tempcontrol.agilent.agilent34970 import Agilent34970Interface
from egse.tempcontrol.agilent.agilent34970 import Agilent34970Simulator
from egse.tempcontrol.agilent.agilent34970_devif import Agilent34970Command
from egse.system import format_datetime
from egse.zmq_ser import bind_address

logger = logging.getLogger(__name__)

FDIR_PREFIX = 600

COMMAND_SETTINGS = Settings.load(filename='agilent34970.yaml')

class Agilent34970Protocol(CommandProtocol):

    def __init__(self, control_server, device_index):

        super().__init__()

        self.control_server = control_server
        self.device_index = device_index

        if Settings.simulation_mode():
            self.agilent = Agilent34970Simulator()
        else:
            self.agilent = Agilent34970Controller(self.device_index)

        self.load_commands(COMMAND_SETTINGS.Commands, Agilent34970Command, Agilent34970Interface)

        self.build_device_method_lookup_table(self.agilent)

        # Get scan list from setup
        setup = GlobalState.setup

        self._setup = setup['gse'][f'agilent34970_{device_index}']
        self._conversions = self._setup['conversion']
        self.channels = []

        self.channels += self._setup.thermocouples
        self.channels += self._setup.two_wire
        self.channels += self._setup.four_wire
        self.channels.sort()

        self.resistance_gauges = [
            Gauge(f'GSRON_AG34970_{device_index}_R{channel}', '') for channel in self.channels]
        self.temperature_gauges = [
            Gauge(f'GSRON_AG34970_{device_index}_T{channel}', '') for channel in self.channels]


    def get_bind_address(self):
        return bind_address(self.control_server.get_communication_protocol(),
                            self.control_server.get_commanding_port())

    def get_status(self):
        return super().get_status()

    def get_housekeeping(self) -> dict:

        hk_dict = {'timestamp': format_datetime()}

        try:
            resistances, temperatures = self.agilent.read_resistance_temperature()
            self.agilent.trigger_scan()
        except Exception as e:
            logger.warning(f'failed to get HK ({e})')

            with SynopticsManagerProxy() as synoptics:
                synoptics.store_th_synoptics(hk_dict)

            return hk_dict

        if len(temperatures.values()) == len(self.channels) and len(resistances.values()) == len(self.channels):
            for idx, (chnl, temp) in enumerate(temperatures.items()):
                hk_dict[f'GSRON_AG34970_{self.device_index}_T{chnl}'] = temp
                self.temperature_gauges[idx].set(temp)
                
            for idx, (chnl, res) in enumerate(resistances.items()):
                hk_dict[f'GSRON_AG34970_{self.device_index}_R{chnl}'] = res
                self.resistance_gauges[idx].set(res)
        else:
            logger.warning(f'Invalid scan result')

        # Store the temperatures as synoptics

        with SynopticsManagerProxy() as synoptics:
            synoptics.store_th_synoptics(hk_dict)

        return hk_dict
