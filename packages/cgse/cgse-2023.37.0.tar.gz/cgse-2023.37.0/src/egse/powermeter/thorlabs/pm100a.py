import logging

from egse.decorators import dynamic_interface
from egse.device import DeviceInterface
from egse.powermeter.thorlabs.pm100a_devif import ThorlabsError
from egse.powermeter.thorlabs.pm100a_devif import ThorlabsPM100USBInterface
from egse.proxy import Proxy
from egse.randomwalk import RandomWalk
from egse.settings import Settings
from egse.zmq_ser import connect_address

logger = logging.getLogger(__name__)

CTRL_SETTINGS = Settings.load("Thorlabs PM100 Control Server")
DEVICE_SETTINGS = Settings.load(filename="pm100a.yaml")


class ThorlabsPM100Interface(DeviceInterface):
    """
    The Thorlabs PM100 base class.
    """

    @dynamic_interface
    def info(self) -> str:
        """
        Retrieve basic information about the Thorlabs controller.

        Returns:
            a multiline string with information about the device.
        """
        return NotImplemented

    @dynamic_interface
    def get_value(self, *args, **kwargs):
        """
        Send a command string to the device and wait for a response.

        Returns:
            a response from the device.
        """
        return NotImplemented

    @dynamic_interface
    def get_id(self, *args, **kwargs):
        """
        Send a command string to the device and wait for a response.

        Returns:
            a response from the device.
        """
        return NotImplemented

    @dynamic_interface
    def get_wavelength(self, *args, **kwargs):
        """
        Send a command string to the device and wait for a response.

        Returns:
            a response from the device.
        """
        return NotImplemented

    @dynamic_interface
    def get_range(self, *args, **kwargs):
        return NotImplemented

    @dynamic_interface
    def get_config(self, *args, **kwargs):
        return NotImplemented

    @dynamic_interface
    def get_average(self, *args, **kwargs):
        """
        Send a command string to the device and wait for a response.

        Returns:
            a response from the device.
        """
        return NotImplemented

    @dynamic_interface
    def get_diameter(self, *args, **kwargs):
        """
        Send a command string to the device and wait for a response.

        Returns:
            a response from the device.
        """
        return NotImplemented

    @dynamic_interface
    def get_autozero(self, *args, **kwargs):
        """
        Send a command string to the device and wait for a response.

        Returns:
            a response from the device.
        """
        return NotImplemented

    @dynamic_interface
    def set_average(self, average):
        """
        Send a command string to the device and wait for a response.

        Returns:
            a response from the device.
        """
        return NotImplemented

    @dynamic_interface
    def set_wavelength(self, wave):
        """
        Send a command string to the device and wait for a response.

        Returns:
            a response from the device.
        """
        return NotImplemented

    @dynamic_interface
    def set_range(self, range, auto=False):
        """
        Send a command string to the device and wait for a response.

        Returns:
            a response from the device.
        """
        return NotImplemented

    @dynamic_interface
    def set_diameter(self, diameter):
        """
        Send a command string to the device and wait for a response.

        Returns:
            a response from the device.
        """
        return NotImplemented

    @dynamic_interface
    def set_zero(self, autozero):
        """
        Send a command string to the device and wait for a response.

        Returns:
            a response from the device.
        """
        return NotImplemented


class ThorlabsPM100Simulator(ThorlabsPM100Interface):
    """
    The Thorlabs PM100 Simulator class.
    """

    def __init__(self):
        self._is_connected = True
        self._value = 0.0
        self._randomwalk = RandomWalk(start=20, boundary=(0.0, 100), scale=0.1, count=0)
        self._wavelength = 535
        self._range = {"range": 2, "auto": 0}
        self._average = 1
        self._diameter = 0.01
        self._autozero = {"set": False, "magnitude (W)": 0.002}

    def is_connected(self):
        return self._is_connected

    def is_simulator(self):
        return True

    def connect(self):
        self._is_connected = True

    def disconnect(self):
        self._is_connected = False

    def reconnect(self):
        self.connect()

    def info(self) -> str:
        return "PM100a - The Thorlabs PM100A Simulator"

    def get_value(self):
        return next(self._randomwalk)

    def get_average(self):
        return self._average

    def get_id(self) -> str:
        return self.info()

    def get_wavelength(self):
        "returns default values"
        return self._wavelength

    def get_range(self):
        "returns dummy range"
        return self._range

    def get_diameter(self):
        return self._diameter

    def get_autozero(self):
        return self._autozero

    def get_config(self):
        """Returns a dummy configuration."""
        measurement = {"Value": self._value, "Average number": self._average}
        return {
            "Measurement": measurement,
            "Correction Wavelength (nm)": self._wavelength,
            "Beam diameter (mm)": self._diameter,
            "Autozero correction": self._autozero,
            "Power Range": self._range,
        }

    def set_wavelength(self, wave):
        "returns default values"
        self._wavelength = wave
        return "wavelength set to: {self._wavelength}"

    def set_range(self, range_action, auto=False):
        # FIXME: the range_action parameter is not used in this method.
        self._range["auto"] = auto
        return self._range

    def set_average(self, average):
        self._average = average

    def set_diameter(self, diameter):
        self._diameter = diameter

    def set_zero(self, autozero):
        self._autozero["set"] = bool(autozero)


class ThorlabsPM100Controller(ThorlabsPM100Interface):
    def __init__(self):
        """Initialize the ThorlabsPM100Controller interface."""

        super().__init__()

        logger.debug("Initializing ThorlabsPM100Controller")

        try:
            self.thorlabs = ThorlabsPM100USBInterface()
            self.thorlabs.connect()

        except ThorlabsError as exc:
            logger.warning(f"ThorlabsError caught: Couldn't establish connection ({exc})")
            raise ThorlabsError(
                "Couldn't establish a connection with the Thorlabs PM100 USB controller."
            ) from exc

    def connect(self):
        """Connects to the Thorlabs PM100 device."""
        try:
            self.thorlabs.connect()
        except ThorlabsError as exc:
             logger.warning(f"ThorlabsError caught: Couldn't establish connection ({exc})")
             raise ConnectionError("Couldn't establish a connection with the Thorlabs PM100 USB controller.") from exc

    def disconnect(self):
         try:
             self.thorlabs.disconnect()
         except ThorlabsError as exc:
             raise ConnectionError("Couldn't establish a connection with the Thorlabs PM100 USB controller.") from exc

    def reconnect(self):
        if self.is_connected():
            self.disconnect()
        self.connect()

    def is_simulator(self):
        return False

    def is_connected(self):
        """Check if the Thorlabs Controller is connected."""
        return self.thorlabs.is_connected()

    def info(self) -> str:
        return self.thorlabs.info()

    def get_value(self) -> float:
        return self.thorlabs.get_value()

    def get_id(self):
        return self.thorlabs.get_id()

    def get_response(self, cmd_string):
        response = self.thorlabs.get_response(cmd_string)
        return response

    def get_wavelength(self) -> int:
        return self.thorlabs.get_wavelength()

    def get_range(self) -> dict:
        return self.thorlabs.get_range()

    def get_average(self):
        return self.thorlabs.get_average()

    def get_diameter(self) -> float:
        return self.thorlabs.get_diameter()

    def get_autozero(self) -> dict:
        return self.thorlabs.get_autozero()

    def get_config(self) -> dict:
        measurement = {
            "Value": self.thorlabs.get_value(),
            "Average number": self.thorlabs.get_average(),
        }
        wavelength = self.thorlabs.get_wavelength()
        beam = self.thorlabs.get_diameter()
        range = self.thorlabs.get_range()
        autozero = self.thorlabs.get_autozero()
        return {
            "Measurement": measurement,
            "Correction Wavelength (nm)": wavelength,
            "Beam diameter (mm)": beam,
            "Autozero correction": autozero,
            "Power Range": range,
        }

    def set_wavelength(self, wave):
        self.thorlabs.set_wavelength(wave)

    def set_average(self, average):
        self.thorlabs.set_average(average)

    def set_range(self, range_action, auto=False):
        old_range = self.thorlabs.get_range()
        if auto:
            self.thorlabs.autorange(int(auto))
        if not auto:
            if range_action == "up":
                self.thorlabs.range(round(old_range["range"] * 10, 4))
            elif range_action == "down":
                self.thorlabs.range(round(old_range["range"] * 0.1, 4))
            elif range_action is None:
                # Allows to switch from Auto to Manual range without changing the range
                pass

    def set_diameter(self, diameter):
        self.thorlabs.set_diameter(diameter)

    def set_zero(self, autozero):
        self.thorlabs.set_zero(autozero)

    @property
    def power_meter(self):
        return self.thorlabs.power_meter

    @property
    def instrument(self):
        return self.thorlabs.instrument


class ThorlabsPM100Proxy(Proxy, ThorlabsPM100Interface):
    """The ThorlabsPM100Proxy class is used to connect to the control server and send commands to
    the Thorlabs device remotely."""

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
