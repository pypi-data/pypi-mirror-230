import logging
from serial import SerialTimeoutException

from egse.serialdevice import SerialDevice
from egse.command import Command
from egse.settings import Settings
from egse.vacuum.pfeiffer.acp40_interface import Acp40Interface

logger = logging.getLogger(__name__)

# Load the device settings from the global common-egse config file
DEVICE_SETTINGS = Settings.load("Pfeiffer ACP40 Controller")

# Load the device protocol
DEVICE_PROTOCOL = Settings.load(filename='acp40.yaml')['Commands']


class Acp40Controller(SerialDevice, Acp40Interface):

    def __init__(self, port=None, baudrate=None, address=None):

        # Load device configuration from the common-egse global config file
        self._port     = DEVICE_SETTINGS.PORT if port is None else port
        self._baudrate = DEVICE_SETTINGS.BAUDRATE if baudrate is None else baudrate
        self._address  = DEVICE_SETTINGS.ADDRESS if address is None else address

        # Initialize the parent class with the port and baudrate
        super().__init__(port=self._port, baudrate=self._baudrate, terminator='\r', timeout=1)
        self.connect()

    def is_connected(self):
        return True
    
    def is_simulator(self):
        return False
    
    def get_idn(self):
        cmd = f"#{self._address:03d}IDN\r"
        return self.query(cmd)

    def get_device_status(self):
        cmd = f"#{self._address:03d}STA\r"
        return self.query(cmd)

    def get_address(self):
        cmd = "#???ADR\r"
        return self.query(cmd)

    def set_standby(self):
        cmd = f"#{self._address:03d}SBY\r"
        return self.query(cmd)

    def set_nominal_speed(self):
        cmd = f"#{self._address:03d}NSP\r"
        return self.query(cmd)

    def set_rpm(self, rpm):
        cmd = f"#{self._address:03d}RPM{rpm:02d}\r"
        return self.query(cmd)

    def set_enable(self, enable):
        enablestr = 'ON' if enable else 'OFF'
        cmd = f"#{self._address:03d}ACP{enablestr:s}\r"
        return self.query(cmd)

    def query(self, command: str):
        """ The ACP40 does some strange undocumented things that does not allow using the normal
            parent class query function other serial controllers use.
        """

        # Attempt to send the command
        self.send_command(command)

        try:
            with self._lock:
                return_string = self._serial.read_until(b'\r', size=1024)

        except SerialTimeoutException as e_timeout:
            raise ConnectionError("Serial timeout during query") from e_timeout

        if len(return_string) == 0:
            raise ConnectionError(f"No reply from device")

        if not b'#' in return_string:
            raise ConnectionError(f"Invalid header character in response: {return_string}")

        # the device sends garbage characters before the `#` starting character.
        # Mostly \x00's but sometimes other non-ascii characters
        response = (b'#' + return_string.split(b'#')[1]).decode()

        return_value = response[5:-1]

        if return_value == 'ERR0':
            raise ConnectionError(f"Setting fault for command: {command}")
        if return_value == 'ERR1':
            raise ConnectionError(f"Context fault for command: {command}")
        if return_value == 'ERR2':
            raise ConnectionError(f"Parameter fault for command: {command}")
        if return_value == 'ERR3':
            raise ConnectionError(f"Order fault for command: {command}")

        return return_value


def main():
    logging.basicConfig()


    dev = Acp40Controller()

    #print(dev.get_address())
    print(dev.get_idn())
    print(dev.get_device_status())
    # print(dev.set_enable(False, address=0))

if __name__ == '__main__':
    main()
