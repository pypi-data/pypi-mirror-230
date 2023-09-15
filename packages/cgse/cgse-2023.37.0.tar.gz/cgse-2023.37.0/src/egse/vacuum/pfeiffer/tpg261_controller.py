# from egse.serialdevice import SerialDevice, SerialTimeoutException
from serial import Serial, SerialTimeoutException
from egse.command import Command
from egse.settings import Settings
from egse.vacuum.pfeiffer.tpg261_interface import Tpg261Interface
import rich
from threading import Lock
from time import sleep

# Load the device settings from the global common-egse config file
DEVICE_SETTINGS = Settings.load("Pfeiffer TPG261 Controller")

# Load the device protocol
DEVICE_PROTOCOL = Settings.load(filename='tpg261.yaml')['Commands']

class Tpg261Controller(Tpg261Interface):
    
    def __init__(self, port=None, baudrate=None, address=None):
        # Load device configuration from the common-egse global config file
        self._port     = DEVICE_SETTINGS.PORT if port is None else port
        self._baudrate = DEVICE_SETTINGS.BAUDRATE if baudrate is None else baudrate
        
        self._lock = Lock()
        self._current_mode = None
        
        self.pressure_1 = 0
        
        # Initialize the serial device with the port and baudrate
        self.dev = Serial(port=self._port, baudrate=self._baudrate, timeout=1)

    def connect(self):
        self.dev.open()
    
    def disconnect(self):
        self.dev.close()
    
    def reconnect(self):
        self.dev.close()
        self.dev.open()

    def is_connected(self):
        return self.dev.is_open
    
    def is_simulator(self):
        return False

    def get_idn(self):
            if self._current_mode == 'PNR':
                return_string = self.enquire()
                return return_string
            else:
                if self.request(f"PNR\r\n"):
                    sleep(1)
                    return_string = self.enquire()
                    self._current_mode = 'PNR'
                    return return_string
                else:
                    raise RuntimeError('Command not acknowledged')
                sleep(1)

    def get_errors(self):
        if self._current_mode == 'ERR':
            return_string = self.enquire()
            return return_string
        else:
            if self.request(f"ERR\r\n"):
                self._current_mode = 'ERR'
                return_string = self.enquire()
                return int(return_string)

            else:
                raise RuntimeError('Command not acknowledged')           

    def reset(self):
        if self.request(f"RES\r\n"):
            return_string = self.enquire()
            return return_string
        else:
            raise RuntimeError('Command not acknowledged')
 
    def turn_off_gauge(self, gauge: int):
        assert 1 <= gauge <= 2
        if self.request(f"SEN1,0\r\n" if gauge == 1 else f"SEN0,1\r\n"):
            return_string = self.enquire()
            return return_string
        else:
            raise RuntimeError('Command not acknowledged')
    
    def turn_on_gauge(self, gauge: int):
        assert 1 <= gauge <= 2
        if self.request(f"SEN20\r\n" if gauge == 1 else f"SEN02\r\n"):
            return_string = self.enquire()
            return return_string
        else:
            raise RuntimeError('Command not acknowledged')
    
    def get_gauge_pressure(self):
            if self._current_mode == 'PR':
                return_string = self.enquire()
            else:
                if self.request('PR1\r\n'):
                    self._current_mode = 'PR'
                    return_string = self.enquire()
                else:
                    raise RuntimeError('Command not acknowledged')    
            return float(return_string[2:-2])     
    
    def send_command(self, command: str):
        try:
            with self._lock:
                self.dev.write(command.encode('ascii', 'ignore'))
        
        except SerialTimeoutException as e_timeout:
            raise ConnectionError("Serial timeout error") from e_timeout
    
    def request(self, command: str):
        self.send_command(command)

        try:
            with self._lock:
                return_string = self.dev.read_until(b'\r\n', size=None)
        except SerialTimeoutException as e_timeout:
            raise ConnectionError("Serial timeout during query") from e_timeout
           
        if return_string[0:1] == b'\x06':
            return True
        elif return_string[0:1] == b'\x05':
            return False
    
    def enquire(self):
        self.send_command('\x05')

        try:
            with self._lock:
                return_string = self.dev.read_until(b'\r\n', size=None)
        except SerialTimeoutException as e_timeout:
            raise ConnectionError("Serial timeout during query") from e_timeout

            
        return return_string
        
            
if __name__ == "__main__":
    tpg = Tpg261Controller()
    tpg.get_idn()
    tpg.get_gauge_pressure()
    tpg.get_gauge_pressure()
    tpg.get_errors()
    tpg.get_gauge_pressure()

