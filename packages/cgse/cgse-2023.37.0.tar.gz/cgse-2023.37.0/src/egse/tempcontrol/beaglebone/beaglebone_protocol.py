import logging
import time

from prometheus_client import Gauge

from egse.control import ControlServer
from egse.protocol import CommandProtocol
from egse.settings import Settings
from egse.tempcontrol.beaglebone.beaglebone import BeagleboneHeaterController
from egse.tempcontrol.beaglebone.beaglebone import BeagleboneInterface
from egse.tempcontrol.beaglebone.beaglebone import BeagleboneSimulator
from egse.tempcontrol.beaglebone.beaglebone import BeagleboneCommand
from egse.system import format_datetime
from egse.zmq_ser import bind_address

COMMAND_SETTINGS = Settings.load(filename='beaglebone.yaml')

logger = logging.getLogger(__name__)


class BeagleboneProtocol(CommandProtocol):

    from gssw.lib.errors import GsswTimeoutError, PeerException, CommunicationError

    def __init__(self, control_server:ControlServer):
        super().__init__()
            
        self.control_server = control_server

        if Settings.simulation_mode():
            self.beaglebone = BeagleboneSimulator()
            self._num_dev = 6
        else:
            self.beaglebone = BeagleboneHeaterController()
            self._num_dev = len(self.beaglebone.heaters)

        self.temperature_gauges = [Gauge(f'GSRON_HTR_TEMP_{device}', '') for device in range(self._num_dev)]
        self.current_gauges     = [[Gauge(f"GSRON_HTR_I_{device}_{channel}", '') for channel in range(4)] for device in range(self._num_dev)]
        self.voltage_gauges     = [[Gauge(f"GSRON_HTR_V_{device}_{channel}", '') for channel in range(4)] for device in range(self._num_dev)]
        self.resistance_gauges  = [[Gauge(f"GSRON_HTR_R_{device}_{channel}", '') for channel in range(4)] for device in range(self._num_dev)]
        self.power_gauges       = [[Gauge(f"GSRON_HTR_P_{device}_{channel}", '') for channel in range(4)] for device in range(self._num_dev)]
        
        self.valid_hk           = [True] * self._num_dev
        self.valid_status       = [True] * self._num_dev
        
        self.load_commands(COMMAND_SETTINGS.Commands, BeagleboneCommand, BeagleboneInterface)

        self.build_device_method_lookup_table(self.beaglebone)

    def get_bind_address(self):
        return bind_address(self.control_server.get_communication_protocol(),
                            self.control_server.get_commanding_port())

    def get_status(self):
        status_info = super().get_status()

        htr_connected = [False] * self._num_dev
        htr_enabled   = [[] * 4] * self._num_dev
        htr_cycle     = [[] * 4] * self._num_dev
        
        
        for i, heater in enumerate(self.beaglebone.heaters.values()):
            
            enabled     = []
            duty_cycle  = []
            
            if heater.connected:
                try:
                    for channel in range(4):
                        enabled.append(heater.get_enable(channel))
                        duty_cycle.append(heater.get_duty_cycle(channel))
    
                    htr_connected[i] = True
                except self.CommunicationError as ex:
                    logger.error("Could not connect to heater %s: %s", i, ex)
                    heater.disconnected()
                except self.PeerException as ex:
                    logger.warning("Could not retrieve housekeeping from heater %s: %s", i, ex)      
                    
            if not heater.connected:
                for channel in range(4):
                    enabled.append(False)
                    duty_cycle.append(0.0)       
        
            htr_enabled[i] = enabled
            htr_cycle[i]   = duty_cycle
        
        status_info['Connected']  = htr_connected
        status_info['Enabled']    = htr_enabled
        status_info['duty_cycle'] = htr_cycle        

        return status_info

    
    def get_housekeeping(self) -> dict:

        hk_dict = {'timestamp': format_datetime()}

        for i, heater in enumerate(self.beaglebone.heaters.values()):
            if heater.connected:
                try:
                    hk_dict[f'GSRON_HTR_TEMP_{i}'] = heater.temperature
                    
                    for channel in range(4):
                        hk_dict[f"GSRON_HTR_V_{i}_{channel}"] = heater.get_voltage(channel)
                        hk_dict[f"GSRON_HTR_I_{i}_{channel}"] = heater.get_current(channel)
                        
                        hk_dict[f"GSRON_HTR_R_{i}_{channel}"] = hk_dict[f"GSRON_HTR_V_{i}_{channel}"] / hk_dict[f"GSRON_HTR_I_{i}_{channel}"] \
                                                                    if hk_dict[f"GSRON_HTR_I_{i}_{channel}"] else 0
                        hk_dict[f"GSRON_HTR_P_{i}_{channel}"] = hk_dict[f"GSRON_HTR_V_{i}_{channel}"] * hk_dict[f"GSRON_HTR_I_{i}_{channel}"]
                except self.GsswTimeoutError as ex:
                    logger.error("Could not connect with Beaglebone heater %s: %s", i, ex)
                    heater.disconnected()
                except self.PeerException as ex:
                    logger.warning("Could not retrieve housekeeping from heater %s: %s", i, ex)
                    heater.disconnected()
                    
            if not heater.connected:
                hk_dict[f'GSRON_HTR_TEMP_{i}'] = 0.0
                        
                for channel in range(4):
                    hk_dict[f"GSRON_HTR_V_{i}_{channel}"] = 0.0
                    hk_dict[f"GSRON_HTR_I_{i}_{channel}"] = 0.0
                    hk_dict[f"GSRON_HTR_R_{i}_{channel}"] = 0.0
                    hk_dict[f"GSRON_HTR_P_{i}_{channel}"] = 0.0     
        
            self.temperature_gauges[i].set(hk_dict[f'GSRON_HTR_TEMP_{i}'])
                        
            for channel in range(4):
                self.voltage_gauges[i][channel].set(hk_dict[f"GSRON_HTR_V_{i}_{channel}"])
                self.current_gauges[i][channel].set(hk_dict[f"GSRON_HTR_I_{i}_{channel}"])
                self.resistance_gauges[i][channel].set(hk_dict[f"GSRON_HTR_R_{i}_{channel}"])
                self.power_gauges[i][channel].set(hk_dict[f"GSRON_HTR_P_{i}_{channel}"])

        return hk_dict
