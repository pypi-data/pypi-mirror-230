import logging

from egse.proxy import Proxy
from egse.decorators import dynamic_interface
from egse.device import DeviceInterface
from egse.settings import Settings
from egse.tempcontrol.agilent.agilent34972_devif import Agilent34972Error
from egse.tempcontrol.agilent.agilent34972_devif import Agilent34972DeviceInterface
from egse.zmq_ser import connect_address

logger = logging.getLogger(__name__)

DEVICE_SETTINGS = Settings.load(filename='agilent34972.yaml')
CTRL_SETTINGS = Settings.load("Agilent 34972 Control Server")


class Agilent34972Interface(DeviceInterface):
    """ Agilent 34972 base class."""

    @dynamic_interface
    def get_idn(self):
        """ Get Agilent34972 IDN message. """
        return NotImplemented

    @dynamic_interface
    def read_resistance_temperature(self, scan_list=None):
        """ Measure 4-wire resistance. """
        return NotImplemented
    
    @dynamic_interface
    def trigger_scan(self):
        """ Perform a scan of th specified channels"""
        return NotImplemented


class Agilent34972Simulator(Agilent34972Interface):
    def __init__(self):
       self._is_connected = True

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

    def get_idn(self, dev_idx):
       return 'Agilent34972'

    def read_resistance_temperature(self):
        return [0, 0, 0, 0], [0, 0, 0, 0]
    
    def trigger_scan(self):
        pass

class Agilent34972Controller(Agilent34972Interface):

    # The device index is used to distinguish between the 2 agilent34972 devices
    def __init__(self, device_index):
        super().__init__()

        logger.debug(f'Initalizing Agilent34972 Controller {device_index}')

        try:
            self.agilent = Agilent34972DeviceInterface(device_index)
        except Agilent34972Error as exc:
            logger.warning(f"Agilent34972Error caught: Couldn't establish connectin ({exc})")
            raise Agilent34972Error(
                "Couldn't establish a connection with Agilent34972 controller."
            ) from exc

    def is_simulator(self):
        return False

    def is_connected(self):
        return self.agilent.is_connected()

    def connect(self):
        if not self.agilent.is_connected():
            self.agilent.connect()

    def disconnect(self):
        self.agilent.disconnect()

    def reconnect(self):
        self.agilent.reconnect()

    def get_idn(self):
        return self.agilent.get_idn()

    def read_resistance_temperature(self):
        return self.agilent.read_resistance_temperature()
    
    def trigger_scan(self):
        return self.agilent.trigger_scan()

class Agilent34972Proxy(Proxy, Agilent34972Interface):
    def __init__(self, agilent_index: int):
        self.name = "DAQ"+str(agilent_index)

        super().__init__(connect_address(CTRL_SETTINGS.PROTOCOL, CTRL_SETTINGS.HOSTNAME, CTRL_SETTINGS[self.name]["COMMANDING_PORT"]), timeout=20000)
