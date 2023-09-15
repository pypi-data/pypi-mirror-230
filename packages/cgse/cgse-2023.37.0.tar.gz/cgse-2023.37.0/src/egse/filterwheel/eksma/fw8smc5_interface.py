from egse.device import DeviceInterface
from egse.decorators import dynamic_interface


class Fw8Smc5Interface(DeviceInterface):

    @dynamic_interface
    def get_idn(self):
        return NotImplemented

    @dynamic_interface
    def get_error_flags(self):
        return NotImplemented

    @dynamic_interface
    def is_moving(self):
        return NotImplemented

    @dynamic_interface
    def get_position_steps(self, id):
        return NotImplemented

    @dynamic_interface
    def set_position_steps(self, id, position):
        return NotImplemented

    @dynamic_interface
    def get_position_wheels(self):
        return NotImplemented

    @dynamic_interface
    def set_position_wheels(self, position_a, position_b):
        return NotImplemented

    @dynamic_interface
    def get_position_index(self):
        return NotImplemented

    @dynamic_interface
    def set_position_index(self, index):
        return NotImplemented

    @dynamic_interface
    def get_relative_intensity(self):
        return NotImplemented

    @dynamic_interface
    def set_relative_intensity(self, rel_intensity):
        return NotImplemented

    @dynamic_interface
    def intensity_level_up(self):
        return NotImplemented

    @dynamic_interface
    def intensity_level_down(self):
        return NotImplemented

    @dynamic_interface
    def home(self):
        return NotImplemented
    
    @dynamic_interface
    def set_position_wheel(self, id, position):
        return NotImplemented
