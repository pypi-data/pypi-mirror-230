import logging

from egse.settings import Settings
from egse.simulator import Simulator
from egse.command import Command
from egse.vacuum.mks.evision_interface import EvisionInterface

logger = logging.getLogger(__name__)

# Load the device protocol
DEVICE_PROTOCOL = Settings.load(filename='evision.yaml')['Commands']


class EvisionSimulator(EvisionInterface, Simulator):

    def __init__(self):
        super().__init__()

        # Create a dict of Command objects for each function
        self._commands = {}
        for name, items in DEVICE_PROTOCOL.items():
            self._commands[name] = Command(name, items['cmd'])

        self.connect()
