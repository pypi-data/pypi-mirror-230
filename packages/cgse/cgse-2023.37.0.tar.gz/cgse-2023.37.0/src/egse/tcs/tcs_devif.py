import logging
import socket
import sys

from egse.device import DeviceConnectionError
from egse.device import DeviceConnectionInterface
from egse.device import DeviceTimeoutError
from egse.device import DeviceTransport
from egse.settings import Settings
from egse.system import Timer
from egse.system import format_datetime

logger = logging.getLogger(__name__)

IDENTIFICATION_QUERY = "*IDN?"

READ_TIMEOUT = 5.0  # seconds
WRITE_TIMEOUT = 1.0  # seconds
CONNECT_TIMEOUT = 3.0  # seconds

DEVICE_SETTINGS = Settings.load("TCS Controller")
DEVICE_NAME = "TCS EGSE"


class TCSEthernetInterface(DeviceConnectionInterface, DeviceTransport):
    """Defines the low-level interface to the Keithley DAQ6510 Controller."""

    def __init__(self, hostname=None, port=None):
        """
        Args:
            hostname (str): the IP address or fully qualified hostname of the TCS EGSE hardware
                controller. The default is defined in the 'settings.yaml' configuration file.

            port (int): the IP port number to connect to. The default is defined in the
                'settings.yaml' configuration file.
        """
        super().__init__()

        self.hostname = hostname or DEVICE_SETTINGS.HOSTNAME
        self.port = port or DEVICE_SETTINGS.COMMANDING_PORT
        self.sock = None

        self.is_connection_open = False

    def connect(self):
        """Connect the device.

        Raises:
            DeviceConnectionError: When the connection could not be established. Check the logging
            messages for more detail.

            DeviceTimeoutError: When the connection timed out.

            ValueError: When hostname or port number are not provided.
        """

        # Sanity checks

        if self.is_connection_open:
            logger.warning(f"{DEVICE_NAME}: trying to connect to an already connected socket.")
            return

        if self.hostname in (None, ""):
            raise ValueError(f"{DEVICE_NAME}: hostname is not initialized.")

        if self.port in (None, 0):
            raise ValueError(f"{DEVICE_NAME}: port number is not initialized.")

        # Create a new socket instance

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as e_socket:
            raise DeviceConnectionError(DEVICE_NAME, "Failed to create socket.") from e_socket

        # Attempt to establish a connection to the remote host

        # FIXME: Socket shall be closed on exception?

        # We set a timeout of CONNECT_TIMEOUT sec before connecting and reset to None
        # (=blocking) after the connect. The reason for this is because when no
        # device is available, e.g during testing, the timeout will take about
        # two minutes which is way too long. It needs to be evaluated if this
        # approach is acceptable and not causing problems during production.

        try:
            logger.debug(f'Connecting a socket to host "{self.hostname}" using port {self.port}')
            self.sock.settimeout(CONNECT_TIMEOUT)
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

    def disconnect(self):
        """Disconnect from the Ethernet connection.

        Raises:
            DeviceConnectionError when the socket could not be closed.
        """

        try:
            if self.is_connection_open:
                logger.debug(f"Disconnecting from {self.hostname}")
                self.sock.close()
                self.is_connection_open = False
        except Exception as e_exc:
            raise DeviceConnectionError(
                DEVICE_NAME, f"Could not close socket to {self.hostname}") from e_exc

    def reconnect(self):
        """
        Reconnect to the device. If the connection is open, this function will first disconnect
        and then connect again.
        """

        if self.is_connection_open:
            self.disconnect()
        self.connect()

    def is_connected(self) -> bool:
        """
        Check if the device is connected.

        Returns:
             True is the device is connected, False otherwise.
        """

        return bool(self.is_connection_open)

    def read(self) -> bytes:
        """
        Read a response from the device.

        Returns:
            A bytes object containing the response from the device. No processing is done
            on the response.
        Raises:
            A DeviceTimeoutError when the read operation timed out.
        """
        idx, n_total = 0, 0
        buf_size = 1024 * 10
        response = bytes()

        # Set a timeout of READ_TIMEOUT to the socket.recv

        saved_timeout = self.sock.gettimeout()
        self.sock.settimeout(READ_TIMEOUT)

        try:
            for idx in range(100):
                data = self.sock.recv(buf_size)
                n = len(data)
                n_total += n
                response += data
                if b'\x03' in response:
                    break
        except socket.timeout as e_timeout:
            logger.warning(f"Socket timeout error: {e_timeout}")
            raise DeviceTimeoutError(DEVICE_NAME, "Socket timeout error") from e_timeout
        finally:
            self.sock.settimeout(saved_timeout)

        # logger.info(f"Total number of bytes received is {n_total}, idx={idx}")
        # logger.info(f"> {len(response)=}")
        # logger.info(f"> {response[:80]=}")

        return response

    def write(self, command: str):
        """
        Send a command to the device.

        No processing is done on the command string, except for the encoding into a bytes object.

        Args:
            command: the command string including terminators.

        Raises:
            A DeviceTimeoutError when the send timed out, and a DeviceConnectionError if
            there was a socket related error.
        """

        try:
            self.sock.sendall(command.encode())
        except socket.timeout as e_timeout:
            raise DeviceTimeoutError(DEVICE_NAME, "Socket timeout error") from e_timeout
        except socket.error as e_socket:
            # Interpret any socket-related error as an I/O error
            raise DeviceConnectionError(DEVICE_NAME, "Socket communication error.") from e_socket

    def trans(self, command: str):
        """
        Send a command to the device and wait for the response.

        No processing is done on the command string, except for the encoding into a bytes object.

        Args:
            command: the command string including terminators.

        Returns:
            A bytes object containing the response from the device. No processing is done
            on the response.

        Raises:
            A DeviceTimeoutError when the send timed out, and a DeviceConnectionError if
            there was a socket related error.
        """

        try:
            # Attempt to send the complete command

            self.sock.sendall(command.encode())

            # wait for, read and return the response (will be at most TBD chars)

            return_string = self.read()

            return return_string

        except socket.timeout as e_timeout:
            raise DeviceTimeoutError(DEVICE_NAME, "Socket timeout error") from e_timeout
        except socket.error as e_socket:
            # Interpret any socket-related error as an I/O error
            raise DeviceConnectionError(DEVICE_NAME, "Socket communication error.") from e_socket


if __name__ == "__main__":

    from rich import print

    def send_command(cmd):
        cmd = cmd.rstrip()
        with Timer("TCS EGSE Query"):
            response = tcs.query(cmd + "\n")
        logger.debug(f"{format_datetime()} Response for {cmd:>20s}: {response.rstrip()}")
        return response.decode()

    tcs = TCSEthernetInterface(hostname='localhost')

    print("-" * 10, end="")
    print("Connecting to the device.")

    try:
        tcs.connect()
    except DeviceTimeoutError as exc:
        print(f"[red]{exc}[/red]")
        sys.exit(-1)

    print("-"*10, end='')
    print("Requesting remote operations.")

    response = send_command("request_remote_operation")
    print(f"{response=}")

    if "not_active" in response:
        print("[red]Remote operation was rejected from the TCS EGSE.[/red]")

    print("Set operation mode .")

    response = send_command("set_parameter operation_mode 6")  # Extended operation mode
    print(f"{response=}")

    print("Stopping remote operations.")

    response = send_command("quit_remote_operation")  # !!!! no response expected !!!!
    print(f"{response=}")

    print("Disconnecting from the device.")

    tcs.disconnect()
