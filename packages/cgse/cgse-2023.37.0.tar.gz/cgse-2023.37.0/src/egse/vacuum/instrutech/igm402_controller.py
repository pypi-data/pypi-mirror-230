import logging
import time
from functools import partial
import random

import yaml

from egse.serialdevice import SerialDevice
from egse.command import Command
from egse.settings import Settings
from egse.setup import get_setup
from egse.vacuum.instrutech.igm402_interface import Igm402Interface

logger = logging.getLogger(__name__)

# Load the device settings from the global common-egse config file
DEVICE_SETTINGS = Settings.load("InstruTech IGM402 Controller")

# Load the device protocol
DEVICE_PROTOCOL = Settings.load(filename='igm402.yaml')['Commands']


class Igm402Controller(SerialDevice, Igm402Interface):

    def __init__(self, port=None, baudrate=None, address=None):

        # Load device configuration from the common-egse global config file
        self._port     = DEVICE_SETTINGS.PORT if port is None else port
        self._baudrate = DEVICE_SETTINGS.BAUDRATE if baudrate is None else baudrate
        self._address  = DEVICE_SETTINGS.ADDRESS if address is None else address

        # Get calibration from setup
        setup = get_setup()

        # Initialize the parent class with the port and baudrate
        super().__init__(port=self._port, baudrate=self._baudrate)
        self.connect()
        
        # Set the temperature points at which the IG filament is dis-/enabled.
        self.set_trip_point_i_low(0.9 * setup.gse.igm402.calibration.enable_filament_pressure)
        time.sleep(0.1)
        self.set_trip_point_i_high(setup.gse.igm402.calibration.enable_filament_pressure)
        time.sleep(0.1)

    def get_idn(self):
        cmd = f"#{self._address:02d}VER\r"
        return self.query(cmd)

    def reset(self):
        cmd = f"#{self._address:02d}RST\r"
        self.send_command(cmd)

    def get_status(self):
        cmd = f"#{self._address:02d}RS\r"
        return self.query(cmd)

    def get_system_pressure(self):
        cmd = f"#{self._address:02d}RDS\r"
        return self.query(cmd)

    def get_ion_gauge_pressure(self):
        cmd = f"#{self._address:02d}RD\r"
        raw_value = self.query(cmd)
        return float(raw_value.rstrip('\x00')) # only when the pressure is zero, the device appends a null character

    def get_cgn_pressure(self, index):
        assert index in [1, 2], 'index must be either 1 or 2'
        cmd = f"#{self._address:02d}RDCG{index:d}\r"
        raw_value = self.query(cmd)
        return float(raw_value.rstrip('\x00')) # only when the pressure is zero, the device appends a null character

    def set_filament_enable(self, enable):
        cmd = f"#{self._address:02d}IG{int(enable):1d}\r"
        return self.query(cmd)

    def set_enable_degas(self, enable):
        cmd = f"#{self._address:02d}DG{int(enable):1d}\r"
        return self.query(cmd)

    def set_emission_current(self, current):
        assert current in [0, 1], 'current selector must be either 0 or 1'
        cmd = f"#{self._address:02d}SE{current:1d}\r"
        return self.query(cmd)

    def set_filament(self, type):
        assert type in [1, 2], 'type must be either 1 or 2'
        cmd = f"#{self._address:02d}SF{type:1d}\r"
        return self.query(cmd)

    def set_trip_point_i_low(self, pressure):
        cmd = f"#{self._address:02d}SL+{pressure:.2E}\r"
        return self.query(cmd)

    def set_trip_point_i_high(self, pressure):
        cmd = f"#{self._address:02d}SL-{pressure:.2E}\r"
        return self.query(cmd)

    def query(self, command: str):
        """ Override the parent class to do some error checking on the response. """

        response = super().query(command)

        if len(response) == 0:
            return "0"
            raise ConnectionError(f"No reply from device")
        elif response[-1] != '\r':
            return "0"
            raise ConnectionError(f"Invalid termination character in response: {response}")
        elif response[0] != '*':
            return "0"
            raise ConnectionError(f"Invalid header character in response: {response}")
        elif response[0] == '?':
            return "0"
            raise ConnectionError(f"Got an error response from device: {response[4:-1]}")

        return response[4:-1]


def main():
    dev = Igm402Controller()
    print(dev.get_idn())
    print(dev.get_ion_gauge_pressure())
    print(dev.get_cgn_pressure(1))
    print(dev.get_cgn_pressure(2))
    
    
if __name__ == '__main__':
    main()
