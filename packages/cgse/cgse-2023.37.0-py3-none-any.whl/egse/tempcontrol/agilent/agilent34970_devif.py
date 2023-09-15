#!/usr/bin/env python3

import logging
import time

from egse.command import ClientServerCommand
from egse.exceptions import DeviceNotFoundError
from egse.serialdevice import SerialDevice
from egse.settings import Settings
from egse.setup import get_setup

logger = logging.getLogger(__name__)



class Agilent34970Error(Exception):
    pass


class Agilent34970Command(ClientServerCommand):
    def get_cmd_string(self, *args, **kwargs):
        out = super().get_cmd_string(*args, **kwargs)
        return out + '\n'


class Agilent34970DeviceInterface(SerialDevice):

    def __init__(self, device_index):

        self._ctrl_settings = Settings.load(f'Agilent 34970 Controller')
        self._setup = get_setup()
        
        self.device_index = device_index
        
        # Load device configuration from the common-egse global config file
        self._port     = self._ctrl_settings[f"DAQ {device_index}"]["PORT"]
        self._baudrate = self._ctrl_settings[f"DAQ {device_index}"]["BAUDRATE"]

        self._setup = self._setup['gse'][f'agilent34970_{device_index}']
        self._conversions = self._setup['conversion']

        # Initialize the SerialDevice class with the port and baudrate
        super().__init__(port=self._port, baudrate=self._baudrate, terminator='\n', timeout=15)
        self.connect()
        
        self.create_scanlist()
        self.configure_agilent()


    def get_idn(self):
        return self.query('*IDN?\n')

    def format_scanlist(self, ch_list):
        scanlist = '(@'
        for idx, ch in enumerate(ch_list):
            if idx == 0:
                scanlist += f'{ch}'
            elif idx < len(ch_list):
                scanlist += f',{ch}'
        scanlist += ')'
        return scanlist
    
    def create_scanlist(self):
        thermocouple = self._setup.thermocouples
        two_wire = self._setup.two_wire
        four_wire = self._setup.four_wire
        pt100 = self._setup.pt100
        
        self.scanlist = thermocouple + two_wire + four_wire
        self.scanlist.sort()
        
        self.thermocouple = thermocouple
        self.two_wire = two_wire
        self.four_wire = four_wire
        self.pt100 = pt100
    
    def configure_agilent(self):
        
        # Extract configuration and scanlist from setup
        scan_list = self.format_scanlist(self.scanlist) if self.scanlist != [] else [] 
        thermocouple_list = self.format_scanlist(self.thermocouple) if self.thermocouple != [] else []
        two_wire_list = self.format_scanlist(self.two_wire) if self.two_wire != [] else []
        four_wire_list = self.format_scanlist(self.four_wire) if self.four_wire != [] else []
        pt100_list = self.format_scanlist(self.pt100) if self.pt100 != [] else []

        logger.info(f"Thermocouples: {thermocouple_list}")
        logger.info(f"Two wire: {two_wire_list}")
        logger.info(f"Four wire: {four_wire_list}")
        logger.info(f"Pt100s: {pt100_list}")
        logger.info(f"Final scanlist: {scan_list}")
       
        # Reset scan list
        self.send_command("*RST\n")
        
        # Configure channels
        if two_wire_list != []:
            self.send_command(f"CONF:RES {two_wire_list}\n")
            time.sleep(1)
        if four_wire_list != []:
            self.send_command(f"CONF:FRES {four_wire_list}\n")
            time.sleep(1)
        if thermocouple_list != []:
            self.send_command(f"CONF:TEMP TC,T,{thermocouple_list}\n")
            time.sleep(1)
        if pt100_list != []:
            self.send_command(f"CALC:SCAL:GAIN 10,{pt100_list}\n")
            self.send_command(f'CALC:SCAL:STAT ON,{pt100_list}\n')
            time.sleep(1)

        # Save values with unit
        self.send_command("FORM:READ:UNIT ON\n")
        self.send_command("FORM:READ:CHAN ON\n")

        
        # Load scan list
        self.send_command(f"ROUT:SCAN {scan_list}\n")
        time.sleep(0.1)
        
        self.send_command(f'SENS:VOLT:DC:NPLC 10\n')
        self.send_command('ROUT:CHAN:DEL 0.1\n')

        self.send_command("INIT\n")
        time.sleep(15)

    def trigger_scan(self):
        self.send_command("INIT\n")

    def read_resistance_temperature(self):
        # Fetch values stored in non-volatile memory
        return_string = self.query(f"DATA:REMOVE? {len(self.scanlist)}\n")

        # Check for errors
        if len(return_string) == 0:
            raise ConnectionError(f"No reply from device")

        if return_string[-1] != '\n':
            raise ConnectionError(f"Invalid termination character in response: {return_string}")
        
        values = return_string.split(',')
        
        resistances = {}
        temperatures = {}

        for i in range(0, len(values), 2):
            value = values[i].split(' ')
            channel = int(values[i+1])
            if 'C' in value or 'C\r' in value:
                resistances[f'{channel}'] = 0
                temperatures[f'{channel}'] = float(value[0])          
            elif 'OHM' in value or 'OHM\r' in value:
                resistances[f'{channel}'] = abs(float(value[0]))
                temperatures[f'{channel}'] = self._convert_resistance(abs(float(value[0])))  
        
        # Return values as list
        return resistances, temperatures

    def _convert_resistance(self, resistance):
        return (  self._conversions[0]
                + self._conversions[1] * resistance
                + self._conversions[2] * resistance**2
                + self._conversions[3] * resistance**3
                + self._conversions[4] * resistance**4
                + self._conversions[5] * resistance**5
        )

def main():

    dev0 = Agilent34970DeviceInterface(0)
    dev1 = Agilent34970DeviceInterface(1)
    print(dev0.get_idn())
    print(dev1.get_idn())

    while True:
        dev0.trigger_scan()
        dev1.trigger_scan()
        time.sleep(10)
        print(dev0.read_resistance_temperature())
        print(dev1.read_resistance_temperature())


if __name__ == '__main__':
    main()
