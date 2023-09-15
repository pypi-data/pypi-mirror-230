import logging

from egse.settings import Settings
from egse.simulator import Simulator
from egse.command import Command
from egse.vacuum.pfeiffer.tpg261_interface import Tpg261Interface

logger = logging.getLogger(__name__)

# Load the device protocol
DEVICE_PROTOCOL = Settings.load(filename='tpg261.yaml')['Commands']


class Tpg261Simulator(Tpg261Interface, Simulator):

    def __init__(self):
        super().__init__()
        self.connect()

    def is_simulator(self):
        return True
    
    def get_idn(self):
        return "TPG261 (simulator)"