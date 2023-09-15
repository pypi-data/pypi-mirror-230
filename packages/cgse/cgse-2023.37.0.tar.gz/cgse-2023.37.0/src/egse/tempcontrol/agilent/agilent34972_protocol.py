import logging

from prometheus_client import Gauge

from egse.confman import ConfigurationManagerProxy
# from egse.fdir.fdir_manager import FdirManagerProxy
from egse.protocol import CommandProtocol
from egse.settings import Settings
from egse.setup import get_setup
from egse.synoptics import SynopticsManagerProxy
from egse.system import format_datetime
from egse.tempcontrol.agilent.agilent34972 import Agilent34972Controller
from egse.tempcontrol.agilent.agilent34972 import Agilent34972Interface
from egse.tempcontrol.agilent.agilent34972 import Agilent34972Simulator
from egse.tempcontrol.agilent.agilent34972_devif import Agilent34972Command
from egse.zmq_ser import bind_address
from egse.synoptics import SynopticsManagerProxy

logger = logging.getLogger(__name__)

FDIR_PREFIX = 600

COMMAND_SETTINGS = Settings.load(filename='agilent34972.yaml')


class Agilent34972Protocol(CommandProtocol):
    def __init__(self, control_server, device_index):

        super().__init__()

        self.control_server = control_server
        self.cs_storage_mnemonic = self.control_server.get_storage_mnemonic()
        self.device_index = device_index

        if Settings.simulation_mode():
            self.agilent = Agilent34972Simulator()
        else:
            self.agilent = Agilent34972Controller(self.device_index)

        self.load_commands(COMMAND_SETTINGS.Commands, Agilent34972Command, Agilent34972Interface)

        self.build_device_method_lookup_table(self.agilent)

        # Get scan list from setup
        setup = get_setup()

        self._setup = setup['gse'][f'agilent34972_{device_index}']
        self._conversions = self._setup['conversion']
        self.channels = []

        self.channels += self._setup.thermocouples
        self.channels += self._setup.two_wire
        self.channels += self._setup.four_wire
        self.channels.sort()

        self.resistance_gauges = [
            Gauge(f'GSRON_AG34972_{self.device_index}_R{channel}', '') for channel in self.channels]
        self.temperature_gauges = [
            Gauge(f'GSRON_AG34972_{self.device_index}_T{channel}', '') for channel in self.channels]


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
                hk_dict[f'GSRON_AG34972_{self.device_index}_T{chnl}'] = temp
                self.temperature_gauges[idx].set(temp)
                
            for idx, (chnl, res) in enumerate(resistances.items()):
                hk_dict[f'GSRON_AG34972_{self.device_index}_R{chnl}'] = res
                self.resistance_gauges[idx].set(res)
        else:
            logger.warning(f'Invalid scan result')

        # Store the temperatures as synoptics

        with SynopticsManagerProxy() as synoptics:
            synoptics.store_th_synoptics(hk_dict)

        return hk_dict