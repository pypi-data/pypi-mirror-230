import logging

from egse.proxy import Proxy
from egse.decorators import dynamic_interface
from egse.device import DeviceInterface
from egse.settings import Settings
from egse.tempcontrol.agilent.agilent34970_devif import Agilent34970Error
from egse.tempcontrol.agilent.agilent34970_devif import Agilent34970DeviceInterface
from egse.zmq_ser import connect_address

logger = logging.getLogger(__name__)

DEVICE_SETTINGS = Settings.load(filename='agilent34970.yaml')
CTRL_SETTINGS = Settings.load("Agilent 34970 Control Server")

class Agilent34970Interface(DeviceInterface):
    """ Agilent 34970 base class."""

    @dynamic_interface
    def get_idn(self):
        """ Get Agilent34970 IDN message. """
        return NotImplemented

    @dynamic_interface
    def read_resistance_temperature(self):
        """ Measure 4-wire resistance. """
        return NotImplemented

    @dynamic_interface
    def trigger_scan(self):
        return NotImplemented

class Agilent34970Simulator(Agilent34970Interface):

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
       return 'Agilent34970'


    def read_resistance_temperature(self):
        return [0, 0, 0, 0], [0, 0, 0, 0]

    def trigger_scan(self):
        pass

class Agilent34970Controller(Agilent34970Interface):

    def __init__(self, device_index):
        super().__init__()

        logger.debug('Initalizing Agilent34970 Controller')

        try:
            self.agilent = Agilent34970DeviceInterface(device_index)
        except Agilent34970Error as exc:
            logger.warning(f"Agilent34970Error caught: Couldn't establish connectin ({exc})")
            raise Agilent34970Error(
                "Couldn't establish a connection with Agilent34970 controller."
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

class Agilent34970Proxy(Proxy, Agilent34970Interface):
    def __init__(self, agilent_index: int):
        self.name = "DAQ"+str(agilent_index)

        super().__init__(connect_address(CTRL_SETTINGS.PROTOCOL, CTRL_SETTINGS.HOSTNAME, CTRL_SETTINGS[self.name]["COMMANDING_PORT"]), timeout=20000)
