from egse.device import DeviceInterface
from egse.decorators import dynamic_interface


class Leo3Interface(DeviceInterface):

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
    def get_pressure(self, address, index):
        return NotImplemented
    
    @dynamic_interface
    def get_temperature(self, address, index):
        return NotImplemented