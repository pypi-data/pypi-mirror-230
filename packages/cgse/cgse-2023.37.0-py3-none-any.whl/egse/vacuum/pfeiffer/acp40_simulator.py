import logging

from egse.settings import Settings
from egse.simulator import Simulator
from egse.command import Command
from egse.vacuum.pfeiffer.acp40_interface import Acp40Interface

logger = logging.getLogger(__name__)


class Acp40Simulator(Acp40Interface, Simulator):

    def __init__(self):
        super().__init__()
        self.connect()

    def is_simulator(self):
        return True

    def get_idn(self):
        return "VPACP40-VB.1 (simulator)"

    def get_device_status(self):
        return "000100,100000,000000,00000,0000,000,027,000,01597"

    def get_address(self):
        raise NotImplementedError

    def set_standby(self):
        raise NotImplementedError

    def set_nominal_speed(self):
        raise NotImplementedError

    def set_rpm(self, rpm):
        raise NotImplementedError

    def set_enable(self, enable):
        raise NotImplementedError
