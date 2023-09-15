import logging

from egse.vacuum.keller.kellerBus import kellerBus
from egse.command import Command
from egse.settings import Settings
from egse.setup import get_setup
from egse.vacuum.keller.leo3_interface import Leo3Interface

logger = logging.getLogger(__name__)

# Load the device settings from the global common-egse config file
DEVICE_SETTINGS = Settings.load("KELLER Leo3 Controller")

# Load the device protocol
DEVICE_PROTOCOL = Settings.load(filename='leo3.yaml')['Commands']

class Leo3Controller(kellerBus, Leo3Interface):
    def __init__(self, port=None, baudrate=None, timeout=1):

        port = DEVICE_SETTINGS.PORT if not port else port
        baudrate = DEVICE_SETTINGS.BAUDRATE if not baudrate else baudrate
        
        super().__init__(port, baudrate, timeout)
    
    def connect(self):
        self.open()
    
    def disconnect(self):
        self.close()
    
    def reconnect(self):
        self.close()
        self.open()
    
    def is_connected(self):
        return self.is_open
    
    def is_simulator(self):
        return False
    
    def get_idn(self, address):
        return self.F69(address)

    def initialize(self, address):
        return self.F48(address)
    
    def get_pressure(self, address):
        p, stat = self.F73(address, 1)
        return p, stat
    
    def get_temperature(self, address):
        t, stat = self.F73(address, 4)
        return t, stat
    
class Leo3Simulator():
    def __init__(self):
        pass
    
    def connect(self):
        return True
    
    def disconnect(self):
        return True
    
    def reconnect(self):
        return True
    
    def is_connected(self):
        return True
    
    def is_simulator(self):
        return False
    
    
    def get_pressure(self, address, index):
        return 10, 1
    
    def get_temperature(self, address, index):
        return 20, 1
    
if __name__ == "__main__":
    leo = Leo3Controller()
    print(leo.get_pressure(1, 1))
