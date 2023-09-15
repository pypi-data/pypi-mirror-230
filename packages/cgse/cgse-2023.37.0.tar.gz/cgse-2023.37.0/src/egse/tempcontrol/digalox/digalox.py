import logging
import random

from egse.command import ClientServerCommand
from egse.proxy import Proxy
from egse.decorators import dynamic_interface
from egse.device import DeviceInterface
from egse.serialdevice import SerialDevice
from egse.settings import Settings
from egse.zmq_ser import connect_address

logger = logging.getLogger(__name__)

DEVICE_SETTINGS = Settings.load(filename='digalox.yaml')
CTRL_SETTINGS = Settings.load("Digalox LN2 level monitor Control Server")


class DigaloxError(Exception):
    pass

class DigaloxCommand(ClientServerCommand):
    def get_cmd_string(self, *args, **kwargs):
        out = super().get_cmd_string(*args, **kwargs)
        return out + '\n'

class DigaloxInterface(DeviceInterface):
    """ Digalox LN2 level monitor Interface base class."""

    @dynamic_interface
    def get_value(self):
        """ Get Digalox value """
        return NotImplemented

class DigaloxSimulator(DigaloxInterface):
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

    def get_value(self):
        return random.random()
        
        
class DigaloxController(DigaloxInterface):

    def __init__(self):
        super().__init__()

        logger.debug('Initalizing Digalox controller')
        
        settings = Settings.load(f'Digalox LN2 level monitor Controller')
        self._port = settings.PORT
        self._baudrate = settings.BAUDRATE
        
        try:
            self.digalox = SerialDevice(self._port ,
                                        baudrate=self._baudrate,
                                        terminator='\r',
                                        timeout=2)
        except ConnectionError as ex:
            raise DigaloxError("Could not connecto to Digalox LN2 level monitor") from ex
        self.digalox.connect()
        
    def is_simulator(self):
        return False

    def is_connected(self):
        return self.digalox.is_connected()

    def connect(self):
        if not self.digalox.is_connected():
            self.digalox.connect()

    def disconnect(self):
        self.digalox.disconnect()

    def reconnect(self):
        self.digalox.reconnect()

    def get_value(self):
        response = self.digalox.query('value?')
        value = response.split(';')[-1]
        return float(value)
        
        

class DigaloxProxy(Proxy, DigaloxInterface):
    def __init__(self):
        super().__init__(connect_address(CTRL_SETTINGS.PROTOCOL, 
                                         CTRL_SETTINGS.HOSTNAME, 
                                         CTRL_SETTINGS.COMMANDING_PORT), 
                         timeout=20000)
