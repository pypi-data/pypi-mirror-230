import logging
import time
import os
from threading import Thread
import threading 
import rich

from egse.serialdevice import SerialDevice
from egse.command import Command
from egse.settings import Settings
from egse.stages.arun.smd3_interface import Smd3Interface
from egse.state import GlobalState

logger = logging.getLogger('smd3_controller')

# Load the device settings from the global common-egse config file
DEVICE_SETTINGS = Settings.load("Arun SMD3 Controller")

# Load the device protocol
# DEVICE_PROTOCOL = Settings.load(filename='smd3.yaml')['Commands']


class Smd3Exception(Exception):
    pass


class Smd3Mode:
    STEP                    = 0
    STEP_TRIGGERED_VELOCITY = 1
    REMOTE                  = 2
    JOYSTICK                = 3
    BAKE                    = 4
    HOME                    = 5

EFLAGS = {
    0: "TSHORT",
    1: "TOPEN",
    2: "TOVR",
    3: "MOTORSHORT",
    4: "EXTERNALDISABLE",
    5: "EMERGENCYSTOP",
    6: "CONFIGURATIONERROR"
}

SFLAGS = {
    0: "JSCON",
    1: "LIMITNEGATIVE",
    2: "LIMITPOSITIVE",
    3: "EXTEN",
    4: "IDENT",
    6: "STANDBY",
    7: "BAKE",
    8: "ATSPEED"
}

class Smd3Controller(SerialDevice, Smd3Interface):
    STEP_SIZE_MM        = 5E-3 # step size (5um) but in mm

    def __init__(self, port='/dev/smd3', baudrate=115200):
        # Load device configuration from the common-egse global config file
        self._port              = DEVICE_SETTINGS.PORT if port is None else port
        self._baudrate          = DEVICE_SETTINGS.BAUDRATE if baudrate is None else baudrate
        
        setup = GlobalState.setup
        self._in_fov_position = setup.gse.smd3.configuration.in_fov_position

        self.status = {}
        self.fault  = {}
        self.homed  = False
        self.homing_thread = None
        self.limits = {'positive':None, 
                       'negative':None}
        
        super().__init__(port=self._port, baudrate=self._baudrate, terminator='\r\n')
        self.connect()
        
        self.emergency_stop()
        # Clear any triggered flags
        self.clear_flags()
        
        self.configure_limits()
        
    # General methods
    def get_idn(self):
        return self._query('SER\r\n')
    
    def get_version(self):
        return self._query('FW\r\n')
    
    def clear_flags(self):
        return self._query('CLR\r\n')
    
    def load_configuration(self):
        return self._query('LOAD\r\n')
    
    def store_configuration(self):
        return self._query('STORE\r\n')
    
    def load_factory_defaults(self):
        return self._query('LOADFD\r\n')
    
    def select_mode(self, mode: Smd3Mode):
        return self._query('MODE,{}\r\n'.format(mode))
    
    def get_status(self):
        return self._query('FLAGS\r\n')
    
    
    # Command movement methods
    def velocity_move(self, direction: str):
        if direction in ['-', '+']:
            return self._query('RUNV,{}\r\n'.format(direction))
        else:
            raise Smd3Exception("Direction can only be '-' or '+'")
    
    def absolute_move(self, absolute_position: float):
        return self._query('RUNA,{}\r\n'.format(absolute_position))
    
    def relative_move(self, relative_position: float):
        return self._query('RUNR,{}\r\n'.format(relative_position))
    
    def bake(self):
        return self._query('RUNB\r\n')
    
    def home(self, direction: str):
        if direction in ['-', '+']:
            return self._query('RUNH,{}\r\n'.format(direction))
        else:
            raise Smd3Exception("Direction can only be '-' or '+'")
    
    def stop(self):
        return self._query('STOP\r\n')
    
    def quick_stop(self):
        return self._query('SSTOP\r\n')
    
    def emergency_stop(self):
        return self._query('ESTOP\r\n')
    
    
    # Motor methods
    def select_tsensor(self, sensor_type=None):
        if sensor_type == None:
            return self._query('TSEL\r\n')
        else:
            return self._query('TSEL,{}\r\n'.format(sensor_type))
    
    def get_temperature(self):
        return self._query('TMOT\r\n')
    
    def run_current(self, current=None):
        if current != None:
            return self._query('IR,{}\r\n'.format(current))
        else:
            return self._query('IR\r\n')
    
    def acceleration_current(self, current=None):
        if current != None:
            return self._query('IA,{}\r\n'.format(current))
        else:
            return self._query('IA\r\n')
            
    
    def hold_current(self, current=None):
        if current != None:
            return self._query('IH,{}\r\n'.format(current))
        else:
            return self._query('IH\r\n')
    
    def power_down_delay(self, delay=None):
        if delay != None:
            return self._query('PDDEL\r\n')
        else:
            return self._query('PDDEL,{}\r\n'.format(delay))
    
    def power_down_ramp_delay(self, delay):
        pass
    
    def set_freewheel(self, fw=None):
        if fw != None:
            return self._query('FW,{}\r\n'.format(fw))
        else:
            return self._query('FW\r\n')
    
    def resolution(self, res=None):
        if res != None:
            return self._query('RES,{}\r\n'.format(res))
        else:
            return self._query('RES\r\n')
    
    
    # Limit input methods
    def global_limit(self, enable=None):
        if enable != None:
            return self._query('L,{}\r\n'.format(enable))
        else:
            return self._query('L\r\n')
    
    def positive_limit(self, enable=None):
        if enable != None:
            return self._query('L+,{}\r\n'.format(enable))
        else:
            return self._query('L+\r\n')
        
    def negative_limit(self, enable=None):
        if enable != None:
            return self._query('L-,{}\r\n'.format(enable))
        else:
            return self._query('L-\r\n'.format(enable))
    
    def positive_limit_polarity(self, polarity=None):
        if polarity != None:
            return self._query('LP+,{}\r\n'.format(polarity))
        else:
            return self._query('LP+\r\n')
        
    def negative_limit_polarity(self, polarity=None):
        if polarity != None:
            return self._query('LP-,{}\r\n'.format(polarity))
        else:
            return self._query('LP-\r\n')
        
    def limit_polarity(self, polarity):
        return self.query('LP,{}\r\n'.format(polarity))
    
    def limit_stop_mode(self, stop_mode):
        return self._query('LSM,{}\r\n'.format(stop_mode))
    
    
    # Profile methods
    def acceleration(self, acceleration=None):
        if acceleration != None:
            return self._query('AMAX,{}\r\n'.format(acceleration))
        else:
            return self._query('AMAX\r\n')
    
    def deceleration(self, deceleration=None):
        if deceleration != None:
            return self._query('DMAX,{}\r\n'.format(deceleration))
        else:
            return self._query('DMAX\r\n')
    
    def start_frequency(self, frequency=None):
        if frequency != None:
            return self._query('VSTART,{}\r\n'.format(frequency))
        else:
            return self._query('VSTART\r\n')
    
    def stop_frequency(self, frequency=None):
        if frequency != None:
            return self._query('VSTOP,{}\r\n'.format(frequency))
        else:
            return self._query('VSTOP\r\n')
    
    def target_frequency(self, frequency=None):
        if frequency != None:
            return self._query('VMAX,{}\r\n'.format(frequency))
        else:
            return self._query('VMAX\r\n')
    
    def actual_frequency(self):
        return self._query('VACT\r\n')
    
    def actual_position(self, position=None):
        if position != None:
            return self._query('PACT,{}\r\n'.format(position))
        else:
            return self._query('PACT\r\n')
    
    def relative_position(self, position=None):
        if position != None:
            return self._query('PREL,{}\r\n'.format(position))
        else:
            return self._query('PREL\r\n')
    
    def time_stop_before_move(self, time):
        if time != None:
            return self._query('TZW,{}\r\n'.format(time))
        else:
            return self._query('TZW\r\n')
    
    def full_step(self, step):
        if step != None:
            return self._query('THIGH,{}\r\n'.format(step))
        else:
            return self._query('THIGH\r\n')
    
    
    # Step/Direction methods
    def step_edge(self, edge):
        if edge != None:
            return self._query('EDGE,{}\r\n'.format(edge))
        else:
            return self._query('EDGE\r\n')
    
    def interpolate(self, enable):
        if enable != None:
            return self._query('INTERP,{}\r\n'.format(enable))
        else:
            return self._query('INTERP\r\n')
 
    # Bake methods
    def bakeout_setpoint(self, setpoint):
        if setpoint != None:
            return self._query('BAKET,{}\r\n'.format(setpoint))
        else:
            return self._query('BAKET\r\n')
    
    
    # Advanced methods
    def configure_limits(self):
        self.global_limit(1)
        self.positive_limit(1)
        self.negative_limit(1)
        self.limit_polarity(0)
        self.negative_limit_polarity(0)
        self.positive_limit_polarity(0)
        self.limit_stop_mode(0)
    
    def configure_homing(self):
        self.select_mode(Smd3Mode.HOME)
        self.target_frequency(500)
    
    def configure_remote(self):
        self.select_mode(Smd3Mode.REMOTE)
        self.target_frequency(1000)
    
    def save_status(self, status_word):
        for bits, name in SFLAGS.items():
            self.status[name] = bool(int(status_word, 0) & (1 << bits))
    
    def save_fault(self, error_word):
        for bits, name in EFLAGS.items():
            self.fault[name]  = bool(int(error_word, 0) & (1 << bits))
    
    def run_homing(self):
        if self.homing_thread is not None:
            if self.homing_thread.is_alive():
                return
        
        self.homing_thread = Thread(target=self.hardware_homing_procedure)
        self.homing_thread.start()
    
    def software_homing_procedure(self):
        logger.info("Starting homing procedure...")
        logger.info("Moving into the end stop")
        
        self.relative_move(-100000)

        # until we stop moving
        time.sleep(0.1)
        _, _, velocity = self.actual_frequency()
        while float(velocity) != 0.0:
            _, _, velocity = self.actual_frequency()
            time.sleep(1)
            
        time.sleep(0.1)
    
        self.actual_position(0.0)
        self.limits['negative'] = 0
        
        self.homed = True
        logger.info("Homing procedure completed!")
    
    def hardware_homing_procedure(self):
        self.configure_homing()
        self.configure_limits()
        logger.info("Starting homing procedure...")

        # Negative homing procedure
        # Home negative side
        self.home('-')

        while not int(self.actual_position()[0], 16) >> 1 & 0x1:
            time.sleep(0.5)
        
        time.sleep(.5)
        
         # Reset actual position
        self.actual_position(0.0)
        self.limits['negative'] = 0

        self.homed = True
        
        logger.info("Homing procedure completed!")
        
        self.configure_remote()
    
    def move_mask_fov(self, enable: bool):
        if self.homed:
            if enable:
                self.absolute_move(self._in_fov_position)
            else:
                self.absolute_move(self.limits['negative'])
        else:
            raise Smd3Exception("SMD3 has not been homed. Move has been ignored")
    
    def mask_in_fov(self):
        if self.homed:
            _, _, position = self.actual_position()
            if self._in_fov_position - 1 <= round(float(position)) <= self._in_fov_position + 1:
                return True
            else:
                return False
        else:
            return False
            
    def actual_position_mm(self):
        _, _, position = self.actual_position()
        return float(position)  * self.STEP_SIZE_MM
    
    def _query(self, command):
        """ Uses the parent query function and adds some sanity checks. """
        response = super().query(command)

        if response[-2:] != '\r\n':
            raise ConnectionError(f"Missing termination characters in response: {response}")

        msg_parts = response.strip().split(',')

        if len(msg_parts) < 2:
            raise ConnectionError(f"Reveived malformed response: {response}")

        status_word = msg_parts[0]
        error_word = msg_parts[1]

        self.save_status(status_word)
        self.save_fault(error_word)
        
        if len(msg_parts) >= 3 and msg_parts[2][:3] == 'ERR':
            raise ConnectionError(f"Reveived error response. Error flags: {msg_parts[1]}, " +
                                  f"Error code: {msg_parts[2]}")

        # return a list if multiple return values are received
        
        if len(msg_parts) == 2:
            return status_word, error_word, None
        elif len(msg_parts) > 3:
            return status_word, error_word, msg_parts[2:]
        else:
            return status_word, error_word, msg_parts[2]   
    
def main():
    dev = Smd3Controller()
    while not dev.homed:
        _, _, velocity = dev.actual_frequency()
        _, _, position = dev.actual_position()
        _, _, temperature = dev.get_temperature()
        rich.print("Position: {}, Velocity: {}, Temperature: {}"
              .format(position, velocity, temperature))
        time.sleep(1)
        
    dev.move_mask_fov(True)
    
    while not dev.mask_in_fov():
        _, _, velocity = dev.actual_frequency()
        _, _, position = dev.actual_position()
        _, _, temperature = dev.get_temperature()
        rich.print("Position: {}, Position(rounded): {}, Position(inted): {}, Velocity: {}, Temperature: {}"
              .format(position, round(float(position)), int(float(position)), velocity, temperature))
        rich.print('Negative: {}, Positive: {}'.format(dev.limits['negative'], dev.limits['positive']))
        time.sleep(1)
    
    print("Hartmann Mask has been enabed")

if __name__ == '__main__':
    main()
    
    
    
    
    
