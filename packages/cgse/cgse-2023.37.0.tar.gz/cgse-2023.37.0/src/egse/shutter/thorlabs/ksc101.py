import logging

from egse.decorators import dynamic_interface
from egse.device import DeviceInterface
from egse.proxy import Proxy
from egse.settings import Settings
from egse.shutter.thorlabs.ksc101_devif import ShutterKSC101Error
from egse.shutter.thorlabs.ksc101_devif import ShutterKSC101USBInterface
from egse.zmq_ser import connect_address


logger = logging.getLogger(__name__)

CTRL_SETTINGS = Settings.load("Shutter KSC101 Control Server")
DEVICE_SETTINGS = Settings.load(filename="ksc101.yaml")


class ShutterKSC101Interface(DeviceInterface):
    """
    The Shutter KSC101 base class.
    """

    @dynamic_interface
    def set_mode(self):
        """
        Sets the Shutter KSC101 Controller control mode
        """
        return NotImplemented

    @dynamic_interface
    def set_enable(self):
        """
        Sets the Shutter KSC101 Controller control mode
        """
        return NotImplemented

    @dynamic_interface
    def set_cycle(self):
        """
        Sets the Shutter KSC101 Controller cycling parameters
        """
        return NotImplemented

    @dynamic_interface
    def get_mode(self):
        """
        Sets the Shutter KSC101 Controller control mode
        """
        return NotImplemented

    @dynamic_interface
    def get_enable(self):
        """
        Sets the Shutter KSC101 Controller solenoid status
        """
        return NotImplemented

    @dynamic_interface
    def get_cycle(self):
        """
        Sets the Shutter KSC101 Controller cycle parameters
        """
        return NotImplemented


class ShutterKSC101Simulator(ShutterKSC101Interface):
    """
    The Thorlabs KSC101 Simulator class.
    """

    def __init__(self):
        self._is_connected = True
        self._mode = "single"
        self._cycle = {"Ontime": 1000, "Offtime": 1000, "Number of cycles": 10}
        self._status = False

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

    def set_mode(self, mode):
        self._mode = mode

    def set_enable(self, status):
        self._status = status

    def set_cycle(self, on, off, number):
        self._cycle["Ontime"] = on
        self._cycle["Offtime"] = off
        self._cycle["Number of cycles"] = number

    def get_mode(self) -> int:
        mode = {"manual": 0x01, "single": 0x02, "auto": 0x03, "trigger": 0x04}
        return mode[self._mode]

    def get_enable(self) -> int:
        return int(self._status)

    def get_cycle(self) -> dict:
        return self._cycle


class ShutterKSC101Controller(ShutterKSC101Interface):
    def __init__(self):
        """Initialize the Shutter KSC101 Controller interface."""

        super().__init__()

        logger.debug(f"Initializing Shutter KSC101 Controller")

        try:
            self.shutter = ShutterKSC101USBInterface()
            self.shutter.connect()

        except ShutterKSC101Error as exc:
            logger.warning(f"KSC101Error caught: Couldn't establish connection ({exc})")
            raise ShutterKSC101Error(
                "Couldn't establish a connection with the Shutter KSC101 controller."
            ) from exc

    # FIXME: connect and disconnect methods are not working properly

    def connect(self):
        """Connects to the Shutter KSC101 device.

        Raises:
            DeviceNotFoundError: when the Shutter KSC101 device is not connected.
        """
        try:
            self.shutter.connect()
        except ShutterKSC101Error as exc:
            raise ConnectionError("Couldn't establish a connection with the Shutter KSC101 controller.") from exc
        # if not self.shutter.is_connected():
        #     self.shutter.connect()

    def disconnect(self):
        try:
            self.shutter.disconnect()
        except ShutterKSC101Error as exc:
            raise ConnectionError("Couldn't establish a connection with the Shutter KSC101 controller.") from exc

    def reconnect(self):
        if self.is_connected():
            self.disconnect()
        self.connect()

    def is_simulator(self):
        return False

    def is_connected(self):
        """Check if the Shutter Controller is connected."""
        return self.shutter.is_connected()

    def get_response(self, cmd_string):
        response = self.shutter.get_response(cmd_string)
        return response

    def set_mode(self, mode):
        self.shutter.set_mode(mode)

    def set_enable(self, status):
        self.shutter.set_enable(status)

    def set_cycle(self, on, off, number):
        self.shutter.set_cycle(on, off, number)

    def get_mode(self) -> int:
        return self.shutter.get_mode()

    def get_enable(self) -> int:
        return self.shutter.get_enable()

    def get_cycle(self) -> dict:
        return self.shutter.get_cycle()


class ShutterKSC101Proxy(Proxy, ShutterKSC101Interface):
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
