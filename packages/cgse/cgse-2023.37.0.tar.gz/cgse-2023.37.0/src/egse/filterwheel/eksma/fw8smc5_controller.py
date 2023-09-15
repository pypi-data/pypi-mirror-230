
import logging
from collections import OrderedDict
from ctypes import cast, byref, c_int, POINTER

import numpy as np
import time

from egse.device import DeviceConnectionError
from egse.filterwheel.eksma.fw8smc5 import Fw8Smc5Interface
from egse.lib.ximc.pyximc import device_information_t, get_position_t, status_t, MoveState
from egse.lib.ximc.pyximc import lib as ximc
from egse.settings import Settings
from egse.state import GlobalState

logger = logging.getLogger(__name__)

CTRL_SETTINGS = Settings.load("Standa 8SMC5 Controller")


class Fw8Smc5Exception(Exception):
    pass


class Fw8Smc5Controller(Fw8Smc5Interface):
    """ This class controls a 8smc5 dual filterwheel controller through two serial devices
        connected via USB. It uses a wrapped c library (ximc) to communicate with the device.
    """

    DEVICE_NAME     = "Standa 8SMC5"
    WHEEL_POSITIONS = 8
    TOTAL_POSITIONS = WHEEL_POSITIONS * WHEEL_POSITIONS
    ROTATION_STEPS  = 600 # number of encoder steps in a full rotation
    POSITION_STEPS  = ROTATION_STEPS // WHEEL_POSITIONS # number of encoder steps between filter positions


    def __init__(self, port0=None, port1=None):
        self._port0 = CTRL_SETTINGS.PORT_0 if port0 is None else port0
        self._port1 = CTRL_SETTINGS.PORT_1 if port1 is None else port1
        self._devIds = [None, None]
        self._is_connected = False


        # Get device calibration from the setup
        self.setup = GlobalState.setup
        self.relative_intensities = self.setup.gse.ogse.calibration.relative_intensity_by_index
        self.home_offsets = self.setup.gse.filterwheel.home_offset
        self.ri_wheel_positions = self.setup.gse.ogse.calibration.relative_intensity_by_wheel

        self.ri_wheel_positions = {eval(k): v for k, v in self.ri_wheel_positions.items()} # convert wheel indices from strings to tuples
        self.ri_wheel_positions = OrderedDict( # Convert to ordereddict sorted by values to match self.relative_intensities
            sorted(self.ri_wheel_positions.items(), key=lambda x: x[1]))

        # self.disconnect()
        try:
            self.connect()
        except Exception as exc:
            logger.error(f"Could not connect to device ({exc})")

        self.home() # avoid being in an invalid position


    # The device sometimes becomes unresponsive when the connection is not closed
    def __del__(self):
        self.disconnect()


    def connect(self):

        if self._is_connected:
            logger.warning("Trying to connect to an already connected device")
        else:
            try:
                self._devIds[0] = ximc.open_device(f"xi-com:{self._port0}".encode())
                self._devIds[1] = ximc.open_device(f"xi-com:{self._port1}".encode())
            except OSError as exc:
                raise DeviceConnectionError(self.DEVICE_NAME, f"Could not connect ({exc}).") from exc
            else:
                self._is_connected = True


    def disconnect(self):

        if not self._is_connected:
            logger.warning("Trying to disconnect to an already disconnected device")
        else:
            try:
                ximc.close_device(byref(cast(self._devIds[0], POINTER(c_int))))
                ximc.close_device(byref(cast(self._devIds[1], POINTER(c_int))))
            except OSError as exc:
                raise DeviceConnectionError(self.DEVICE_NAME, f"Could not disconnect ({exc}).") from exc
            else:
                self._is_connected = False


    def reconnect(self):

        if self._is_connected:
            self.disconnect()
        self.connect()


    def is_connected(self):

        return self._is_connected


    def is_simulator(self):

        return False


    def get_idn(self):

        device_information = device_information_t()
        result = ximc.get_device_information(self._devIds[0], byref(device_information))

        return device_information.ProductDescription.decode()


    def get_error_flags(self):

        status0, status1 = self._get_status()

        return (status0.Flags, status1.Flags)


    def is_moving(self):

        status0, status1 = self._get_status()

        return (bool(status0.MoveSts & MoveState.MOVE_STATE_MOVING),
                bool(status1.MoveSts & MoveState.MOVE_STATE_MOVING))


    def get_position_steps(self, id):

        get_position = get_position_t()
        ximc.get_position(self._devIds[id], byref(get_position))

        return get_position.Position


    def set_position_steps(self, id, position):

        assert id in [0, 1], 'Device id must be in [0, 1]'

        position = position % self.ROTATION_STEPS

        ximc.command_move(self._devIds[id], position, 0)

        # TODO: add some error checking and maybe a timout to this loop
        while self.get_position_steps(id) != position:
            time.sleep(0.1)


    def get_position_wheels(self):

        return self._get_position_wheel(0), self._get_position_wheel(1)


    def set_position_wheels(self, position_a, position_b):

        self.set_position_wheel(0, position_a)
        self.set_position_wheel(1, position_b)


    def get_position_index(self):

        # Get the current wheel positions
        p0, p1 = self.get_position_wheels()

        if p0 is None or p1 is None:
            raise Fw8Smc5Exception('Wheel(s) in intermediate position')

        try:
            return list(self.ri_wheel_positions.keys()).index((p0, p1))
        except ValueError:
            return None
            # Do we really need to crash the CS/Leave a log message if the comination is non indexed?
            # I think we are better off just returning an impossible value
            # logger.warning("Filterwheel is in a non-indexed combination of wheel positions")
            # raise Fw8Smc5Exception("Filterwheel is in a non-indexed combination of wheel positions")


    def set_position_index(self, index):

        index0, index1 = list(self.ri_wheel_positions.keys())[index]
        self.set_position_wheels(index0, index1)


    def get_relative_intensity(self):
        index = self.get_position_index()
        if index in self.relative_intensities:
            return self.relative_intensities[index]
        else:
            return 9.99999e9


    def set_relative_intensity(self, relative_intensity):

        # Find the index that matches the desired relative_intensity the closest.
        index = int(np.abs(
            np.array(list(self.relative_intensities.values())) - relative_intensity).argmin())

        # Look up corresponding wheel positions
        p0, p1 = list(self.ri_wheel_positions.keys())[index]

        self.set_position_wheels(p0, p1)

        logger.info(f'set relative intensity to {relative_intensity}')


    def intensity_level_up(self):

        index = self.get_position_index() # get current index
        index = min(index + 1, self.TOTAL_POSITIONS - 1) # increment
        self.set_position_index(index)


    def intensity_level_down(self):

        index = self.get_position_index() # get current index
        index = max(index - 1, 0) # decrement
        self.set_position_index(index)


    # NOTE: this is blocking but the position might still be outdated when read directly after homing
    def home(self):

        logger.info('Homing started...')

        ximc.command_homezero(self._devIds[0])
        ximc.command_homezero(self._devIds[1])

        self.set_position_steps(0, self.home_offsets[0])
        self.set_position_steps(1, self.home_offsets[1])

        logger.info('Homing complete')


    def _get_status(self):

        status0 = status_t()
        status1 = status_t()

        ximc.get_status(self._devIds[0], byref(status0))
        ximc.get_status(self._devIds[1], byref(status1))

        return (status0, status1)


    def _get_position_wheel(self, id):
        """ Get the position of one of the wheels.
            Returns None for inbetween positions.
        """

        position = self.get_position_steps(id) - self.home_offsets[id]
        offset = position % self.POSITION_STEPS

        if offset != 0:
            return None
        else:
            return position // self.POSITION_STEPS % self.WHEEL_POSITIONS


    def set_position_wheel(self, id, position):
        """ Set the position of one of the wheels. """

        assert 0 <= position < self.WHEEL_POSITIONS, f"Filterwheel index out of range ({position})"

        position_steps = (position * self.POSITION_STEPS + self.home_offsets[id]) % self.ROTATION_STEPS
        self.set_position_steps(id, position_steps)

        logger.debug(f'set wheel {id} to step position {position_steps}')

        while(self.get_position_steps(id) != position_steps):
            logger.info(f'position = {self.get_position_steps(id)}')
            time.sleep(1)


def main():
    dev = Fw8Smc5Controller()

    print('id      :', dev.get_idn())
    print('status  :', dev.get_error_flags())
    print('position:', (dev.get_position_steps(0), dev.get_position_steps(0)))

    print(list(dev.ri_wheel_positions.keys()).index(('(0, 0)')))


    # dev.home()
    # print(dev.get_position_index())
    # print(dev.get_position_wheels())
    #
    # dev.set_position_index(24)
    # print(dev.get_position_index())
    # print(dev.get_position_wheels())
    #
    # dev.set_relative_intensity(1E-4)
    # print(dev.get_position_index())
    # print(dev.get_position_wheels())



if __name__ == '__main__':
    main()
