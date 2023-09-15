"""
This module defines the basic classes to access the UPS and TVAC info and send alarms to TVAC readout ensured by
NI CDAQ9375 controller that is used.
"""
import logging
from typing import List

from egse.decorators import dynamic_interface
from egse.device import DeviceConnectionState
from egse.device import DeviceInterface
from egse.ni.alarms.cdaq9375_devif import cdaq9375Error, cdaq9375SocketInterface
from egse.proxy import Proxy
from egse.settings import Settings
from egse.zmq_ser import connect_address
from egse.mixin import dynamic_command
from egse.mixin import add_lf
from egse.system import format_datetime
from datetime import datetime
from numpy import array, sum


LOGGER = logging.getLogger(__name__)

CTRL_SETTINGS = Settings.load("NI Control Server")
CDAQ_SETTINGS = Settings.load("NI Controller")
DEVICE_SETTINGS = Settings.load(filename="cdaq9375.yaml")


class cdaq9375Interface(DeviceInterface):
    """
    Interface definition for the Signals acquisitions and emission of the CDAQ9375 Controller, Simulator and Proxy..
    """
    @dynamic_interface
    def info(self) -> str:
        """
        Returns basic information about the device, its name, firmware version etc.

        The string returned is subject to change without notice and can not be used for parsing
        information.

        Returns:
            An identification string of the instrument.
        """
        raise NotImplementedError


    @dynamic_interface
    def get_tvac_and_ups_state(self):
        """
        Returns a dictionary with the state (1 or 0) of UPS_Ix and UPS_Arrakis (alarm summary and power supply absence)
        and the state of TVAC. The timestamp (well formatted with the fucntion format_datetime) with the CDAQ9375 time
        is included in the dictionary:
        {"timestamp": 2023-05-17T13:27:45.335,
        "UPS_Arrakis_alarm_summary": 1/0,
        "UPS_Arrakis_power_supply_absence": 1/0,
        "UPS_Ix_alarm_summary": 1/0,
        "UPS_Ix_power_supply_absence": 1/0,
        "TVAC_low_temp": 1/0,
        "TVAC_High_Temp": 1/0,
        "TVAC_Interlock_Cryo": 1/0,
        "TVAC_vacuum": 1/0}
        """

        raise NotImplementedError


    @dynamic_interface
    def send_egse_state_to_tvac(self):
        """
        Send to TVAC the state of EGSE (EXP1, EXP2, EXP3, EXP4)
        EXP1: Low Temp NOP
        EXP2: High Temp NOP
        EXP3: low/High Temp OP
        EXP4: UPS alarm (UPS_Ix_alarm_summary or UPS_Ix_power_supply_absence or UPS_Arrakis_alarm_summary or UPS_Arrakis_power_supply_absence)
        """

        raise NotImplementedError

    @dynamic_interface
    def dec2bitlist_compl(self, d:int):
        """
        Decompose a integer (base 10) into a list of power of 2.
        e.g. 14 -> [8, 4, 2] (8+4+2 = 14)
        Args:
            d: integer base 10 to decompose (d <= 15)
        returns:
            list of power of 2
        """

        raise  NotImplementedError



class cdaq9375Simulator(cdaq9375Interface):
    """
    The cdaq9375 Simulator class.
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

    def get_id(self):
        pass

    def info(self):
        pass

    def get_tvac_and_ups_state(self):
        pass

    def send_egse_state_to_tvac(self):
        pass

    def dec2bitlist_compl(self, d:int):
        pass


class cdaq9375Controller(cdaq9375Interface):
    """The cdaq9375Controller allows controlling the NI CDAQ 9375 alarms device."""

    def __init__(self):
        """Initialize the cdaq9375 Controller interface."""

        super().__init__()

        LOGGER.debug("Initializing NI CDAQ 9375")

        try:
            self.cdaq = cdaq9375SocketInterface()
            self.cdaq.connect(CDAQ_SETTINGS.HOSTNAME) # IP address of the computer with Labview

        except cdaq9375Error as exc:
            LOGGER.warning(f"TempError caught: Couldn't establish connection ({exc})")
            raise cdaq9375Error(
                "Couldn't establish a connection with the NI CDAQ 9375 controller."
            ) from exc

    def connect(self):
        """Connects to the CDAQ9375 alarms device.

        Raises:
            DeviceNotFoundError: when the CDAQ9375 alarms device is not connected.
        """
        try:
            self.cdaq.connect(CDAQ_SETTINGS.HOSTNAME)
        except cdaq9Error as exc:
             LOGGER.warning(f"cdaqError caught: Couldn't establish connection ({exc})")
             raise ConnectionError("Couldn't establish a connection with the NI DAQ9375 controller.") from exc

        self.notify_observers(DeviceConnectionState.DEVICE_CONNECTED)


    def disconnect(self):
        try:
            self.cdaq.disconnect()
        except cdaq9375Error as exc:
            raise ConnectionError("Couldn't establish a connection with the NI CDAQ 9375 controller.") from exc

        self.notify_observers(DeviceConnectionState.DEVICE_NOT_CONNECTED)


    def reconnect(self):
        if self.is_connected():
            self.disconnect()
        self.connect()

    def is_connected(self):
        """Check if the CDAQ9375 Controller is connected."""
        return self.cdaq.is_connected()

    def is_simulator(self):
        return False

    def get_id(self):
        return self.cdaq.get_id()

    def info(self):
        pass

    def get_tvac_and_ups_state(self) -> dict:
        """
        Returns a dictionary with the state (1 or 0) of UPS_Ix and UPS_Arrakis (alarm summary and power supply absence)
        and the state of TVAC. The timestamp (well formatted with the fucntion format_datetime) with the CDAQ9375 time
        is included in the dictionary:
        {"timestamp": 2023-05-17T13:27:45.335,
        "UPS_Arrakis_alarm_summary": 1/0,
        "UPS_Arrakis_power_supply_absence": 1/0,
        "UPS_Ix_alarm_summary": 1/0,
        "UPS_Ix_power_supply_absence": 1/0,
        "TVAC_low_temp": 1/0,
        "TVAC_High_Temp": 1/0,
        "TVAC_Interlock_Cryo": 1/0,
        "TVAC_vacuum": 1/0}
        """

        response = self.cdaq.trans("\x00\x00\x00\x16READ_P1P2_NIDAQ_9181")
        # the 2 last elements of response are the alarm values, first is P2 (UPS) and second is P1 (TVAC): P2P1
        # Contacts both for P1 and P2 are normally closed, so we must take the complement

        response = response.strip()
        data_time = response.split("R")[0]
        timestamp = format_datetime(datetime.strptime(data_time, "%y/%m/%d%H:%M:%S.%f"))

        total_alarm = {"timestamp": timestamp}

        p2_code = int(response[-2], 16)
        p2_bitlist = self.dec2bitlist_compl(p2_code)
        p2_bit_to_alarm_name = {1: "UPS_Arrakis_alarm_summary", 2: "UPS_Arrakis_power_supply_absence", 4: "UPS_Ix_alarm_summary", 8: "UPS_Ix_power_supply_absence"}
        p2_alarm = {"UPS_Arrakis_alarm_summary": 0, "UPS_Arrakis_power_supply_absence": 0, "UPS_Ix_alarm_summary": 0, "UPS_Ix_power_supply_absence": 0}
        if p2_bitlist != []:
            for bit in p2_bitlist:
                p2_alarm[p2_bit_to_alarm_name[bit]] = 1

        p1_code = int(response[-1], 16)
        p1_bitlist = self.dec2bitlist_compl(p1_code)
        p1_bit_to_alarm_name = {1: "TVAC_low_temp", 2: "TVAC_High_Temp", 4: "TVAC_Interlock_Cryo", 8: "TVAC_vacuum"}
        p1_alarm = {"TVAC_low_temp": 0, "TVAC_High_Temp": 0, "TVAC_Interlock_Cryo": 0, "TVAC_vacuum": 0}
        if p1_bitlist != []:
            for bit in p1_bitlist:
                p1_alarm[p1_bit_to_alarm_name[bit]] = 1

        total_alarm.update(p2_alarm)
        total_alarm.update(p1_alarm)

        return total_alarm

    def send_egse_state_to_tvac(self, alarm_exp1: bool, alarm_exp2: bool, alarm_exp3: bool, alarm_exp4: bool) -> str:
        """
        Send to TVAC the state of EGSE (EXP1, EXP2, EXP3, EXP4)
        EXP1: Low Temp NOP
        EXP2: High Temp NOP
        EXP3: low/High Temp OP
        EXP4: UPS alarm (UPS_Ix_alarm_summary or UPS_Ix_power_supply_absence or UPS_Arrakis_alarm_summary or UPS_Arrakis_power_supply_absence)
        """
        alarm_list = [int(not(alarm_exp1)), int(not(alarm_exp2)), int(not(alarm_exp3)), int(not(alarm_exp4))]
        bit_array = array([alarm_list[i] * 2 ** i for i in range(4)])
        bit_array = bit_array[bit_array != 0]
        if len(bit_array) == 0:
            return self.cdaq.trans("\x00\x00\x00\x16WRITE_P3X_NIDAQ_918100")
        else:
            value_alarm = hex(sum(bit_array))[-1].upper()
            return self.cdaq.trans(f"\x00\x00\x00\x16WRITE_P3X_NIDAQ_91810{value_alarm}")


    def dec2bitlist_compl(self, d:int) -> list:
        """
        Decompose a integer (base 10) into a list of power of 2.
        e.g. 14 -> [8, 4, 2] (8+4+2 = 14)
        Args:
            d: integer base 10 to decompose (d <= 15)
        returns:
            list of power of 2
        """
        bits = []
        bits_compl = []
        for i in [8, 4, 2, 1]:
            if i <= d:
                bits.append(i)
                d %= i
        for i in [8, 4, 2, 1]:
            if i not in bits:
                bits_compl.append(i)
        return bits_compl

class cdaq9375Proxy(Proxy, cdaq9375Interface):
    """The cdaq9375Proxy class is used to connect to the control server and send commands to
    the NI CDAQ 9375 device remotely."""
    def __init__(
        self,
        protocol=CTRL_SETTINGS.PROTOCOL,
        hostname=CTRL_SETTINGS.HOSTNAME,
        port=CTRL_SETTINGS.CDAQ9375.get("COMMANDING_PORT"),
        timeout = CTRL_SETTINGS.CDAQ9375.get("TIMEOUT") * 1000
    ):
        """
        Args:
            protocol: the transport protocol [default is taken from settings file]
            hostname: location of the control server (IP address)
                [default is taken from settings file]
            port: TCP port on which the control server is listening for commands
                [default is taken from settings file]
        """
        super().__init__(connect_address(protocol, hostname, port), timeout=timeout)

