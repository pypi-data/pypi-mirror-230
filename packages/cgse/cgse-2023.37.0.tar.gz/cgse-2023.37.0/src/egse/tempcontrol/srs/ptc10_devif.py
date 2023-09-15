"""
The device interface for the temperature regulation controller  that will be used at IAS for TVAC the PLATO Cameras.

"""

import logging
import time
import datetime
from typing import List

from telnetlib import Telnet


from egse.settings import Settings
from egse.exceptions import DeviceNotFoundError
from egse.device import DeviceConnectionError
from egse.device import DeviceConnectionInterface, DeviceTransport, DeviceTimeoutError
from egse.command import ClientServerCommand

logger = logging.getLogger(__name__)

ctrl_settings = Settings.load("SRS PTC10 Controller")

IDENTIFICATION_QUERY = "*IDN?"


class ptc10Error(Exception):
    """Base exception for all ptc10 errors."""
    pass

class ptc10Command(ClientServerCommand):
    def get_cmd_string(self, *args, **kwargs) -> str:
        out = super().get_cmd_string(*args, **kwargs)
        return out + "\n"


class ptc10TelnetInterface(DeviceConnectionInterface, DeviceTransport):
    "Low level Telnet IF"
    TELNET_TIMEOUT = 0.5

    def __init__(self):
        self._temp = None
        self.telnet = Telnet()
        self.is_connection_open = False
        self._id = None

    def connect(self, hostname: str):

        try:
            self.telnet.open(hostname, 23)
            time.sleep(0.5)
            # Asking for instrument description
            _id = self.get_id()
            logger.warning(f"Connected to: {_id}")


        except (ValueError, Exception) as exc:
            logger.warning(f"Could not open device connection: {exc}")
            raise DeviceNotFoundError("Could not open device connection.") from exc

        self.is_connection_open = True

    def disconnect(self):
        """
        Disconnects from the device
        Raises:
            DeviceConnectionError when the connection has not been closed correctly

        """
        try:
            if self.is_connection_open:
                logger.debug(f"disconnecting from {self._id}")

                self.telnet.read_very_eager()
                self.telnet.close()

            self.is_connection_open= False
            logger.info("PTC10 device has been disconnected")

        except Exception as e_exc:
            raise DeviceConnectionError(f"Couldn't close the device connection: {self.device_id}") from e_exc

    def is_connected(self):
        """Return True if the device is connected."""
        if not self.is_connection_open:
            return False
        try:
            self.write(IDENTIFICATION_QUERY)
            time.sleep(0.1)
            _id = self.read()
            time.sleep(0.1)
        except OSError:  # FIXME: Check which errors are actually thrown here
            self.disconnect()
            return False
        return True

    def get_response(self, cmd_string):
        pass

    def get_id(self):
        self.write("Description")
        self._id = self.read()
        return self._id

    def write(self, cmd: str):
        self.telnet.write(cmd.encode() + b"\r\n")

    def read(self):
        response = self.telnet.read_until(b'\x06\r\n', timeout=self.TELNET_TIMEOUT)
        response = response.decode()
        parts = response.replace("\r\n", "")
        return parts

    def trans(self, cmd: str) -> List:
        self.write(cmd)
        response = self.read()
        return response

