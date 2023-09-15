"""
This module defines the device classes to be used to connect to and control the Gimbal from
Symétrie.

"""
from cmath import nan
import logging
import math
import time
from datetime import datetime
from datetime import timedelta

import numpy as np

from egse.bits import set_bit
from egse.coordinates.referenceFrame import ReferenceFrame
from egse.device import DeviceConnectionState
from egse.device import DeviceInterface
from egse.gimbal import GimbalError
from egse.gimbal.symetrie import pmac
from egse.gimbal.symetrie.alpha import AlphaControllerInterface
from egse.gimbal.symetrie.pmac import PMACError
from egse.gimbal.symetrie.pmac import PmacEthernetInterface
from egse.gimbal.symetrie.pmac import decode_Q29
from egse.gimbal.symetrie.pmac import decode_Q36
from egse.proxy import Proxy
from egse.settings import Settings
from egse.zmq_ser import connect_address

logger = logging.getLogger(__name__)

GIMBAL_SETTINGS = Settings.load("Gimbal Controller")
CTRL_SETTINGS = Settings.load("Gimbal Control Server")
DEVICE_SETTINGS = Settings.load(filename="gimbal.yaml")

NUM_OF_DECIMALS = 6  # used for rounding numbers before sending to PMAC


class GimbalInterface(AlphaControllerInterface, DeviceInterface):
    """
    Interface definition for the GimbalController, the GimbalProxy and the GimbalSimulator.
    """


class GimbalController(GimbalInterface):
    """
    The GimbalController class allows controlling a Symétrie Gimbal through an Ethernet
    interface that is connecting a Symétrie Controller.

    The Symétrie Controller can be either in simulation mode or have a real Gimbal
    connected.

    **Synopsis**

        from egse.gimbal.symetrie.gimbal import GimbalController
        gimbal = GimbalController(hostname="10.33.178.145", port=1025)
        try:
            gimbal.connect()

            # do some useful things here with the gimbal

        except GimbalError as exc:
            print(exc)
        finally:
            gimbal.disconnect()

    The constructor also sets the connection parameters and tries to connect
    to the controller. Make sure that you explicitly use the gimbal.disconnect()
    command when no connection is needed anymore.

    The controller can also be used as a context manager, in which case the `connect()`
    and `disconnect()` methods should not be called:

        with GimbalController() as gimbal:
            gimbal.info()

    """

    SPEC_POS_MACHINE_ZERO = 0
    """Gimbal machine zero, for maintenance or Jog only."""
    SPEC_POS_USER_ZERO = 2
    """Gimbal user zero position."""

    def __init__(self, hostname=GIMBAL_SETTINGS.HOSTNAME, port=GIMBAL_SETTINGS.PORT):
        """
        Opens a TCP/IP socket connection with the Gimbal Hardware Controller.

        Args:
            hostname (str): the IP address or fully qualified hostname of the Gimbal hardware
            controller.
                The default is defined in the ``settings.yaml`` configuration file.

            port (int): the IP port number to connect to, by default set in the ``settings.yaml``
            configuration file.

        Raises:
            GimbalError: when the connection could not be established for some reason.
        """

        super().__init__()

        logger.debug(f"Initializing GimbalController with hostname={hostname} on port={port}")

        try:
            self.pmac = PmacEthernetInterface()
            self.pmac.setConnectionParameters(hostname, port)
        except PMACError as exc:
            logger.warning(
                f"GimbalError: Couldn't establish connection with the Gimbal Hardware "
                f"Controller: ({exc})"
            )

    def is_simulator(self):
        return False

    def is_connected(self):
        return self.pmac.isConnected()

    def connect(self):
        try:
            self.pmac.connect()
        except PMACError as exc:
            logger.warning(f"PMACError caught: Couldn't establish connection ({exc})")
            raise ConnectionError("Couldn't establish a connection with the Gimbal.") from exc

        self.notify_observers(DeviceConnectionState.DEVICE_CONNECTED)

    def disconnect(self):
        try:
            self.pmac.disconnect()
        except PMACError as exc:
            raise ConnectionError("Couldn't disconnect from Gimbal.") from exc

        self.notify_observers(DeviceConnectionState.DEVICE_NOT_CONNECTED)

    def reconnect(self):
        if self.is_connected():
            self.disconnect()
        self.connect()

    def is_in_position(self):
        try:
            out = self.pmac.getQVars(36, [0], int)
        except PMACError as exc:
            raise GimbalError(
                "Couldn't retrieve information from Gimbal Hardware Controller.") from exc
        return bool(out[0] & 0x04)

    def info(self):
        try:
            msg = "Info about the Gimbal:\n"
            msg += f"model   = {self.pmac.getPmacModel()}\n"
            msg += f"CID     = {self.pmac.getCID()}\n"
            msg += f"version = {self.pmac.getVersion()}\n"
            msg += f"cpu     = {self.pmac.getCPU()}\n"
            msg += f"type    = {self.pmac.getType()}\n"
            msg += f"vendorID= {self.pmac.getVID()}\n"
            msg += f"date    = {self.pmac.getDate()}\n"
            msg += f"time    = {self.pmac.getTime()}\n"
            msg += f"today   = {self.pmac.getToday()}\n"
        except PMACError as exc:
            raise GimbalError(
                "Couldn't retrieve information from Gimbal Hardware Controller."
            ) from exc

        return msg

    def stop(self):
        try:
            rc = self.pmac.sendCommand(pmac.CMD_STOP)
        except PMACError as exc:
            raise GimbalError("Couldn't complete the STOP command.") from exc

        return rc

    def homing(self):
        try:
            rc = self.pmac.sendCommand(pmac.CMD_HOMING)
        except PMACError as exc:
            raise GimbalError("Couldn't complete the HOMING command.") from exc

        logger.info("Homing: Command was successful")

        return rc

    def is_homing_done(self):
        try:
            rc = self.pmac.getQVars(26, [0], int)[0]
        except PMACError as pmac_exc:
            logger.error(f"PMAC Exception: {pmac_exc}", exc_info=True)
            return False

        msg = {  # noqa: F841
            0: "Homing status is undefined.",
            1: "Homing is in progress",
            2: "Homing is done",
            3: "An error occurred during the Homing process.",
        }

        if rc == 2:
            return True

        return False

    def activate_control_loop(self):
        try:
            rc = self.pmac.sendCommand(pmac.CMD_CONTROLON)
        except PMACError as exc:
            raise GimbalError("Couldn't activate the control loop.") from exc

        msg = {  # noqa: F841
            0: "Command was successful",
            -1: "Command was ignored",
            -2: "Control of the servo motors has failed",
        }

        return rc

    def deactivate_control_loop(self):
        try:
            rc = self.pmac.sendCommand(pmac.CMD_CONTROLOFF)
        except PMACError as exc:
            raise GimbalError("Couldn't de-activate the control loop.") from exc

        return rc

    def __move(self, cm, grx, gry):
        """
        Ask the controller to perform the movement defined by the arguments.

        For all control modes cm, the rotation centre coincides with the Object
        Coordinates System origin and the movements are controlled with translation
        components at first (Tx, Ty, tZ) and then the rotation components (Rx, Ry, Rz).

        Control mode cm:
            * 0 = absolute control, object coordinate system position and orientation
                    expressed in the invariant user coordinate system
            * 1 = user relative, motion expressed in the Object Coordinate System

        Args:
            cm (int): control mode
            grx (float): rotation around the X-axis [deg]
            gry (float): rotation around the Y-axis [deg]

        Returns:
            0 on success, -1 when ignored, -2 on error.

        Raises:
            PMACError: when the arguments do not match up or when there is a time out or when
            there is a socket
            communication error.

        .. note:: When the command was not successful, this method will query the ``POSVALID?``
                  using the checkAbsolutePosition() and print a summary of the error messages
                  to the log file.
        """
        rc = self.pmac.sendCommand(pmac.CMD_MOVE, cm=cm, grx=grx, gry=gry)

        error_code_msg = {
            0: "Command was successful",
            -1: "Command was ignored",
            -2: "Command was invalid, check with POSVALID?",
        }

        if rc < 0:
            msg = f"Move command returned ({rc}: {error_code_msg[rc]})."

            if rc == -2:
                Q29, errors = self.__check_movement(cm, grx, gry)

                msg += "\nError messages returned from POSVALID?:\n"
                for key, value in errors.items():
                    msg += f"  bit {key:<2d}: {value}\n"

            logger.debug(msg)

        return rc

    def __check_movement(self, cm, grx, gry):
        """
        Ask the controller if the movement defined by the arguments is feasible.

        Returns a tuple where the first element is an integer that represents the
        bitfield encoding the errors. The second element is a dictionary with the
        bit numbers that were (on) and the corresponding error description.

        Args:
            grx (float): rotation around the X-axis [deg]
            gry (float): rotation around the Y-axis [deg]

        """
        out = self.pmac.sendCommand(pmac.CMD_POSVALID_GET, cm=cm, grx=grx, gry=gry)
        
        Q29 = decode_Q29(out[0])
        return out[0], Q29

    def move_absolute(self, grx, gry):
        try:
            rc = self.__move(0, grx, gry)
        except PMACError as exc:
            raise GimbalError("Couldn't execute the moveAbsolute command.") from exc

        return rc

    def check_absolute_movement(self, grx, gry):
        return self.__check_movement(0, grx, gry)

    def move_relative(self, grx, gry):
        try:
            rc = self.__move(10, grx, gry)
        except PMACError as exc:
            raise GimbalError("Couldn't execute the relative movement [user] command.") from exc

        return rc

    def check_relative_movement(self, grx, gry):
        return self.__check_movement(10, grx, gry)

    def perform_maintenance(self, axis):
        try:
            rc = self.pmac.sendCommand(pmac.CMD_MAINTENANCE, axis=axis)
        except PMACError as exc:
            raise GimbalError("Couldn't perform maintenance cycle.") from exc

        msg = {0: "Command was successfully executed", -1: "Command was ignored"}  # noqa: F841

        return rc

    def goto_specific_position(self, pos):
        try:
            rc = self.pmac.sendCommand(pmac.CMD_SPECIFICPOS, pos=pos)
        except PMACError as exc:
            raise GimbalError(f"Couldn't goto specific position [pos={pos}].") from exc

        msg = {
            0: "Command was successfully executed",
            -1: "Command was ignored",
            -2: "Invalid movement command",
        }

        logger.info(f"Goto Specific Position [{pos}]: {msg[rc]}")

        if rc < 0:
            try:
                out = self.pmac.getQVars(0, [29], int)
            except PMACError as exc:
                raise GimbalError("Couldn't get a response from the Gimbal controller.") from exc
            Q29 = decode_Q29(out[0])

            msg = "Error messages returned in Q29:\n"
            for key, value in Q29.items():
                msg += f"  {key:2d}: {value}\n"

            logger.debug(msg)

        return rc

    def goto_zero_position(self):
        try:
            rc = self.pmac.sendCommand(pmac.CMD_SPECIFICPOS, pos=self.SPEC_POS_USER_ZERO)
        except PMACError as exc:
            raise GimbalError("Couldn't goto user zero position.") from exc

        msg = {
            0: "Command was successfully executed",
            -1: "Command was ignored",
            -2: "Invalid movement command",
        }

        logger.info(f"Goto User Zero Position [2]: {msg[rc]}")

        if rc < 0:
            try:
                out = self.pmac.getQVars(0, [29], int)
            except PMACError as exc:
                raise GimbalError("Couldn't get a response from the Gimbal controller.") from exc
            Q29 = decode_Q29(out[0])

            msg = "Error messages returned in Q29:\n"
            for key, value in Q29.items():
                msg += f"  {key:2d}: {value}\n"

            logger.debug(msg)

        return rc

    def get_buffer(self):
        return_string = self.pmac.getBuffer()
        return return_string

    def clear_error(self):
        try:
            rc = self.pmac.sendCommand(pmac.CMD_CLEARERROR)
        except PMACError as exc:
            raise GimbalError("Couldn't clear errors in the controller software.") from exc

        return rc

    def jog(self, axis: int, inc: float) -> int:
        if not (1 <= axis <= 2):
            logger.error(f"The axis argument must be 1 <= axis <= 2, given {axis}.")
            raise GimbalError("Illegal Argument Value: axis is {axis}, should be 1 <= axis <= 2.")

        try:
            rc = self.pmac.sendCommand(pmac.CMD_JOG, axis=axis, inc=inc)
        except PMACError as exc:
            raise GimbalError(
                f"Couldn't execute the jog command for axis={axis} with inc={inc} [deg]."
            ) from exc

        msg = {0: "Command was successfully executed", -1: "Command was ignored"}

        logger.info(f"JOG on axis [{axis}] of {inc} deg: {msg[rc]}")

        return rc

    def configure_offsets(self, grx, gry):
        try:

            rc = self.pmac.sendCommand(
                pmac.CMD_CFG_OFFSET,
                grx = round(grx, NUM_OF_DECIMALS),
                gry = round(gry, NUM_OF_DECIMALS))
        except PMACError as exc:
            raise GimbalError(
                "Couldn't configure coordinate systems on the gimbal controller."
            ) from exc

        return rc

    def get_offsets(self):
        try:
            out = self.pmac.sendCommand(pmac.CMD_CFG_OFFSET_GET)
        except PMACError as exc:
            raise GimbalError(
                "Couldn't get the coordinate systems information from the gimbal controller."
            ) from exc

        return out

    def get_debug_info(self):
        try:
            out = self.pmac.sendCommand(pmac.CMD_STATE_DEBUG_GET)
        except PMACError as exc:
            raise GimbalError(
                "Couldn't get the debugging information from the gimbal controller."
            ) from exc

        return out

    def set_speed(self, sr):
        try:
            rc = self.pmac.sendCommand(pmac.CMD_CFG_SPEED, sr=sr)
        except PMACError as exc:
            raise GimbalError(
                "Couldn't set the speed for rotation [{sr} deg/s]."
            ) from exc

        return rc

    def get_speed(self):
        try:
            out = self.pmac.sendCommand(pmac.CMD_CFG_SPEED_GET)
        except PMACError as exc:
            raise GimbalError(
                "Couldn't get the speed settings from the gimbal controller."
            ) from exc

        return out

    def get_general_state(self):
        try:
            out = self.pmac.getQVars(36, [0], int)
        except PMACError as pmac_exc:
            logger.error(f"PMAC Exception: {pmac_exc}", exc_info=True)
            return None

        return out[0], pmac.decode_Q36(out[0])

    def get_actuator_state(self):
        try:
            out = self.pmac.getQVars(30, [0, 1], int)
        except PMACError as pmac_exc:
            logger.error(f"PMAC Exception: {pmac_exc}", exc_info=True)
            return None

        return [pmac.decode_Q30(value) for value in out]

    def get_user_positions(self):
        try:
            out = self.pmac.sendCommand(pmac.CMD_POSUSER_GET)
        except PMACError as pmac_exc:
            logger.error(f"PMAC Exception: {pmac_exc}", exc_info=True)
            return None

        return out

    def get_machine_positions(self):
        try:
            out = self.pmac.getQVars(47, [0, 1], float)
        except PMACError as pmac_exc:
            logger.error(f"PMAC Exception: {pmac_exc}", exc_info=True)
            return None

        return out

    def get_actuator_length(self):
        try:
            out = self.pmac.getQVars(41, [0, 1], float)
        except PMACError as pmac_exc:
            logger.error(f"PMAC Exception: {pmac_exc}", exc_info=True)
            return None

        return out

    def get_motor_temperatures(self):
        try:
            out = self.pmac.sendCommand(pmac.CMD_STATE_AI_GET)
        except PMACError as pmac_exc:
            logger.error(f"PMAC Exception: {pmac_exc}", exc_info=True)
            return None

        return out

    def reset(self, wait=True, verbose=False):
        try:
            self.pmac.sendCommand(pmac.CMD_RESETSOFT)
        except PMACError as exc:
            raise GimbalError("Couldn't (soft) reset the gimbal controller.") from exc

        # How do I know when the RESETSOFT has finished and we can send further commands?

        if wait:
            logger.info("Sent a soft reset, this will take about 30 seconds to complete.")
            self.__wait(30, verbose=verbose)

    def __wait(self, duration, verbose=False):
        """
        Wait for a specific duration in seconds.
        """
        _timeout = timedelta(seconds=duration)
        _start = datetime.now()

        _rate = timedelta(seconds=5)  # every _rate seconds print a message
        _count = 0

        logger.info(f"Just waiting {duration} seconds ...")

        while datetime.now() - _start < _timeout:

            if verbose and (datetime.now() - _start > _count * _rate):
                _count += 1
                logger.info(f"waited for {_count * _rate} of {_timeout} seconds, ")
                print(f"waited for {_count * _rate} of {_timeout} seconds, ")

            time.sleep(0.01)


class GimbalSimulator(GimbalInterface):
    """
    GimbalSimulator simulates the Symétrie Gimbal. The class is heavily based on the
    ReferenceFrames in the `egse.coordinates` package.

    The simulator implements the same methods as the GimbalController class which acts on the
    real hardware controller in either simulation mode or with a real Gimbal connected.

    Therefore, the GimbalSimulator can be used instead of the Gimbal class in test harnesses
    and when the hardware is not available.

    This class simulates all the movements and status of the Gimbal.
    """

    def __init__(self):
        self.grx_off = 0.
        self.gry_off = 0.
        self.mach_rx = 0.
        self.mach_ry = 0.

        # NOTE: These limits affect to user angles, NOT machine angles
        self.min_rx  = -20.51 # Tested empirically
        self.max_rx  = +20.51 # Tested empirically

        self.min_ry  = -20.51 # Tested empirically
        self.max_ry  = +20.51 # Tested empirically

        # TODO: Look into these defaults
        self.sr      = GIMBAL_SETTINGS.DEFAULT_SPEED
        self.sr_min  = 1e-1
        self.sr_max  = 1

        # Internal flags
        self.homing_done  = True  # Tested empirically
        self.control_loop = False
        self.cs_error     = False
        self.off_limits   = False

        self.connected = False

    def is_simulator(self):
        return True

    def connect(self):
        self.connected = True

    def reconnect(self):
        if self.is_connected():
            self.disconnect()
        self.connect()

    def disconnect(self):
        # TODO:
        #   Should I keep state in this class to check if it has been disconnected?
        #
        # TODO:
        #   What happens when I re-connect to this Simulator? Shall it be in Homing position or
        #   do I have to keep state via a persistency mechanism?
        self.connected = False

    def is_connected(self):
        return self.connected

    def reset(self, wait=True, verbose=False):
        # TODO:
        #   Find out what exactly a reset() should be doing. Does it bring back the Gimbal
        #   in it's original state, loosing all definitions of coordinate systems? Or does it
        #   do a clearError() and a homing()?
        pass

    def homing(self):
        # Symétrie's Gimbal relies on absolute encoders. This causes the current Gimbal
        # position to be unaltered, although the control loop stops.
        self.homing_done = True
        self.control_loop = False
        return 0

    def is_homing_done(self):
        return self.homing_done

    def stop(self):
        pass

    def clear_error(self):
        self.cs_error   = False
        self.off_limits = False

        return 0

    def activate_control_loop(self):
        self.control_loop = True
        return self.control_loop

    def deactivate_control_loop(self):
        self.control_loop = False
        return self.control_loop

    def configure_offsets(self, grx, gry):
        self.grx_off = grx
        self.gry_off = gry
        return 0

    def get_offsets(self):
        return [self.grx_off, self.gry_off]

    def __compose_Q29(self):
        q29 = 0

        if not self.homing_done:
            q29 |= 1

        if self.cs_error:
            q29 |= 2
        
        if self.off_limits:
            q29 |= 32
        
        return q29
        
    def __check_movement(self, cm, grx, gry):
        """
        Ask the controller if the movement defined by the arguments is feasible.

        Returns a tuple where the first element is an integer that represents the
        bitfield encoding the errors. The second element is a dictionary with the
        bit numbers that were (on) and the corresponding error description.

        Args:
            grx (float): rotation around the X-axis [deg]
            gry (float): rotation around the Y-axis [deg]

        """

        ret = 0

        self.off_limits = False

        if cm == 0:
            target_x = grx - self.grx_off
            target_y = gry - self.gry_off
        elif cm == 1:
            target_x = grx - self.grx_off
            target_y = self.mach_ry
        elif cm == 2:
            target_x = self.mach_rx
            target_y = gry - self.gry_off
        elif cm == 10:
            target_x = grx + self.mach_rx
            target_y = gry + self.mach_ry
        elif cm == 11:
            target_x = grx + self.mach_rx
            target_y = self.mach_ry
        elif cm == 12:
            target_x = self.mach_rx
            target_y = gry + self.mach_ry
        else:
            target_x = math.nan
            target_y = math.nan
            ret = -1

        # Minimal error checking. Limit checking is performed against user coordinates,
        # and not machine coordinates.
        user_x = target_x + self.grx_off
        user_y = target_y + self.gry_off

        if not self.homing_done:
            ret = -2
        elif user_x < self.min_rx or user_x > self.max_rx \
          or user_y < self.min_ry or user_y > self.max_ry:
            ret = -2
            self.off_limits = True

        sim_Q29 = self.__compose_Q29()

        Q29 = decode_Q29(sim_Q29)
        return ret, sim_Q29, Q29, target_x, target_y

    def __move(self, cm, grx, gry):
        rc, Q29, errors, tx, ty = self.__check_movement(cm, grx, gry)

        error_code_msg = {
            0: "Command was successful",
            -1: "Command was ignored",
            -2: "Command was invalid, check with POSVALID?",
        }

        if rc < 0:
            msg = f"Move command returned ({rc}: {error_code_msg[rc]})."

            if rc == -2:
                msg += "\nError messages returned from POSVALID?:\n"
                for key, value in errors.items():
                    msg += f"  bit {key:<2d}: {value}\n"

            logger.debug(msg)
        else:
            self.activate_control_loop() # Tested empirically
            self.mach_rx = tx
            self.mach_ry = ty

        return rc

    def move_absolute(self, grx, gry):
        return self.__move(0, grx, gry)

    def check_absolute_movement(self, grx, gry):
        ret, sim_Q29, Q29, target_x, target_y = self.__check_movement(0, grx, gry)
        return ret, Q29

    def move_relative(self, grx, gry):
        return self.__move(10, grx, gry)

    def check_relative_movement(self, grx, gry):
        ret, sim_Q29, Q29, target_x, target_y = self.__check_movement(10, grx, gry)
        return ret, Q29

    def get_user_positions(self):
        pos = [self.mach_rx + self.grx_off, self.mach_ry + self.gry_off]
        return pos

    def get_machine_positions(self):
        pos = [self.mach_rx, self.mach_ry]
        return pos

    def get_actuator_length(self):
        # Tested empirically. It looks like the Gimbal holds a 1 deg/mm relationship
        # between each axis and the corresponding actuator.
        return self.get_machine_positions()

    def get_motor_temperatures(self):
        # Return random values, so we can see some activity in the UI during
        # simulations.
        return [30 + .1 * np.random.randn(), 30 + .1 * np.random.randn()]
    
    def get_general_state(self):
        state = 0
        state = set_bit(state, 1)  # System Initialized
        state = set_bit(state, 2)  # In Position
        if self.homing_done:
            state = set_bit(state, 4)
        if self.control_loop:
            state = set_bit(state, 3)
        return state, decode_Q36(state)

    def goto_specific_position(self, pos):
        if pos == GimbalController.SPEC_POS_MACHINE_ZERO:
            return self.__move(0, self.grx_off, self.gry_off)
        elif pos == GimbalController.SPEC_POS_USER_ZERO:
            return self.__move(0, 0, 0)
        else:
            return -1

    def goto_zero_position(self):
        return self.goto_specific_position(GimbalController.SPEC_POS_USER_ZERO)

    def is_in_position(self):
        return True

    def jog(self, axis: int, inc: float) -> int:
        pass

    def get_debug_info(self):
        pass

    def set_speed(self, sr):
        self.sr = sr

    def get_speed(self):
        return (self.sr, self.sr_min, self.sr_max)

    def get_actuator_state(self):
        return [({0: 'In position', 1: 'Control loop on servo motors active', 2: 'Homing done',
                  4: 'Input "Positive limit switch"', 5: 'Input "Negative limit switch"',
                  6: 'Brake control output'},
                 [1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), (
                {0: 'In position', 1: 'Control loop on servo motors active', 2: 'Homing done',
                 4: 'Input "Positive limit switch"', 5: 'Input "Negative limit switch"',
                 6: 'Brake control output'},
                [1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])]

    def perform_maintenance(self, axis):
        pass

    def info(self):

        msg = "Info about the GimbalSimulator:\n"
        msg += "\n"
        msg += "This Gimbal Simulator works with several reference frames:\n"
        msg += "  * The machine reference frame\n"
        msg += "  * The user reference frame\n\n"
        msg += (
            "Any movement commands result in a transformation of the appropriate coordinate "
            "systems."
        )

        logger.info(msg)

        return msg


class GimbalProxy(Proxy, GimbalInterface):
    """The GimbalProxy class is used to connect to the control server and send commands to the
    Gimbal remotely."""

    def __init__(
        self,
        protocol=CTRL_SETTINGS.PROTOCOL,
        hostname=CTRL_SETTINGS.HOSTNAME,
        port=CTRL_SETTINGS.COMMANDING_PORT,
    ):
        """
        Args:
            protocol: the transport protocol [default is taken from settings file]
            hostname: location of the control server (IP address) [default is taken from settings
            file]
            port: TCP port on which the control server is listening for commands [default is
            taken from settings file]
        """
        super().__init__(connect_address(protocol, hostname, port))
