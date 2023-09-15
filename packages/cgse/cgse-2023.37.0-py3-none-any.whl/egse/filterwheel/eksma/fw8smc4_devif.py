# Filter wheel required by filterwheel

import logging
import os
import sys
import time
from ctypes import *

from egse.lib.ximc.pyximc import lib as ximc
from egse.lib.ximc.pyximc import device_information_t, get_position_t, status_t, MoveState
from egse.command import ClientServerCommand
from egse.device import DeviceConnectionError
from egse.settings import Settings

if sys.version_info >= (3, 0):
    pass


class FilterWheel8SMC4Command(ClientServerCommand):
    def get_cmd_string(self, *args, **kwargs) -> str:
        out = super().get_cmd_string(*args, **kwargs)
        return out + "\n"

logger = logging.getLogger(__name__)

ctrl_settings = Settings.load("Filter Wheel 8SMC4 Controller")

# Dependences

# For correct usage of the library libximc,
# you need to add the file pyximc.py wrapper with the structures of the library to python path.
cur_dir = os.path.abspath(os.path.dirname(__file__)) + "/../../lib/ximc"  # Specifies the current directory.
sys.path.append(cur_dir)

#path to the encription key of the network interface:
keyfile_dir = os.path.join(cur_dir, "libximc.framework", "Resources", "keyfile.sqlite")

try:
    from egse.lib.ximc.pyximc import *
except ImportError as err:
    print(
        "Can't import pyximc module. The most probable reason is that you changed the relative location of the testpython.py and pyximc.py files. See developers' documentation for details.")
    exit()
except OSError as err:
    print(err)
    print(
        "Can't load libximc library. Please add all shared libraries to the appropriate places. It is decribed in detail in developers' documentation. On Linux make sure you installed libximc-dev package.\nmake sure that the architecture of the system and the interpreter is the same")
    exit()

####################################################################################################
# TODO:
#
#    The following line where 'lib' is defined shall move into the __init__ method of
#    FilterWheel8SMC4EthernetInterface. Also, the wildcard import above of egse.lib.ximc.pyximc
#    shall be changed into specific imports.
#
####################################################################################################

# to be replaced by logger event

sbuf = create_string_buffer(64)
lib.ximc_version(sbuf)

logger.debug("Library Loaded: version = " + sbuf.raw.decode().rstrip("\0"))


# Set bindy network key file. Must be called before any "enumerate_device" or "open_device' is colled
#setting the encription key for the network interface. In python, make sure to pass a byte array object to this
#function (b"string literal")
lib.set_bindy_key(keyfile_dir.encode("utf-8"))


class FilterWheel8SMC4Error(Exception):
    """Base exception for all Filter Wheel errors."""
    pass


DEVICE_NAME = "Filter Wheel 8SMC4"


class FilterWheel8SMC4USBInterface:
    """ This class controls a 8smc4 filterwheel controller through serial devices
        connected via USB. It uses a wrapped c library (ximc) to communicate with the device.
    """

    def __init__(self):
        self._port = ctrl_settings.PORT
        self._is_connected = False
        self._devId = None

        try:
            self.connect()
        except Exception as exc:
            logger.error(f"Could not connect to device ({exc})")


    def connect(self):
        if self._is_connected:
            logger.warning("Trying to connect to an already connected device")
        else:
            try:
                self._devId = ximc.open_device(f"xi-com:{self._port}".encode())                
            except OSError as exc:
                raise DeviceConnectionError(self.DEVICE_NAME, f"Could not connect ({exc}).") from exc
            self._is_connected = True

    def disconnect(self):
        if not self._is_connected():
            logger.warning("Trying to disconnect to an already disconnected device")
        try:
            ximc.close_device(byref(cast(self._devId, POINTER(c_int))))
        except OSError as exc:
            raise DeviceConnectionError(self.DEVICE_NAME, f"Could not disconnect ({exc}).") from exc
        else:
            self._is_connected = False

    def is_connected(self):
        return self._is_connected

    def get_response(self, cmd_string):
        pass

    def get_id(self):
        x_device_information = device_information_t()
        result = ximc.get_device_information(self._devId, byref(x_device_information))
        device_id = {}
        if result == Result.Ok:
            version = (
                f"{x_device_information.Major!r}."
                f"{x_device_information.Minor!r}."
                f"{x_device_information.Release!r}"
            )
            description = f"{string_at(x_device_information.ProductDescription).decode()!r}"
            device_id = {
                "Product Description": description,
                "Version": version
            }
        else:
            logger.warning("Wheel has not been correctly connected")
        return device_id

    def get_position(self):
        x_pos = get_position_t()
        ximc.get_position(self._devId, byref(x_pos))
        result = [x_pos.Position, x_pos.uPosition]
        return result

    def equalize_wheels(self, position):
        # This makes the 2 wheels move to the index defined by the position argument
        # If the highest wheel index position is > than the actual step position of the filter wheel, then it
        # sets both wheels to the highest wheel index position in order to perform further movements
        logger.info("Equalizing the wheels by moving first to zero")
        self.move_wheel(1)
        self.move_wheel(9)

        self.command_zero()
        
        self.move_wheel(position+1)

    def move_wheel(self, steps):
        steps = steps - 1
        try:
            ximc.command_move(self._devId, steps*25, 0)
            time.sleep(2)
            while self.get_speed() != 0:
                time.sleep(1)
        except AssertionError:
            logger.warning("Something went wrong when moving the filterwheel")

    def set_pos(self, pos_wheel2, pos_wheel1):
        self.homing()
        while self.get_speed() != 0:
            time.sleep(1)

        # delay so the commands don't overlap
        # the wheel 2 is the one that moves (opposite side of the motor)
        # gets the actual position
        pos = self.get_position()
        pos = pos[0]
        # from manual: command_move(device_t id, Position, uPosition)
        # the engine starts to move with the pre-set parameters to the point specified by Position and uPosition
        # uPosition sets the microstep in range -255 to 255
        # 1 turn of the wheel has 200 steps, so each transition is reached by 25 steps.
        if pos_wheel1 == pos_wheel2:
            self.equalize_wheels(pos_wheel2)

        elif pos_wheel1 < pos_wheel2:
            if abs(pos) < pos_wheel1*25:
                self.move_wheel(pos_wheel1+1)
            else:
                self.equalize_wheels(pos_wheel1)

            self.move_wheel(pos_wheel2-7)

        elif pos_wheel1 > pos_wheel2:

            if pos < pos_wheel1*25:
                self.move_wheel(pos_wheel1+1)

            else:
                self.equalize_wheels(pos_wheel1)
            self.move_wheel(pos_wheel2+1)


        return 0

    def command_zero(self):
        logger.warning("Commanding the wheels to zero position")
        try:
            ximc.command_zero(self._devId)
            while self.get_speed() != 0:
                time.sleep(0.03)
        except AssertionError:
            logger.warning("Something went wrong when moving the filterwheel")

    def homing(self):
        logger.info("Starting homing sequence")
        ximc.command_homezero(self._devId)


    def get_status(self):
        status = status_t()
        ximc.get_status(self._devId, byref(status))

        return status

    def get_speed(self):
        _speed = self.get_status()
        return _speed.CurSpeed

    def get_flags(self):
        status = self.get_status()
        return (status.Flags)

    def is_moving(self):
        mvt = self.get_status()
        return mvt.MoveSts






class FilterWheel8SMC4EthernetInterface:
    def __init__(self):

        self.is_connection_open = False
        self._fw = None

        # open_name of the device address
        self.open_name = "xi-net://" + ctrl_settings["IP"] + "/000040AC"

    def connect(self):
        # Sanity checks:
        if self.is_connection_open:
            logger.warning("Trying to connect to an already connected device")
        try:
            self._fw = lib.open_device(self.open_name.encode())
        except OSError as exc:
            raise DeviceConnectionError(DEVICE_NAME, f"OSError caught ({exc}).") from exc

        self.is_connection_open = True

        if not self.is_connected():
            raise FilterWheel8SMC4Error(f"Device is not connected, check logging messages for the cause.")

    def disconnect(self):
        try:
            if self.is_connection_open:
                logger.debug(f"Disconnecting from {self.open_name}")
                lib.close_device(byref(cast(self._fw, POINTER(c_int))))
                logger.info("Filter Wheel disconnected")
                self.is_connection_open = False
        except OSError as exc:
            raise FilterWheel8SMC4Error(f"Could not close Filterwheel connection") from exc

    def is_connected(self):
        """
        Check if the device is connected. This will send a query for the device identification
        and validate the answer.

        Returns:
             True is the device is connected and answered with the proper ID, False otherwise.
        """
        if not self.is_connection_open:
            return False

        try:
            self.get_id()
        except OSError as exc:
            logger.error(
                f"While trying to talk to the device the following exception occurred, "
                f"exception={exc}")
            self.disconnect()
            return False
        return True

    def get_response(self, cmd_string):
        pass

    def get_id(self):
        x_device_information = device_information_t()
        result = lib.get_device_information(self._fw, byref(x_device_information))
        device_id = {}
        if result == Result.Ok:
            version = (
                f"{x_device_information.Major!r}."
                f"{x_device_information.Minor!r}."
                f"{x_device_information.Release!r}"
            )
            # version = repr(x_device_information.Major) + "." + \
            #           repr(x_device_information.Minor) + "." + \
            #           repr(x_device_information.Release)
            description = f"{string_at(x_device_information.ProductDescription).decode()!r}"
            device_id = {
                "Product Description": description,
                "Version": version
            }
        else:
            logger.warning("Wheel has not been correctly connected")
        return device_id

    def get_position(self):
        x_pos = get_position_t()
        lib.get_position(self._fw, byref(x_pos))
        result = [x_pos.Position, x_pos.uPosition]
        return result

    def equalize_wheels(self, position):
        # This makes the 2 wheels move to the index defined by the position argument
        # If the highest wheel index position is > than the actual step position of the filter wheel, then it
        # sets both wheels to the highest wheel index position in order to perform further movements
        logger.info("Equalizing the wheels by moving first to zero")
        self.move_wheel(1)
        self.move_wheel(9)

        self.command_zero()
        logging.info(f"New zero position reached:({self.get_position()[0]})")
        logging.info(f"Commanding the wheels to the equalized position:({position})")

        self.move_wheel(position+1)
        logging.info(f"New equalized position reached at:({self.get_position()[0]})")

    def move_wheel(self, steps):
        print("moving wheel to the following number of x25 steps:", steps)
        steps = steps - 1
        try:
            lib.command_move(self._fw, steps*25, 0)
            time.sleep(0.3)
            logger.info("The wheel is moving ...")
            while self.is_moving() != 0:
                time.sleep(0.3)
            logger.info("... the wheel stopped its movement")
        except AssertionError:
            logger.warning("Something went wrong when moving the filterwheel")

    def set_pos(self, pos_wheel1, pos_wheel2):
        self.homing()
        # delay so the commands don't overlap
        # the wheel 2 is the one that moves (opposite side of the motor)
        # gets the actual position
        pos = self.get_position()
        pos = pos[0]
        # from manual: command_move(device_t id, Position, uPosition)
        # the engine starts to move with the pre-set parameters to the point specified by Position and uPosition
        # uPosition sets the microstep in range -255 to 255
        # 1 turn of the wheel has 200 steps, so each transition is reached by 25 steps.
        if pos_wheel1 == pos_wheel2:
            self.equalize_wheels(pos_wheel2)
            logger.info("Positions reached for both wheels")

        elif pos_wheel1 < pos_wheel2:
            if abs(pos) < pos_wheel1*25:
                self.move_wheel(pos_wheel1+1)
            else:
                self.equalize_wheels(pos_wheel1)

            logger.info("position 1 reached")
            self.move_wheel(pos_wheel2-7)
            logger.info("position 2 reached")

        elif pos_wheel1 > pos_wheel2:

            if pos < pos_wheel1*25:
                self.move_wheel(pos_wheel1+1)

            else:
                self.equalize_wheels(pos_wheel1)
            logger.info("position 1 reached")
            self.move_wheel(pos_wheel2+1)
            logger.info("position 2 reached")

        _output = self.wait_stop(10)
        if _output == 0:
            logger.info("Movement finished")
        if _output > 0:
            logger.warning("Movement finished after forcing the wait_stop")
        if _output < 0:
            logger.error("Error on movement")
        return _output

    def command_zero(self):
        logger.warning("Commanding the wheels to zero position")
        try:
            lib.command_zero(self._fw)
            time.sleep(0.3)
            logger.info("The wheel is moving to zero...")
            while self.is_moving() != 0:
                time.sleep(0.3)
            logger.info("... the wheel stopped its movement")
        except AssertionError:
            logger.warning("Something went wrong when moving the filterwheel")

    def homing(self):
        """ standard ".cfg" file, which can be downloaded to device using XILab,
            overloads command_homezero command """
        logger.info("Starting homing sequence ...")
        # From libxim Manual, command_homezero make home command, waits until it's finished then makes a zero command
        # so the behaviour is the same than for the CSL collimator code
        lib.command_homezero(self._fw)
        # != and else cases are not normally gonna happen as the command_zero normally already waits for the wheel
        # to stop
        logger.info("... Wheels homing succeeded")

    def get_status(self):
        x_status = status_t()
        result = lib.get_status(self._fw, byref(x_status))
        if result == Result.Ok:
            pass
        else:
            logger.warning("Something went wrong when trying to get the wheel status")
            x_status = -1
        return x_status

    def get_speed(self):
        _speed = self.get_status()
        return _speed.CurSpeed

    #fixme: this is not working, so don't use it for the moment. Replaced with time.sleeps
    def wait_stop(self, t):
        _output = None
        timeout = time.time() + t
        time.sleep(0.3)
        _speed = self.get_speed()
        while time.time() < timeout:
            time.sleep(0.03)
            _speed = self.get_speed()
            if _speed == 0:
                break
        if _speed != 0:
            logger.warning("wait_stop timeout over but the motor is still running, forcing the wheel to stop")
            result = lib.command_wait_for_stop(self._fw, 10)
            if result.Result == Ok:
                logger.warning("The wheel stopped after forcing command")
                _output = 1
            else:
                logger.error("An error occurred during the movement")
                _output = -1
        else:
            _output = 0
        return _output

    def get_flags(self):
        x_status = status_t()
        result = lib.get_status(self._fw, byref(x_status))
        x_status.Flags = StateFlags.STATE_IS_HOMED
        result = lib.get_status(self._fw, byref(x_status))
        print(StateFlags.STATE_ALARM, StateFlags.STATE_IS_HOMED, StateFlags.STATE_CONTR, StateFlags.STATE_CONTROLLER_OVERHEAT)
        print(repr(x_status.Flags))

    def is_moving(self):
        mvt = self.get_status()
        return mvt.MoveSts
