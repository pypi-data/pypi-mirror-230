from egse.simulator import Simulator
from egse.vacuum.instrutech.igm402_interface import Igm402Interface


class Igm402Simulator(Igm402Interface, Simulator):

    def __init__(self):
        super().__init__()

    def is_simulator(self):
        return True

    def get_idn(self):
        return NotImplemented

    def get_status(self):
        return NotImplemented

    def get_ion_gauge_pressure(self):
        return 0.0

    def get_cgn_pressure(self, index):
        assert index in [1, 2], 'index must be either 1 or 2'
        return 0.0

    def set_filament_enable(self, enable):
        return NotImplemented

    def set_enable_degas(self, enable):
        return NotImplemented

    def set_emission_current(self, current):
        return NotImplemented

    def set_filament(self, type):
        return NotImplemented
