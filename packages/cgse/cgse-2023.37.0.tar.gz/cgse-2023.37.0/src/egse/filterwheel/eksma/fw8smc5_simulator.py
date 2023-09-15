import logging

from egse.settings import Settings
from egse.simulator import Simulator
from egse.command import Command
from egse.filterwheel.eksma.fw8smc5_interface import Fw8Smc5Interface

logger = logging.getLogger(__name__)

# Load the device protocol
DEVICE_PROTOCOL = Settings.load(filename='fw8smc5.yaml')['Commands']


class Fw8Smc5Simulator(Fw8Smc5Interface, Simulator):

    def __init__(self):
        super().__init__()

        # Create a dict of Command objects for each function
        self._commands = {}
        for name, items in DEVICE_PROTOCOL.items():
            self._commands[name] = Command(name, items['cmd'])

        self.connect()


    def is_simulator(self):

        return True
