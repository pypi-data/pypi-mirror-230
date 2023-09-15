from egse.device import DeviceInterface
from egse.decorators import dynamic_interface


class Sc10Interface(DeviceInterface):

    @dynamic_interface
    def get_idn(self):
        return NotImplemented

    @dynamic_interface
    def get_enable(self):
        return NotImplemented

    @dynamic_interface
    def toggle_enable(self):
        return NotImplemented

    @dynamic_interface
    def set_mode(self, mode):
        return NotImplemented

    @dynamic_interface
    def set_open_duration(self, duration):
        return NotImplemented
