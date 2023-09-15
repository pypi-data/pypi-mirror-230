from egse.decorators import dynamic_interface


class AlphaControllerInterface:
    @dynamic_interface
    def info(self):
        """Returns basic information about the gimbal and the controller.

        Returns:
            a multiline response message containing the device info.
        Raises:
            GimbalError: when information can not be retrieved.
        """
        raise NotImplementedError

    @dynamic_interface
    def reset(self, wait=True):
        """Completely resets the Gimbal hardware controller with the standard boot cycle.

        Args:
            wait (bool): after the reset command has been sent to the controller, wait
                for 30 seconds which should complete the cycle, i.e. this command will
                only return after 30 seconds.

        .. Note::
           This command is equivalent to power cycling the controller manually.

        """
        raise NotImplementedError

    @dynamic_interface
    def homing(self):
        """Start the homing cycle for the Gimbal.

        Homing is required before performing a control movement. Without absolute encoders,
        the homing is performed with a gimbal movement until detecting the reference sensor
        on each of the actuators. The Gimbal will go to a position were the sensors are
        reached that signal a known calibrated position and then returns to the zero position.

        Whenever a homing is performed, the method will return before the actual movement
        is finished.

        The homing cycle takes about two minutes to complete, but the ``homing()`` method
        returns almost immediately. Therefore, to check if the homing is finished, use
        the is_homing_done() method.

        Returns:
            0 on success.
        Raises:
            GimbalError: when there is a time out or when there is a communication error with
            the gimbal.
        """
        raise NotImplementedError

    #
    # Gimbal does not support virtual homing
    #
    # @dynamic_interface
    # def set_virtual_homing(self, tx, ty, tz, rx, ry, rz):


    @dynamic_interface
    def stop(self):
        """Stop the current motion. This command can be send during a motion of the Gimbal.

        Returns:
            0 on success.
        Raises:
            GimbalError: when there is a time out or when there is a communication error with
            the gimbal.
        """
        raise NotImplementedError

    @dynamic_interface
    def clear_error(self):
        """Clear all errors in the controller software.

        Returns:
            0 on success.
        Raises:
            GimbalError: when there is Time-Out or when there is a communication error with the
            gimbal.
        """
        raise NotImplementedError

    @dynamic_interface
    def activate_control_loop(self):
        """Activates the control loop on motors.

        Returns:
            0 on success, -1 when ignored, -2 on error.
        Raises:
            GimbalError: when there is a time out or when there is a communication error with
            the gimbal
                hardware controller.
        """
        raise NotImplementedError

    @dynamic_interface
    def deactivate_control_loop(self):
        """Disables the control loop on the servo motors.

        Returns:
            0 on success.
        Raises:
            GimbalError: when there is a time out or when there is a communication error with
            the gimbal.
        """
        raise NotImplementedError

    @dynamic_interface
    def jog(self, axis: int, inc: float) -> int:
        """Perform a JOG-type movement on the specified actuator.

        .. note::
            This is a maintenance feature.

        Args:
            axis (int): number of the actuator (1 to 2)
            inc (float): increment to achieve in [deg]
        Returns:
            0 on success, -1 if command was ignored due to non-compliance.
        Raises:
            GimbalError: when there is a time out or when there is a communication error with
            the gimbal.
        """
        raise NotImplementedError

    @dynamic_interface
    def get_debug_info(self):
        """
        Request debug information from the Gimbal Controller.

        The method returns four values that represent the following status:

        1. ``Homing``: state of the homing
        2. ``PosRef``: state of the Position Reference command
        3. ``KinError``: error in kinematic calculation
        4. ``Panel``: Panel state

        Note many of these codes overlap PUNA's debug codes. These have been
        thoroughly reviewed before defining the interface.

        The Homing can take the following values:

            =====     ==================
            Value     Meaning
            =====     ==================
            0         Undefined
            1         Homing in progress
            2         Homing done
            3         Error
            =====     ==================

        The PosRef can take the following values:

            =======     =====================
             Value       Meaning
            =======     =====================
               0         Undefined
               1         Abort input error
               2         Movement in progress
               3         Position reached
               4         Error
            =======     =====================

        The KinError can take the following values:

            =======     ===============================================
             Value       Meaning
            =======     ===============================================
               0         none
               1         Homing not done
               2         Inverse kinematic model (MGI) – workspace
               3         Inverse kinematic model (MGI) – joint angle
               4         Forward kinematic model (MGD) – workspace
               5         Forward kinematic model (MGD) – max iteration
               6         Position calculation (PLCC) – workspace
               7         Position calculation (PLCC) – max iteration.
            =======     ===============================================

        The Panel status can take the following values:

            ======   ===============
            Index       Command
            ======   ===============
            -2       Command error
            -1       Ignored / Command not allowed
            **0**       **None**
            1        Homing
            2        Stop
            3        Control ON
            4        Control OFF
            10       Valid POS
            11       Move
            12       Sequence
            13       Specific POS
            15       Clear Error
              **Family “Set config”**
            ------------------------
            21       Config CS
            22       Config Limits_mTn
            23       Config Limits_uTo
            24       Config Limits_Enabled
            25       Config Speed
            26       Config Current
            27       Config Backlash
              **Family “Get config”**
            ------------------------
            31       Config CS
            32       Config Limits_mTn
            33       Config Limits_uTo
            34       Config Limits_Enabled
            35       Config Speed
            36       Config Current
            37       Config Backlash
              **Family “Maintenance”**
            ------------------------
            41       Jog
            50       Config Save
            51       Config Default
            52       Config Saved?
            55       Version
            ======   ===============

        """
        raise NotImplementedError

    @dynamic_interface
    def configure_offsets(self, grx, gry):
        """
        Changes the definition of offsets. This is the Gimbal's equivalent of changing the
        PUNA's coordinate system.

        The parameters grx and gry are used to define axes offsets. The position with
        offset is named Position or User position. The position without offset is named
        Machine position.

        Args:
            grx (float): offset on the Rx axis [deg]
            gry (float): offset on the Ry axis [deg]

        Returns:
            0 on success and -1 when the configuration is ignored, e.g. when password protection
            is enabled.
        """
        raise NotImplementedError

    @dynamic_interface
    def get_offsets(self):
        """Retrieve the definition of the gimbal offsets.

        Returns:
            grx and gry in [deg].
        Raises:
            GimbalError: when an error occurred while trying to retrieve the information.
        """
        raise NotImplementedError

    @dynamic_interface
    def move_absolute(self, grx, gry):
        """Rotates the gimbal in both axes, absolute coordinates.

        Args:
            grx (float): rotation around the X-axis [deg]
            gry (float): rotation around the Y-axis [deg]

        Returns:
            return_code: 0 on success, -1 when ignored, -2 on error

        Raises:
            GimbalError: when the arguments do not match up, or when there is a time out or when
            there is a
            socket communication error.

        .. note::
           When the command was not successful, this method will query the
           POSVALID? using the checkAbsolutePosition() and print a summary
           of the error messages to the log file.

        .. todo::
           do we want to check if the movement is valid before actually performing
           the movement?

        """
        raise NotImplementedError

    @dynamic_interface
    def move_relative(self, grx, gry):
        """Move the gimbal relative to its current position.

        Args:
            grx (float): rotation around the X-axis [deg]
            gry (float): rotation around the Y-axis [deg]

        Returns:
            0 on success, -1 when ignored, -2 on error.

        Raises:
            GimbalError: when the arguments do not match up, or when there is a time out or when
            there is a
            socket communication error.

        .. todo:: do we want to check if the movement is valid before actually performing
                  the movement?

        """
        raise NotImplementedError

    @dynamic_interface
    def check_absolute_movement(self, grx, gry):
        """Check if the requested gimbal movement is valid.

        Args:
            grx (float): rotation around the X-axis [deg]
            gry (float): rotation around the Y-axis [deg]

        Returns:
            tuple: where the first element is an integer that represents the
                bitfield encoding the errors. The second element is a dictionary
                with the bit numbers that were (on) and the corresponding error
                description.

        .. todo:: either provide a more user friendly return value or a method/function
                  to process the information into a human readable form. Also update
                  the documentation of this method with more information about the
                  bitfields etc.
        """
        raise NotImplementedError

    @dynamic_interface
    def check_relative_movement(self, grx, gry):
        """Check if the requested object movement is valid.

        The relative motion is expressed in the object coordinate system.

        Args:
            grx (float): rotation around the X-axis [deg]
            gry (float): rotation around the Y-axis [deg]

        Returns:
            tuple: where the first element is an integer that represents the
                bitfield encoding the errors. The second element is a dictionary
                with the bit numbers that were (on) and the corresponding error
                description.

        .. todo:: either provide a more user friendly return value or a method/function
                  to process the information into a human readable form. Also update
                  the documentation of this method with more information about the
                  bitfields etc.
        """
        raise NotImplementedError

    @dynamic_interface
    def get_user_positions(self):
        """Retreive the current position of the gimbal.

        Asks the current position of the gimbal. Position returned corresponds to the
        user position (position with offsets).

        Returns:
            array: an array of two float values for grx, gry
            None: when an Exception was raised and logs the error message.

        .. note:: This is equivalent to the POSUSER? command.
        """
        raise NotImplementedError

    @dynamic_interface
    def get_machine_positions(self):
        """Retreive the current position of the gimbal.

        Asks the current position of the gimbal. Position returned corresponds to the
        machine position (position without offsets).

        Returns:
            array: an array of two float values for grx, gry
            None: when a PMACError was raised and logs the error message.

        .. note:: This is equivalent to the POSMACH? command.
        """
        raise NotImplementedError

    @dynamic_interface
    def get_motor_temperatures(self):
        """Retreive the current temperatures of the Gimbal motors.

        Asks the current temperatures of the motors as measured by their
        corresponding thermocouples. Results are in Celsius.

        Returns:
            array: an array of two float values for grx, gry
            None: when a PMACError was raised and logs the error message.

        .. note:: This is equivalent to the STATE#AI? command.
        """
        raise NotImplementedError

    @dynamic_interface
    def get_actuator_length(self):
        """Retrieve the current length of the gimbal actuators.

        Returns:
            array: an array of 2 float values for actuator length L1 to L2 in [mm], and \
            None: when an Exception was raised and logs the error message.
        """

        raise NotImplementedError

    @dynamic_interface
    def set_speed(self, sr):
        """Set the speed of the gimbal movements.

        Args:
            sr (float): The angular speed, expressed in deg per second [deg/s].

        The argument sr is automatically limited by the controller between the
        minimum and maximum speeds allowed for the gimbal.

        Returns:
            0 on success and -1 when the configuration is ignored, e.g. when password protection
            is enabled.
        """
        raise NotImplementedError

    @dynamic_interface
    def get_speed(self):
        """Retrieve the configuration of the movement speed.

        Returns:
            sr, sr_min, sr_max

        Where:
            * ``sr`` is the angular speed of the gimbal in deg per second [deg/s]
            * ``sr_min``, ``sr_max`` are the limits for the rotation speed [deg/s]

        """
        raise NotImplementedError

    @dynamic_interface
    def get_general_state(self):
        """Retrieve general state information of the gimbal.

        Returns:
            tuple: where the first element is an integer where the bits represent each state, and
                the second element is an array of True/False flags for each state described in
                Gimbal
                Controller API, section 2.5.6.

            None: when an Exception was raised and logs the error message.

        .. note:: This is equivalent to the STATE#GIMBAL? Command.
        """
        raise NotImplementedError

    @dynamic_interface
    def get_actuator_state(self):
        """Retreive general state information of the actuators.

        For each of the two actuators, an integer value is returned that should be interpreted as a
        bit field containing status bits for that actuator.

            ======   ========================
             Bit      Function
            ======   ========================
              0       In position
              1       Control loop on servo motors active
              2       Homing done
              3       Input "Home Switch"
              4       Input "Positive limit switch"
              5       Input "Negative limit switch"
              6       Brake control output
              7       Following error (warning)
              8       Following error (Fatal)
              9       Actuator out of bounds error
             10       Amplifier error
             11       Encoder error
             12       Phasing error (brushless engine only)
             13-23    Reserved
            ======   ========================

        Returns:
            array: an array of two (2) dictionaries with True/False flags for each actuator state
            as described in
                Gimbal Controller API, section 2.5.5.
            None: when an Exception was raised and logs the error message.

        .. note:: This is equivalent to the STATE#ACTUATOR? Command.
        """
        raise NotImplementedError

    @dynamic_interface
    def goto_specific_position(self, pos):
        """Ask to go to a specific position.

        * pos=0 Machine zero position (jog & maintenance only!)
        * pos=1 Unused (not valid for the Gimbal)
        * pos=2 User zero position (with offsets)

        Returns:
            0 on success, -1 when ignored, -2 for an invalid movement command

        Raises:
            GimbalError: when there is Time-Out or when there is a communication error with the
            gimbal controller.
        """
        raise NotImplementedError

    @dynamic_interface
    def goto_zero_position(self):
        """Ask the gimbal to go to the user zero position.

        Returns:
            0 on success, -1 when ignored, -2 for an invalid movement command

        Raises:
            GimbalError: when there is Time-Out or when there is a socket communication error.
        """
        raise NotImplementedError

    @dynamic_interface
    def is_homing_done(self):
        """
        Check if Homing is done. This method checks the ``Q26`` variable.
        When this variable indicates 'Homing is done' it means the command has properly been
        executed,
        but it doesn't mean the Gimbal is in position. The gimbal might still be moving to its
        zero position.

        Returns:
            True when the homing is done, False otherwise.
        """
        raise NotImplementedError

    @dynamic_interface
    def is_in_position(self):
        """
        Checks if the actuators are in position.

        This method queries the Q36 variable and examines the third bit which is the 'Is
        Position' bit.
        This method does **not** query the actuator state variables Q30 till Q36.

        Returns:
            True when in position, False otherwise.
        """
        raise NotImplementedError

    @dynamic_interface
    def perform_maintenance(self, axis):
        """Perform a maintenance cycle which consists to travel the full range
        on one axis corresponding to the Gimbal machine limits. The movement is
        also in machine coordinate system.

        Undocumented. Ask Symetrie.

        Args:
            axis (int): on which axis the full range movement is executed
        Returns:
            0 on success, -1 when ignored for non-compliance.
        Raises:
            GimbalError: when there is Time-Out or when there is a socket communication error.
        """
        raise NotImplementedError

    def log_positions(self):
        """
        Log the current position of the gimbal (level=INFO). The positions correspond to

          * the position of the object in the User Coordinate System, and
          * the position of the gimbal in the Machine Coordinate System.

        """

        pos = self.get_user_positions()
        logger.info(
            f"Object [in User]     : "
            f"{pos[0]:2.5f}, {pos[1]:2.5f}"
        )

        pos = self.get_machine_positions()
        logger.info(
            f"Platform [in Machine]: "
            f"{pos[0]:2.5f}, {pos[1]:2.5f}"
        )

