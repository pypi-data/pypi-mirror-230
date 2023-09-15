import logging
from random import seed, randint
from egse.command import ClientServerCommand
from egse.decorators import dynamic_interface
from egse.device import DeviceInterface
from egse.proxy import Proxy
from egse.settings import Settings
from egse.zmq_ser import connect_address

logger = logging.getLogger(__name__)

CTRL_SETTINGS = Settings.load("SPID Control Server")
DEVICE_SETTINGS = Settings.load(filename='spid.yaml')


class PidError(Exception):
    pass


class PidCommand(ClientServerCommand):
    def get_cmd_string(self, *args, **kwargs):
        return super().get_cmd_string(*args, **kwargs)


class PidInterface(DeviceInterface):
    """ PID base class."""

    @dynamic_interface
    def set_temperature(self, heater_index, setpoint_temperature):
        """ PID setpoint temperature. """
        return NotImplemented

    @dynamic_interface
    def get_temperature(self, heater_index):
        return NotImplemented

    @dynamic_interface
    def enable(self, channel):
        return NotImplemented

    @dynamic_interface
    def disable(self, channel):
        return NotImplemented
    
    @dynamic_interface
    def get_running(self, channel):
        return NotImplemented
    
    @dynamic_interface
    def set_pid_parameters(self, channel, Kp, Ki, Kd, int_max=1000, int_min=0, reset=True):
        return NotImplemented
    
    @dynamic_interface
    def get_pid_parameters(self, channel):
        return NotImplemented


class PidSimulator(PidInterface):
   """ PID simulator class. """

   def __init__(self):
       self._is_connected = True
       seed()
       self.running = [1, 1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0]
       self.setpoints = [randint(-180, +250) for x in range(0, 14)]
       self.temperature = [randint(-180, +250) for x in range(0, 14)]
       self.timestamp =  [0 for x in range(0, 14)]
       self.errors   = [randint(0, 200) for x in range(0, 14)]
       self.isum = [randint(0, 900) for x in range(0, 14)]
       self.inputs = [randint(-180, +250) for x in range(0, 14)]
       self.outputs = [randint(-180, +250) for x in range(0, 14)]



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

   def set_temperature(self, heater_idx, setpoint_temperature):
       logger.info("Settings temperature forPID {heater_idx} to {setpoint}")
       self.setpoints[heater_idx] = setpoint_temperature
       self.temperature[heater_idx] = setpoint_temperature - 10

   def enable(self, channel):
       logger.info(f"Enabling {channel}")
       self.running[channel] = 1

   def disable(self, channel):
       logger.info(f"Disabling {channel}")
       self.running[channel] = 0

class PidProxy(Proxy, PidInterface):
    def __init__(self, protocol=CTRL_SETTINGS.PROTOCOL,
                 hostname=CTRL_SETTINGS.HOSTNAME,
                 port=CTRL_SETTINGS.COMMANDING_PORT):
        super().__init__(connect_address(protocol, hostname, port))
