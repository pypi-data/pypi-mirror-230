from calendar import day_abbr
import logging

from egse.decorators import dynamic_interface
from egse.device import DeviceInterface
from egse.proxy import Proxy
from egse.settings import Settings
from egse.lampcontrol.beaglebone.beaglebone_devif import BeagleboneDeviceInterface
from egse.zmq_ser import connect_address

logger = logging.getLogger(__name__)

CTRL_SETTINGS = Settings.load("BeagleBone Lamp Control Server")
DEVICE_SETTINGS = Settings.load(filename='beaglebone.yaml')


class BeagleboneError(Exception):
    pass


class BeagleboneInterface(DeviceInterface):
    """ BeagleBone GSM controller base class."""

    @dynamic_interface
    def set_lamp(self, state):
        return NotImplemented

    @dynamic_interface
    def set_interlock(self, state):
        return NotImplemented

    @dynamic_interface
    def get_lamp_on(self):
        return NotImplemented

    @dynamic_interface
    def get_laser_on(self):
        return NotImplemented

    @dynamic_interface
    def get_lamp_module_fault(self):
        return NotImplemented

    @dynamic_interface
    def get_controller_fault(self):
        return NotImplemented

    @dynamic_interface
    def fix_controller_fault(self):
        return NotImplemented


class BeagleboneSimulator(BeagleboneInterface):

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

    def set_lamp(self, state):
        pass

    def set_interlock(self, state):
        pass

    def get_lamp_on(self):
        return 0

    def get_laser_on(self):
        return 0

    def get_lamp_module_fault(self):
        return 0

    def get_controller_fault(self):
        return 0


class BeagleboneController(BeagleboneInterface):

    def __init__(self):
        super().__init__()

        logger.debug('Initalizing BeagleBone GSM Controller')

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

    def set_lamp(self, state):
        self.beaglebone.set_lamp(state)


    def set_interlock(self, state):
        self.beaglebone.set_interlock(state)


    def get_lamp_on(self):
        return self.beaglebone.get_lamp_on()


    def get_laser_on(self):
        return self.beaglebone.get_laser_on()


    def get_lamp_module_fault(self):
        return self.beaglebone.get_lamp_module_fault()


    def get_controller_fault(self):
        return self.beaglebone.get_controller_fault()

    def fix_controller_fault(self):
        self.beaglebone.fix_controller_fault()


class BeagleboneProxy(Proxy, BeagleboneInterface):
    def __init__(self, protocol=CTRL_SETTINGS.PROTOCOL,
                 hostname=CTRL_SETTINGS.HOSTNAME,
                 port=CTRL_SETTINGS.COMMANDING_PORT):
        super().__init__(connect_address(protocol, hostname, port))


if __name__ == "__main__":
    bbb = BeagleboneProxy()
    
    print(f"Lamp state: {bbb.get_lamp_on()}\n"\
          f"Laster state: {bbb.get_laser_on()}\n"\
          f"Module fault: {bbb.get_lamp_module_fault()}\n"\
          f"Controller fault: {bbb.get_controller_fault()}\n")
    bbb.set_lamp(True)
    
    while not bbb.get_lamp_on():
        pass
    
    while not bbb.get_laser_on():
        pass
    
    print(f"Lamp state: {bbb.get_lamp_on()}\n"\
          f"Laster state: {bbb.get_laser_on()}\n"\
          f"Module fault: {bbb.get_lamp_module_fault()}\n"\
          f"Controller fault: {bbb.get_controller_fault()}")