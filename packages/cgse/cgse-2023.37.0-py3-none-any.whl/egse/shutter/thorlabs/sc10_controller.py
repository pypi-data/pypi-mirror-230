import logging

from egse.serialdevice import SerialDevice
from egse.command import Command
from egse.settings import Settings
from egse.shutter.thorlabs.sc10_interface import Sc10Interface

logger = logging.getLogger(__name__)

# Load the device settings from the global common-egse config file
DEVICE_SETTINGS = Settings.load("Thorlabs SC10 Controller")

# Load the device protocol
DEVICE_PROTOCOL = Settings.load(filename='sc10.yaml')['Commands']


class Sc10Controller(SerialDevice, Sc10Interface):

    def __init__(self, port=None, baudrate=None, address=None):

        # Load device configuration from the common-egse global config file
        self._port     = DEVICE_SETTINGS.PORT if port is None else port
        self._baudrate = DEVICE_SETTINGS.BAUDRATE if baudrate is None else baudrate

        # Create a dict of Command objects for each function
        self._commands = {}
        for name, items in DEVICE_PROTOCOL.items():
            if 'cmd' in items:
                self._commands[name] = Command(name, items['cmd'])

        # Initialize the parent class with the port and baudrate
        super().__init__(port=self._port, baudrate=self._baudrate, terminator='\r', timeout=1)
        self.connect()


    def get_idn(self):
        return self.query(self._commands['get_idn'].get_cmd_string())


    def get_enable(self):
        return self.query(self._commands['get_enable'].get_cmd_string()) == "1\r"


    def toggle_enable(self):
        return self.query(self._commands['toggle_enable'].get_cmd_string())


    def set_mode(self, mode):
        return self.query(self._commands['set_mode'].get_cmd_string(mode=mode))


    def set_open_duration(self, duration):
        return self.query(self._commands['set_open_duration'].get_cmd_string(duration=duration))


    def query(self, command: str):
        """ Override the parent class to do some error checking on the response. """

        # The device first echos the command with a promt and then sends the response.
        # To handle this, the device is read twice.
        _ = super().query(command)
        response = self.read()

        if len(response) == 0:
            raise ConnectionError(f"No reply from device")

        return response


def main():
    logging.basicConfig()

    dev = Sc10Controller()
    print(dev.get_idn())
    print(dev.get_enable())
    dev.toggle_enable()
    print(dev.get_enable())


if __name__ == '__main__':
    main()
