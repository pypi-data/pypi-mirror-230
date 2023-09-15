"""
This module defines the basic classes to access the Hamamatsu lamp connected to the
EQ99 Manager controller that will be used in the IAS and INTA TVAC setup.
"""
import logging

from egse.decorators import dynamic_interface
from egse.device import DeviceInterface
from egse.lampcontrol import LampError
from egse.lampcontrol.energetiq.lampEQ99_devif import LampEQ99Error, LampEQ99USBInterface
from egse.proxy import Proxy
from egse.settings import Settings
from egse.zmq_ser import connect_address

LOGGER = logging.getLogger(__name__)
CTRL_SETTINGS = Settings.load("Lamp EQ99 Control Server")
DEVICE_SETTINGS = Settings.load(filename="eq99.yaml")


class LampEQ99Interface(DeviceInterface):
    """
    Interface definition for the Lamp EQ-99 Manager Controller, Simulator and Proxy..
    """
    @dynamic_interface
    def get_id(self, *args, **kwargs):
        """
        Send a command string to the device and wait for a response.

        Returns:
            a response from the device.
        """
        return NotImplemented

    @dynamic_interface
    def info(self) -> str:
        """
        Retrieve basic information about the Lamp controller.

        Returns:
            a multiline string with information about the device.
        """
        return NotImplemented

    @dynamic_interface
    def get_lamp_time(self):
        """
        Queries the lamp runtime

        Returns:
            The number of hours accumulated while the lamp was on. The value is in hours.
        """
        return NotImplemented

    @dynamic_interface
    def set_lamp_time(self):
        """
        Resets the lamp runtime to the new value in hours.

        Args:
            _time: int value in hours
        """
        return NotImplemented

    @dynamic_interface
    def get_lamp(self):
        """
        Queries the lamp output states

        Returns:
            Returns the output state. Will return true as soon as the turned on process has started, even if the lamp
            has not yet turned on. To determine the lamp and laser state use get_lamp_state
        """
        return NotImplemented

    @dynamic_interface
    def set_lamp(self):
        """
        Turns the lamp output on or off
        Args:
            enable(bin)
        """
        return NotImplemented

    @dynamic_interface
    def get_lamp_status(self):
        """
        Queries LDLS condition register

        Returns:
            Returns the LDLS condition register. The condition register reflects the state of the instrument at the
            time the condition register is read.

            Bit     Value       Description
            0       1           Interlock
            1       2           Controller not detected
            2       4           Controller fault
            3       8           Lamp fault
            4       16          Output on
            5       32          Lamp on
            6       64          Laser on
            7       128         Laser stable
            8       256         Shutter open

        """
        return NotImplemented

    @dynamic_interface
    def lamp_errors(self):
        """
        Queries for errors

        Returns:
            Returns a comma delimited list of error codes with a string description included.
            If no error has occurred, a 0 is returned.
        """
        return NotImplemented

    @dynamic_interface
    def ldls_reset(self):
        """
        Resets the instrument to the factory default and the ouput is shut off. The unit remains in remote mode

        """
        return NotImplemented


class LampEQ99Simulator(LampEQ99Interface):
    """
    The Lamp Simulator class.
    """

    def __init__(self):
        self._connected = True
        self.lamp_operation = False
        self.lamp_time = 36
        self.error_message = '0' # '0' means no error (lampEQ99 user manual p.21). Error message example (from lampEQ99 user manual p.22) : self.error_message = '201,"Out of range",124,"Data mismatch"'

    def is_connected(self):
        return self._connected

    def is_simulator(self):
        return True

    def connect(self):
        self._connected = True

    def disconnect(self):
        self._connected = False

    def reconnect(self):
        self._connected = True

    def get_id(self):
        pass

    def ldls_reset(self):
        pass

    def get_lamp_time(self):
        return self.lamp_time

    def lamp_errors(self):
        return f"Error Message: {self.error_message}"
        
    def set_lamp(self, _enable):
        self.lamp_operation = _enable

    def get_lamp(self):
        return self.lamp_operation


class LampEQ99Controller(LampEQ99Interface):
    """The LampEQ99Controller allows controlling a Hamamatsu Lamp."""

    def __init__(self):
        """Initialize the EQ-99 Manager Controller interface."""

        super().__init__()

        LOGGER.debug("Initializing EQ99 Manager")

        try:
            self.lamp = LampEQ99USBInterface()
            self.lamp.connect()
        except LampEQ99Error as exc:
            LOGGER.warning(f"LampError caught: Couldn't establish connection ({exc})")
            raise LampError(
                "Couldn't establish a connection with the Lamp EQ-99 controller."
            ) from exc

    def connect(self):
        """Connects to the Lamp device.

        Raises:
            DeviceNotFoundError: when the Lamp device is not connected.
        """
        if not self.lamp.is_connected():
            try:
                self.lamp.connect()
            except LampEQ99Error as exc:
                LOGGER.warning(f"LampEQ99Error caught: Couldn't establish connection ({exc})")

    def disconnect(self):
        self.lamp.disconnect()

    def reconnect(self):
        if self.is_connected():
            self.disconnect()
        self.connect()

    def is_connected(self):
        """Check if the Lamp Controller is connected."""
        return self.lamp.is_connected()

    def is_simulator(self):
        return False

    def get_id(self):
        self.lamp.write_message("*IDN?")
        _id = self.lamp.read_message()
        return _id

    def ldls_reset(self):
        self.lamp.write_message("*RST")

    def lamp_errors(self):
        self.lamp.write_message("ERRSTR?")
        _errmsg = self.lamp.read_message()[:-1] # [:-1] is to remove the unwanted last character '\r'
        return(f"Error Message: {_errmsg}")

    def get_lamp_status(self):
        "Query LDLS condition register"
        self.lamp.write_message("LDLS:COND?")
        _lamp = self.lamp.read_message()[:-1]
        return(_lamp)

    def set_lamp(self, _enable):
        "Turns the ouput on/off"
        self.lamp.write_message("LDLS:OUTput {}".format(str(_enable))) # _enable can be either bool or 0 or 1

    def get_lamp(self):
        """Query the lamp output state.
        Will return true as soon as the turned on process has started, even if the lamp has not yet turned on.
        To determine the lamp and laser state, use get_lamp_status function"""
        self.lamp.write_message("LDLS:OUTput?")
        _lamp = self.lamp.read_message() # _lamp is either '0\r' or '1\r' so _lamp is a str and not a bool
        _lamp = bool(int(_lamp)) # now _lamp is a bool
        return(_lamp)

    def set_lamp_time(self, _time):
        "Resets the Run time of the lifetime to the specified value (in hours). Useful to set to zero after Lamp replacement."
        self.lamp.write_message("LDLS:LAMPTIME {}".format(int(_time)))

    def get_lamp_time(self):
        "Query the lamp runtime (in hours)."
        self.lamp.write_message("LDLS:LAMPTIME?")
        _lamp = self.lamp.read_message()[:-1]
        return(_lamp)

    def _beep(self):
        "This is only used for debugging purposes"
        self.lamp._beep()


class LampEQ99Proxy(Proxy, LampEQ99Interface):
    """The LampEQ99Proxy class is used to connect to the control server and send commands to
     the Lamp device remotely."""

    def __init__(
            self,
            protocol=CTRL_SETTINGS.PROTOCOL,
            hostname=CTRL_SETTINGS.HOSTNAME,
            port=CTRL_SETTINGS.COMMANDING_PORT,
    ):
        """
        Args:
            protocol: the transport protocol [default is taken from settings file]
            hostname: location of the control server (IP address)
                [default is taken from settings file]
            port: TCP port on which the control server is listening for commands
                [default is taken from settings file]
        """
        super().__init__(connect_address(protocol, hostname, port))
