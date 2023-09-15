import logging
import time
from functools import partial
from copy import deepcopy

from egse.serialdevice import SerialDevice
from egse.command import Command
from egse.settings import Settings
from egse.vacuum.pfeiffer.tc400_interface import Tc400Interface, Tc400Command

logger = logging.getLogger(__name__)

# Load the device settings from the global common-egse config file
DEVICE_SETTINGS = Settings.load("Pfeiffer TC400 Controller")

# Load the device protocol
DEVICE_PROTOCOL = Settings.load(filename='tc400.yaml')['Commands']



def get_checksum(data):
    """ Checksum is the addition modulo 265 of ascii values in the dataword. """

    charsum = sum(ord(c) for c in data)
    return charsum % 256


class Tc400Controller(SerialDevice, Tc400Interface):

    def __init__(self, port=None, baudrate=None, address=None):

        # Load device configuration from the common-egse global config file
        self._port     = DEVICE_SETTINGS.PORT if port is None else port
        self._baudrate = DEVICE_SETTINGS.BAUDRATE if baudrate is None else baudrate
        self._address  = DEVICE_SETTINGS.ADDRESS if address is None else address

        # Initialize the parent class with the port and baudrate
        super().__init__(port=self._port, baudrate=self._baudrate)
        self.connect()

    def get_idn(self):
        cmd = f"{self._address:03d}0034902=?"
        cmd += f"{get_checksum(cmd):03d}" + "\r"
        return self.query(cmd)

    def get_last_error(self):
        cmd = f"{self._address:03d}0030302=?"
        cmd += f"{get_checksum(cmd):03d}" + "\r"
        return int(self.query(cmd))

    def get_active_speed(self):
        cmd = f"{self._address:03d}0030902=?"
        cmd += f"{get_checksum(cmd):03d}" + "\r"
        return int(self.query(cmd))

    def get_drive_power(self):
        cmd = f"{self._address:03d}0031602=?"
        cmd += f"{get_checksum(cmd):03d}" + "\r"
        return int(self.query(cmd))

    def get_motor_temperature(self):
        cmd = f"{self._address:03d}0034602=?"
        cmd += f"{get_checksum(cmd):03d}" + "\r"
        return int(self.query(cmd))

    def set_heating(self, enable):
        cmd = f"{self._address:03d}1000101{int(enable):1d}"
        cmd += f"{get_checksum(cmd):03d}" + "\r"
        return self.query(cmd)

    def set_standby(self, enable):
        cmd = f"{self._address:03d}1000201{int(enable):1d}"
        cmd += f"{get_checksum(cmd):03d}" + "\r"
        return self.query(cmd)

    def set_pumpingstation(self, enable):
        cmd = f"{self._address:03d}1001001{int(enable):1d}"
        cmd += f"{get_checksum(cmd):03d}" + "\r"
        return self.query(cmd)

    def set_motorpump(self, enable):
        cmd = f"{self._address:03d}1002301{int(enable):1d}"
        cmd += f"{get_checksum(cmd):03d}" + "\r"
        return self.query(cmd)

    def set_gasmode(self, mode):
        cmd = f"{self._address:03d}100271{mode:1d}"
        cmd += f"{get_checksum(cmd):03d}" + "\r"
        return self.query(cmd)

    def query(self, command: str):
        """ Override the parent class to do some error checking on the response. """

        response = super().query(command)

        if len(response) == 0:
            raise ConnectionError(f"No reply from device")

        elif response[-1] != '\r':
            raise ConnectionError(f"Invalid termination character in response: {response}")

        elif int(response[:3]) != self._address:
            raise ConnectionError(
                f"Got response with incorrect address from device: {response[:3]}")

        elif response[3] != '1':
            raise ConnectionError(f"Invalid opcode in response: {response}")

        elif Tc400Command.get_checksum(response[:-4]) != int(response[-4:-1]):
            raise ConnectionError(
                f"Invalid checksum in response: {get_checksum(response[:-4])} != {int(response[-4:-1])}")

        elif int(response[8:10]) == 6:
            if response[10:16] == 'NO_DEF':
                raise ConnectionError(f"Error response: parameter {response[5:8]} does not exist")
            elif response[10:16] == '_RANGE':
                raise ConnectionError(f"Error response: data outside permitted range")
            elif response[10:16] == '_LOGIC':
                raise ConnectionError(f"Error response: Logic access violation")

        return response[10:-4]


def main():
    logging.basicConfig()

    dev = Tc400Controller()

    print(dev.get_idn())
    print(dev.get_active_speed())
    print(dev.get_drive_power())
    print(dev.get_motor_temperature())
    print(dev.get_last_error())

    #print(dev.set_motorpump(False))
    # print(dev.set_pumpingstation(False))


if __name__ == '__main__':
    main()
