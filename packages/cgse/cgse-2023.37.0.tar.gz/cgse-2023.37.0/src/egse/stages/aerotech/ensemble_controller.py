import logging

from numpy import degrees, arccos, cos, radians

from egse.command import Command
from egse.settings import Settings
from egse.socketdevice import SocketDevice
from egse.stages.aerotech.ensemble_interface import EnsembleInterface
from egse.stages.aerotech.ensemble_parameters import EnsembleParameter
from egse.state import GlobalState

logger = logging.getLogger(__name__)

# Load the device settings from the global common-egse config file
DEVICE_SETTINGS = Settings.load("Aerotech Ensemble Controller")

# Load the device protocol
DEVICE_PROTOCOL = Settings.load(filename='ensemble.yaml')['Commands']


class EnsembleException(Exception):
    pass


class EnsembleController(SocketDevice, EnsembleInterface):
    def __init__(self, hostname=None, port=None):

        # Load device configuration from the common-egse global config file
        self._hostname      = DEVICE_SETTINGS.HOSTNAME if hostname is None else hostname
        self._port          = DEVICE_SETTINGS.PORT if port is None else port
        

        # Create a dict of Command objects for each function
        self._commands = {}
        for name, items in DEVICE_PROTOCOL.items():
            if 'cmd' in items:
                self._commands[name] = Command(name, items['cmd'])

        # Get the movement speed from the setup
        setup = GlobalState.setup
        self.speed = setup.gse.ensemble.maximum_speed
        self.limit = setup.gse.ensemble.limit
        
        self.limits         = {'X': [(0 - self.limit), self.limit], 'Y': [(0 - self.limit), self.limit]}
        # Initialize the parent class with the port and baudrate
        super().__init__(hostname=self._hostname, port=self._port, timeout=10000)
        self.connect()
        
        self.set_absolute()
        self.set_wait_mode('NOWAIT')


    def get_idn(self):
        return self.query(self._commands['get_idn'].get_cmd_string())


    def reset(self):
        return self.query(self._commands['reset'].get_cmd_string())


    def abort(self):
        return self.query(self._commands['abort'].get_cmd_string())


    def clear_errors(self):
        return self.query(self._commands['clear_errors'].get_cmd_string())

    def get_plane_status(self):
        status = self.query(self._commands['get_plane_status'].get_cmd_string())
        return int(status) & 0xFFFFFFF # turn into unsigned

    def get_status(self, axis):
        status = self.query(self._commands['get_status'].get_cmd_string(axis=axis))
        return int(status) & 0xFFFFFFFF # turn into unsigned

    def get_fault(self, axis):
        fault = self.query(self._commands['get_fault'].get_cmd_string(axis=axis))
        return int(fault) & 0xFFFFFFFF # turn into unsigned

    def set_blocking(self, axis, enable):
        enable_string = 'ON' if enable else 'OFF'
        return self.query(self._commands['set_blocking'].get_cmd_string(
            axis=axis, enable=enable_string))

    def get_command_position(self, axis):
        return float(self.query(self._commands['get_command_position'].get_cmd_string(axis=axis)))

    def get_actual_position(self, axis):
        return float(self.query(self._commands['get_actual_position'].get_cmd_string(axis=axis)))

    def get_error_position(self, axis):
        return float(self.query(self._commands['get_error_position'].get_cmd_string(axis=axis)))

    def get_command_velocity(self, axis):
        return float(self.query(self._commands['get_command_velocity'].get_cmd_string(axis=axis)))

    def get_actual_velocity(self, axis):
        return float(self.query(self._commands['get_actual_velocity'].get_cmd_string(axis=axis)))

    def get_command_current(self, axis):
        return float(self.query(self._commands['get_command_current'].get_cmd_string(axis=axis)))

    def get_actual_current(self, axis):
        return float(self.query(self._commands['get_actual_current'].get_cmd_string(axis=axis)))

    def enable_axis(self, axis):
        logger.info(f"Enabeling the {axis} axis")
        return self.query(f"ENABLE {axis}\n")
    
    def enable_axes(self):
        logger.info("Enabling X Y Axes")
        return self.query("ENABLE X Y\n")
    
    def disable_axis(self, axis):
        logger.info(f"Disabeling the {axis} axis")
        return self.query(f"DISABLE {axis}\n")
    
    def disable_axes(self):
        logger.info("Disabling the X Y axes")
        return self.query(f"DISABLE X Y\n")

    def set_wait_mode(self, mode):
        return self.query(f"WAIT MODE {mode}\n")
    
    def set_absolute(self):
        return self.query(self._commands['set_absolute'].get_cmd_string())

    def set_incremental(self):
        return self.query(self._commands['set_incremental'].get_cmd_string())

    def move_axis_degrees(self, axis, position):
        if not self.is_homed(axis):
            logger.warning("The gimbal has not been homed")
            raise EnsembleException(f'axis {axis} is not homed')

        if not (self.limits[axis][0] <= position <= self.limits[axis][1]):
            logger.warning("Move denied: Position out of limit")
            raise EnsembleException(f'position {axis} outside limits\
                {self.limits[axis][0]} <= {position} <= {self.limits[axis][1]}')

        logger.info(f"Moving {axis} axis to {position}")

        self.query(f"LINEAR {axis} {position} {axis}F {self.speed}\n")

    def move_axes_degrees(self, position_x, position_y):
        if not self.is_homed('X') or not self.is_homed('Y'):
            logger.warning("The gimbal has not been homed")
            raise EnsembleException(f'not all axes are homed')

        if not (self.limits['X'][0] <= position_x <= self.limits['X'][1]):
            logger.warning("Move denied: X Position out of limit")
            raise EnsembleException(f"position X outside limits \
                {self.limits['X'][0]} <= {position_x} <= {self.limits['X'][1]}")

        if not (self.limits['Y'][0] <= position_y <= self.limits['Y'][1]):
            logger.warning("Move denied: Y Position out of limit")
            raise EnsembleException(f"position Y outside limits \
                {self.limits['Y'][0]} <= {position_y} <= {self.limits['Y'][1]}")

        radius = degrees(arccos(cos(radians(position_x)) * cos(radians(position_y))))

        # Due to rounding errors, we have to round the radius as well
        radius = round(radius, 6)
        
        logger.info(f"Radial distance is: {radius}")
      
        if not (radius <= self.limit):
            logger.warning("Move denied: radial distance out of limit")
            raise EnsembleException(f"Command is outside allowed radial distance \
                {radius} <= {self.limit}")                

        logger.info(f"Moving Y to {position_y} and X to {position_x}")

        self.query(f"LINEAR X {position_x} Y {position_y} F {self.speed}\n")


    def home_axis(self, axis):
        if self.is_homed(axis):
            logger.info("Gimbal has already been homed")
            return

        logger.info(f"Homing the {axis} axis...")

        self.query(f"HOME {axis}\n")

        logger.info(f"{axis} axis has been homed")


    def home_axes(self):
        if self.is_homed('Y') and self.is_homed('X'):
            logger.info("Gimbal was already homed")
            return

        logger.info(f"Homing both axis")

        self.query(f"HOME X Y\n")

        logger.info(f"Homing complete")

    def is_moving(self, axis):
        return bool(self.get_status(axis) & 0x08)

    def is_homed(self, axis):
        return bool(self.get_status(axis) & 0x02)

    def get_parameter(self, paramId: EnsembleParameter):
        return int(self.query(self._commands['get_parameter'].get_cmd_string(index=paramId)))

    def set_parameter(self, paramId: EnsembleParameter, value):
        return self.query(self._commands['set_parameter'].get_cmd_string(index=paramId, value=value))

    def print_status(self):
        """ Pretty print the status word. """
        status = self.get_status('X')
        print('STATUS:')
        print(f'\t{"Enabled":20s}: {bool(status & 0x00000001)}')
        print(f'\t{"Homed":20s}: {bool(status & 0x00000002)}')
        print(f'\t{"InPosition":20s}: {bool(status & 0x00000004)}')
        print(f'\t{"MoveActive":20s}: {bool(status & 0x00000008)}')
        print(f'\t{"AccelPhase":20s}: {bool(status & 0x00000010)}')
        print(f'\t{"DecelPhase":20s}: {bool(status & 0x00000020)}')
        print(f'\t{"PositionCapture":20s}: {bool(status & 0x00000040)}')
        print(f'\t{"CurrentClamp":20s}: {bool(status & 0x00000080)}')
        print(f'\t{"BrakeOutput":20s}: {bool(status & 0x00000100)}')
        print(f'\t{"MotionIsCw":20s}: {bool(status & 0x00000200)}')
        print(f'\t{"MasterSlaveControl":20s}: {bool(status & 0x0000400)}')
        print(f'\t{"CalActive":20s}: {bool(status & 0x00000800)}')
        print(f'\t{"CallEnabled":20s}: {bool(status & 0x00001000)}')
        print(f'\t{"JoystickControl":20s}: {bool(status & 0x0002000)}')
        print(f'\t{"Homing":20s}: {bool(status & 0x00004000)}')
        print(f'\t{"MasterSupress":20s}: {bool(status & 0x00008000)}')
        print(f'\t{"GantryActive":20s}: {bool(status & 0x00010000)}')
        print(f'\t{"GantryMaster":20s}: {bool(status & 0x00020000)}')
        print(f'\t{"AutoFocusActive":20s}: {bool(status & 0x00040000)}')
        print(f'\t{"CommandFilterDone":20s}: {bool(status & 0x00080000)}')
        print(f'\t{"InPosition2":20s}: {bool(status & 0x00100000)}')
        print(f'\t{"ServoControl":20s}: {bool(status & 0x002000000)}')
        print(f'\t{"CwEOTLimit":20s}: {bool(status & 0x004000000)}')
        print(f'\t{"CcwEOTLimit":20s}: {bool(status & 0x008000000)}')
        print(f'\t{"HomeLimit":20s}: {bool(status & 0x01000000)}')
        print(f'\t{"MarkerInput":20s}: {bool(status & 0x02000000)}')
        print(f'\t{"HallAInput":20s}: {bool(status & 0x04000000)}')
        print(f'\t{"HallBInput":20s}: {bool(status & 0x08000000)}')
        print(f'\t{"HallCInput":20s}: {bool(status & 0x10000000)}')
        print(f'\t{"SineEncoderError":20s}: {bool(status & 0x20000000)}')
        print(f'\t{"CosineEncoderError":20s}: {bool(status & 0x40000000)}')
        print(f'\t{"ESTOPInput":20s}: {bool(status & 0x80000000)}')

    def query(self, command: str):
        """ Override the parent class to do some error checking on the response. """

        # print(command)

        response = super().query(command)

        # print(response)

        if response[-1] != '\n':
            raise ConnectionError(f"Invalid termination character in response: {response}")
        elif response[0] == '!':
            raise ConnectionError(f"Command invalid error for command: {command}")
        elif response[0] == '#':
            raise ConnectionError(f"Command fault error for command: {command}")
        elif response[0] != '%':
            raise ConnectionError(f"Invalid starting character in response: {response}")
        elif len(response[:-1]) > 1:
            return response[1:-1]
        else:
            return None
        
if __name__ == "__main__":
    ens = EnsembleController()
    ens.get_idn()
    
    ens.move_axes_degrees(14, 13, True)
