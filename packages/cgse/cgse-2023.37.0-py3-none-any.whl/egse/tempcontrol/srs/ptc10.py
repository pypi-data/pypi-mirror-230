"""
This module defines the basic classes to access the MaRi regulation ensured by
SRS PTC10 controller that will be used in the IAS TVAC setup.
"""
import logging
from typing import List


from egse.decorators import dynamic_interface
from egse.device import DeviceInterface
from egse.tempcontrol.srs.ptc10_devif import ptc10Error
from egse.tempcontrol.srs.ptc10_devif import ptc10TelnetInterface
from egse.proxy import Proxy
from egse.settings import Settings
from egse.zmq_ser import connect_address
from egse.mixin import dynamic_command
from egse.mixin import add_lf
from time import sleep, strftime, gmtime
from egse.confman import ConfigurationManagerProxy
from egse.system import format_datetime
from datetime import datetime


LOGGER = logging.getLogger(__name__)

CTRL_SETTINGS = Settings.load("SRS PTC10 Control Server")
PTC10_SETTINGS = Settings.load("SRS PTC10 Controller")
DEVICE_SETTINGS = Settings.load(filename="ptc10.yaml")

def load_setup_from_configuration_manager():
    """Loads a Setup YAML file from the Configuration Manager."""
    with ConfigurationManagerProxy() as cm:
        setup = cm.get_setup()

    return setup


class ptc10Interface(DeviceInterface):
    """
    Interface definition for the Temp regulation SRS PTC10 Controller, Simulator and Proxy..
    """

    @dynamic_interface
    def connect(self):
        """Connects to the Temp regulation device.

        Raises:
            DeviceNotFoundError: when the Temp regulation device is not connected.
        """

        raise NotImplementedError

    @dynamic_interface
    def disconnect(self):
        raise NotImplementedError

    @dynamic_interface
    def reconnect(self):
        raise NotImplementedError

    @dynamic_interface
    def is_connected(self):
        """Check if the Temp Controller is connected."""
        raise NotImplementedError

    @dynamic_interface
    def is_simulator(self):
        raise NotImplementedError

    @dynamic_interface
    def info(self) -> str:
        """
        Returns basic information about the device, its name, firmwre version etc.
        Returns:
            An identification string of the instrument.
        """
        raise NotImplementedError

    @dynamic_interface
    def alarm_status(self) -> str:
        """
        Returns the current value of the Alarm Status Register (ASR), and then clears the register.
        """
        raise NotImplementedError

    @dynamic_interface
    def get_names(self):
        """
        Returns a tuple of 2 lists with the names of inputs (3 sensors) in the first list and the names of
        outputs (3 heaters) in the second list.
        """
        raise NotImplementedError

    @dynamic_interface
    def set_name(self, old_name: str, new_name: str):
        """Modifies the name of the specified channel (input or output)."""
        raise NotImplementedError

    @dynamic_interface
    def clear_error(self):
        """
        Erases all error messages for the port over which the instruction was transmitted. Also clears all messages
        from the System.Com. Errors window regardless of which port generated them.
        """
        raise NotImplementedError

    @dynamic_interface
    def stop(self):
        """
        kill.all stops all currently running macros with the given runtime name. The runtime name is assigned with the
        "name" instruction and is not necessarily the same as the file name that a macro may be saved under.
        The kill.all instruction stops all currently-running macros regardless of name or which port started the macro.
        """
        raise NotImplementedError

    @dynamic_interface
    def standby(self):
        """
        Puts the PTC10 into stby mode, in which the outputs are turned off, data acquisition is paused, macros are
        paused, the front panel display and system fan are shut off, and the system does not respond to remote commands.
        The PTC321's excitation currents remain on, and the chassis cooling fan may switch on occassionally.
        Press the "Output Enable" key to exit standby mode. There is no remote command to leave stand by mode.
        """
        raise NotImplementedError

    @dynamic_command(
        cmd_type="write",
        cmd_string="*RST",
        process_cmd_string=add_lf,
    )
    def reset(self):
        """
        Resets the PTC10.

        The *RST instruction is equivalent to turning the instrument off and back on again, except the Power On bit of
        the Event Status Register is not set. *RST has the following effects:
        - Outputs are disabled (as if the “Output enable” button were pressed).
        - All currently-running macros are stopped, regardless of whether the macros were started by the GPIB interface,
        another I/O port, or the Program screen.
        - The instrument returns to the Select screen.
        -Partially-received instructions on all I/O ports are cleared.
        - All pending transmissions on all I/O ports are cancelled.
        - The error queues for all I/O ports are cleared.
        - The plot screen returns to showing the most recent data on autoscaled Y axes.
        - The instrument automatically triggers at the rate set with the “A/D rate” control.
        - Clears all locally-stored log data. Logs on USB devices are not affected. If data is not being logged to a
        USB storage device, the Plot screen shows no accumulated data immediately after a *RST command.
        """
        raise NotImplementedError

    @dynamic_interface
    def read_temperature(self):
        """
        Reads the temperature from the 3 PT1000 corresponding to TRP2/TRP3/TRP4.

        Notes: <channel>.value? returns the current value of the channel. Ex: 2A.value? queries the output of channel 2A
                <channel>? also works
        """

        raise NotImplementedError

    @dynamic_interface
    def read_heater(self):
        """
        Reads the 3x heater outputs with the unit (W, A or V).
        Returns a tuple. 1st element is a list with the 3 values of the heaters. 2nd element is a string with the unit
        ('W', 'A' or 'V').
        """

        raise NotImplementedError

    @dynamic_interface
    def disable_heater(self, output_ch: int):
        """
        Disables the specified heater output. output_ch = 1, 2, 3

        Notes: <channel>.Off cancels any active autotuning process, turns PID feedback off, and sets the channel's
        output to zero or the lower limit.
        """

        raise NotImplementedError

    @dynamic_interface
    def outputs_enable(self):
        """Enables all outputs. Equivalent to press the red button twice on the front panel of the PTC10 when outputs disabled."""
        raise NotImplementedError

    @dynamic_interface
    def outputs_disable(self):
        """Disables all outputs. Equivalent to press the red button on the front panel of the PTC10 when output enabled."""
        raise NotImplementedError

    @dynamic_interface
    def disable_all(self):
        """Both disable_heater function used for all heaters AND outputs_disable."""
        raise NotImplementedError

    @dynamic_interface
    def is_outputs_enable(self) -> bool:
        """
        Returns a boolean corresponding to the state of the red button/light on the front panel of the PTC10.
        True means outputs enabled (red light switch on)
        False means outputs disabled (red light switch off)
        """

        raise NotImplementedError

    @dynamic_interface
    def output_limit(self, output_ch: int, low: float, high: float):
        """
        Sets the min and max output and can be used to prevent the PID loop for delivering excessive power to a
        heater. The limits must be expressed in the same units that the output is expressed in. The limits must
        normally be reset when the output units are changed, since the limits are not converted to the new units.
        output_ch = 1, 2, 3
        low = float >= 0
        high = float > low

        Notes:
            by default the DC heater driver output is measured in watts. But can be changed to either A or V.
            <channel>.Units{W, A, V}
        """

        raise NotImplementedError

    @dynamic_interface
    def output_unit(self, unit: str):
        """
        Sets the unit for the 3 heaters
        unit = W, A, V, or in lowercase w, a, v
        """

        raise NotImplementedError

    @dynamic_interface
    def set_heater_input(self, output_ch: int, input: str):
        """
        Sets the sensor as input for the specified heater.
        output_ch = 1, 2, 3
        input = name of the sensor (e.g. TRP2)
        """

        raise NotImplementedError

    @dynamic_interface
    def setpoint(self, output_ch: int, setpoint: float):
        """
        Sets the temperature setpoint. The PID attemps to keep the input at this value by changing the output.
        output_ch = 1, 2, 3
        setpoint = float (°C)

        Notes:
            usage: <channel>.PID.Setpoint<setpoint>
        """

        raise NotImplementedError

    @dynamic_interface
    def get_PID(self, output_ch: int) -> dict:
        """
        Returns a dictionary with P, I and D parameters as float, {"P": P_value, "I": I_value, "D": D_value}
        output_ch = 1, 2, 3
        """

        raise NotImplementedError

    @dynamic_interface
    def set_PID(self, input_ch: int, output_ch: int, PID: List[float]):
        """
        The input must be stable before either Step or Relay tuning is started. Furthermore, the output must be greater
        than half the step height before starting relay tuning. The best time to start a step response is when the
        system is first turned on at the beginning of the day, i.e the heater is cold and its temperature stable.
        See User Manual for further details.
        input_ch parameter sets the PID input channel which is the temperature that the PID feedback loop controls. intput_ch = 1, 2, 3
        output_ch parameter sets the PID output channel. output_ch = 1, 2, 3
        PID parameter sets the three coefficients respectively in P, I and D. PID = [float, float, float]

        Notes
        PID: <channel>.PID.D<value>, <channel>.PID.I<value>, <channel>.PID.P<value>
        <channel>.PID.Input<channel name>
        """

        raise NotImplementedError

    @dynamic_interface
    def autotune_PID(self, input_ch: int, output_ch: int):
        """

        """

        raise NotImplementedError

    @dynamic_interface
    def set_auto(self, output_ch: int, setpoint: float):
        """
        Enables the specified output to reach the specified setpoint automatically.
        output_ch = 1, 2, 3
        setpoint = float (°C)
        """
        raise NotImplementedError

    @dynamic_interface
    def set_manual(self, output_ch: int, value: float):
        """
        Enables the specified output manually with the specified value.
        The unit is the one currently in effect (W, A or V).
        output_ch = 1, 2, 3
        value = float >= 0
        """

        raise NotImplementedError

    @dynamic_interface
    def set_survival(self):
        """
        Sets all outputs to the min Non op temperature for TRP2, TRP3 and TRP4 as given in the Setup YAML file.
        We assume that P, I and D coefficients are already correctly set.
        """

        raise NotImplementedError

    @dynamic_interface
    def set_stable(self, setpoint: float):
        """
        Sets all outputs to the same temperature setpoint given as parameter.
        We assume that P, I and D coefficients are already correctly set.
        """

        raise NotImplementedError

    @dynamic_interface
    def set_custom(self, outputs_dict: dict):
        """
        Sets the outputs given as parameter to the corresponding temperature given as parameter.
        If an output channel is not given as parameter in the dictionary outputs_dict, this output channel will remain
        at the same state and with same setpoint as before.
        outputs_dict = {output_ch: setpoint} for example: {3: -110, 1: -106}
        """

        raise NotImplementedError

    @dynamic_interface
    def heater_sensor_error(self) -> list:
        """
        Returns a list with names of sensors (TRP) and heaters which cannot be read by the PTC10.
        """

        raise NotImplementedError

    @dynamic_interface
    def disable_heater_error(self):
        """
        Disables heaters whose PT1000 sensors are faulty.
        This function does not re-enable heater if a PT1000 is no longer faulty.
        """

        raise NotImplementedError

    @dynamic_interface
    def get_time(self) -> str:
        """
        Returns PTC10 time as a string.
        """

        raise NotImplementedError


    @dynamic_interface
    def update_time(self):
        """
        Updates the PTC10 date and time in UTC from the server's time which is ntp synchronised.
        """

        raise NotImplementedError


class ptc10Simulator(ptc10Interface):
    """
    The ptc10 Simulator class.
    """

    def __init__(self):
        self._is_connected = True
        self.temp_operation = False

    def is_connected(self):
        return self._is_connected

    def is_simulator(self):
        return True

    def connect(self):
        self._is_connected = True

    def disconnect(self):
        self._is_connected = False

    def reconnect(self):
        self.connect()

    def info(self):
        pass

    def read_temperature(self):
        pass

    def read_heater(self):
        pass


class ptc10Controller(ptc10Interface):
    """The ptc10Controller allows controlling a SRS ptc10 temperature regulation device."""

    def __init__(self):
        """Initialize the ptc10 Controller interface."""
        self.output_mode_var = None
        self.setpoint_var = None
        self.PID = None
        self.limits = None
        setup = load_setup_from_configuration_manager()
        self.T_min_NOP = setup.gse.PTC10.T_min_NOP # TRP2, TRP3 and TRP4 min NOP (°C)

        super().__init__()

        LOGGER.debug("Initializing PTC10")

        try:
            self.temp = ptc10TelnetInterface()
            self.temp.connect(PTC10_SETTINGS.HOSTNAME)
        except ptc10Error as exc:
            LOGGER.warning(f"TempError caught: Couldn't establish connection ({exc})")
            raise ptc10Error(
                "Couldn't establish a connection with the Temp PTC10 controller."
            ) from exc

    def connect(self):
        """Connects to the Temp regulation device.

        Raises:
            DeviceNotFoundError: when the Temp regulation device is not connected.
        """
        try:
            self.temp.connect(PTC10_SETTINGS.HOSTNAME)
        except ptc10Error as exc:
             LOGGER.warning(f"ptc10Error caught: Couldn't establish connection ({exc})")
             raise ConnectionError("Couldn't establish a connection with the SRS PTC10 controller.") from exc

    def disconnect(self):
        try:
            self.temp.disconnect()
        except ptc10Error as exc:
            raise ConnectionError("Couldn't establish a connection with the SRS PTC10 controller.") from exc

    def reconnect(self):
        if self.is_connected():
            self.disconnect()
            sleep(1)
        self.connect()

    def is_connected(self):
        """Check if the Temp Controller is connected."""
        return self.temp.is_connected()

    def is_simulator(self):
        return False

    def info(self):
        """
        Returns basic information about the device, its name, firmwre version etc.
        Returns:
            An identification string of the instrument.
        """

        self.temp.write("*IDN?")
        _info = self.temp.read()
        return _info

    def alarm_status(self) -> str:
        """Returns the current value of the Alarm Status Register (ASR), and then clears the register."""

        self.temp.write("*ASR?")
        status = self.temp.read()
        return status

    def get_names(self):
        """
        Returns a tuple of 2 lists with the names of inputs (4 sensors) in the first list and the names of
        outputs (3 heaters) in the second list.
        """

        self.temp.write("getOutput.names")
        NAMES = self.temp.read().split(", ")

        Sensors = NAMES[3:7]

        Heaters = NAMES[:3]

        return Sensors, Heaters

    def set_name(self, old_name: str, new_name: str):
        """Modifies the name of the specified channel (input or output)."""

        self.temp.write(f'({old_name}.Name) "{new_name}"')

    def clear_error(self):
        """
        Erases all error messages for the port over which the instruction was transmitted. Also clears all messages
        from the System.Com. Errors window regardless of which port generated them.
        """

        self.temp.write("clearerrors")

    def stop(self):
        """
        kill.all stops all currently running macros with the given runtime name. The runtime name is assigned with the
        "name" instruction and is not necessarily the same as the file name that a macro may be saved under.
        The kill.all instruction stops all currently-running macros regardless of name or which port started the macro.
        """

        self.temp.write("kill.all")

    def standby(self):
        """
        Puts the PTC10 into stby mode, in which the outputs are turned off, data acquisition is paused, macros are
        paused, the front panel display and system fan are shut off, and the system does not respond to remote commands.
        The PTC321's excitation currents remain on, and the chassis cooling fan may switch on occassionally.
        Press the "Output Enable" key to exit standby mode. There is no remote command to leave stand by mode.
        """

        self.temp.write("standby")

    def reset(self):
        """
        Resets the PTC10.

        The *RST instruction is equivalent to turning the instrument off and back on again, except the Power On bit of
        the Event Status Register is not set. *RST has the following effects:
        - Outputs are disabled (as if the “Output enable” button were pressed).
        - All currently-running macros are stopped, regardless of whether the macros were started by the GPIB interface,
        another I/O port, or the Program screen.
        - The instrument returns to the Select screen.
        -Partially-received instructions on all I/O ports are cleared.
        - All pending transmissions on all I/O ports are cancelled.
        - The error queues for all I/O ports are cleared.
        - The plot screen returns to showing the most recent data on autoscaled Y axes.
        - The instrument automatically triggers at the rate set with the “A/D rate” control.
        - Clears all locally-stored log data. Logs on USB devices are not affected. If data is not being logged to a
        USB storage device, the Plot screen shows no accumulated data immediately after a *RST command.
        """

        self.temp.write("*RST")

    def read_temperature(self) -> list:
        """Reads the temperature from the 3 PT1000 corresponding to TRP2/TRP3/TRP4."""

        Sensor_names = self.get_names()[0]
        Sensors_values = []
        for channel_name in Sensor_names:
            self.temp.write(f"({channel_name}?)")
            Sensors_values.append(float(self.temp.read()))
        return Sensors_values

    def read_heater(self) -> tuple:
        """
        Reads the 3x heater outputs with the unit (W, A or V).
        Returns a tuple. 1st element is a list with the 3 values of the heaters. 2nd element is a string with the unit
        ('W', 'A' or 'V').
        """

        Heater_names = self.get_names()[1]
        Heaters_values = []
        for channel_name in Heater_names:
            self.temp.write(f"({channel_name}?)")
            Heaters_values.append(float(self.temp.read()))
        self.temp.write(f"({Heater_names[0]}.Units?)")
        heater_unit = self.temp.read()
        return Heaters_values, heater_unit

    def disable_heater(self, output_ch: int):
        """
        Disables the specified heater output. output_ch = 1, 2, 3

        Notes: <channel>.Off cancels any active autotuning process, turns PID feedback off, and sets the channel's
        output to zero or the lower limit.
        """

        self.temp.write(f"({self.get_names()[1][output_ch - 1]}.Off)")

    def outputs_enable(self):
        """Enables all outputs. Equivalent to press the red button twice on the front panel of the PTC10 when outputs disabled."""

        self.temp.write("outputEnable = on")

    def outputs_disable(self):
        """Disables all outputs. Equivalent to press the red button on the front panel of the PTC10 when output enabled."""

        self.temp.write("outputEnable = off")

    def disable_all(self):
        """Both disable_heater function used for all heaters AND outputs_disable."""

        for output_ch in [1,2,3]:
            self.disable_heater(output_ch)
        self.outputs_disable()

    def is_outputs_enable(self) -> bool:
        """
        Returns a boolean corresponding to the state of the red button/light on the front panel of the PTC10.
        True means outputs enabled (red light switch on)
        False means outputs disabled (red light switch off)
        """

        is_enable = {"On": True, "Off": False}
        self.temp.write("outputEnable?")
        return is_enable[self.temp.read()]

    def output_limit(self, output_ch: int, low: float, high: float):
        """
        Sets the min and max output and can be used to prevent the PID loop for delivering excessive power to a
        heater. The limits must be expressed in the same units that the output is expressed in. The limits must
        normally be reset when the output units are changed, since the limits are not converted to the new units.
        output_ch = 1, 2, 3
        low = float >= 0
        high = float > low

        Notes:
            by default the DC heater driver output is measured in watts. But can be changed to either A or V.
            <channel>.Units{W, A, V}
        """

        heater = self.get_names()[1][output_ch - 1]
        self.temp.write(f"({heater}.Low lmt) {low}")
        self.temp.write(f"({heater}.Hi lmt) {high}")

    def output_unit(self, unit: str):
        """
        Sets the unit for the 3 heaters
        unit = W, A, V, or in lowercase w, a, v
        """

        unit = unit.upper()
        for output_ch in [1, 2, 3]:
            heater = self.get_names()[1][output_ch - 1]
            self.temp.write(f'({heater}.Units) "{unit}"')

    def set_heater_input(self, output_ch: int, input: str):
        """
        Sets the sensor as input for the specified heater.
        output_ch = 1, 2, 3
        input = name of the sensor (e.g. TRP2)
        """

        heater = self.get_names()[1][output_ch - 1]
        self.temp.write(f'({heater}.PID.Input) "{input}"')

    def setpoint(self, output_ch: int, setpoint: float):
        """
        Sets the temperature setpoint. The PID attemps to keep the input at this value by changing the output.
        output_ch = 1, 2, 3
        setpoint = float (°C)

        Notes:
            usage: <channel>.PID.Setpoint<setpoint>
        """

        heater = self.get_names()[1][output_ch - 1]
        self.temp.write(f"({heater}.PID.Setpoint) {setpoint}")

    def get_PID(self, output_ch: int) -> dict:
        """
        Returns a dictionary with P, I and D parameters as float, {"P": P_value, "I": I_value, "D": D_value}
        output_ch = 1, 2, 3
        """
        heater = self.get_names()[1][output_ch - 1]

        self.temp.write(f"({heater}.PID.P?)")
        P = float(self.temp.read())
        self.temp.write(f"({heater}.PID.I?)")
        I = float(self.temp.read())
        self.temp.write(f"({heater}.PID.D?)")
        D = float(self.temp.read())

        return {"P": P, "I": I, "D": D}

    def set_PID(self, input_ch: int, output_ch: int, PID: List[float]):
        """
        The input must be stable before either Step or Relay tuning is started. Furthermore, the output must be greater
        than half the step height before starting relay tuning. The best time to start a step response is when the
        system is first turned on at the beginning of the day, i.e the heater is cold and its temperature stable.
        See User Manual for further details.
        input_ch parameter sets the PID input channel which is the temperature that the PID feedback loop controls. intput_ch = 1, 2, 3
        output_ch parameter sets the PID output channel. output_ch = 1, 2, 3
        PID parameter sets the three coefficients respectively in P, I and D. PID = [float, float, float]

        Notes
        PID: <channel>.PID.D<value>, <channel>.PID.I<value>, <channel>.PID.P<value>
        <channel>.PID.Input<channel name>
        """

        sensor = self.get_names()[0][input_ch - 1]
        heater = self.get_names()[1][output_ch - 1]

        self.temp.write(f'({heater}.PID.Input) "{sensor}"')
        PID_dict = {"P": PID[0], "I": PID[1], "D": PID[2]}
        for corrector in PID_dict:
            self.temp.write(f"({heater}.PID.{corrector}) {PID_dict[corrector]}")

    def autotune_PID(self, input_ch: int, output_ch: int):
        """
        Configures the PID with autotune.
        User Manual p.50 "If the system has never been tuned, start with the feedback turned off and the heater at ambient temperature.
        If the system has been tuned before, it’s better to wait for the temperature to stabilize at the setpoint.
        In either case, the key to successful autotuning is to start with a stable temperature."
        Prints message if failure to autotune PID. Old values for P, I and D are retained.
        input_ch parameter sets the PID input channel which is the temperature that the PID feedback loop controls. intput_ch = 1, 2, 3
        output_ch parameter sets the PID output channel. output_ch = 1, 2, 3
        """

        sensor = self.get_names()[0][input_ch - 1]
        heater = self.get_names()[1][output_ch - 1]
        output_enable_state = self.is_outputs_enable()
        self.temp.write(f"({heater}.PID.Mode?)")
        PID_mode = self.temp.read()
        self.temp.write(f"({heater}.Value?)")
        heater_initial_value = self.temp.read()

        PID_initial = self.get_PID(output_ch)

        self.temp.write(f"({heater}.PID.Mode) off")
        self.temp.write(f'({heater}.PID.Input) "{sensor}"')
        if not output_enable_state:
            self.temp.write("outputEnable = on")
        self.temp.write(f"({heater}.Tune.Mode) Auto")

        self.temp.write(f"({heater}.Tune.mode?)")
        Tune_mode = self.temp.read()
        while Tune_mode != "Off":
            self.temp.write(f"({heater}.Tune.mode?)")
            Tune_mode = self.temp.read()
        self.temp.write(f"({heater}.PID.Mode) {PID_mode}")
        if PID_mode == "Off":
            self.temp.write(f"({heater}.Value) {heater_initial_value}")
        if not output_enable_state:
            self.temp.write("outputEnable = off")

        #TODO: investigate to find a better way to know if autotune was successful or not (maybe with status function?)
        PID_final = self.get_PID(output_ch)
        if PID_initial == PID_final:
            print(f"Failure to autotune PID. Old values for P, I and D are retained.\nP = {PID_final['P']}\nI = {PID_final['I']}\nD = {PID_final['D']}\n"
                  "The key to successful autotuning is to start with a stable temperature.")
        else:
            print(f"Successful PID autotuning!!\nP = {PID_final['P']}\nI = {PID_final['I']}\nD = {PID_final['D']}")

    def set_auto(self, output_ch: int, setpoint: float):
        """
        Enables the specified output to reach the specified setpoint automatically.
        output_ch = 1, 2, 3
        setpoint = float (°C)
        """

        heater = self.get_names()[1][output_ch - 1]
        self.temp.write(f"({heater}.PID.Setpoint) {setpoint}")
        self.temp.write(f"({heater}.PID.mode) on")

        if not self.is_outputs_enable():
            self.temp.write("outputEnable = on")

    def set_manual(self, output_ch: int, value: float):
        """
        Enables the specified output manually with the specified value.
        The unit is the one currently in effect (W, A or V).
        output_ch = 1, 2, 3
        value = float >= 0
        """

        heater = self.get_names()[1][output_ch - 1]
        output_enable_state = self.is_outputs_enable()
        if not output_enable_state:
            self.temp.write("outputEnable = on")

        self.temp.write(f"({heater}.PID.mode) off")
        self.temp.write(f"({heater}.Value) {value}")
        response = self.temp.read()
        if response != "":
            print(f"{response}. The old value is retained.")
            if not output_enable_state:
                self.temp.write("outputEnable = off")

    def set_survival(self):
        """
        Sets all outputs to the min Non op temperature for TRP2, TRP3 and TRP4 as given in the Setup YAML file.
        We assume that P, I and D coefficients are already correctly set.
        """

        for output_ch in [1,2,3]:
            self.set_auto(output_ch, self.T_min_NOP)

    def set_stable(self, setpoint: float):
        """
        Sets all outputs to the same temperature setpoint given as parameter.
        We assume that P, I and D coefficients are already correctly set.
        """

        for output_ch in [1, 2, 3]:
            self.set_auto(output_ch, setpoint)

    def set_custom(self, outputs_dict: dict):
        """
        Sets the outputs given as parameter to the corresponding temperature given as parameter.
        If an output channel is not given as parameter in the dictionary outputs_dict, this output channel will remain
        at the same state and with same setpoint as before.
        outputs_dict = {output_ch: setpoint} for example: {3: -110, 1: -106}
        """

        channels =  [1,2,3]
        for output_ch in channels:
            if output_ch in outputs_dict:
                self.set_auto(output_ch, outputs_dict[output_ch])

    def heater_sensor_error(self) -> list:
        """
        Returns a list with names of sensors (TRP) and heaters which cannot be read by the PTC10.
        """

        INPUTS_OUTPUTS = self.read_temperature() + self.read_heater()[0]
        NAMES = self.get_names()
        NAMES = NAMES[0] + NAMES[1]
        ERROR = []
        for i in range(len(INPUTS_OUTPUTS)):
            in_out = INPUTS_OUTPUTS[i]
            if in_out != in_out: # This line tests if in_out is NaN
                ERROR.append(NAMES[i])
        return ERROR

    def disable_heater_error(self):
        """
        Disables heaters whose PT1000 sensors are faulty.
        This function does not re-enable heater if a PT1000 is no longer faulty.
        """

        list_error = self.heater_sensor_error()
        sensor_names = self.get_names()[0]
        for i in sensor_names:
            if i in list_error[:4]:
                self.disable_heater(sensor_names.index(i) + 1)

    def update_time(self):
        """Updates the PTC10 date and time in UTC from the server's time which is ntp synchronised."""
        self.temp.write("systemtime.dmy " + strftime("%d/%m/%Y", gmtime()))
        self.temp.write("systemtime.hms " + strftime("%H:%M:%S", gmtime()))

    def get_time(self) -> str:
        smhdmy = self.temp.trans("Systemtime.smh?")
        timestamp = format_datetime(datetime.strptime(smhdmy + " +0000", '%S %M %H %d %m %Y %z'))
        return timestamp

class ptc10Proxy(Proxy, ptc10Interface):
    """The ptc10Proxy class is used to connect to the control server and send commands to
    the SRS PTC10 device remotely."""
    def __init__(
        self,
        protocol=CTRL_SETTINGS.PROTOCOL,
        hostname=CTRL_SETTINGS.HOSTNAME,
        port=CTRL_SETTINGS.COMMANDING_PORT,
        timeout=CTRL_SETTINGS.TIMEOUT * 1000 # timeout in ms
    ):
        """
        Args:
            protocol: the transport protocol [default is taken from settings file]
            hostname: location of the control server (IP address)
                [default is taken from settings file]
            port: TCP port on which the control server is listening for commands
                [default is taken from settings file]
        """
        super().__init__(connect_address(protocol, hostname, port))

