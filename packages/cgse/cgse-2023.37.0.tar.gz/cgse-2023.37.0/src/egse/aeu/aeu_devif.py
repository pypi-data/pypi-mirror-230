import logging
import socket
import time
from string import digits

from egse.control import time_in_s
from egse.device import DeviceConnectionError, DeviceTimeoutError
from egse.mixin import CARRIAGE_RETURN, LINE_FEED
from egse.system import SignalCatcher

logger = logging.getLogger(__name__)

CONNECT_TIMEOUT = 3.0   # Timeout when connecting the socket [s]
CMD_DELAY = {           # Time between subsequent commands [s]
    "CRIO": 0.2,
    "PSU": 0.2,
    "AWG": 0.5
}

TM_TERMINATOR = {
    "CRIO": (CARRIAGE_RETURN + LINE_FEED).encode("latin1"),
    "PSU": LINE_FEED.encode("latin1"),
    "AWG": (CARRIAGE_RETURN + LINE_FEED).encode("latin1")
}

TM_MAX_LENGTH = {
    "CRIO": 4096,
    "PSU": None,
    "AWG": None
}


remove_digits = str.maketrans('', '', digits)


class AEUError(Exception):
    """ An AEU-specific error."""

    pass


class AEUEthernetInterface(object):
    """ Ethernet Interface for the AEU devices (cRIO, PSUs, and AWGs)."""

    def __init__(self, name, hostname, port):
        """ Initialisation of an Ethernet Interface for an AEU device.

        Args:
            - name: Name for the AEU device (CRIO, PSU[1:6], AWG[1:2]).
            - hostname: Hostname.
            - port: Port number.
        """

        self.name = name
        self.hostname = hostname
        self.port = port

        self.is_connection_open = False
        self.socket = None

        self.cmd_delay = CMD_DELAY[name.translate(remove_digits)]

        self.killer = SignalCatcher()

    def connect(self):
        """ Connect the AEU device.

        Raises:
            - DeviceConnectionError: When the connection could not be established. Check the logging messages for more
                                     detail.
            - DeviceTimeoutError: When the connection timed out.
            - ValueError: When hostname and/or port number are not provided.
        """

        # Sanity checks

        if self.is_connection_open:

            logger.warning(f"{self.name}: trying to connect to an already connected socket.")
            return

        if self.hostname in (None, ""):

            raise ValueError(f"{self.name}: hostname is not initialised.")

        if self.port in (None, 0):

            raise ValueError(f"{self.name}: port number is not initialised.")

        # Create a new socket instance

        try:

            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        except socket.error as e_socket:

            raise AEUError(self.name, "Failed to create socket.") from e_socket

        # FIXME: Socket shall be closed on exception?

        try:

            # Attempt to establish a connection to the remote host

            logger.debug(f'Connecting a socket to {self.name} on host "{self.hostname}" using port {self.port}')
            self.socket.settimeout(CONNECT_TIMEOUT)
            self.socket.connect((self.hostname, self.port))
            self.socket.settimeout(None)

        except ConnectionRefusedError as exc:

            raise AEUError(
                self.name, f"Connection refused to  {self.name} on {self.hostname}:{self.port}."
            ) from exc

        except TimeoutError as exc:

            raise AEUError(
                self.name, f"Connection to {self.name} on {self.hostname}:{self.port} timed out."
            ) from exc

        except socket.gaierror as exc:

            raise AEUError(
                self.name, f"socket address info error for {self.hostname}"
            ) from exc

        except socket.herror as exc:

            raise AEUError(
                self.name, f"socket host address error for {self.hostname}"
            ) from exc

        except socket.timeout as exc:

            raise AEUError(
                self.name, f"socket timeout error for {self.name} on {self.hostname}:{self.port}"
            ) from exc

        except OSError as exc:

            raise AEUError(self.name, f"OSError caught ({exc}).") from exc

        self.is_connection_open = True

        if not self.is_connected():

            raise AEUError(self.name, "Device is not connected, check logging messages for the cause.")

    def is_connected(self) -> bool:
        """Check if the device is connected.
        This will send a query for the device identification and validate the answer.

        Returns:
            - True is the device is connected and answered with the proper ID, False otherwise.
        """

        # TODO
        return self.is_connection_open

    def disconnect(self):
        """ Disconnect from the Ethernet connection.

        Raises:
            - AEUError on failure.
        """

        try:
            if self.is_connection_open:

                logger.debug(f'Disconnecting {self.name} on {self.hostname}')
                self.socket.close()
                self.is_connection_open = False

        except Exception as e_exc:

            raise AEUError(f"Could not close socket to {self.name} on {self.hostname}") from e_exc

    def reconnect(self):
        """ Reconnect to the Ethernet connection.

        Raises:
            - AEUError on failure.
        """

        if self.is_connection_open:

            self.disconnect()

        self.connect()

    def write(self, command):
        """ Send a write command.

        Args:
            - command: Write command to send.

        Raises:
            - DeviceTimeoutError: for socket timeouts
            - DeviceConnectionError: for any socket-related error
        """

        start_time = time_in_s()

        try:

            encoded_cmd = command.encode("latin1")

            reply = self.socket.send(encoded_cmd)

        except socket.timeout as e_timeout:

            raise DeviceTimeoutError(self.name, "Socket timeout error") from e_timeout

        except socket.error as e_socket:

            # Interpret any socket-related error as an I/O error

            raise DeviceConnectionError(self.name, "Socket communication error.") from e_socket

        elapsed_time = time_in_s() - start_time
        wait_time = max(0, CMD_DELAY[self.name.translate(remove_digits)] - elapsed_time)
        time.sleep(wait_time)

    def read(self):
        """ Send a read command."""

        buf_size = 1024
        response = bytes()
        response_length = 0

        first_batch = None
        try:

            while True:

                data = self.socket.recv(buf_size)
                response_length += len(data)

                response += data

                # TM terminator received

                if data.find(TM_TERMINATOR[self.name.translate(remove_digits)]) != -1:

                    break

                # Maximum amount of data received for the cRIO

                if self.name == "CRIO":

                    if response_length == TM_MAX_LENGTH[self.name.translate(remove_digits)]:

                        break

                # Result from ARB[1:4]? command (for AWG)

                if response.startswith(b"#"):

                    # First batch of data: check how much data is supposed to be received in total

                    if first_batch is None:

                        first_batch = data.decode(encoding="latin1")

                        # Header:
                        # #<number of digits describing the number of bytes in the data><number of bytes in the data>

                        len_num_bytes = int(first_batch[1])     # Digits describing number of bytes in the data
                        num_bytes_data = int(first_batch[2:2 + len_num_bytes])  # Number of bytes in the data

                        # How many bytes should be received in total (header + data)?

                        expected_num_bytes_total = 2 + len_num_bytes + num_bytes_data

                    if response_length == expected_num_bytes_total:

                        break

        except socket.timeout as e_timeout:

            logger.warning(f"Socket timeout error: {e_timeout}")
            raise DeviceTimeoutError(self.name, "Socket timeout error") from e_timeout

        # logger.debug(f"> {response}")

        return response

    def trans(self, command):
        """ Send a query command.

        Args:
            - command: Query command to send.

        Raises:
            - DeviceTimeoutError: for socket timeouts
            - DeviceConnectionError: for any socket-related error
        """

        try:

            # Attempt to send the complete command

            self.write(command)

            # Wait for, read, and return the response

            response = self.read()

            return response

        except socket.timeout as e_timeout:

            raise DeviceTimeoutError(self.name, "Socket timeout error") from e_timeout

        except socket.error as e_socket:

            # Interpret any socket-related error as an I/O error

            raise DeviceConnectionError(self.name, "Socket communication error.") from e_socket
