import logging
import struct
import time
import socket
import errno
import os

from egse.command import ClientServerCommand
from egse.settings import Settings


logger = logging.getLogger(__name__)
ctrl_settings = Settings.load('BeagleBone Valve Control Server')


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
         
        self.valves= {
            "MV011"         : 20,
            "MV012"         : 26,
            "MV013"         : 27,
            "MV014"         : 44,
            "MV021"         : 45,
            "MV022"         : 46,
            "MV023"         : 47,
            "MV024"         : 48,
            "MV002"         : 49,
            "MV001"         : 50   
        }
        
        self.valvefb = {
            "LN2_SHROUD_RMT"     : 61,
            "LN2_TEB-FEE_RMT"    : 65,
            "LN2_TEB-TOU_RMT"    : 66,
            "LN2_TRAP_RMT"       : 67,
            "N2_SHROUD_RMT"      : 68,
            "N2_TEB-FEE_RMT"     : 69,
            "N2_TEB-TOU_RMT"     : 115,
            "N2_TRAP_RMT"        : 117,
            "VENT_VALVE_RMT"     : 112,
            "GATE_VALVE_RMT"     : 2,
            "LN2_SHROUD_FB"      : 113,
            "LN2_TEB-FEE_FB"     : 5,
            "LN2_TEB-TOU_FB"     : 14,
            "LN2_TRAP_FB"        : 4,
            "N2_SHROUD_FB"       : 15,
            "N2_TEB-FEE_FB"      : 89,
            "N2_TEB-TOU_FB"      : 87,
            "N2_TRAP_FB"         : 88,
            "VENT_VALVE_FB"      : 22,
            "GATE_OPEN_FB"       : 10,
            "GATE_CLOSE_FB"      : 86,
            "INTRLCK_DOOR_FB"    : 23
        }

        self._dev_gpio = Device('gpio_vacuum', config, hal)
        # self._export_control()
        # self._export_feedback()

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

    def _export_feedback(self):
        for pin in self.valvefb.values():
            self._dev_gpio.setMultiple([('GPIO_PIN', pin), ('GPIO_EXPORT', True), ('GPIO_EXPORT', True), ('GPIO_DIRECTION', False)])
    
    def _export_control(self):
        for pin in self.valves.values():
            self._dev_gpio.setMultiple([('GPIO_PIN', pin), ('GPIO_EXPORT', True), ('GPIO_EXPORT', True), ('GPIO_DIRECTION', True)])
    
    def set_valve(self, valve_idx, valve_state):
        if valve_idx in self.valves.keys():
            # logger.info(f"{valve_idx} {valve_state}")
            state = self._dev_gpio.getSetMultiple([('GPIO_PIN', self.valves[valve_idx]), ('GPIO_VALUE', valve_state), ('GPIO_VALUE', None)])
            return state[0]
        else:
            raise ValueError(f"{self.valves[valve_idx]} is not a valid valve ctrl ID")

    def get_valve(self, valve_idx):
        if valve_idx in self.valvefb.keys():
            state = self._dev_gpio.getSetMultiple([('GPIO_PIN', self.valvefb[valve_idx]), ('GPIO_VALUE', None)])
            return state[0]
        else:
            raise ValueError(f"{self.valvefb[valve_idx]} is not a valid valve feedback ID")

def main():
    bbb = BeagleboneDeviceInterface()
    
    # Open all valves
    for i in bbb.valves.values():
        bbb.set_valve(i, True)
    
    # Confirm state of all valves (Remote ON, Valves OPEN)
    for key, i in bbb.valvefb.items():
        print(f"{key}: {bbb.get_valve(i)}")
    
    input("Confirm remote control ON, Valves OPEN")
    
    # Close all valves
    for i in bbb.valves.values():
        bbb.set_valve(i, False)
        
    # Confirm state of all valves (Remote ON, Valves CLOSED)
    for key, i in bbb.valvefb.items():
        print(f"{key}: {bbb.get_valve(i)}")
        
    input("Confirm remote control ON, Valves CLOSED")
        
    input("Turn all switches to open state")
    
    # Confirm state of all valves
    for key, i in bbb.valvefb.items():
        print(f"{key}: {bbb.get_valve(i)}")
        
    input("Confirm remote control OFF, Valves OPEN")
    
    input("Turn all switches to open state")
    
    # Confirm state of all valves
    for key, i in bbb.valvefb.items():
        print(f"{key}: {bbb.get_valve(i)}")

    input("Confirm remote control OFF, Valves CLOSED") 


if __name__ == '__main__':
    main()
