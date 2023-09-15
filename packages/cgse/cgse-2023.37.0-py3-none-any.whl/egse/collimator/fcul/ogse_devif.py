"""
The device interface for the RT-OGSE that will be used at CSL for alignment of the PLATO Cameras.

"""
import logging
import socket
import time

from egse.device import DeviceConnectionError
from egse.device import DeviceConnectionInterface
from egse.device import DeviceTimeoutError
from egse.device import DeviceTransport
from egse.settings import Settings
from egse.system import format_datetime, Timer

logger = logging.getLogger(__name__)

READ_TIMEOUT = 10.0  # seconds
WRITE_TIMEOUT = 1.0  # seconds
CONNECT_TIMEOUT = 3.0  # seconds

CTRL_SETTINGS = Settings.load("OGSE Controller")
DEVICE_NAME = "OGSE"


class OGSEError(Exception):
    """Generic Error for the OGSE low-level classes."""

    pass


class OGSEEthernetInterface(DeviceConnectionInterface, DeviceTransport):
    """Defines the low-level interface to the OGSE Controller."""

    def __init__(self, hostname=None, port=None):
        """
        Args:
            hostname (str): the IP address or fully qualified hostname of the OGSE hardware
                controller. The default is defined in the ``settings.yaml`` configuration file.

            port (int): the IP port number to connect to. The default is defined in the
                `settings.yaml` configuration file.
        """
        super().__init__()
        self.hostname = hostname or CTRL_SETTINGS.HOSTNAME
        self.port = port or CTRL_SETTINGS.PORT
        self.sock = None

        self.is_connection_open = False

    def connect(self):
        """
        Connect the OGSE device.

        Raises:
            DeviceConnectionError when the connection could not be established. Check the logging
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

        # The OGSE will respond with a message when connecting. We have to read this
        # message from the buffer and can do some version checking if needed.

        response = self.read()

        # The expected response has the following format: b'This is PLATO RT-OGSE 2.1\n'

        if b"PLATO RT-OGSE" in response:
            version = response.rsplit(maxsplit=1)[-1]
            logger.info(f"Connected to the PLATO RT-OGSE, {version=}")
        else:
            logger.warning(f"Unexpected response after connecting to the RT-OGSE. {response=}")

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

        if self.is_connection_open:
            self.disconnect()
        self.connect()

    def is_connected(self) -> bool:
        """
        Check if the device is connected.

        Returns:
             True is the device is connected, False otherwise.
        """

        if not self.is_connection_open:
            return False

        return True

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
                # time.sleep(0.1)  # Give the device time to fill the buffer
                data = self.sock.recv(buf_size)
                n = len(data)
                n_total += n
                response += data
                if n < buf_size:
                    break
        except socket.timeout as e_timeout:
            logger.warning(f"Socket timeout error: {e_timeout}")
            raise DeviceTimeoutError(DEVICE_NAME, "Socket timeout error") from e_timeout
        finally:
            self.sock.settimeout(saved_timeout)

        # logger.debug(f"Total number of bytes received is {n_total}, idx={idx}")
        # logger.debug(f"> {response[:80]=}")

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
        logger.debug(f"{command=}")

        try:
            self.sock.sendall(command.encode())
        except socket.timeout as e_timeout:
            raise DeviceTimeoutError(DEVICE_NAME, "Socket timeout error") from e_timeout
        except socket.error as e_socket:
            # Interpret any socket-related error as an I/O error
            raise DeviceConnectionError(DEVICE_NAME, "Socket communication error.") from e_socket

    def trans(self, command: str) -> bytes:
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
        # logger.debug(f"{command=}")

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

    def send_command(cmd):
        cmd = cmd.rstrip()
        with Timer("OGSE Query"):
            response = ogse.query(cmd + "\n")
        print(f"{format_datetime()} Response for {cmd:>20s}: {response.rstrip()}")
        return response

    def wait_for_att():
        while b'*' in ogse.query("level\n"):
            time.sleep(1)


    ogse = OGSEEthernetInterface()

    print("-" * 10, end="")
    print("Connecting to the device.")

    ogse.connect()

    print("-"*10, end='')
    print("Requesting all info.")

    send_command("get flags")
    send_command("get interlock")
    send_command("get power")
    send_command("get lamp")
    send_command("get laser")
    send_command("get lamp-fault")
    send_command("get controller-fault")
    send_command("get psu")
    send_command("get operate")
    send_command("get XXX")

    print("-"*10, end='')
    print("Requesting lamp status.")

    send_command("ldls status")

    print("-"*10, end='')
    print("Playing with attenuator commands")

    send_command("att status")

    send_command("level")
    send_command("level 0.1")
    wait_for_att()
    send_command("level up")
    wait_for_att()
    send_command("level")
    send_command("level up")
    wait_for_att()
    send_command("level")
    send_command("level down")
    wait_for_att()
    send_command("level")
    send_command("level down")
    wait_for_att()
    send_command("level")
    send_command("level up")
    wait_for_att()
    send_command("level")
    send_command("level 0.8")
    wait_for_att()
    send_command("level")

    print("-"*10, end='')
    print("Running through attenuation levels")

    for a in range(1, 9):
        for b in range(1, 9):
            send_command(f"level {a} {b}")
            wait_for_att()
            send_command("level")

    print("-"*10, end='')
    print("Request info from Power Meter")

    send_command("read")

    print("-"*10, end='')
    print("Request 10 power meter measurements")

    for _ in range(10):
        send_command("read")
        time.sleep(1)

    ogse.disconnect()
