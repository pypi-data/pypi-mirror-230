"""
This module defines the basic classes to access the photodiodes readout ensured by
NI CDAQ9184 controller that will be used in the IAS TVAC setup.
"""
import logging
from typing import List

from egse.decorators import dynamic_interface
from egse.device import DeviceConnectionState
from egse.device import DeviceInterface
from egse.powermeter.ni.cdaq9184_devif import cdaq9184Error, cdaq9184SocketInterface
from egse.proxy import Proxy
from egse.settings import Settings
from egse.zmq_ser import connect_address
from egse.mixin import dynamic_command
from egse.mixin import add_lf


LOGGER = logging.getLogger(__name__)

CTRL_SETTINGS = Settings.load("NI Control Server")
CDAQ9184_SETTINGS = Settings.load("NI Controller")
DEVICE_SETTINGS = Settings.load(filename="cdaq9184.yaml")


class cdaq9184Interface(DeviceInterface):
    """
    Interface definition for the Signals acquisitions of the CDAQ9184 Controller, Simulator and Proxy..
    """
    @dynamic_interface
    def info(self) -> str:
        """
        Returns basic information about the device, its name, firmwre version etc.

        The string returned is subject to change without notice and can not be used for parsing
        information.

        Returns:
            An identification string of the instrument.
        """
        raise NotImplementedError


    @dynamic_interface
    def read_values(self):
        """
        Reads the signals of the  channels of the CDAQ9181. Adds timestamp and returns a list.
        Channels read are:
        Photodiode_1 (V) from the integrating sphere, read as ch0 from NI9239
        Photodiode_2 (V) from the integrating sphere, read as ch1 from NI9239

        collimator_1_temp (°C) from the OGSE collimator, read as ch0 from NI9226
        collimator_2_temp (°C) from the OGSE collimator, read as ch1 from NI9226
        sphere_temp (°C) from the integrating sphere, read as ch2 from NI9226

        the returned values are mean and dev from 5 samples acquired at 100Hz.
        The values are sent by a Labview application installed in the Keynes working station

        """

        raise NotImplementedError

    @dynamic_interface
    def read_photodiodes(self):
        """

        Returns: echo values from read_values method, timestamp and photodides' signals in V

        """
        raise NotImplementedError

    @dynamic_interface
    def read_temperatures(self):
        """

        Returns: echo values from read_values method, timestamp and temperature values in °C

        """
        raise NotImplementedError



class cdaq9184Simulator(cdaq9184Interface):
    """
    The pcdaq9184 Simulator class.
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

    def read_values(self):
        pass

    def read_photodiodes(self):
        pass

    def read_temperatures(self):
        pass


class cdaq9184Controller(cdaq9184Interface):
    """The cdaq9184Controller allows controlling a NI CDAQ 9184 photodiode measurement device."""

    def __init__(self):
        """Initialize the cdaq9184 Controller interface."""

        super().__init__()

        LOGGER.debug("Initializing NI CDAQ 9184")

        try:
            self.cdaq = cdaq9184SocketInterface()
            self.cdaq.connect(CDAQ9184_SETTINGS.HOSTNAME) # IP address of the computer with Labview

        except cdaq9184Error as exc:
            LOGGER.warning(f"TempError caught: Couldn't establish connection ({exc})")
            raise cdaq9184Error(
                "Couldn't establish a connection with the NI CDAQ 9184 controller."
            ) from exc

    def connect(self):
        """Connects to the photodiode measurement device.

        Raises:
            DeviceNotFoundError: when the photodiode device is not connected.
        """
        try:
            self.cdaq.connect(CDAQ9184_SETTINGS.HOSTNAME)
        except cdaq9184Error as exc:
             LOGGER.warning(f"cdaqError caught: Couldn't establish connection ({exc})")
             raise ConnectionError("Couldn't establish a connection with the NI DAQ9184 controller.") from exc

        self.notify_observers(DeviceConnectionState.DEVICE_CONNECTED)


    def disconnect(self):
        try:
            self.cdaq.disconnect()
        except cdaq9184Error as exc:
            raise ConnectionError("Couldn't establish a connection with the NI CDAQ 9184 controller.") from exc

        self.notify_observers(DeviceConnectionState.DEVICE_NOT_CONNECTED)


    def reconnect(self):
        if self.is_connected():
            self.disconnect()
        self.connect()

    def is_connected(self):
        """Check if the Temp Controller is connected."""
        return self.cdaq.is_connected()

    def is_simulator(self):
        return False

    def get_id(self):
        return self.cdaq.get_id()

    def info(self):
        pass

    def read_values(self) -> list:
        data = self.cdaq.trans("get_value")
        return data

    def read_temperatures(self) -> dict:
        values = self.read_values()
        all_temp = values[14:26]

        temp_mean = [all_temp[i] for i in range(0, len(all_temp), 2)]
        temp_mean = values[2:] + temp_mean # c'est pas plutôt values[:2] ?
        temp_std = [all_temp[i] for i in range(1, len(all_temp), 2)]
        temp_std = values[2:] + temp_std # c'est pas plutôt values[:2] ?

        temperatures = {"temp_mean": temp_mean, "temp_std": temp_std}

        return temperatures

    def read_photodiodes(self):
        pass


class cdaq9184Proxy(Proxy, cdaq9184Interface):
    """The cdaq9184Proxy class is used to connect to the control server and send commands to
    the NI CDAQ 9184 device remotely."""
    def __init__(
        self,
        protocol=CTRL_SETTINGS.PROTOCOL,
        hostname=CTRL_SETTINGS.HOSTNAME,
        port=CTRL_SETTINGS.CDAQ9184.get("COMMANDING_PORT"),
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

