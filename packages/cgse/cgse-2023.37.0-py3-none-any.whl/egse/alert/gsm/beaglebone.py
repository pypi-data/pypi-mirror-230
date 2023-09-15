import logging
import time

from egse.decorators import dynamic_interface
from egse.device import DeviceInterface
from egse.proxy import Proxy
from egse.settings import Settings
from egse.alert.gsm.beaglebone_devif import BeagleboneDeviceInterface
from egse.zmq_ser import connect_address

logger = logging.getLogger(__name__)

CTRL_SETTINGS = Settings.load("BeagleBone GSM Control Server")
DEVICE_SETTINGS = Settings.load(filename='beaglebone.yaml')


class BeagleboneError(Exception):
    pass


class BeagleboneInterface(DeviceInterface):
    """ BeagleBone base class."""
    @dynamic_interface
    def set_alert(self, pin):
        NotImplemented
        
    @dynamic_interface
    def unset_alert(self, pin):
        NotImplemented
    @dynamic_interface
    def get_alert(self, pin):
        NotImplemented

    @dynamic_interface
    def toggle_watchdog(self):
        NotImplemented


class BeagleboneSimulator(BeagleboneInterface):
   """ BeagleBone simulator class. """

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



class BeagleboneController(BeagleboneInterface):

    def __init__(self):
        super().__init__()

        logger.debug('Initalizing BeagleBone Controller')

        try:
            self.beaglebone = BeagleboneDeviceInterface()
            self.beaglebone.connect()
        except BeagleboneError as exc:
            logger.warning(f"BeagleboneError caught: Couldn't establish connection ({exc})")
            raise BeagleboneError(
                "Couldn't establish a connection with BeagleBone controller."
            ) from exc

    def is_simulator(self):
        return False

    def is_connected(self):
        return self.beaglebone.is_connected()

    def connect(self):
        if not self.beaglebone.is_connected():
            self.beaglebone.connect()

    def disconnect(self):
        self.beaglebone.disconnect()

    def reconnect(self):
        self.beaglebone.reconnect()
        
    def set_alert(self, pin):
        self.beaglebone.set_alert(pin)

    def unset_alert(self, pin):
        self.beaglebone.unset_alert(pin)

    def get_alert(self, pin):
        return self.beaglebone.get_alert(pin)

    def toggle_watchdog(self):
        self.beaglebone.toggle_watchdog()



class BeagleboneProxy(Proxy, BeagleboneInterface):
    def __init__(self, protocol=CTRL_SETTINGS.PROTOCOL,
                 hostname=CTRL_SETTINGS.HOSTNAME,
                 port=CTRL_SETTINGS.COMMANDING_PORT):
        super().__init__(connect_address(protocol, hostname, port))

if __name__ == "__main__":
    bb = BeagleboneProxy()
    bb.set_alert(0)
    bb.set_alert(1)
    bb.set_alert(2)
    
    time.sleep(2)
    
    bb.get_alert(0)
    bb.get_alert(1)
    bb.get_alert(2)
    
    time.sleep(2)
    
    bb.unset_alert(0)
    bb.unset_alert(1)
    bb.unset_alert(2)
    
    time.sleep(2)
    
    bb.get_alert(0)
    bb.get_alert(1)
    bb.get_alert(2)