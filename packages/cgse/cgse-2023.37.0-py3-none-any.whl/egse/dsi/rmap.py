"""
This module provides Python wrapper functions to (most of) the library functions from the C library ESL-RMAP.c.

We use one single Exception specific for these wrapper functions. An RMAPError is thrown whenever the C function
returns an error from which we can not recover. This allows to cascade the python functions in a try: except: clause
making the code much more readable.

The C code depends heavily on a C structure which we had to re-define using the Structure class provided by ctypes.

"""

import ctypes
import logging
import struct
from contextlib import contextmanager
from ctypes import POINTER
from ctypes import Structure
from ctypes import c_char_p
from ctypes import c_int
from ctypes import c_ubyte
from ctypes import c_uint
from ctypes import c_ulonglong
from ctypes import c_void_p as c_int_p
from ctypes import cdll
from pathlib import Path
from typing import Tuple

import egse.dsi.constants as constants
from egse.config import find_file
from egse.dsi.constants import esl_rmap_error_codes
from egse.dsi.esl import esl_flush
from egse.dsi.esl import esl_get_product_string
from egse.dsi.esl import esl_p
from egse.dsi.esl import esl_read_packet
from egse.dsi.esl import esl_write_packet
from egse.dsi.esl import pretty_print_packet
from egse.settings import Settings
from egse.system import get_os_name
from egse.system import get_os_version

logger = logging.getLogger(__name__)

dsi_settings = Settings.load("DSI")

# Maintain a transmit and receive buffer

rxbuf = ctypes.create_string_buffer(dsi_settings.RX_BUFFER_LENGTH)
txbuf = ctypes.create_string_buffer(dsi_settings.TX_BUFFER_LENGTH)

# Initialize the status variable which is a c pointer that is set by the library routines to
# pass a status.

status = c_int(0)
status_p = ctypes.pointer(status)

# NOTE: These memory areas are currently equal for N-FEE and F-FEE. Don't know if this will
#       change in the future.

CRITICAL_AREA_START = 0x0000_0000
CRITICAL_AREA_END = 0x0000_00FC
GENERAL_AREA_START = 0x0000_0100
GENERAL_AREA_END = 0x0000_06FC
HK_AREA_START = 0x0000_0700
HK_AREA_END = 0x0000_07FC
WINDOWING_AREA_START = 0x0080_0000
WINDOWING_AREA_END = 0x00FF_FFFC


class ESL_RMAP(Structure):
    _fields_ = [
        ("spw_device",                esl_p),
        ("target_key",                c_ubyte),
        ("target_logical_address",    c_ubyte),
        ("target_spw_address",        c_ubyte * 12),
        ("target_spw_address_len",    c_int),
        ("reply_spw_address",         c_ubyte * 12),
        ("reply_spw_address_len",     c_int),
        ("initiator_logical_address", c_ubyte),
        ("transaction_identifier",    c_uint),
        ("ESL_RMAP_error",            c_int)
    ]


rmap_p = POINTER(ESL_RMAP)


class RMAPError(Exception):
    pass


# Depending on the OS, and the OS version, we load the dynamic library from a specific location
# Only some OS/OS-version combinations are supported.

if get_os_name() == 'macos':
    in_dir = 'lib/macOS'
elif get_os_name() == 'debian':
    in_dir = 'lib/Debian'
elif get_os_name() == 'centos':
    in_dir = 'lib/CentOS-7' if get_os_version().startswith('7') else 'lib/CentOS-8'
elif get_os_name() == 'ubuntu':
    in_dir = 'lib/Ubuntu-20' if get_os_version().startswith('20') else 'lib/Linux'
else:
    in_dir = None

dylib_filename = Path(dsi_settings.RMAP_DYLIB_FILENAME)

logger.debug(f"Locating shared library {dylib_filename} in dir '{in_dir}'")

dylib_filename = find_file(dylib_filename, in_dir=in_dir)

logger.debug(f"Loading shared library: {dylib_filename}")

if not dylib_filename:
    raise FileNotFoundError(f"Could not find dynamic library: {dylib_filename}")

librmap = cdll.LoadLibrary(dylib_filename)

# Mapping of functions.
# Please note that when there is no need to wrap the C library function, we do not take the burden

librmap_open                                = librmap.ESL_RMAP_open
librmap_open.argtypes                       = [esl_p]
librmap_open.restype                        = rmap_p

librmap_set_verbosity                       = librmap.ESL_RMAP_set_verbosity
librmap_set_verbosity.argtypes              = [c_int]

librmap_get_target_key                      = librmap.ESL_RMAP_get_target_key
librmap_get_target_key.argtypes             = [rmap_p]
librmap_get_target_key.restype              = c_ubyte

librmap_set_target_key                      = librmap.ESL_RMAP_set_target_key
librmap_set_target_key.argtypes             = [rmap_p, c_ubyte]

librmap_get_target_logical_address          = librmap.ESL_RMAP_get_target_logical_address
librmap_get_target_logical_address.argtypes = [rmap_p]
librmap_get_target_logical_address.restype  = c_ubyte

librmap_set_target_logical_address          = librmap.ESL_RMAP_set_target_logical_address
librmap_set_target_logical_address.argtypes = [rmap_p, c_ubyte]

librmap_set_target_spw_address              = librmap.ESL_RMAP_set_target_spw_address
librmap_set_target_spw_address.argtypes     = [rmap_p, c_char_p, c_int]

librmap_get_initiator_logical_address          = librmap.ESL_RMAP_get_initiator_logical_address
librmap_get_initiator_logical_address.argtypes = [rmap_p]
librmap_get_initiator_logical_address.restype  = c_ubyte

librmap_set_initiator_logical_address          = librmap.ESL_RMAP_set_initiator_logical_address
librmap_set_initiator_logical_address.argtypes = [rmap_p, c_ubyte]

librmap_crc_check                           = librmap.RMAP_crc_check
librmap_crc_check.argtypes                  = [c_char_p, c_uint, c_uint]
librmap_crc_check.restype                   = c_uint

librmap_read                                = librmap.ESL_RMAP_read
librmap_read.argtypes                       = [rmap_p, c_ulonglong, c_char_p, c_uint, c_int_p]
librmap_read.restype                        = c_int

librmap_read_TO                             = librmap.ESL_RMAP_read_TO
librmap_read_TO.argtypes                    = [rmap_p, c_ulonglong, c_char_p, c_uint, c_int_p, c_int]
librmap_read_TO.restype                     = c_int

librmap_write                                = librmap.ESL_RMAP_write
librmap_write.argtypes                       = [rmap_p, c_ulonglong, c_char_p, c_uint, c_int_p]
librmap_write.restype                        = c_int


@contextmanager
def rmap_connection(esl_link):
    """
    Context manager that opens an RMAP connection on the EtherSpaceLink ESL.

    Args:
        esl_link (ESL): the ESL structure that defines the connection to the DSI

    Returns:
        an RMAP link connection
    """
    yield rmap_open_connection(esl_link)


def rmap_open_connection(esl_link):

    logger.info(f"Open and setup RMAP connection to {esl_get_product_string(esl_link)}")

    rmap_link = librmap_open(esl_link)
    if not rmap_link:
        raise RMAPError(f"Couldn't open RMAP connection to {esl_get_product_string(esl_link)}")

    rmap_set_verbosity(1)     # 1=normal; 5 or 15 for lots of debugging

    logger.info("RMAP connection opened successfully.")

    return rmap_link


def rmap_configure(rmap_link: ESL_RMAP, initiator_logical_address,
                   target_key=constants.RMAP_TARGET_KEY,
                   target_logical_address=constants.RMAP_TARGET_LOGICAL_ADDRESS_DEFAULT):
    """
    Configure the RMAP EtherSpaceWire link.

    Args:
        rmap_link: the RMAP link connection
        initiator_logical_address: logical address of the SpaceWire node that starts the transaction
        target_key: the key field used for command authorisation
        target_logical_address: logical address of the target node (default: 0xFE)

    Returns:
        Nothing

    """
    rmap_set_initiator_logical_address(rmap_link, initiator_logical_address)
    rmap_set_target_key(rmap_link, target_key)
    rmap_set_target_logical_address(rmap_link, target_logical_address)
    rmap_set_target_spw_address(rmap_link, b'\x00', 0)


# FIXME: Is this code rmap_read() still needed? We now have rmap_read_request()
#        which handles everything this code does, except it doesn't use the ESL_RMAP
#        dynamic library!

def rmap_read(rmap_link: ESL_RMAP, address: int, length: int, timeout: int = 1000):
    """
    Read `length` bytes from the remote memory starting at `address`. If there is no reply
    after the given `timeout`, TODO: WHAT WILL HAPPEN THEN?

    .. note:: We are using the global ``rxbuf`` read buffer here.
        The content of the buffer will be overwritten by the RMAP read request.

    Args:
        rmap_link: the RMAP link connection
        address: the start address (32-bit aligned) in the remote memory
        length: the number of bytes to read from the remote memory
        timeout: timeout in milli-seconds

    Returns:
        the buffer containing the data read from the remote memory.

    """

    data_length = librmap_read_TO(rmap_link, address, rxbuf, length, status_p, timeout)

    # If data_length < 0 it can have the following values:
    # -1 = status was != 0 indicating a read error, the packet was eaten...discarded?
    # -4 = wrong TLA field in header
    # -5 = wrong TID field in header

    # FIXME: Think about if we should raise an RMAPError here instead of returning None when result is negative.
    #        I would go for an Exception, since we loose the information on the error anyway as code information (
    #        None is returned, not data_length), and now the caller must check the return code from this read command.

    if data_length < 0:
        logger.warning(
            f"Couldn't read data within timeout of {timeout} ms, "
            f"ESL RMAP Error Code = {esl_rmap_error_codes[rmap_link.contents.ESL_RMAP_error]} "
            f"[{rmap_link.contents.ESL_RMAP_error}]"
        )
        return None
    else:
        return rxbuf[:data_length]


def rmap_read_request(rmap_link: ESL_RMAP, address: int, length: int, timeout: int = 1000) -> Tuple[int, bytes]:
    """
    Read `length` bytes from the remote memory starting at `address`.

    .. todo:: the timeout parameter is currently not implemented

    Args:
        rmap_link: the RMAP link connection
        address: the start address (32-bit aligned) in the remote memory
        length: the number of bytes to read from the remote memory
        timeout: timeout in milli-seconds

    Returns:
        A tuple containing the terminator value and the RMAP Reply packet with the data read from the remote memory.

    """
    buffer = create_rmap_read_request_packet(rmap_link, address, length)

    logger.log(5, "Pretty Print Read Request Packet:\n" + pretty_print_packet(buffer))

    result = esl_write_packet(rmap_link.contents.spw_device, buffer, len(buffer), constants.ESL_EOP)
    if result:
        raise RMAPError(
            f"Couldn't send data within timeout of {timeout} ms, "
            f"ESL RMAP Error Code = {esl_rmap_error_codes[rmap_link.contents.ESL_RMAP_error]} ["
            f"{rmap_link.contents.ESL_RMAP_error}]")

    result = esl_flush(rmap_link.contents.spw_device)
    if result:
        raise RMAPError(
            f"Couldn't send data or clear buffers, "
            f"ESL RMAP Error Code = {esl_rmap_error_codes[rmap_link.contents.ESL_RMAP_error]} ["
            f"{rmap_link.contents.ESL_RMAP_error}]")

    # Read the read request reply

    terminator, rx_buffer = esl_read_packet(rmap_link.contents.spw_device)

    logger.log(5, "Pretty Print Read Request Reply Packet:\n" + pretty_print_packet(rx_buffer))

    return terminator, rx_buffer


def rmap_write_request(rmap_link: ESL_RMAP,
                       address: int, data: bytes, length: int = 4, timeout: int = 1000) -> Tuple[int, bytes]:
    """
    Sends an RMAP write command over the SpaceWire link.

    Based on the address this function will decided to send a verified or unverified write request.

    .. todo:: the timeout parameter is currently not implemented

    Args:
        rmap_link (ESL_RMAP): the RMAP link connection
        address: the starting memory address to which the data from buffer will be written
        data: the data that will be written into the targets memory
        length: the number of bytes to write (the buffer maybe longer) [default=4]
        timeout: timeout in milliseconds [default=1000]

    Returns:
        return_code: zero (0) on success.

    Raises:
        RMAPError: when data can not be written on the target.

    """

    if CRITICAL_AREA_START <= address <= CRITICAL_AREA_END:
        buffer = create_rmap_verified_write_packet(rmap_link, address, data)
    else:
        buffer = create_rmap_unverified_write_packet(rmap_link, address, data, length)

    logger.log(5, "Pretty Print Write Request Packet:\n" + pretty_print_packet(buffer))

    result = esl_write_packet(rmap_link.contents.spw_device, buffer, len(buffer), constants.ESL_EOP)
    if result:
        raise RMAPError(
            f"Couldn't send data within timeout of {timeout} ms, "
            f"ESL RMAP Error Code = {esl_rmap_error_codes[rmap_link.contents.ESL_RMAP_error]} ["
            f"{rmap_link.contents.ESL_RMAP_error}]")

    result = esl_flush(rmap_link.contents.spw_device)
    if result:
        raise RMAPError(
            f"Couldn't send data or clear buffers, "
            f"ESL RMAP Error Code = {esl_rmap_error_codes[rmap_link.contents.ESL_RMAP_error]} ["
            f"{rmap_link.contents.ESL_RMAP_error}]")

    # Read the write reply

    terminator, rx_buffer = esl_read_packet(rmap_link.contents.spw_device)

    logger.log(5, "Pretty Print Write Request Reply Packet:\n" + pretty_print_packet(rx_buffer))

    return terminator, rx_buffer


def create_rmap_read_request_packet(rmap_link: ESL_RMAP, address: int, length: int) -> ctypes.Array:
    """
    Creates an RMAP Read Request SpaceWire packet.

    The read request is an RMAP command that read a number of bytes from the FEE register memory.

    The function returns a ``ctypes`` character array (which is basically a bytes array) that
    can be passed into the EtherSpaceLink library function ``esl_write_packet()``.

    Address shall be within the 0x0000_0000 and 0x00FF_FFFC. The memory map (register) is divided
    in the following areas:

        0x0000_0000 - 0x0000_00FC   Critical Configuration Area (verified write)
        0x0000_0100 - 0x0000_06FC   General Configuration Area (unverified write)
        0x0000_0700 - 0x0000_07FC   Housekeeping area
        0x0000_0800 - 0x007F_FFFC   Not Supported
        0x0080_0000 - 0x00FF_FFFC   Windowing Area (unverified write)
        0x0010_0000 - 0xFFFF_FFFC   Not Supported

    All read requests to the critical area shall have a fixed data length of 4 bytes.
    All read requests to a general area shall have a maximum data length of 256 bytes.
    All read requests to the housekeeping area shall have a maximum data length of 256 bytes.
    All read requests to the windowing area shall have a maximum data length of 4096 bytes.

    Args:
        rmap_link (ESL_RMAP): the RMAP link connection
        address (int): the FEE register memory address
        length (int): the data length

    Returns:
        a bytes array containing the full RMAP Read Request packet.
    """

    check_address_and_data_length(address, length)

    buf = ctypes.create_string_buffer(16)

    # The transaction identifier shall be incremented for each read request

    tid = update_transaction_identifier(rmap_link)

    # NOTE: The first bytes would each carry the target SpW address or a destination port,
    #       but this is not used for point-to-point connections, so we're safe.

    buf[0] = 0x51  # Target N-FEE or F-FEE
    buf[1] = 0x01  # RMAP Protocol ID
    buf[2] = 0x4C  # Instruction: 0b1001100, RMAP Request, Read, Incrementing address, reply address = 0
    buf[3] = 0xD1  # Destination Key
    buf[4] = 0x50  # Initiator is always the DPU
    buf[5] = (tid >> 8) & 0xFF        # MSB of the Transition ID
    buf[6] = tid & 0xFF               # LSB of the Transition ID
    buf[7] = 0x00                     # Extended address is not used
    buf[8] = (address >> 24) & 0xFF   # address (MSB)
    buf[9] = (address >> 16) & 0xFF   # address
    buf[10] = (address >> 8) & 0xFF   # address
    buf[11] = address & 0xFF          # address (LSB)
    buf[12] = (length >> 16) & 0xFF   # data length (MSB)
    buf[13] = (length >> 8) & 0xFF    # data length
    buf[14] = length & 0xFF           # data length (LSB)
    buf[15] = rmap_crc_check(buf, 0, 15) & 0xFF
    return buf


def create_rmap_write_reply_packet(rmap_link: ESL_RMAP) -> ctypes.Array:
    pass


def create_rmap_read_reply_packet(rmap_link: ESL_RMAP, instruction_field: int, tid: int, status: int,
                                  buffer: bytes, buffer_length: int) -> ctypes.Array:
    """
    Creates an RMAP Reply to a RMAP Read Request packet.

    The function returns a ``ctypes`` character array (which is basically a bytes array) that
    can be passed into the EtherSpaceLink library function ``esl_write_packet()``.

    Args:
        rmap_link (ESL_RMAP): the RMAP link connection
        instruction_field (int): the instruction field of the RMAP read request packet
        tid (int): the transaction identifier of the read request packet
        status (int): shall be 0 if the read request was successful, contain an error code otherwise.
        TODO: which error code?
        buffer (bytes): the data that was read as indicated by the read request
        buffer_length (int): the data length

    Returns:
        packet: a ctypes Array containing the full RMAP Reply packet.
    """

    buf = ctypes.create_string_buffer(12 + buffer_length + 1)

    buf[0] = 0x50  # Initiator address N-DPU or F-DPU
    buf[1] = 0x01  # RMAP Protocol ID
    buf[2] = instruction_field & 0x3F  # Clear the command bit as this is a reply
    buf[3] = status & 0xFF  # Status field: 0 on success
    buf[4] = 0x51  # Target address is always the N-FEE or F-FEE
    buf[5] = (tid >> 8) & 0xFF        # MSB of the Transition ID
    buf[6] = tid & 0xFF               # LSB of the Transition ID
    buf[7] = 0x00                     # Reserved
    buf[8] = (buffer_length >> 16) & 0xFF    # data length (MSB)
    buf[9] = (buffer_length >> 8) & 0xFF     # data length
    buf[10] = buffer_length & 0xFF           # data length (LSB)
    buf[11] = rmap_crc_check(buf, 0, 11) & 0xFF  # Header CRC

    # Note that we assume here that len(buffer) == buffer_length.

    if len(buffer) != buffer_length:
        logger.warning(
            f"While creating an RMAP read reply packet, the length of the buffer ({len(buffer)}) not equals "
            f"the buffer_length ({buffer_length})"
        )

    for idx, value in enumerate(buffer):
        buf[12+idx] = value

    buf[12 + buffer_length] = rmap_crc_check(buf, 12, 12 + buffer_length) & 0xFF  # data CRC

    return buf


def create_rmap_verified_write_packet(rmap_link: ESL_RMAP, address: int, data: bytes) -> ctypes.Array:
    """
    Create an RMAP packet for a verified write request on the FEE. The length of the data is by convention always 4
    bytes and therefore not passed as an argument.

    Args:
        rmap_link: the RMAP link structure
        address: the start memory address on the FEE register map
        data: the data to be written in the register map at address [4 bytes]

    Returns:
        packet: a bytes object containing the SpaceWire packet.
    """

    if len(data) < 4:
        raise ValueError(f"The data argument should be at least 4 bytes, but it is only {len(data)} bytes.")

    if address > CRITICAL_AREA_END:
        raise ValueError(f"The address range for critical configuration is [0x00 - 0xFC].")

    tid = update_transaction_identifier(rmap_link)

    # Buffer length is fixed at 24 bytes since the data length is fixed at 4 bytes (32 bit addressing)

    buf = ctypes.create_string_buffer(21)
    offset = 0

    # The values below are taken from the PLATO N-FEE to N-DPU Interface Requirements Document [PLATO-DLR-PL-ICD-0010]

    buf[offset+0] = 0x51  # Logical Address
    buf[offset+1] = 0x01  # Protocol ID
    buf[offset+2] = 0x7C  # Instruction
    buf[offset+3] = 0xD1  # Key
    buf[offset+4] = 0x50  # Initiator Address
    buf[offset+5] = (tid >> 8) & 0xFF        # MSB of the Transition ID
    buf[offset+6] = tid & 0xFF               # LSB of the Transition ID
    buf[offset+7] = 0x00                     # Extended address
    buf[offset+8] = (address >> 24) & 0xFF   # address (MSB)
    buf[offset+9] = (address >> 16) & 0xFF   # address
    buf[offset+10] = (address >> 8) & 0xFF   # address
    buf[offset+11] = address & 0xFF          # address (LSB)
    buf[offset+12] = 0x00                    # data length (MSB)
    buf[offset+13] = 0x00                    # data length
    buf[offset+14] = 0x04                    # data length (LSB)
    buf[offset+15] = rmap_crc_check(buf, 0, 15) & 0xFF  # header CRC
    buf[offset+16] = data[0]
    buf[offset+17] = data[1]
    buf[offset+18] = data[2]
    buf[offset+19] = data[3]
    buf[offset+20] = rmap_crc_check(buf, 16, 4) & 0xFF  # data CRC

    return buf


def create_rmap_unverified_write_packet(rmap_link: ESL_RMAP, address: int, data: bytes, length: int) -> ctypes.Array:
    """
    Create an RMAP packet for a unverified write request on the FEE.

    Args:
        rmap_link: the RMAP link structure
        address: the start memory address on the FEE register map
        data: the data to be written in the register map at address
        length: the length of the data

    Returns:
        packet: a bytes object containing the SpaceWire packet.
    """

    # We can only handle data for which the length >= the given length argument.

    if len(data) < length:
        raise ValueError(
            f"The length of the data argument ({len(data)}) is smaller than "
            f"the given length argument ({length})."
        )

    if len(data) > length:
        logger.warning(
            f"The length of the data argument ({len(data)}) is larger than "
            f"the given length argument ({length}). The data will be truncated "
            f"when copied into the packet."
        )

    if address <= CRITICAL_AREA_END:
        raise ValueError(f"The given address (0x{address:08X}) is in the range for critical configuration is [0x00 - "
                         f"0xFC]. Use the verified write function for this.")

    tid = update_transaction_identifier(rmap_link)

    # Buffer length is fixed at 24 bytes since the data length is fixed at 4 bytes (32 bit addressing)

    buf = ctypes.create_string_buffer(16 + length + 1)
    offset = 0

    buf[offset+0] = 0x51  # Logical Address
    buf[offset+1] = 0x01  # Protocol ID
    buf[offset+2] = 0x6C  # Instruction
    buf[offset+3] = 0xD1  # Key
    buf[offset+4] = 0x50  # Initiator Address
    buf[offset+5] = (tid >> 8) & 0xFF        # MSB of the Transition ID
    buf[offset+6] = tid & 0xFF               # LSB of the Transition ID
    buf[offset+7] = 0x00                     # Extended address
    buf[offset+8] = (address >> 24) & 0xFF   # address (MSB)
    buf[offset+9] = (address >> 16) & 0xFF   # address
    buf[offset+10] = (address >> 8) & 0xFF   # address
    buf[offset+11] = address & 0xFF          # address (LSB)
    buf[offset+12] = (length >> 16) & 0xFF   # data length (MSB)
    buf[offset+13] = (length >> 8) & 0xFF    # data length
    buf[offset+14] = length & 0xFF           # data length (LSB)
    buf[offset+15] = rmap_crc_check(buf, 0, 15) & 0xFF  # header CRC

    offset = offset + 16

    for idx, value in enumerate(data):
        buf[offset+idx] = value

    buf[offset + length] = rmap_crc_check(buf, offset, length) & 0xFF  # data CRC

    return buf


def rmap_set_verbosity(flags):
    """
    Set vebosity of the RMAP API.

    Report errors by default:

    * bitval  1 : output textual error messages
    * bitval  2 : output SpaceWire read/write packet tracing
    * bitval  4 : output API function call tracing
    * bitval  8 : output API parameter  / data packet tracing
    * bitval 16 : output API data packet tracing

    Args:
        flags (int): verbosy level

    Returns:
        None

    """
    librmap_set_verbosity(flags)


def rmap_get_target_key(rmap_link):
    logger.debug("Calling rmap_get_target_key(rmap_link)")
    return librmap_get_target_key(rmap_link)


def rmap_set_target_key(rmap_link, key):
    logger.debug(f"Calling rmap_set_target_key({key})")
    librmap_set_target_key(rmap_link, key)


def rmap_get_target_logical_address(rmap_link):
    logger.debug("Calling rmap_get_target_logical_address(rmap_link)")
    return librmap_get_target_logical_address(rmap_link)


def rmap_set_target_logical_address(rmap_link, address):
    logger.debug(f"Calling rmap_set_target_logical_address(rmap_link, 0x{address:02X})")
    librmap_set_target_logical_address(rmap_link, address)


def rmap_set_target_spw_address(rmap_link, spw_address, spw_address_length):
    logger.debug(f"Calling rmap_set_target_spw_address(rmap_link, spw_address, {spw_address_length})")
    librmap_set_target_spw_address(rmap_link, spw_address, spw_address_length)


def rmap_get_initiator_logical_address(rmap_link):
    # logger.debug("Calling rmap_get_initiator_logical_address(rmap_link)")
    return librmap_get_initiator_logical_address(rmap_link)


def rmap_set_initiator_logical_address(rmap_link, address):
    # logger.debug(f"Calling rmap_set_initiator_logical_address(rmap_link, 0x{address:02X})")
    librmap_set_initiator_logical_address(rmap_link, address)


def rmap_crc_check(data, start, length):
    # logger.debug(f"Calling rmap_crc_check(data, {start}, {length})")
    return librmap_crc_check(data, start, length)


class CheckError(RMAPError):
    """
    Raised when a check fails and you want to pass a status values along with the message.
    """

    def __init__(self, message, status):
        self.message = message
        self.status  = status


def is_rmap(rx_buffer):
    return get_protocol_id(rx_buffer) == constants.RMAP_PROTOCOL_ID


# Functions to interpret the Instrument Field

def is_reserved(instruction):
    """The reserved bit of the 2-bit packet type field from the instruction field.

    For PLATO this bit shall be zero as the 0b10 and 0b11 packet field values are reserved.

    Returns:
        bit value: 1 or 0.
    """
    return (instruction & 0b10000000) >> 7


def is_command(instruction):
    """Returns True if the RMAP packet is a command packet."""
    return (instruction & 0b01000000) >> 6


def is_reply(instruction):
    """Returns True if the RMAP packet is a reply to a previous command packet."""
    return not is_command(instruction)


def is_write(instruction):
    """Returns True if the RMAP packet is a write request command packet."""
    return (instruction & 0b00100000) >> 5


def is_read(instruction):
    """Returns True if the RMAP packet is a read request command packet."""
    return not is_write(instruction)


def is_verify(instruction):
    """Returns True if the RMAP packet needs to do a verify before write."""
    return (instruction & 0b00010000) >> 4


def is_reply_required(instruction):
    """Returns True if the reply bit is set in the instruction field.

    Args:
        instruction (int): the instruction field of an RMAP packet

    .. note:: the name of this function might be confusing.

        This function does **not** test if the packet is a reply packet, but it checks
        if the command requests a reply from the target. If you need to test if the
        packet is a command or a reply, use the is_command() or is_reply() function.

    """
    return (instruction & 0b00001000) >> 3


def is_increment(instruction):
    """Returns True if the data is written to sequential memory addresses."""
    return (instruction & 0b00000100) >> 2


def reply_address_length(instruction):
    """Returns the content of the replay address length field.

    The size of the replay address field is then decoded from the following table:

        Address Field Length  |  Size of Address Field
        ----------------------+-----------------------
             0b00             |      0 bytes
             0b01             |      4 bytes
             0b10             |      8 bytes
             0b11             |     12 bytes

    """
    return (instruction & 0b00000011) << 2

# Helper Functions ---------------------------------------------------------------------------------


def get_protocol_id(rx_buffer):
    return rx_buffer[1]


def get_reply_address_field_length(rx_buffer) -> int:
    """Returns the size of reply address field.

    This function returns the actual size of the reply address field. It doesn't return the content of the
    reply address length field. If you need that information, use the reply_address_length() function that work on
    the instruction field.

    Returns:
         length: the size of the reply address field.
    """
    instruction = get_instruction_field(rx_buffer)
    return reply_address_length(instruction) * 4


def get_data(rxbuf) -> bytes:
    """Return the data from the RMAP packet.

    Raises:
        ValueError: if there is no data section in the packet (TODO: not yet implemented)
    """
    instruction_field = get_instruction_field(rxbuf)
    address_length = get_reply_address_field_length(rxbuf)
    data_length = get_data_length(rxbuf)

    offset = 12 if is_read(instruction_field) else 16

    return rxbuf[offset + address_length:offset + address_length + data_length]


def check_data_crc(rxbuf):
    instruction_field = get_instruction_field(rxbuf)
    address_length = get_reply_address_field_length(rxbuf)
    data_length = get_data_length(rxbuf)

    offset = 12 if is_read(instruction_field) else 16
    idx = offset + address_length

    d_crc = rxbuf[idx + data_length]
    c_crc = rmap_crc_check(rxbuf, idx, data_length) & 0xFF
    if d_crc != c_crc:
        raise CheckError(
            f"Data CRC doesn't match calculated CRC, d_crc=0x{d_crc:02X} & c_crc=0x{c_crc:02X}",
            constants.RMAP_GENERAL_ERROR
        )


def check_header_crc(rxbuf):
    instruction_field = get_instruction_field(rxbuf)
    if is_command(instruction_field):
        offset = 15
    elif is_write(instruction_field):
        offset = 7
    else:
        offset = 11

    idx = offset + get_reply_address_field_length(rxbuf)
    h_crc = rxbuf[idx]
    c_crc = rmap_crc_check(rxbuf, 0, idx)
    if h_crc != c_crc:
        raise CheckError("Header CRC doesn't match calculated CRC, h_crc=0x{:X} & c_crc=0x{:X}"
                             .format(h_crc, c_crc), constants.RMAP_GENERAL_ERROR)


def get_data_length(rxbuf) -> int:
    """Returns the length of the data in bytes.

    Raises:
        TypeError: when this method is used on a Write Request Reply packet (which has no
            data length).
    """
    instruction_field = get_instruction_field(rxbuf)

    if not is_command(instruction_field) and is_write(instruction_field):
        raise TypeError("There is no data length field for Write Request Reply packets, "
                        "asking for the data length is an invalid operation.")

    offset = 12 if is_command(instruction_field) else 8
    idx = offset + get_reply_address_field_length(rxbuf)

    # We could use two alternative decoding methods here:
    #   int.from_bytes(rxbuf[idx:idx+3], byteorder='big')    (timeit=1.166s)
    #   struct.unpack('>L', b'\x00' + rxbuf[idx:idx+3])[0]   (timeit=0.670s)
    data_length = struct.unpack('>L', b'\x00' + rxbuf[idx:idx + 3])[0]
    return data_length


def get_address(rxbuf) -> int:
    """Returns the address field (including the extended address field if the address is 40-bits).

    Raises:
        TypeError: when this method is used on a Reply packet (which has no address field).
    """
    instruction_field = get_instruction_field(rxbuf)

    if not is_command(instruction_field):
        raise TypeError("There is no address field for Reply packets, asking for the address is "
                        "an invalid operation.")

    idx = 7 + get_reply_address_field_length(rxbuf)
    extended_address = rxbuf[idx]
    idx += 1
    address = struct.unpack('>L', rxbuf[idx:idx + 4])[0]
    if extended_address:
        address = address + (extended_address << 32)
    return address


def get_transaction_identifier(rxbuf):
    idx = 5 + get_reply_address_field_length(rxbuf)
    tid = struct.unpack('>h', rxbuf[idx:idx + 2])[0]
    return tid


def get_initiator_logical_address(rxbuf):
    idx = 4 + get_reply_address_field_length(rxbuf)
    ila_rxbuf = rxbuf[idx]
    return ila_rxbuf


def check_initiator_logical_address(rxbuf, ila):
    ila_rxbuf = get_initiator_logical_address(rxbuf)
    if ila != ila_rxbuf:
        raise CheckError(
            f"Initiator Logical Address doesn't match, ila=0x{ila:02X} & ila_rxbuf=0x{ila_rxbuf:02X}",
            constants.RMAP_GENERAL_ERROR
        )


def check_key(rmap_link, rxbuf):
    idx = 3
    key = rmap_get_target_key(rmap_link)
    key_rxbuf = rxbuf[idx]
    if key != key_rxbuf:
        raise CheckError(
            f"Key doesn't match, key={key} & key_rxbuf={key_rxbuf}", constants.RMAP_INVALID_KEY
        )


def get_instruction_field(rxbuf):
    idx = 2
    return rxbuf[idx]


def check_instruction(rx_buffer) -> None:
    """
    Check the instruction field for inconsistencies and report the values in the logger at DEBUG level.


    Args:
        rx_buffer (bytes): The read buffer which contains the SpW packet

    Raises:
        CheckError: when the reserved bit is not zero,

    Returns:
        None.
    """
    # The Instruction Field is the third byte (base=0) of the packet buffer.
    # Description of the Instruction Field can be found in ECSS-E-ST-50-52C.

    instruction = get_instruction_field(rx_buffer)
    if is_reserved(instruction):
        raise CheckError(
            f"Instruction field [{instruction:08b}] reserved bit is not 0x00",
            constants.RMAP_NOT_IMPLEMENTED_AUTHORISED
        )

    msg = "RMAP Instruction Field: "
    msg += "Command; " if is_command(instruction) else "Reply; "
    msg += "write; " if is_write(instruction) else "read; "
    msg += "verify; " if is_verify(instruction) else "don't verify; "
    msg += "reply; " if is_reply_required(instruction) else "don't reply; "
    msg += "increment; " if is_increment(instruction) else "no increment; "

    logger.debug(msg)
    if reply_address_length(instruction):
        logger.debug(f"Reply address length = {reply_address_length(instruction)} bytes.")


def check_protocol_id(rxbuf):
    idx = 1
    protocol_id = rxbuf[idx]
    if protocol_id != constants.RMAP_PROTOCOL_ID:
        raise CheckError(
            f"Protocol id is not the expected value {protocol_id}, expected {constants.RMAP_PROTOCOL_ID}",
            constants.RMAP_GENERAL_ERROR)


def get_target_logical_address(rmap_link: ESL_RMAP, rxbuf: bytes) -> int:
    tla_idx = 0
    tla_rxbuf = rxbuf[tla_idx]
    return tla_rxbuf


def check_target_logical_address(rmap_link, rxbuf, tla):
    tla_rxbuf = get_target_logical_address(rmap_link, rxbuf)
    if tla != tla_rxbuf:
        raise CheckError(
            f"Target Logical Address doesn't match, tla=0x{tla:02X} & rxbuf[0]=0x{tla_rxbuf:02X}",
            constants.RMAP_GENERAL_ERROR
        )


def update_transaction_identifier(rmap_link) -> int:
    """
    Updates the transaction identifier and returns the new value.

    Args:
        rmap_link (ESL_RMAP): the RMAP link connection

    Returns:
        the updated transaction identifier (int).
    """
    tid = rmap_link.contents.transaction_identifier
    tid = (tid + 1) & 0xFFFF
    rmap_link.contents.transaction_identifier = tid
    return tid


def check_address_and_data_length(address: int, length: int) -> None:
    """
    Checks the address and length in the range of memory areas used by the FEE.

    The ranges are taken from the PLATO-DLR-PL-ICD-0010 N-FEE to N-DPU IRD.

    Args:
        address (int): the memory address of the FEE Register
        length (int): the number of bytes requested

    Raises:
        RMAPError: when address + length fall outside any specified area.
    """

    # All these restrictions have been relaxed on the N-FEE.
    # We are returning here immediately instead of removing or commenting out the code.
    # These reason is that we can then bring back restriction easier and gradually.

    return

    if length % 4:
        raise RMAPError("The requested data length shall be a multiple of 4 bytes.", address, length)

    if address % 4:
        raise RMAPError("The address shall be a multiple of 4 bytes.", address, length)

    # Note that when checking the given data length, at the defined area end, we can still read 4 bytes.

    if CRITICAL_AREA_START <= address <= CRITICAL_AREA_END:
        if length != 4:
            raise RMAPError("Read requests to the critical area have a fixed data length of 4 bytes.",
                                address, length)

    elif GENERAL_AREA_START <= address <= GENERAL_AREA_END:
        if length > 256:
            raise RMAPError(f"Read requests to the general area have a maximum data length of 256 bytes.",
                                address, length)
        if address + length > GENERAL_AREA_END + 4:
            raise RMAPError(
                f"The requested data length for the general area is too large.\n"
                f"The address + length exceeds the general area boundaries.\n", address, length
            )

    elif HK_AREA_START <= address <= HK_AREA_END:
        if length > 256:
            raise RMAPError(f"Read requests to the housekeeping area have a maximum data length of 256 bytes.",
                                address, length)
        if address + length > HK_AREA_END + 4:
            raise RMAPError(
                f"The requested data length for the housekeeping area is too large.\n"
                f"The address + length exceeds the housekeeping area boundaries.\n", address, length
            )

    elif WINDOWING_AREA_START <= address <= WINDOWING_AREA_END:
        if length > 4096:
            raise RMAPError(f"Read requests to the windowing area have a maximum data length of 4096 bytes.",
                                address, length)
        if address + length > WINDOWING_AREA_END + 4:
            raise RMAPError(
                f"The requested data length for the windowing area is too large.\n"
                f"The address + length exceeds the windowing area boundaries.\n", address, length
            )

    else:
        raise RMAPError(f"Register address for RMAP read requests is invalid.", address, length)
