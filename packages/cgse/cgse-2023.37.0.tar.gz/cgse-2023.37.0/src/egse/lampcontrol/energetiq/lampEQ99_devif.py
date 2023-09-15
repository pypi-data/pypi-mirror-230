"""
The device interface for the LDLS Lamp controller  that will be used at IAS and INTA for TVAC the PLATO Cameras.

"""

import datetime
import logging
import time

import pylibftdi

from egse.device import DeviceConnectionError
from egse.command import ClientServerCommand
from egse.exceptions import DeviceNotFoundError
from egse.settings import Settings

logger = logging.getLogger(__name__)

ctrl_settings = Settings.load("Lamp EQ99 Controller")

IDENTIFICATION_QUERY = "*IDN?"
DEVICE_NAME = "Lamp EQ99"


class LampEQ99Error(Exception):
    """Base exception for all Lamp errors."""
    pass

class LampEQ99Command(ClientServerCommand):
    def get_cmd_string(self, *args, **kwargs) -> str:
        out = super().get_cmd_string(*args, **kwargs)
        return out + "\n"

class LampEQ99USBInterface:
    def __init__(self):
        "Init parameters"
        "FTDI UART driver need to be installed: a CD is provided by the manufacturer"

        self._lamp = None
        self.baudrate = ctrl_settings.BAUDRATE
        self.device_id = ctrl_settings.DEVICE_ID

        self.is_connection_open = False

    def connect(self):
        "Low level interface to the FTDIUART"

        # Sanity checks:
        if self.is_connection_open:
            logger.warning("Trying to connect to an already connected device")
            return

        try:
            self._lamp = pylibftdi.Device(mode='t', device_id=self.device_id)

        # EQ99 Manager uses full size USB Type B socket. Any USB 1.1 or 2.0 certified socked with the following config
        # might be used (from manual)
        # Baud rate = 38400
            self._lamp.baudrate = self.baudrate
        # 8 data bits, 1 stop bit, no parity
            self._lamp.ftdi_fn.ftdi_set_line_property(8, 1, 0)

            # Pre purge dwell 50 ms
            time.sleep(50.0 / 1000)

            # Purge the device
            self._lamp.flush(pylibftdi.FLUSH_BOTH)

            # Post purge dwell 50 ms
            time.sleep(50.0 / 1000)

        #Ensure to disable flow control. Failure to do so will prevent the instrument from sending data back to PC
            self._lamp.ftdi_fn.ftdi_setflowctrl(0)

        except (ValueError, Exception) as exc:
            logger.warning(f"Could not open USB FTDI device: {exc}")
            raise DeviceNotFoundError("Could not open USB FTDI device.") from exc

        try:
            logger.debug(f"Connecting tu UART device named: {self.device_id}")
            self._lamp.open()
        except OSError as exc:
            raise DeviceConnectionError(DEVICE_NAME, f"OSError caught ({exc})") from exc

        self.is_connection_open = True

        response = self.get_id()

        if self.device_id in response:
            logger.info("Well connected to the EQ99 Manager")

    def disconnect(self):
        """
        Disconnects from the device
        Raises:
            DeviceConnectionError when the connection has not been closed correctly

        """
        try:
            if self.is_connection_open:
                logger.debug(f"disconnecting from {self.device_id}")
                self._lamp.close()
            self.is_connection_open = False
            logger.info("EQ99 Lamp Manager device has been disconnected")
        except Exception as e_exc:
            raise DeviceConnectionError(
                DEVICE_NAME, f"Couldn't close the FTDI UART: {self.device_id}") from e_exc

    def is_connected(self):
        """Return True if the device is connected."""
        if not self.is_connection_open:
            return False
        try:
            self.write_message(IDENTIFICATION_QUERY)
            time.sleep(0.1)
            _id = self.read_message()
            time.sleep(0.1)
        except OSError:  # FIXME: Check which errors are actually thrown here
            self.disconnect()
            return False
        return True

    def get_response(self, cmd_string):
        pass

    def get_id(self):
        self.write_message(IDENTIFICATION_QUERY)
        _id = self.read_message()
        return _id

    def _beep(self):
        self.write_message("BEEP")

    def write_message(self, command: str):
        """
        Send a single command to the device controller without waiting for a response.

        Args:
            command: an order command for the controller.
        """
        command = command + "\r" + "\n"
        self._lamp.write(command)

    def read_message(self):
        message = ""
        t1 = datetime.datetime.now()
        while True:
            _byte = self._lamp.read(1)
            time.sleep(0.001)
            if (datetime.datetime.now()-t1).seconds > 2:
                logging.warning("Device timeout")
                break
            if _byte == "\n":
                break
            else:
                message += _byte

        return message
