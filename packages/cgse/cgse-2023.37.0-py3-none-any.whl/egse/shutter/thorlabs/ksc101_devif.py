import logging
import struct
import time

import pylibftdi
from pylibftdi import USB_VID_LIST, USB_PID_LIST

USB_PID_LIST.append(0xfaf0) #adds shutter PID to the USB PID List

from egse.command import ClientServerCommand
from egse.exceptions import DeviceNotFoundError
from egse.settings import Settings

logger = logging.getLogger(__name__)
ctrl_settings = Settings.load("Shutter KSC101 Controller")

# TODO:
#   Add functions to retrieve the controller info and the interlock/error state


class ShutterKSC101Error(Exception):
    """Base exception for all Shutter errors."""
    pass


class ShutterKSC101Command(ClientServerCommand):
    def get_cmd_string(self, *args, **kwargs) -> str:
        out = super().get_cmd_string(*args, **kwargs)
        return out + "\n"


class ShutterKSC101USBInterface:

    def __init__(self):

        self._shutter = None
        self.baudrate = ctrl_settings.BAUDRATE
        self.device_id = ctrl_settings.DEVICE_ID
        self._is_connected = False

        self._modes = {"manual": 0x01, "single": 0x02, "auto": 0x03, "trigger": 0x04}

    def connect(self):
        try:
            # device mode 't' is latin-1 encoding, to be used later for unpacking the message reads
            # you added PID and VID to the list of devices of pylibftdi as suggested by
            # https://pylibftdi.readthedocs.io/en/latest/how_to.html
            self._shutter = pylibftdi.Device(mode = 't', device_id = self.device_id)

        # Steps to perform from APT Communication Protocol section 2.1:
        # Baud rate = 115200
            self._shutter.baudrate = self.baudrate

        # 8 data bits, 1 stop bit, no parity
            self._shutter.ftdi_fn.ftdi_set_line_property(8, 1, 0)

        # Pre purge dwell 50 ms
            time.sleep(50.0 / 1000)

        # Purge the device
            self._shutter.flush(pylibftdi.FLUSH_BOTH)

        # Post purge dwell 50 ms
            time.sleep(50.0 / 1000)

        # Set flow control to RTS/CTS
            SIO_RTS_CTS_HS = (0x1 << 8)
            self._shutter.ftdi_fn.ftdi_setflowctrl(SIO_RTS_CTS_HS)  # returns 0 if OK

        # Set RTS
            self._shutter.ftdi_fn.ftdi_setrts(1)                    # returns 0 if OK

        except (ValueError, Exception) as exc:
            logger.warning(f"Could not open USB FTDI device: {exc}")
            raise DeviceNotFoundError("Could not open USB FTDI device.") from exc

        self._is_connected = True

    def disconnect(self):
        try:
            if self._is_connected:
                logger.debug(f'Disconnecting from {self.device_id}')
                self._shutter.close()
                self._is_connected = False
        except Exception as e_exc:
            raise ShutterKSC101Error(f"Could not close {self.device_id}") from e_exc

        # if not self._shutter.closed:
        #     self._shutter.close()
        # else:
        #     pass
        # self.is_connected = False

    def is_connected(self):
        """Return True if the device is connected."""

        if not self._is_connected:
            return False
        try:
            self.get_id()
        except OSError:  # FIXME: Check which errors are actually thrown here
            self.disconnect()
            return False

        return True

    def get_id(self):
        return('To be implemented')

    def info(self):
        return f"Thorlabs KSC101 Shutter Controller: {self.get_id()}."

    def get_response(self, cmd_string):
        logger.debug(f"get_response() called with {cmd_string}")
        return NotImplemented

    def send_message(self, m):
        "Sends the packed message to the KSC101 Controller"
        self._shutter.write(m.pack())

    def set_mode(self, mode):
        if mode in self._modes.keys():
            tx = struct.pack('HBBBB', 0x04C0, 0x01, self._modes[mode], 0x50, 0x01)
            self._shutter.write(tx)
        else:
            print("Error, command not executed")
        #TODO:ask Rik how to handle this error

    def set_cycle(self, on, off, number):

        tx = struct.pack('<HHBBBBLLL', 0x04C3, 0x000E, 0xD0, 0x01, 0x01, 0x00, on, off, number)
        self._shutter.write(tx)

    def set_enable(self, state):
        if state:
            parameter = 0x01        # Open
        if not state:
            parameter = 0x02        # Closed
        tx = struct.pack('HBBBB', 0x04CB, 0x01, parameter, 0x50, 0x01)
        self._shutter.write(tx)
        #TODO: write else condition to avoid wrong parameter value

##### TELEMETRY
#     Apart from the last two categories (status update messages and error messages), in general
# the message exchanges follow the SET ‐> REQUEST ‐> GET pattern, i.e. for most commands a
# trio of messages are defined. The SET part of the trio is used by the host (or, sometimes in
# card‐slot systems the motherboard) to set some parameter or other. If then the host
# requires some information from the sub‐module, then it may send a REQUEST for this
# information, and the sub‐module responds with the GET part of the command. Obviously,
# there are cases when this general scheme does not apply and some part of this message trio
# is not defined. For consistency, in the description of the messages this SET‐>REQUEST‐>GET
# scheme will be used throughout.

# FIXME:
#   The shutter gets stuck if I follow the documentation from the Manual: Note that,
#   as the scheme suggests, this is a master‐slave type of system, so sub‐modules

    def get_enable(self):
        tx = struct.pack('HBBBB', 0x04CB, 0x01, 0x00, 0x50, 0x01)    # requests enable state
        self._shutter.write(tx)
        rx =  struct.pack('HBBBB', 0x04CC, 0x01, 0x01, 0x50, 0x01)   # gets enable state
        self._shutter.write(rx)

        time.sleep(50.0 / 1000)                                 #wait time needed between write and read

        _enable = bytes(self._shutter.read(6), "latin -1")         # gets the 6 read bytes
        return _enable[3]

    def get_mode(self):
        tx = struct.pack('HBBBB', 0x04C1, 0x01, 0x00, 0x50, 0x01)    # requests enable state
        self._shutter.write(tx)
        rx = struct.pack('HBBBB', 0x04C2, 0x01, 0x01, 0x50, 0x01)   # gets enable state
        self._shutter.write(rx)

        time.sleep(50.0 / 1000)                                 #wait time needed between write and read

        _mode = bytes(self._shutter.read(6), "latin -1")         # gets the 6 read bytes

        if _mode[3] in self._modes.values():                    # byte 4 gets the mode status
            mode = _mode[3]
        else:
            mode = None
        return mode
        #FIXME: put a case in which _mode is empty to prevent errors

    def get_cycle(self):
        tx = struct.pack('HBBBB',0x04C4,0x01,0x00,0x50,0x01)    # requests enable state
        self._shutter.write(tx)
        rx =  struct.pack('HBBBB',0x04C5,0x01,0x01,0x50,0x01)   # gets enable state
        self._shutter.write(rx)

        time.sleep(50.0 / 1000)                                 #wait time needed between write and read
        # gets 20 bytes
        _cycle = bytes(self._shutter.read(20), "latin -1")       # gets the 20 read bytes

        # gets the 3 parameters coded in 4 bytes (long) little endian each
        on =  struct.unpack('<L',_cycle[8:12])
        off = struct.unpack('<L',_cycle[12:16])
        number = struct.unpack('<L',_cycle[16:])

        return {"Ontime": on[0],"Offtime": off[0], "Number of cycles": number[0]}
