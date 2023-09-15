"""
This module defines a generic base class for serial based device interface classes.
"""

import logging
from serial import Serial, SerialTimeoutException, SerialException
from threading import Lock

from egse.decorators import dynamic_interface
from egse.device import DeviceConnectionInterface


logger = logging.getLogger(__name__)


class SerialDevice(DeviceConnectionInterface):
    """ Generic base class for serial based device interface classes.

        This base class handles the serial connection.
    """


    def __init__(self, port=None, baudrate=9600, terminator='\r', timeout=5, encoding='ascii', errors='strict'):
        self._port       = port
        self._baudrate   = baudrate
        self._terminator = terminator
        self._encoding   = encoding
        self._errors     = errors
        self._timeout    = timeout
        self._serial     = None
        self._connected  = False
        self._lock       = Lock()


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
        """ Create the serial conection.

            Raises a ConnectionError on failure.
        """

        # Sanity checks
        if self._connected:
            raise ConnectionError("Serial connection is already open")
        if self._port in (None, ""):
            raise ValueError("Serial port not initialized")
        if self._baudrate in (None, 0):
            raise ValueError("Baudrate not initialized")

        # Create a new serial connection
        try:
            self._serial = Serial(port=self._port, baudrate=self._baudrate,
                                  timeout=self._timeout, write_timeout=self._timeout)
        except ValueError as e_value:
            raise ConnectionError("Invalid parameters for serial connection") from e_value
        except SerialException as e_serial:
            raise ConnectionError("Failed to open serial device.") from e_serial

        self._connected = True


    def disconnect(self):
        """ Disconnect from the serial connection.

            Raises a ConnectionError on failure.
        """

        try:
            if self._connected:
                logger.debug(f"Disconnecting from {self._port}")
                with self._lock:
                    self._serial.close()
                self._connected = False
        except Exception as e_exc:
            raise ConnectionError(f"Could not close serial connection to {self._port}") from e_exc


    def reconnect(self):
        """ Disconnect the serial connection if it is already connected and try to connect.
        """

        if self._connected:
            self.disconnect()

        self.connect()


    def is_connected(self):
        """ Check if the socket connection to the device is active.
            This function assumes the child class implements the get_idn method.
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

        # print("send: ", repr(command))

        try:
            with self._lock:
                self._serial.write(command.encode(encoding=self._encoding, errors=self._errors))

        except SerialTimeoutException as e_timeout:
            raise ConnectionError("Serial timeout error") from e_timeout


    def read(self):
        """
        Read a response from the device until a termination character is encountered.

        Returns:
            Either a string returned by the controller (on success), or an error message (on
            failure).

        Raises:
            ConnectionError when there was an I/O problem during communication with the
            controller.
        """

        try:
            with self._lock:
                # Read the response
                # NOTE: the serial module reads until it encounters the \n termination character
                return_string = self._serial.read_until(self._terminator.encode(encoding=self._encoding, errors=self._errors), size=1024)
                # print(f"recv: ", repr(return_string))

            return return_string.decode(encoding=self._encoding, errors=self._errors)

        except SerialTimeoutException as e_timeout:
            raise ConnectionError("Serial timeout during query") from e_timeout


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

        # Attempt to send the command
        self.send_command(command)
        return self.read()
