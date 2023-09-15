import logging
import random

from egse.decorators import dynamic_interface
from egse.device import DeviceInterface
from egse.proxy import Proxy
from egse.settings import Settings
from egse.vacuum.beaglebone.beaglebone_devif import BeagleboneDeviceInterface
from egse.zmq_ser import connect_address

logger = logging.getLogger(__name__)

CTRL_SETTINGS = Settings.load("BeagleBone Valve Control Server")
DEVICE_SETTINGS = Settings.load(filename='beaglebone.yaml')


class BeagleboneError(Exception):
    pass


class BeagleboneInterface(DeviceInterface):
    """ BeagleBone Valve controller base class."""

    @dynamic_interface
    def set_valve(self, valve_idx, valve_state):
        """ Sets the state of the selected valve to the given state """
        return NotImplemented

    @dynamic_interface
    def get_valve(self, valve_idx):
        """ Returns the state of the selected valve """
        return NotImplemented



class BeagleboneSimulator(BeagleboneInterface):
   """ BeagleBone Valve controller simulator class. """

   def __init__(self):
        self.valvefb = {
            "LN2_SHROUD_RMT"     : 1,
            "LN2_TEB-FEE_RMT"    : 1,
            "LN2_TEB-TOU_RMT"    : 1,
            "LN2_TRAP_RMT"       : 1,
            "N2_SHROUD_RMT"      : 1,
            "N2_TEB-FEE_RMT"     : 1,
            "N2_TEB-TOU_RMT"     : 1,
            "N2_TRAP_RMT"        : 1,
            "VENT_VALVE_RMT"     : 1,
            "GATE_VALVE_RMT"     : 1,
            "LN2_SHROUD_FB"      : random.getrandbits(1),
            "LN2_TEB-FEE_FB"     : random.getrandbits(1),
            "LN2_TEB-TOU_FB"     : random.getrandbits(1),
            "LN2_TRAP_FB"        : random.getrandbits(1),
            "N2_SHROUD_FB"       : random.getrandbits(1),
            "N2_TEB-FEE_FB"      : random.getrandbits(1),
            "N2_TEB-TOU_FB"      : random.getrandbits(1),
            "N2_TRAP_FB"         : random.getrandbits(1),
            "VENT_VALVE_FB"      : random.getrandbits(1),
            "GATE_OPEN_FB"       : random.getrandbits(1),
            "GATE_CLOSE_FB"      : random.getrandbits(1),
            "INTRLCK_DOOR_FB"    : random.getrandbits(1)
        }
        
        self.valves = {
            "MV011" : self.valvefb['LN2_SHROUD_FB'],
            "MV012" : self.valvefb['LN2_TEB-FEE_FB'],
            "MV013" : self.valvefb['LN2_TEB-TOU_FB'],
            "MV014" : self.valvefb['LN2_TRAP_FB'],
            "MV021" : self.valvefb['N2_SHROUD_FB'],
            "MV022" : self.valvefb['N2_TEB-FEE_FB'],
            "MV032" : self.valvefb['N2_TEB-TOU_FB'],
            "MV042" : self.valvefb['N2_TRAP_FB'],
            'MV001' : self.valvefb['VENT_VALVE_FB'],
            'MV002' : self.valvefb['GATE_OPEN_FB']
        }
        
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

   def set_valve(self, valve_idx, valve_state):
       logger.info(f"Settings {valve_idx} to {valve_state}")
       self.valves[valve_idx] = valve_state

   def get_valve(self, valve_idx):
       return self.valvefb[valve_idx]


class BeagleboneController(BeagleboneInterface):

    def __init__(self):
        super().__init__()

        logger.debug('Initalizing BeagleBone Valve Controller')

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

    def set_valve(self, valve_idx, valve_state):
        return self.beaglebone.set_valve(valve_idx, valve_state)

    def get_valve(self, valve_idx):
        return self.beaglebone.get_valve(valve_idx)



class BeagleboneProxy(Proxy, BeagleboneInterface):
    def __init__(self, protocol=CTRL_SETTINGS.PROTOCOL,
                 hostname=CTRL_SETTINGS.HOSTNAME,
                 port=CTRL_SETTINGS.COMMANDING_PORT):
        super().__init__(connect_address(protocol, hostname, port))
