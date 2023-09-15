from egse.device import DeviceInterface
from egse.decorators import dynamic_interface

class Acp40Interface(DeviceInterface):

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
    def get_device_status(self):
        return NotImplemented

    @dynamic_interface
    def get_address(self):
        return NotImplemented

    @dynamic_interface
    def set_standby(self):
        return NotImplemented

    @dynamic_interface
    def set_nominal_speed(self):
        return NotImplemented

    @dynamic_interface
    def set_rpm(self, rpm):
        return NotImplemented

    @dynamic_interface
    def set_enable(self, enable):
        return NotImplemented
