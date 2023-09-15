import logging

from egse.settings import Settings
from egse.simulator import Simulator
from egse.command import Command
from egse.vacuum.pfeiffer.tc400_interface import Tc400Interface

logger = logging.getLogger(__name__)

# Load the device protocol
DEVICE_PROTOCOL = Settings.load(filename='tc400.yaml')['Commands']


class Tc400Simulator(Tc400Interface, Simulator):

    def __init__(self):
        super().__init__()
        self.connect()

    def is_simulator(self):
        return True
    
    def get_idn(self):
        return "TM 700 (simulator)"
