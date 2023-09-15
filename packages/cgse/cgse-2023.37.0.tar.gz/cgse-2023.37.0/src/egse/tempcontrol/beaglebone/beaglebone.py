import os
import logging

from egse.decorators import dynamic_interface
from egse.device import DeviceInterface
from egse.proxy import Proxy
from egse.settings import Settings
from egse.command import ClientServerCommand
from egse.confman import ConfigurationManagerProxy
from egse.zmq_ser import connect_address

logger = logging.getLogger(__name__)

CTRL_SETTINGS = Settings.load("BeagleBone Heater Control Server")
DEVICE_SETTINGS = Settings.load(filename='beaglebone.yaml')

LED_PINS = [69, 68, 66, 67]
PWM_PINS = [4, 5, 7, 8]

class BeagleboneCommand(ClientServerCommand):
    def get_cmd_string(self, *args, **kwargs):
        out = super().get_cmd_string(*args, **kwargs)
        return out + '\n'

class BeagleboneError(Exception):
    pass

class BeagleboneInterface(DeviceInterface):
    """ BeagleBone base class."""

    @dynamic_interface
    def connect_beaglebone(self, device):
        return NotImplemented

    @dynamic_interface
    def set_enable(self, dev_idx, chnl_idx, enable):
        """ Enable PWM pin. """
        return NotImplemented

    @dynamic_interface
    def set_duty_cycle(self, dev_idx, chnl_idx, duty_cycle):
        """ Duty cycle duration in ns. """
        return NotImplemented

    @dynamic_interface
    def set_period(self, dev_idx, chnl_idx, period):
        """ Period duration in ns. """
        return NotImplemented

    @dynamic_interface
    def get_temperature(self, dev_idx):
        """ Get board temperature. """
        return NotImplemented

    @dynamic_interface
    def get_voltage(self, dev_idx, chnl_idx):
        """ Get channel voltage. """
        return NotImplemented

    @dynamic_interface
    def get_current(self, dev_idx, chnl_idx):
        """ Get channel current. """
        return NotImplemented

    @dynamic_interface
    def get_power(self, dev_idx, chnl_idx):
        """ Get channel power. """
        return NotImplemented
    
    @dynamic_interface
    def get_enable(self, dev_idx, chnl_idx):
        """ Get enabled state. """
        return NotImplemented

    @dynamic_interface
    def get_duty_cycle(self, dev_idx, chnl_idx):
        """ Get duty cycle. """
        return NotImplemented


class BeagleboneSimulator(BeagleboneInterface):
    
    def __init__(self):
        super().__init__()
        self._is_connected = True
        self.duty_cycle = [[[] for _ in range(4)] for _ in range(6)]
        self.enabled = [[[] for _ in range(4)] for _ in range(6)]   
        
        for htr_idx in range(0, 6):
            for ch_idx in range(0, 4):
                self.duty_cycle[htr_idx][ch_idx] = 2 * ch_idx + htr_idx
                self.enabled[htr_idx][ch_idx] = False


    def is_connected(self):
        return self._is_connected

    def is_simulator(self):
        return True

    def connect(self):
        self._is_connected = True

    def disconnect(self):
        self._is_connected = False

    def reconnect(self):
       if self.is_connected():
           self.disconnect()
       self.connect()

    def set_enable(self, dev_idx, chnl_idx, enable):
       logger.info(f"Heater {dev_idx} Channel {chnl_idx} state has been set to {enable}")
       self.enabled[dev_idx][chnl_idx] = enable

    def set_duty_cycle(self, dev_idx, chnl_idx, duty_cycle):
       logger.info(f"Duty cycle for Heater {dev_idx} Channel {chnl_idx} set to {duty_cycle}ns")
       self.duty_cycle[dev_idx][chnl_idx] = duty_cycle

    def set_period(self, dev_idx, chnl_idx, period):
       logger.info(f"Period for Heater {dev_idx} Channel {chnl_idx} set to {period} ns")


    def get_temperature(self, dev_idx):
       return 20.0

    def get_voltage(self, dev_idx, chnl_idx):
       return 1.0

    def get_current(self, dev_idx, chnl_idx):
       return 0.1

    def get_power(self, dev_idx, chnl_idx):
       return 1.0
   
    def get_enable(self, dev_idx, chnl_idx):
       return self.enabled[dev_idx][chnl_idx]
   
    def get_duty_cycle(self, dev_idx, chnl_idx):
       return self.duty_cycle[dev_idx][chnl_idx]
   
    def get_availability(self):
       return [True] * 6


class BeagleboneHeater:
    
    # Perform SRON gssw imports here to avoid issues at other THs
    from gssw.lib.device import Device
    
    def __init__(self, num, config, hal):
        self.num        = num + 1
        
        self.config     = config
        self.hal        = hal
        
        self._is_connected     = False
        
        try:
            self.connect()
        except Exception:
            self._is_connected = False
        
    @property
    def connected(self):
        return self._is_connected

    def connect(self):
        self.pwm  = self.Device(f'pwm_{self.num}', self.config, self.hal)
        self.i2c  = self.Device(f'i2c_{self.num}', self.config, self.hal)
        self.gpio = self.Device(f'gpio_{self.num}', self.config, self.hal)
        
        for i in range(4):
            self.set_period(i, 10000)
            
        self._is_connected = True

    def disconnect(self):
        if self.pwm.socket:
            self.pwm.socket.close()
        if self.i2c.socket:
            self.i2c.socket.close()
        if self.gpio.socket:
            self.gpio.socket.close()
        
        self._is_connected = False

    def disconnected(self):
        self._is_connected = False

    @property
    def temperature(self):
        def twosComp(val, bits):
            if (val & (1 << (bits - 1))) != 0:
                val = val - (1 << bits)
            return val
        raw = self.i2c.get('TEMP')
        val = ((raw << 8) & 0xFF00) + (raw >> 8)
        val = val >> 4
        return twosComp(val, 12) * (128/0x7FF)


    
    def set_enable(self, channel, state):
        self.pwm.setMultiple([('PWM_NUM', PWM_PINS[channel]),
                            ('PWM_ENABLE', state)])
        self.gpio.setMultiple([('GPIO_PIN', LED_PINS[channel]),
                            ('GPIO_VALUE', state)])

    
    def set_duty_cycle(self, channel, duty_cycle):
        self.pwm.setMultiple([('PWM_NUM', PWM_PINS[channel]), 
                            ('PWM_DUTY_CYCLE', duty_cycle)])

    
    def set_period(self, channel, period):
        self.pwm.setMultiple([('PWM_NUM', PWM_PINS[channel]), 
                            ('PWM_PERIOD', period)])
    
    def get_voltage(self, channel):
        raw = self.i2c.get(f'V_{channel}')
        val = ((raw << 8) & 0xFF00) + (raw >> 8)
        val = val >> 4
        return val * 0.025

    
    def get_current(self, channel):
        raw = self.i2c.get(f'I_{channel}')
        val = ((raw << 8) & 0xFF00) + (raw >> 8)
        val = val >> 4
        return val * 5e-4

    
    def get_power(self, channel):
        return self.get_voltage(channel) * self.get_current(channel)

    
    def get_enable(self, channel):
        pwm_enable = self.pwm.getSetMultiple([('PWM_NUM', PWM_PINS[channel]), 
                                                ('PWM_ENABLE', None)])[0]
        return bool(pwm_enable)
    
    def get_duty_cycle(self, channel):

        pwm_duty_cycle = self.pwm.getSetMultiple([('PWM_NUM', PWM_PINS[channel]), ('PWM_DUTY_CYCLE', None)])
        return int(pwm_duty_cycle[0])

            
    def set_timeout(self, timeout):
        self.pwm.setTimeout(timeout)
        self.gpio.setTimeout(timeout)
        self.i2c.setTimeout(timeout)


class BeagleboneHeaterController(BeagleboneInterface):

    def __init__(self):
        super().__init__()

        # Perform SRON gssw imports here to avoid issues at other THs
        from gssw.config.configclient import ConfigClient
        from gssw.common import addLoggingLevel
        from gssw.hal.hal import Hal
        from gssw.hal.halclient import HalClient

        logger.debug('Initalizing BeagleBone Black Heater Controller')

        configClient = ConfigClient(os.getenv('GSSW_CONFIGURATION_FILE'))
        self.config = configClient.config
        addLoggingLevel('data', 15)

        with ConfigurationManagerProxy() as cm:
            setup = cm.get_setup()

        self._availability = setup.gse.beaglebone_heater.availability
        self._active       = [False] * len(self._availability)
        
        self.hal = Hal()
        hal_client = HalClient(self.hal, self.config)
        hal_client.requestHal()
        
        self.heaters = {}
        
        for htr, available in enumerate(self._availability):
            if available:
                self.heaters[htr] = BeagleboneHeater(htr, self.config, self.hal)

    def is_simulator(self):
        return False

    def is_connected(self):
        return all([heater.connected for heater in self.heaters.values()])

    def connect(self):
        for heater in self.heaters.values():
            heater.connect()
    
    def disconnect(self):
        for heater in self.heaters.values():
            heater.disconnect()

    def reconnect(self):
        for heater in self.heaters.values():
            heater.disconnect()
            heater.connect()

    def connect_beaglebone(self, device):
        self.heaters[device].connect()

    def set_enable(self, dev_idx, chnl_idx, enable):
        self.heaters[dev_idx].set_enable(chnl_idx, enable)

    def set_duty_cycle(self, dev_idx, chnl_idx, duty_cycle):
        self.heaters[dev_idx].set_duty_cycle(chnl_idx, duty_cycle)

    def set_period(self, dev_idx, chnl_idx, period):
        self.heaters[dev_idx].set_period(chnl_idx, period)

    def get_temperature(self, dev_idx):
        return self.heaters[dev_idx].temperature

    def get_voltage(self, dev_idx, chnl_idx):
        return self.heaters[dev_idx].get_voltage(chnl_idx)

    def get_current(self, dev_idx, chnl_idx):
        return self.heaters[dev_idx].get_current(chnl_idx)

    def get_power(self, dev_idx, chnl_idx):
        return self.heaters[dev_idx].get_power(chnl_idx)
    
    def get_enable(self, dev_idx, chnl_idx):
        return self.heaters[dev_idx].get_enable(chnl_idx)
    
    def get_duty_cycle(self, dev_idx, chnl_idx):
        return self.heaters[dev_idx].get_duty_cycle(chnl_idx)


class BeagleboneProxy(Proxy, BeagleboneInterface):
    def __init__(self, protocol=CTRL_SETTINGS.PROTOCOL,
                 hostname=CTRL_SETTINGS.HOSTNAME,
                 port=CTRL_SETTINGS.COMMANDING_PORT):
        super().__init__(connect_address(protocol, hostname, port))
