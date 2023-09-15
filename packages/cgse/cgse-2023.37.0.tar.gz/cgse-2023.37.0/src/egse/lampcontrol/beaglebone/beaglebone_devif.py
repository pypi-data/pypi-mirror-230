import logging
import struct
import time
import socket
import errno
import os

from egse.command import ClientServerCommand
from egse.exceptions import DeviceNotFoundError
from egse.settings import Settings

LAMP = 50
EX_INTERLOCK = 20

LAMP_ON=66
LASER_ON=61
LAMP_MODULE_FAULT = 67
CONTROLLER_FAULT = 65

logger = logging.getLogger(__name__)
ctrl_settings = Settings.load('BeagleBone Lamp Control Server')


class BeagleboneCommand(ClientServerCommand):
    def get_cmd_string(self, *args, **kwargs):
        out = super().get_cmd_string(*args, **kwargs)
        return out + '\n'


class BeagleboneDeviceInterface:
    def __init__(self):

        # Perform SRON gssw imports here to avoid issues at other THs
        from gssw.config.configclient import ConfigClient
        from gssw.common import addLoggingLevel
        from gssw.hal.hal import Hal
        from gssw.hal.halclient import HalClient
        from gssw.lib.device import Device

        self._is_connected = False

        # InitGssw does something to zmq that breaks cgse logging.
        # So instead I copied the essentials here.
        configClient = ConfigClient(os.getenv('GSSW_CONFIGURATION_FILE'))
        config = configClient.config
        addLoggingLevel('data', 15)

        hal = Hal()
        hal_client = HalClient(hal, config)
        hal_client.requestHal()

        self._dev_gpio = Device('gpio_gsm', config, hal)

    def connect(self):
        self._is_connected = True

    def disconnect(self):
        self._is_connected = False

    def reconnect(self):
        if self._is_connected:
            self.disconnect()
        self.connect()

    def is_connected(self):
        return self._is_connected

    def set_lamp(self, state):
        try:
            logger.info(f"Lamp source is now: {'ON' if state == 1 else 'Off'}")
            self._dev_gpio.setMultiple([('GPIO_PIN', LAMP), ('GPIO_VALUE', state)])
        except Exception as exc:
            logger.error(f'Could not turn on the light source: {exc}')
            raise exc

    def set_interlock(self, state):
        try:
            logger.info(f"Lamp external interlock is now: {'ON' if state == 1 else 'Off'}")
            self._dev_gpio.setMultiple([('GPIO_PIN', EX_INTERLOCK), ('GPIO_VALUE', state)])
        except Exception as exc:
            logger.error(f'Could not turn set interlock: {exc}')
            raise exc

    def get_lamp_on(self):
        try:
            lamp_on = self._dev_gpio.getSetMultiple([("GPIO_PIN", LAMP_ON), ("GPIO_VALUE", None)])
            return bool(not lamp_on[0])
        except Exception as exc:
            logger.error(f'Could not read lamp state: {exc}')
            raise exc

    def get_laser_on(self):
        try:
            laser_on = self._dev_gpio.getSetMultiple([("GPIO_PIN", LASER_ON), ("GPIO_VALUE", None)])
            return bool(not laser_on[0])
        except Exception as exc:
            logger.error(f'Could not get laser state: {exc}')
            raise exc

    def get_lamp_module_fault(self):
        try:
            lamp_module_fault = self._dev_gpio.getSetMultiple([("GPIO_PIN", LAMP_MODULE_FAULT), ("GPIO_VALUE", None)])
            return bool(lamp_module_fault[0])
        except Exception as exc:
            logger.error(f'Could not get lamp module faults: {exc}')
            raise exc
        
    def get_controller_fault(self):
        try:
            controller_fault = self._dev_gpio.getSetMultiple([("GPIO_PIN", CONTROLLER_FAULT), ("GPIO_VALUE", None)])
            return bool(controller_fault[0])
        except Exception as exc:
            logger.error(f'Could not get controller faults: {exc}')
            raise exc
        
    def fix_controller_fault(self):
        # 1. Close interlocks
        self.set_interlock(True)
        # 2. Turn on lamp
        self.set_lamp(True)
        # 3. Wait for a second
        time.sleep(2)
        # 4. Disable lamp 
        self.set_lamp(False)
            

def main():
    bbb = BeagleboneDeviceInterface()
    
    print(f"Lamp state: {bbb.get_lamp_on()}\n"\
          f"Laster state: {bbb.get_laser_on()}\n"\
          f"Module fault: {bbb.get_lamp_module_fault()}\n"\
          f"Controller fault: {bbb.get_controller_fault()}\n")
    # bbb.set_lamp(True)
    
    # while not bbb.get_lamp_on():
    #     pass
    
    # while not bbb.get_laser_on():
    #     pass
    
    # print(f"Lamp state: {bbb.get_lamp_on()}\n"\
    #       f"Laster state: {bbb.get_laser_on()}\n"\
    #       f"Module fault: {bbb.get_lamp_module_fault()}\n"\
    #       f"Controller fault: {bbb.get_controller_fault()}")
    


if __name__ == '__main__':
    main()
