from egse.device import DeviceInterface
from egse.decorators import dynamic_interface


class Smd3Interface(DeviceInterface):

    @dynamic_interface
    def get_idn(self):
        return NotImplemented
    
    @dynamic_interface
    def clear_flags(self):
        return NotImplemented
    
    @dynamic_interface
    def run_homing(self):
        return NotImplemented
    
    @dynamic_interface
    def move_mask_fov(self, enable):
        return NotImplemented

    @dynamic_interface
    def mask_in_fov(self):
        return NotImplemented
    
    @dynamic_interface
    def emergency_stop(self):
        return NotImplemented
    
    @dynamic_interface
    def bake(self):
        return NotImplemented
    
    @dynamic_interface
    def actual_position(self):
        return NotImplemented
    
    @dynamic_interface
    def actual_position_mm(self):
        return NotImplemented
    
    @dynamic_interface
    def actual_frequency(self):
        return NotImplemented
    
    @dynamic_interface
    def absolute_move(self):
        return NotImplemented
    
    @dynamic_interface
    def relative_move(self):
        return NotImplemented
