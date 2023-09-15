from egse.device import DeviceInterface
from egse.decorators import dynamic_interface


class EnsembleInterface(DeviceInterface):
    @dynamic_interface
    def get_idn(self):
        return NotImplemented

    @dynamic_interface
    def reset(self):
        return NotImplemented

    @dynamic_interface
    def abort(self, axis):
        return NotImplemented

    @dynamic_interface
    def clear_errors(self):
        return NotImplemented

    @dynamic_interface
    def get_status(self, axis):
        return NotImplemented

    @dynamic_interface
    def get_fault(self, axis):
        return NotImplemented

    @dynamic_interface
    def get_plane_status(self):
        return NotImplemented

    @dynamic_interface
    def set_blocking(self, axis, enable):
        return NotImplemented

    @dynamic_interface
    def get_actual_position(self, axis):
        return NotImplemented

    @dynamic_interface
    def get_command_position(self, axis):
        return NotImplemented

    @dynamic_interface
    def get_error_position(self, axis):
        return NotImplemented

    @dynamic_interface
    def get_command_velocity(self, axis):
        return NotImplemented

    @dynamic_interface
    def get_actual_velocity(self, axis):
        return NotImplemented

    @dynamic_interface
    def get_actual_current(self, axis):
        return NotImplemented

    @dynamic_interface
    def get_command_current(self, axis):
        return NotImplemented

    @dynamic_interface
    def enable_axis(self, axis):
        return NotImplemented

    @dynamic_interface
    def enable_axes(self):
        return NotImplemented
    
    @dynamic_interface
    def disable_axis(self, axis):
        return NotImplemented

    @dynamic_interface
    def disable_axes(self):
        return NotImplemented

    @dynamic_interface
    def set_absolute(self):
        return NotImplemented

    @dynamic_interface
    def set_incremental(self):
        return NotImplemented

    @dynamic_interface
    def set_wait_mode(self, mode):
        return NotImplemented

    @dynamic_interface
    def move_axis_degrees(self, axis, position):
        return NotImplemented

    @dynamic_interface
    def move_axes_degrees(self, position_x, position_y):
        return NotImplemented

    @dynamic_interface
    def home_axes(self):
        return NotImplemented

    @dynamic_interface
    def home_axis(self, axis):
        return NotImplemented

    @dynamic_interface
    def is_moving(self, axis):
        return NotImplemented

    @dynamic_interface
    def is_homed(self, axis):
        return NotImplemented

    @dynamic_interface
    def get_parameter(self, index):
        return NotImplemented

    @dynamic_interface
    def set_parameter(self, index, value):
        return NotImplemented

    @dynamic_interface
    def print_status(self):
        return NotImplemented

    @dynamic_interface
    def query(self, command):
        return NotImplemented
