from egse.simulator import Simulator
from egse.shutter.thorlabs.sc10_interface import Sc10Interface

class Sc10Simulator(Sc10Interface, Simulator):

    def __init__(self):
        super().__init__()
        self._is_enable = False


    def is_simulator(self):
        return True

    def get_idn(self):
        return NotImplemented

    def get_enable(self):
        return self._is_enable

    def toggle_enable(self):
        if(self._is_enable):
            self._is_enable = False
        else:
            self._is_enable = True
            
    def set_mode(self, mode):
        return NotImplemented

    def set_open_duration(self, duration):
        return NotImplemented
