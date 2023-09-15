"""
The device interface for the NICDAQ 9184 Controller that will be used at IAS for TVAC the PLATO Cameras.

"""

import logging
import time
import socket
import struct
from typing import List

from egse.settings import Settings
from egse.exceptions import DeviceNotFoundError
from egse.device import DeviceConnectionError, DeviceError
from egse.device import DeviceConnectionInterface, DeviceTransport, DeviceTimeoutError
from egse.command import ClientServerCommand

logger = logging.getLogger(__name__)

ctrl_settings = Settings.load("NI Controller")

DEVICE_NAME = "CDAQ9184"

READ_TIMEOUT = 1


class cdaq9184Error(Exception):
    """Base exception for all ptc10 errors."""
    pass


class cdaq9184Command(ClientServerCommand):
    def get_cmd_string(self, *args, **kwargs) -> str:
        out = super().get_cmd_string(*args, **kwargs)
        return out + "\n"


class cdaq9184SocketInterface(DeviceConnectionInterface, DeviceTransport):
    """Defines the low-level interface to the NI CDAQ919 Controller.
    Connects to the Labview interface via TCP/IP socket"""

    def __init__(self, hostname=None, port=None):
        self.hostname = ctrl_settings.HOSTNAME if hostname is None else hostname
        self.port = ctrl_settings.CDAQ9174_PORT if port is None else port
        self.sock = None

        self.is_connection_open = False

    def connect(self, hostname: str):
        # Sanity checks
        if self.is_connection_open:
            logger.warning(f"{DEVICE_NAME}: trying to connect to an already connected socket.")
            return
        if self.hostname in (None, ""):
            raise ValueError(f"{DEVICE_NAME}: hostname is not initialized.")

        if self.port in (None, 0):
            raise ValueError(f"{DEVICE_NAME}: port number is not initialized.")

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            _id = self.get_id()
            logger.warning(f"Connected to: {_id}")

        except socket.error as e_socket:
            raise DeviceConnectionError(DEVICE_NAME, "Failed to create socket.") from e_socket
            # Asking for instrument description

        # We set a timeout of 3 sec before connecting and reset to None
        # (=blocking) after the connect. The reason for this is because when no
        # device is available, e.g during testing, the timeout will take about
        # two minutes which is way too long. It needs to be evaluated if this
        # approach is acceptable and not causing problems during production.

        try:
            logger.debug(f'Connecting a socket to host "{self.hostname}" using port {self.port}')
            self.sock.settimeout(3)
            self.sock.connect((self.hostname, self.port))
            self.sock.settimeout(None)
        except ConnectionRefusedError as exc:
            raise DeviceConnectionError(
                DEVICE_NAME, f"Connection refused to {self.hostname}:{self.port}."
            ) from exc
        except TimeoutError as exc:
            raise DeviceTimeoutError(
                DEVICE_NAME, f"Connection to {self.hostname}:{self.port} timed out."
            ) from exc
        except socket.gaierror as exc:
            raise DeviceConnectionError(
                DEVICE_NAME, f"socket address info error for {self.hostname}"
            ) from exc
        except socket.herror as exc:
            raise DeviceConnectionError(
                DEVICE_NAME, f"socket host address error for {self.hostname}"
            ) from exc
        except socket.timeout as exc:
            raise DeviceTimeoutError(
                DEVICE_NAME, f"socket timeout error for {self.hostname}:{self.port}"
            ) from exc
        except OSError as exc:
            raise DeviceConnectionError(DEVICE_NAME, f"OSError caught ({exc}).") from exc

        self.is_connection_open = True

        if not self.is_connected():
            raise DeviceConnectionError(
                DEVICE_NAME, "Device is not connected, check logging messages for the cause."
            )

    def disconnect(self):
        """
        Disconnects from the device
        Raises:
            DeviceConnectionError when the connection has not been closed correctly

        """
        try:
            if self.is_connection_open:
                logger.debug(f"Disconnecting from {self.hostname}")
                self.sock.close()
                self.is_connection_open = False
        except Exception as e_exc:
            raise DeviceConnectionError(
                DEVICE_NAME, f"Could not close socket to {self.hostname}") from e_exc

    def is_connected(self):
        """Return True if the device is connected."""
        if not self.is_connection_open:
            return False
        return True

    def get_response(self, cmd_string):
        pass

    def get_id(self):
        return DEVICE_NAME

    def write(self, command: str):
        try:
            #logger.info(f"{command=}")
            self.sock.sendall(command.encode())

        except socket.timeout as e_timeout:
            raise DeviceTimeoutError(DEVICE_NAME, "Socket timeout error") from e_timeout
        except socket.error as e_socket:
            # Interpret any socket-related error as a connection error
            raise DeviceConnectionError(DEVICE_NAME, "Socket communication error.") from e_socket
        except AttributeError:
            if not self.is_connection_open:
                msg = "The CDAQ9184 is not connected, use the connect() method."
                raise DeviceConnectionError(DEVICE_NAME, msg)
            raise

    def read(self) -> List:
        # Set a timeout of READ_TIMEOUT to the socket.recv
        saved_timeout = self.sock.gettimeout()
        self.sock.settimeout(READ_TIMEOUT)
        try:
            # Extracts the msg size from 4 bytes sent by Labview - mind the encoding. The number
            # reprensets the number of bytes of data
            size = struct.unpack('i', self.sock.recv(4))[0]
            data = self.sock.recv(size)
        except socket.timeout as e_timeout:
            logger.warning(f"Socket timeout error from {e_timeout}")
            return b"\r\n"
        except TimeoutError as exc:
            logger.warning(f"Socket timeout error: {exc}")
            return b"\r\n"
        finally:
            self.sock.settimeout(saved_timeout)

        #logger.info(f"Total number of bytes received from the cdaq 9184 is {size}")

        data = data.decode("ascii")
        data = data.replace("\x00", " ")
        data = data.replace("\x08", " ")
        data = data.replace("\n", " ")
        data = data.replace(",", ".")
        data = data.replace("\x0c", ",")
        data = data.replace("\r", ",")
        data = data.replace("\x04", ",")
        data = data.replace("\x12", ",")
        data = data.replace("\x0e", ",")
        data = data.replace("    ", ",")
        data = data.replace("0^", "E")
        data = data.split(",")

        data = [element.strip() for element in data]

        # The first element of data is "#" so I delete it.
        # But to avoid to delete a relevant value I check if this unwanted element is well in data before deleting.
        if data[0] == "#":
            del data[0]

        return data

    def trans(self, cmd: str) -> List:
        self.write(cmd)
        response = self.read()
        return response

