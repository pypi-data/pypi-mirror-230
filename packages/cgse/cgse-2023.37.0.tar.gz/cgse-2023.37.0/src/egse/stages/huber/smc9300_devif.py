"""
HUBER Device Interface to the SMC 9300 motor controller.
"""

import logging
import socket
import threading
import time

from egse.command import ClientServerCommand
from egse.device import DeviceConnectionError
from egse.device import DeviceConnectionInterface
from egse.device import DeviceTimeoutError
from egse.device import DeviceTransport
from egse.settings import Settings
from egse.system import Timer
from egse.system import format_datetime

# Explicitly set the module name instead of __name__. When module is executed instead of imported
# __name__ will result in __main__ and no logging to zmq will be done.

MODULE_LOGGER = logging.getLogger("egse.stages.huber.smc9300_devif")

READ_TIMEOUT = 10.0  # seconds
WRITE_TIMEOUT = 1.0  # seconds
CONNECT_TIMEOUT = 3.0  # seconds

HUBER_SETTINGS = Settings.load("Huber Controller")
DEVICE_NAME = "SMC9300"


class HuberError(Exception):
    pass


class HuberSMC9300Command(ClientServerCommand):
    def get_cmd_string(self, *args, **kwargs) -> str:
        out = super().get_cmd_string(*args, **kwargs)
        return out + "\r\n"


class HuberSMC9300EthernetInterface(DeviceConnectionInterface, DeviceTransport):
    """
    Defines the low-level interface to the HUBER stages controller.

    Args:
        hostname (str): the IP address or fully qualified hostname of the OGSE hardware
            controller. The default is defined in the ``settings.yaml`` configuration file.

        port (int): the IP port number to connect to. The default is defined in the
            `settings.yaml` configuration file.
    """
    def __init__(self, hostname: str = None, port: int = None):

        super().__init__()

        # Basic connection settings, loaded from the configuration YAML file

        self.hostname = hostname or HUBER_SETTINGS.HOSTNAME
        self.port = port or HUBER_SETTINGS.PORT
        self.sock = None

        # Access-to-the-connection semaphore. Use this to lock/unlock I/O access to the
        # connection (whatever type it is) in child classes.

        self.semaphore = threading.Semaphore()

        self.is_connection_open = False

        self._num_axes = HUBER_SETTINGS.NUMBER_OF_AXES

    def connect(self):
        """
        Connects the TCP socket to the device controller.

        Returns:
            None.

        Raises:
            ValueError when hostname or port number are not initialized properly.

            DeviceConnectionError on any socket error except timeouts.

            DeviceTimeoutError on a socket timeout.
        """
        # Sanity checks

        if self.is_connection_open:
            MODULE_LOGGER.warning(
                f"{DEVICE_NAME}: trying to connect to an already connected socket.")
            return

        if self.hostname in (None, ""):
            raise ValueError(f"{DEVICE_NAME}: hostname is not initialized.")

        if self.port in (None, 0):
            raise ValueError(f"{DEVICE_NAME}: port number is not initialized.")

        # Create a new socket instance

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # self.sock.setblocking(1)

            # DON'T set a timeout on the socket, this will not result in the expected behavior.
            #
            # If the timeout is set, this will result in the following problem:
            # DEBUG    234    huber.py  send_direct_command: Sent out to HUBER: 'goto1:0.0\r\n'
            # DEBUG    284    huber.py  wait_until_axis_ready: Wait until axis 1 is ready...
            # DEBUG    191    huber.py  get_response: Sent out to HUBER: '?s1\r\n'
            # DEBUG    198    huber.py  get_response: Receiving data after cmd=''?s1\r\n''...
            # WARNING  263    huber.py  wait_for_response: Socket timeout error from timed out
            # DEBUG    200    huber.py  get_response: Received from HUBER: b'\r\n'
            #

            # self.sock.settimeout(3)

        except socket.error as e_socket:
            raise DeviceConnectionError(DEVICE_NAME, "Failed to create socket.") from e_socket

        # Attempt to establish a connection to the remote host

        # FIXME: Socket shall be closed on exception?

        # We set a timeout of 3 sec before connecting and reset to None
        # (=blocking) after the connect() method. The reason for this that when no
        # HUBER SMC is available, e.g. during testing, the timeout will take about
        # two minutes which is way too long. It needs to be evaluated if this
        # approach is acceptable and not causing problems during production.

        try:
            MODULE_LOGGER.debug(
                f'Connecting a socket to host "{self.hostname}" using port {self.port}')
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

        # The first thing to receive should be the 'smc 1.2.1093' string.

        response = self.read()
        MODULE_LOGGER.debug(f"After connection, we got '{response}' as a response.")

    def disconnect(self):
        """
        Disconnect the Ethernet connection from the device controller.

        Raises:
             a DeviceConnectionError on failure.
        """
        try:
            if self.is_connection_open:
                MODULE_LOGGER.debug(f'Disconnecting from {self.hostname}')
                self.semaphore.acquire()
                self.sock.close()
                self.semaphore.release()
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
            for _ in range(100):
                # time.sleep(0.1)  # Give the device time to fill the buffer
                data = self.sock.recv(buf_size)
                n = len(data)
                n_total += n
                response += data
                if n < buf_size:
                    break
        except socket.timeout as e_timeout:
            MODULE_LOGGER.warning(f"Socket timeout error: {e_timeout}")
            raise DeviceTimeoutError(DEVICE_NAME, "Socket timeout error") from e_timeout
        finally:
            self.sock.settimeout(saved_timeout)

        # logger.debug(f"Total number of bytes received is {n_total}, idx={idx}")
        # logger.debug(f"> {response[:80]=}")

        return response

    def write(self, command: str) -> None:
        """
        Send a command to the device.

        No processing is done on the command string, except for the encoding into a bytes object.

        Args:
            command: the command string including terminators.

        Raises:
            A DeviceTimeoutError when the sendall() timed out, and a DeviceConnectionError if
            there was a socket related error.
        """

        # MODULE_LOGGER.debug(f"{command.encode() = }")

        try:
            self.sock.sendall(command.encode())

            # Give the SMC time to start a new command: see issue #1209
            time.sleep(0.5)

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
            A DeviceTimeoutError when the sendall() timed out, and a DeviceConnectionError if
            there was a socket related error.
        """
        # MODULE_LOGGER.debug(f"{command.encode() = }")

        try:
            # Attempt to send the complete command

            self.sock.sendall(command.encode())

            # wait for, read and return the response (will be at most TBD chars)

            return self.read()

        except socket.timeout as e_timeout:
            raise DeviceTimeoutError(DEVICE_NAME, "Socket timeout error") from e_timeout
        except socket.error as e_socket:
            # Interpret any socket-related error as an I/O error
            raise DeviceConnectionError(DEVICE_NAME, "Socket communication error.") from e_socket


if __name__ == "__main__":

    from rich import print

    def send_command(cmd):
        cmd = cmd.rstrip()
        with Timer(f"{DEVICE_NAME} Query"):
            response = huber.query(cmd + "\r\n")
        print(f"{format_datetime()} Response for {cmd:>20s}: {response}")
        response = response.rstrip()
        return response

    huber = HuberSMC9300EthernetInterface()

    print(f"{' ' :->10} Connecting to {DEVICE_NAME}..")

    huber.connect()

    print(f"{' ' :->10} Requesting info..")

    send_command("?")
    send_command("?v")
    send_command("?s1")
    send_command("?status1")
    send_command("?status2")
    send_command("?status3")
    send_command("?err1")
    send_command("?conf1")
    send_command("?conf2")
    send_command("?conf3")
    send_command("?p1")
    send_command("?e1")
    send_command("?ec1")
    send_command("?ip")
    send_command("?pgm")  # command not yet available
    send_command("?ffast1")
    send_command("?ffast2")
    send_command("?ffast3")

    print(f"{' ' :->10} Closing connection..")

    huber.disconnect()
