from calendar import day_abbr, day_name
from egse.device import DeviceInterface
from egse.decorators import dynamic_interface
from egse.command import ClientServerCommand

class Tpg261Command(ClientServerCommand):
    pass

class Tpg261Interface(DeviceInterface):
    @dynamic_interface
    def connect(self):
        return NotImplemented
    
    @dynamic_interface
    def disconnect(self):
        return NotImplemented
    
    @dynamic_interface
    def reconnect(self):
        return NotImplemented
    
    @dynamic_interface
    def is_connected(self):
        return NotImplemented
    
    @dynamic_interface
    def is_simulator(self):
        return NotImplemented
    
    @dynamic_interface
    def get_idn(self):
        return NotImplemented
    
    @dynamic_interface
    def get_errors(self):
        return NotImplemented
    
    @dynamic_interface
    def reset(self):
        return NotImplemented
    
    @dynamic_interface
    def turn_off_gauge(self, gauge):
        return NotImplemented
    
    @dynamic_interface
    def turn_on_gauge(self, gauge):
        return NotImplemented
    
    @dynamic_interface
    def get_gauge_pressure(self, gauge):
        return NotImplemented
    
    @dynamic_interface
    def request(self, command):
        return NotImplemented
    
    @dynamic_interface
    def enquire(self):
        return NotImplemented