from egse.device import DeviceInterface
from egse.decorators import dynamic_interface


class Igm402Interface(DeviceInterface):

    @dynamic_interface
    def get_idn(self):
        return NotImplemented

    @dynamic_interface
    def get_status(self):
        return NotImplemented

    @dynamic_interface
    def get_system_pressure(self):
        return NotImplemented

    @dynamic_interface
    def get_ion_gauge_pressure(self):
        return NotImplemented

    @dynamic_interface
    def get_cgn_pressure(self, index):
        return NotImplemented

    @dynamic_interface
    def set_filament_enable(self, enable):
        return NotImplemented

    @dynamic_interface
    def set_enable_degas(self, enable):
        return NotImplemented

    @dynamic_interface
    def set_emission_current(self, current):
        return NotImplemented

    @dynamic_interface
    def set_filament(self, type):
        return NotImplemented

    @dynamic_interface
    def set_trip_point_i_low(self, pressure):
        return NotImplemented

    @dynamic_interface
    def set_trip_point_i_high(self, pressure):
        return NotImplemented
