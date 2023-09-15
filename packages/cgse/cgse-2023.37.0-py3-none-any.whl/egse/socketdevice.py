"""
This module defines a generic base class for ethernet socket based device interface classes.
"""

import logging
import socket
import time
from threading import Lock

from egse.decorators import dynamic_interface
from egse.device import DeviceConnectionInterface


logger = logging.getLogger(__name__)


class SocketDevice(DeviceConnectionInterface):
    """ Generic base class for socket based device interface classes.

        This base class handles the socket connection.
    """


    def __init__(self, hostname=None, port=None, timeout=5):
        self._hostname  = hostname
        self._port      = port
        self._timeout   = timeout
        self._sock      = None
        self._connected = False
        self._lock      = Lock()


    @dynamic_interface
    def get_idn(self):
        """ Get the device ID string

            Child classes must implement this function because it is required for `is_connected()`

            Raises:
                ConnectionError: when the connection failed.
        """
        raise NotImplementedError


    def is_simulator(self):
        return False


    def connect(self):
        """ Connect the ethernet socket.

            Raises a ConnectionError on failure.
        """

        # Sanity checks
        if self._connected:
            raise ConnectionError("Socket is already open")
        if self._hostname in (None, ""):
            raise ValueError("Hostname not initialized")
        if self._port in (None, 0):
            raise ValueError("Port number not initialized")

        # Create a new socket instance
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.setblocking(1)
            self._sock.settimeout(self._timeout)
        except socket.error as e_socket:
            raise ConnectionError("Failed to create socket.") from e_socket

        # Attempt to establish a connection to the remote host
        try:
            logger.debug(f'Connecting a socket to host "{self._hostname}" using port {self._port}')
            with self._lock:
                self._sock.connect((self._hostname, self._port))
        except ConnectionRefusedError as e_cr:
            raise ConnectionError(f"Connection refused to {self._hostname}") from e_cr
        except socket.gaierror as e_gai:
            raise ConnectionError(f"Socket address info error for {self._hostname}") from e_gai
        except socket.herror as e_h:
            raise ConnectionError(f"Socket host address error for {self._hostname}") from e_h
        except socket.timeout as e_timeout:
            raise ConnectionError(f"Socket timeout error for {self._hostname}") from e_timeout
        except OSError as ose:
            raise ConnectionError(f"OSError caught ({ose}).") from ose

        self._connected = True


    def disconnect(self):
        """ Disconnect from the Ethernet connection.

            Raises a ConnectionError on failure.
        """

        try:
            if self._connected:
                logger.debug(f"Disconnecting from {self._hostname}")
                with self._lock:
                    self._sock.close()
                self._connected = False
        except Exception as e_exc:
            raise ConnectionError(f"Could not close socket to {self._hostname}") from e_exc


    def reconnect(self):
        """ Disconnect the device socket if it is already connected and try to connect.
        """

        if self._connected:
            self.disconnect()

        self.connect()


    def is_connected(self):
        """ Check if the socket connection to the device is active.
        """

        if not self._connected:
            return False

        try:
            response = self.get_idn()
        except ConnectionError as err:
            logger.error(f'While trying to talk to the device the following exception occured,',
                         'exception={err}')
            self.disconnect()
            return False

        return True


    def send_command(self, command: str):
        """
        Send a single command to the device controller without waiting for a response.

        Args:
            command: an order command for the controller.

        Raises:
            ConnectionError when the command could not be sent due to a timeout or a communication
            problem.
        """
        # print('send:', repr(command))

        try:
            with self._lock:
                self._sock.sendall(command.encode())

        except socket.timeout as e_timeout:
            raise ConnectionError("Socket timeout error") from e_timeout
        except socket.error as e_socket:
            # Interpret any socket-related error as an I/O error
            raise ConnectionError("Socket communication error.") from e_socket


    def query(self, command: str):
        """
        Send a single command to the device controller and block until a response from the
        controller. This function can be overridden by the child class to implement device specific
        sanity checks on the reponse.

        Args:
            command: is the command to be sent

        Returns:
            Either a string returned by the controller (on success), or an error message (on
            failure).

        Raises:
            ConnectionError when there was an I/O problem during communication with the
            controller.
        """

        try:
            with self._lock:

                raw_command = command.encode()
                # print('send:', repr(raw_command))

                # Attempt to send the complete command
                self._sock.sendall(raw_command)

                # wait for, read and return the response the device
                return_string = self.wait_for_response()

                # print('recv:', repr(return_string))

            return return_string.decode()

        except socket.timeout as e_timeout:
            logger.error(e_timeout)
            raise ConnectionError("Socket timeout error") from e_timeout
        except socket.error as e_socket:
            # Interpret any socket-related error as an I/O error
            raise ConnectionError("Socket communication error.") from e_socket


    def wait_for_response(self):
        n_total = 0
        buf_size = 2048

        try:
            for idx in range(100):
                time.sleep(0.001)  # Give the device time to fill the buffer
                data = self._sock.recv(buf_size)
                n = len(data)
                n_total += n
                if n < buf_size:
                    break

        except socket.timeout as e_timeout:
            raise ConnectionError("Socket timeout error") from e_timeout

        #logger.debug(f"Total number of bytes received is {n_total}, idx={idx}")

        return data
