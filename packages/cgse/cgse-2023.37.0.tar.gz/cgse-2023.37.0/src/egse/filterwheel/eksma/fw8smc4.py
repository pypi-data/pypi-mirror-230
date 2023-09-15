"""
This module defines the basic classes to access the EKSMA Filter wheel connected to the
8SMC4 motor controller that will be used in the IAS TVAC setup.
Note the EKSMA filter wheel is made of 2x filterwheels coupled to a same stepper motor. Each filter wheel has up to 8
filter placements that leads to up to 64 filter combinations
"""
import logging

import numpy as np

from egse.confman import ConfigurationManagerProxy
from egse.decorators import dynamic_interface
from egse.device import DeviceInterface
from egse.filterwheel import FilterWheelError
from egse.filterwheel.eksma.fw8smc4_devif import FilterWheel8SMC4Error
from egse.filterwheel.eksma.fw8smc4_devif import FilterWheel8SMC4EthernetInterface
from egse.filterwheel.eksma.fw8smc4_devif import FilterWheel8SMC4USBInterface


from egse.proxy import Proxy
from egse.settings import Settings
from egse.zmq_ser import connect_address

LOGGER = logging.getLogger(__name__)

CTRL_SETTINGS = Settings.load("Filter Wheel 8SMC4 Control Server")
DEVICE_SETTINGS = Settings.load(filename="fw8smc4.yaml")
SITE = Settings.load("SITE")


class FilterWheel8SMC4Interface(DeviceInterface):
    """
    Interface definition for the Filter Wheel 8SMC4 Controller, Simulator and Proxy..
    """
    @dynamic_interface
    def load_wheels(self):
        """
        Gets the attenuation setup configuration loaded from the configuration manager proxy
        """
        return NotImplemented

    @dynamic_interface
    def wheel_factors(self):
        """
        Gets the attenuation setup configuration loaded from the configuration manager proxy
        """
        return NotImplemented


    @dynamic_interface
    def set_position(self):
        """
        Sets the position of each og the filter wheels

        Args:
            pos_wheel1(int)  the position number of wheel 1 from 0 to 7
            pos_wheel2(int)  the position number of wheel 2 from 0 to 7
        """
        return NotImplemented

    @dynamic_interface
    def get_position(self):
        """
        Gets the position of each of the filter wheels

        Returns:
            A list of 2 integers with the position of the wheels
        """
        return NotImplemented

    @dynamic_interface
    def homing(self):
        """

        """
        return NotImplemented

    @dynamic_interface
    def get_status(self):
        """

        """
        return NotImplemented

    @dynamic_interface
    def att_get_level(self):
        """
        Reports current attenuator level (a factor 0..1).

        Returns:
            A float from 0 to 1.
        """
        return NotImplemented

    @dynamic_interface
    def att_set_level_factor(self):
        """
        Sets attenuator to the level closest to <factor>. There are 38 levels of attenuation available, from 0 to 1.
        This command chooses the level closest to the requested value.

        Args:
            fwc_fraction(float) from 0 to 1

        """
        return NotImplemented

    @dynamic_interface
    def att_set_level_position(self):
        """
        Sets attenuator wheels to positions <a> and <b> #same command than set_position
        (wheels positions go from 1 to 8).

        Args:
            pos_wheel1(int)  the position number of wheel 1 from 0 to 7
            pos_wheel2(int)  the position number of wheel 2 from 0 to 7
        """
        return NotImplemented

    @dynamic_interface
    def att_level_up(self):
        """
        Sets the attenuator to the level immediately above the current level. It won't go above 1.
        """
        return NotImplemented

    @dynamic_interface
    def att_level_down(self):
        """
        Sets the attenuator to the level immediately below the current level.It won't go lower than 0.
        """
        return NotImplemented

    @dynamic_interface
    def att_status(self):
        """
        Reports if device attenuator is ready for use.
        """
        return NotImplemented


class FilterWheel8SMC4Simulator(FilterWheel8SMC4Interface):
    """
    The Filter Wheel Simulator class.
    """

    def __init__(self):

        self._att_position_1 = 1
        self._att_position_2 = 1
        self._is_connected = False
        self._wheel_position = [175, 0]

        # when the wheel factor is 0 there is no filter in the wheel, if OD units are considered
        # when the wheel factor is a character, the filter is a spectral filter
        # will be late replaced by the setup configuration
        self.wheel1 = {0: 0,
                      1: 2,
                      2: 1,
                      3: 0.03,
                      4: "T4K",
                      5: "T5K",
                      6: "T6K",
                      7: "T6.5K"}

        self.wheel2 = {0: 0,
                      1: 0.3,
                      2: 0.05,
                      3: 5,
                      4: 2,
                      5: 0.1,
                      6: 0.15,
                      7: 3}
        self._setup = None
        self._att_level = [self.wheel1, self.wheel2, 0]

        # attenuator factor and index position list length 64
        self.factor = []
        self.index = []

        # wheel status
        self.wheel_status = {"Control": 0,
                             "Err C": 0,
                             "Err D": 0,
                             "Err V": 0,
                             "EEPROM Connected": 0,
                             "Is homed": 0,
                             "Secur": 0,
                             "Alarm": 0,
                             "CTP error": 0,
                             "Power Overheat": 0,
                             "Controller Overheat": 0,
                             "Overload power voltage": 0,
                             "Overload power current": 0,
                             "Overload USB Voltage": 0,
                             "Low USB Voltage": 0,
                             "Overload USB Current": 0,
                             "Borders Swap Misset": 0,
                             "Low power voltage": 0,
                             "H bridge fault": 0,
                             "Current Motor Bits": 0,
                             "Current Motor 0": 0,
                             "Current Motor 1": 0,
                             "Current Motor 2": 0,
                             "Current Motor 3": 0}


    def is_connected(self):
        return True

    def is_simulator(self):
        return True

    def connect(self):
        self._is_connected = True

    def disconnect(self):
        self._is_connected = False

    def reconnect(self):
        self.connect()

    def load_wheels(self):
        with ConfigurationManagerProxy() as cm:
            self._setup = cm.get_setup()
        #todo: still some work here to manage the default setup to be loaded
        return self._setup

    def set_position(self, pos_wheel1, pos_wheel2):
        self._wheel_position = [pos_wheel1, pos_wheel2]
        return 1

    def get_position(self) -> list:
        return self._wheel_position

    def homing(self):
        self._wheel_position = [0, 0]
        return self._wheel_position

    def get_status(self):
        _status = [0, 0, 30, 4, 30, hex(67)]
        return _status

    def att_get_level(self) -> list:
        #retrieves the wheel position
        position = self.get_position()

        if any(y > 7 or y < 0 for y in position):
            logging.warning("Trying to set the wheels to an out of range position, command aborted, try to do homing")
            pass
        else:
            #gets the corresponding attenuation factor of each wheel
            att1 = self.wheel1.get(position[0])
            att2 = self.wheel2.get(position[1])
            try:
                att = att1 + att2 #in case the attenuations are given in OD, otherwise multiply
            except TypeError:
                att = None
            self._att_level = [self.wheel1, self.wheel2, att]
        return self._att_level

    def att_level_up(self) -> list:
        # gets actual position
        actual_position = self._wheel_position
        # finds the position index:
        _index = self.index.index(actual_position)
        #gets the increased index position:
        new_position = self.index[_index + 1]
        if (_index < 64):
            logging.info("moving the wheel to an upper limit")
            self.set_position(new_position[0], new_position[1])
        elif _index > 64:
            logging.info(" Trying to move the wheel to an out of range position, command not executed")
        return self._wheel_position

    def att_level_down(self) -> list:
        # gets actual position
        actual_position = self._wheel_position
        # finds the position index:
        _index = self.index.index(actual_position)
         # gets the increased index position:
        new_position = self.index[_index - 1]
        if _index > 0:
            logging.info("moving the wheel to an lower limit")
            self.set_position(new_position[0], new_position[1])
        else:
            logging.info(" Trying to move the wheel to an out of range position, command not executed")
        return self._wheel_position

    def att_set_level_factor(self):
        pass

    def att_set_level_position(self):
        pass

    def att_status(self, _flags) -> dict:
        _flag = 0x20
        s_flags = [int(x) for x in np.binary_repr(_flag)]
        # from int to bit list of 24 elements corresponding to the filterwheel flag state bits
        # Note that the last 5 bits are obsolete in with library versions > 2.12.5 (email exchanges)
        s_flags = [int(x) for x in np.binary_repr(_flag)]
        s_flags.reverse()
        z = [0]*(24-len(s_flags))
        s_flags = s_flags + z

        _keys = list(self.wheel_status.keys())
        for k, i in zip(_keys, s_flags):
            self.wheel_status[k] = i
        return self.wheel_status

    def wheel_factors(self) -> list:
        # computes the configuration of the attenuation of both wheels
        # wheel1 and 2 are dictionaries containing the wheels attenuation factors
        #TODO: asks Rik clarification on how this load setup works, after starting the cm_ui and loading a new setup, if the cm_ui is setup the setup remains

        if self._setup is None:
            logging.info("The ConfMan Proxy is not started and no setup configuration has been loaded, fake values of the filter wheel will be computed")
        else:
            try:
                logging.info("Loading the wheels setup from the ConfMan Proxy")
                self.wheel1 = self._setup.gse.filter_wheel.wheel_1
                self.wheel2 = self._setup.gse.filter_wheel.wheel_2

            except AttributeError:
                logging.warning("The actual setup does not contain the wheels configuration, try to load another setup")

        d_index = []
        s_index = []
        d_factor = []
        s_factor = []
        for i in self.wheel1:
            for e in self.wheel2:
                try:
                    element = round(self.wheel1[i] + self.wheel2[e], 2)
                    d_factor.append(element)
                    d_index.append([i, e])
                except TypeError:
                    element = str(repr(self.wheel1[i]) + '+' + repr(self.wheel2[e]))
                    s_factor.append(element)
                    s_index.append([i, e])

        # here we sort the list of number and their corresponding indexes.
        # then both number and string list are concatenated
        temp = sorted(zip(d_factor, d_index), key=lambda x: x)
        d_factor, d_index = map(list, zip(*temp))

        _duplicated = [idx for idx, item in enumerate(d_factor) if item in d_factor[:idx]]

        # popping duplicated index
        d_factor = [i for j, i in enumerate(d_factor) if j not in _duplicated]
        d_index = [i for j, i in enumerate(d_index) if j not in _duplicated]
        # putting all together
        self.factor = d_factor + s_factor
        self.index = d_index + s_index
        return [self.factor, self.index]


class FilterWheel8SMC4Controller(FilterWheel8SMC4Interface):
    """The FilterWheel8SMC4Controller allows controlling a Thorlabs 8SMC4 Filter Wheel."""

    def __init__(self):
        """Initialize the Filter Wheel Controller interface."""

        super().__init__()

        LOGGER.debug("Initializing Filter Wheel 8SMC4 Controller")
        # when the wheel factor is 0 there is no filter in the wheel, if OD units are considered
        # when the wheel factor is a character, the filter is a spectral filter
        # will be late replaced by the setup configuration
        self.wheel1 = {0: 0,
                      1: 2,
                      2: 1,
                      3: 0.03,
                      4: "T4K",
                      5: "T5K",
                      6: "T6K",
                      7: "T6.5K"}

        self.wheel2 = {0: 0,
                       1: 0.3,
                       2: 0.05,
                       3: 5,
                       4: 2,
                       5: 0.1,
                       6: 0.15,
                       7: 3}

        # Initializes the to wheel positions dummy variables
        self.wheel_position = [0, 0]

        # Initializes the wheel status:

        self.wheel_status = {"Control": 0,
                             "Err C": 0,
                             "Err D": 0,
                             "Err V": 0,
                             "EEPROM Connected": 0,
                             "Is homed": 0,
                             "Secur": 0,
                             "Alarm": 0,
                             "CTP error": 0,
                             "Power Overheat": 0,
                             "Controller Overheat": 0,
                             "Overload power voltage": 0,
                             "Overload power current": 0,
                             "Overload USB Voltage": 0,
                             "Low USB Voltage": 0,
                             "Overload USB Current": 0,
                             "Borders Swap Misset": 0,
                             "Low power voltage": 0,
                             "H bridge fault": 0,
                             "Current Motor Bits": 0,
                             "Current Motor 0": 0,
                             "Current Motor 1": 0,
                             "Current Motor 2": 0,
                             "Current Motor 3": 0}

        try:
            if SITE.ID == "INTA":
                self.fw = FilterWheel8SMC4USBInterface()
            else:
                self.fw = FilterWheel8SMC4EthernetInterface()
            self.fw.connect()
        except FilterWheel8SMC4Error as exc:
            LOGGER.warning(f"FilterWheel8SMC4Error caught: Couldn't establish connection ({exc})")
            raise FilterWheelError(
                "Couldn't establish a connection with the Filter Wheel 8SMC4 controller."
            ) from exc

    def connect(self):
        """Connects to the Filter Wheel device.

        Raises:
            DeviceNotFoundError: when the Filter Wheel device is not connected.
        """
        if not self.is_connected():
            try:
                self.fw.connect()
            except FilterWheelError as exc:
                LOGGER.warning(f"HuberError caught: Couldn't establish connection ({exc})")

    def disconnect(self):
        try:
            self.fw.disconnect()
        except FilterWheelError as exc:
            raise FilterWheelError("Couldn't disconnect from FilterWheel Controller.") from exc

    def reconnect(self):
        if self.is_connected():
            self.disconnect()
        self.connect()

    def is_connected(self):
        """Check if the Filter Wheel Controller is connected."""
        return self.fw.is_connected()

    def is_simulator(self):
        return False

    def load_wheels(self):
        with ConfigurationManagerProxy() as cm:
            self._setup = cm.get_setup()
        #todo: still some work here to manage the default setup to be loaded
        return self._setup

    def get_id(self):
        return self.fw.get_id()


    def get_response(self, cmd_string):
        response = self.fw.get_response(cmd_string)
        return response

    def move_wheel(self, steps):
        self.fw.move_wheel(steps)

    def set_position(self, pos_wheel1, pos_wheel2):
        # Wheel 1 is the "Master" wheel. It hooks wheel_2 when a complete turn is performed
        #todo: document the wheels reference and the way they move
        _check = [pos_wheel1, pos_wheel2] # from 0 to 7 equivalent to 1 to 8 on the wheels

        if any(y > 7 or y < 0 for y in _check):
            logging.warning("Trying to set the wheels to an out of range position, command aborted")

        else:
            logging.info("Moving the filter wheels to the required positions")
            _output = self.fw.set_pos(pos_wheel1, pos_wheel2)
            self.wheel_position = [pos_wheel1, pos_wheel2]
        return _output

    def command_zero(self):
        self.fw.command_zero()

    def get_status(self) -> list:
        x_status = self.fw.get_status()
        _status = [x_status.CurPosition, x_status.CurSpeed, round(x_status.CurT * 0.1, 1), x_status.Ipwr,
         round(x_status.Upwr * 0.01, 2), hex(x_status.Flags)]
        return _status

    def get_position(self) -> list:
        return self.fw.get_position()

    def homing(self):
        """ standard ".cfg" file, which can be downloaded to device using XILab,
            overloads command_homezero command. The command takes time to be executed as the wheel needs time to get
             to the home position"""
        self.fw.homing()
        self.wheel_position = [0, 0]

    def wheel_factors(self) -> list:
        # computes the configuration of the attenuation of both wheels
        # wheel1 and 2 are dictionaries containing the wheels attenuation factors
        # TODO: asks Rik clarification on how this load setup works, after starting the cm_ui and loading a new setup, if the cm_ui is setup the setup remains

        if self._setup is None:
            logging.info(
                "The ConfMan Proxy is not started and no setup configuration has been loaded, fake values of the filter wheel will be computed")
        else:
            try:
                logging.info("Loading the wheels setup from the ConfMan Proxy")
                self.wheel1 = self._setup.gse.filter_wheel.wheel_1
                self.wheel2 = self._setup.gse.filter_wheel.wheel_2

            except AttributeError:
                logging.warning("The actual setup does not contain the wheels configuration, try to load another setup")

        d_index = []
        s_index = []
        d_factor = []
        s_factor = []
        for i in self.wheel1:
            for e in self.wheel2:
                try:
                    element = round(self.wheel1[i] + self.wheel2[e], 2)
                    d_factor.append(element)
                    d_index.append([i, e])
                except TypeError:
                    element = str(repr(self.wheel1[i]) + '+' + repr(self.wheel2[e]))
                    s_factor.append(element)
                    s_index.append([i, e])

        # here we sort the list of number and their corresponding indexes.
        # then both number and string list are concatenated
        temp = sorted(zip(d_factor, d_index), key=lambda x: x)
        d_factor, d_index = map(list, zip(*temp))

        _duplicated = [idx for idx, item in enumerate(d_factor) if item in d_factor[:idx]]

        # popping duplicated index
        d_factor = [i for j, i in enumerate(d_factor) if j not in _duplicated]
        d_index = [i for j, i in enumerate(d_index) if j not in _duplicated]
        # putting all together
        self.factor = d_factor + s_factor
        self.index = d_index + s_index
        return [self.factor, self.index]


    # TODO: the following commands will be defined after discussion as they are similar to CSL Collimator
    def att_get_level(self, position) -> list:
        # retrieves the wheel position
        level = [None, None, None]

        if any(y > 7 or y < 0 for y in position):
            logging.warning("Trying to set the wheels to an out of range position, command aborted, try to do homing")
            pass
        else:
            # gets the corresponding attenuation factor of each wheel
            att1 = self.wheel1.get(position[0])
            att2 = self.wheel2.get(position[1])
            try:
                att = att1 + att2 # in case the attenuations are given in OD, otherwise multiply
            except TypeError:
                att = repr(att1) + repr(att2)
            level = [self.wheel1, self.wheel2, att]
        return level

    def att_set_level_factor(self, level):
        # Will find the closest defined attenuation level, retrieve the pos_wheel1 and pos_wheel2 and move the wheels
        pos_wheel1 = 0
        pos_wheel2 = 0

        self.fw.set_pos_calb(pos_wheel1, pos_wheel2)

    def att_get_level(self) -> list:
        #retrieves the wheel position
        position = self.wheel_position
        try:
            #gets the corresponding attenuation factor of each wheel
            att1 = self.wheel1.get(position[0])
            att2 = self.wheel2.get(position[1])

            att = att1 + att2 #in case the attenuations are given in OD, otherwise multiply
        except TypeError:
            att = None
        self._att_level = [self.wheel1, self.wheel2, att]
        return self._att_level

    def att_level_up(self) -> list:
        # gets actual position
        actual_position = self.wheel_position
        # finds the position index:
        _index = self.index.index(actual_position)
        #gets the increased index position:
        new_position = self.index[_index + 1]
        if (_index < 64):
            logging.info("moving the wheel to an upper limit")
            self.set_position(new_position[0], new_position[1])
        elif _index > 64:
            logging.info(" Trying to move the wheel to an out of range position, command not executed")
        return self.wheel_position

    def att_level_down(self) -> list:
        # gets actual position
        actual_position = self.wheel_position
        # finds the position index:
        _index = self.index.index(actual_position)
         # gets the increased index position:
        new_position = self.index[_index - 1]
        if _index > 0:
            logging.info("moving the wheel to an lower limit")
            self.set_position(new_position[0], new_position[1])
        else:
            logging.info(" Trying to move the wheel to an out of range position, command not executed")
        return self.wheel_position

    def att_status(self, _flag) -> dict:
        _flag = int(_flag, 16)
        #logging.info("The received hex flag bit code is:", _flag)
        # from int to bit list of 24 elements corresponding to the filterwheel flag state bits
        # Note that the last 5 bits are obsolete in with library versions > 2.12.5 (email exchanges)
        s_flags = [int(x) for x in np.binary_repr(_flag)]
        s_flags.reverse()
        z = [0]*(24-len(s_flags))
        s_flags = s_flags + z
        _keys = list(self.wheel_status.keys())
        for k, i in zip(_keys, s_flags):
            #print(k, "=", i)
            self.wheel_status[k] = i
        #print(self.wheel_status)

        return self.wheel_status

    def get_speed(self) -> list:
        return self.fw.get_speed()

class FilterWheel8SMC4Proxy(Proxy, FilterWheel8SMC4Interface):
    def __init__(
            self,
            protocol=CTRL_SETTINGS.PROTOCOL,
            hostname=CTRL_SETTINGS.HOSTNAME,
            port=CTRL_SETTINGS.COMMANDING_PORT,
    ):
        """
        Args:
            protocol: the transport protocol
                [default is taken from settings file]
            hostname: location of the control server (IP address)
                [default is taken from settings file]
            port: TCP port on which the control server is listening for commands
                [default is taken from settings file]
        """
        super().__init__(connect_address(protocol, hostname, port))
