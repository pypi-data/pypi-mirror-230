"""
This module provides Python wrapper functions to (most of) the library functions from
the C library `EtherSpaceLink.c`.

Basic Usage

For accessing the EtherSpaceLink interface, use the context manager to get an ESL connection:

    with esl_connection(dsi_address) as esl_link:
        # do your configuration and commanding here

For special cases it might be useful to open and close the ESL connection yourself. Be careful
however to close the connection with every exception that is thrown.

        try:
            esl_link = esl_open_connection(dsi_address)
            # do your configuration and commanding
        finally:
            if esl_link:
                esl_close_connection(esl_link)

It should be clear that using the context manager is preferred and should be considered the normal usage.

We use one single Exception (`ESLError`) specific for these wrapper functions.
An `ESLError` is thrown whenever the C function returns an error from which we can not recover.
This allows to cascade the python functions in a `try: except:` clause making
the code much more readable.

Developer Info

The C interface depends heavily on a C structure which we had to re-define using
the Structure class provided by ctypes.

"""
import ctypes
import logging
import time
from contextlib import contextmanager
from ctypes import POINTER
from ctypes import Structure
from ctypes import c_char_p
from ctypes import c_int
from ctypes import c_size_t
from ctypes import c_ssize_t
from ctypes import c_uint32
from ctypes import c_uint64
from ctypes import c_uint8
from ctypes import c_void_p
from ctypes import c_void_p as c_int_p
from ctypes import cdll
from pathlib import Path
from typing import Tuple

from egse.config import find_file
from egse.dsi import constants
from egse.dsi.constants import esl_error_codes
from egse.dsi.constants import esl_extension_codes
from egse.dsi.constants import esl_terminator_codes
from egse.settings import Settings
from egse.spw import HousekeepingPacket
from egse.system import get_os_name
from egse.system import get_os_version

logger = logging.getLogger(__name__)

dsi_settings = Settings.load("DSI")

# Create and initialize a memory buffer for transmissions

rx_buffer = ctypes.create_string_buffer(dsi_settings.RX_BUFFER_LENGTH)
tx_buffer = ctypes.create_string_buffer(dsi_settings.TX_BUFFER_LENGTH)

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

dylib_filename = Path(dsi_settings.ESL_DYLIB_FILENAME)

logger.debug(f"Locating shared library {dylib_filename} in dir '{in_dir}'")

dylib_filename = find_file(dylib_filename, in_dir=in_dir)

logger.debug(f"Loading shared library: {dylib_filename}")

if not dylib_filename:
    raise FileNotFoundError(f"Could not find dynamic library: {dylib_filename}")
libesl = cdll.LoadLibrary(dylib_filename)


class ESL(Structure):
    _fields_ = [
        ("sock", c_int),
        ("tx_buffer", c_char_p),
        ("tx_buffer_length", c_size_t),
        ("tx_buffer_content", c_size_t),
        ("rx_buffer", c_char_p),
        ("rx_buffer_length", c_size_t),
        ("rx_buffer_content", c_ssize_t),
        ("rx_buffer_ptr", c_int),
        ("rx_state", c_int),
        ("rx_count", c_int),
        ("rx_param", c_int),
        ("rx_timeout", c_int),
        ("rx_final_flags", c_int),
        ("extn_count", c_int),
        ("extn_size", c_int),
        ("extn_cmd", c_int),
        ("extn_byte", c_int),
        ("extn_link", c_int),
        ("cmd_buffer", c_char_p),
        ("time_buffer", c_char_p),

        ("special_cb", c_void_p),
        ("extension_cb", c_void_p),

        ("number_of_links", c_int),
        ("number_of_slots", c_int),
        ("slot_content", c_int_p),
        ("record_file", c_void_p),
        ("log_file", c_void_p),
        ("max_length", c_int),
        ("log_rx_port", c_int),
        ("log_tx_port", c_int),

        ("ram_io", c_int),
        ("current_port", c_int),

        ("check_record_writes", c_int),
        ("total_raw_bytes_received", c_uint64),

        ("options", c_char_p),
        ("option", c_int),
        ("ESL_error_errno", c_int),

        ("rx_timeout_returns_error", c_int),

        ("max_dumps", c_uint32),
        ("context", c_void_p),

        ("rxinfo", c_uint32),

        ("read_calls", c_uint64),
        ("read_io_calls", c_uint64),
        ("file", c_int),
        ("filesize", c_uint64),
        ("recordsize", c_uint64),

        ("ram_io_int", c_int),

        ("eintr_enabled", c_int),
        ("timezero", c_size_t),
        ("timedata", c_uint64),
        ("timedata_ns", c_uint32),

        ("partialframesz", c_size_t),
        ("partialframe_offset", c_size_t),
        ("system_type", c_int),
        ("auto_flush", c_int),
        ("live", c_int),

        ("epollfd", c_int),
    ]


esl_p = POINTER(ESL)


class ESLError(Exception):
    pass


def esl_read_packet(esl_link: ESL, timeout: int = None) -> Tuple[int, bytes]:
    """
    Reads a full packet from the SpaceWire link.

    .. note:: since this function returns a packet as a bytes object, the content of the packet can not be changed.

    Args:
        esl_link (ESL): the ESL structure that defines the connection to the DSI
        timeout (int): the maximum timeout that read_packet() will wait for data before returning [milliseconds]

    Returns:
        A tuple with the terminator value and a bytes object containing the packet.
        When an error occurred, the first value in the tuple will be negative and contains the error number,
        the second item in the tuple will then be an empty buffer.

    """
    terminator = c_int(0)
    terminator_p = ctypes.pointer(terminator)

    bytes_received = esl_read_packet_full(
        esl_link, rx_buffer, dsi_settings.RX_BUFFER_LENGTH, terminator_p,
        constants.ESL_RETURN_EXTENSION_DATA | constants.ESL_RETURN_SPECIAL_DATA, timeout=timeout)

    logger.log(0, f"Number of bytes received: {bytes_received}")

    if bytes_received < 0:
        return bytes_received, bytes()

    return terminator.value, rx_buffer[:bytes_received]


@contextmanager
def esl_connection(dsi_address: str) -> ESL:
    """
    Context Manager that opens a EtherSpaceLink connection with the DSI (Diagnostic SpaceWire Interface).

    Args:
        dsi_address (str): the IP address of the DSI

    Returns:
        a pointer to the ESL structure
    """
    esl_link = None
    try:
        esl_link = esl_open_connection(dsi_address)
        yield esl_link
    finally:
        if esl_link:
            esl_close_connection(esl_link)


def esl_open_connection(dsi_address: str) -> ESL:
    """
    Open a connection to the EtherSpaceLink DSI on the given IP address.
    This function will keep trying to connect for 10 seconds before aborting
    and throwing an `ESLError`.

    Args:
        dsi_address (str): the IP address of the DSI

    Returns:
        a pointer to the ESL structure

    """
    logger.info(f"Open and setup EtherSpaceLink connection on {dsi_address}.")

    retry = 20  # number of retries before failing to open connection
    esl_link = None

    while retry:
        esl_link = libesl_open(c_char_p(dsi_address.encode()))
        if esl_link:
            break
        else:
            time.sleep(0.5)  # wait half a second before trying again
            logger.info(f"Trying to connect to {dsi_address}, {retry / 2.0} sec before shutdown.")
            retry -= 1
    if not esl_link:
        raise ESLError(f"Couldn't open connection to DSI on {dsi_address}.")

    logger.info(f"EtherSpaceLink connection to {dsi_address} opened successfully.")

    return esl_link


def esl_close_connection(esl_link):
    """
    Close the connection to the EtherSpaceLink DSI.

    This also flushes and closes the log and record files if they were used.

    Args:
        esl_link (ESL): the ESL structure that defines the connection to the DSI

    Returns:
        Nothing
    """
    libesl_close(esl_link)
    logger.info("EtherSpaceLink connection closed successfully.")


def esl_flush(esl_link) -> int:
    """
    Flush all outstanding data to the destination. This function puts queued data onto the wire.

    Args:
        esl_link (ESL): the ESL structure that defines the connection to the DSI

    Returns:
        0 on success, !0 otherwise
    """
    result = libesl_flush(esl_link)
    # We don't want this to raise an exception, the result value should be checked by the caller instead.
    # if result:
    #     raise ESLError(
    #         f"Could not flush/send transmit buffer, "
    #         f"ESL error code={esl_error_codes[esl_link.contents.ESL_error]} [{esl_link.contents.ESL_error}]"
    #     )
    return result


def esl_configure(esl_link: ESL,
                  active_link: int = 1, speed: int = 50, mode: int = constants.ESL_LINK_MODE_NORMAL,
                  report: int = 0):
    """
    Configure the `esl_link` EtherSpaceWire link to the DSI.

    The reporting parameter is used to enable reporting for the following events:

        ESL_ER_REPORT_PARITY_ERROR
        ESL_ER_REPORT_TIME_CODE
        ESL_ER_REPORT_ESC_EOP
        ESL_ER_REPORT_ESC_EEP
        ESL_ER_REPORT_ESC_ESC
        ESL_ER_REPORT_TIMEOUT

    Args:
        esl_link (ESL): the ESL structure that defines the connection to the DSI
        active_link: the port number on the DSI where the SpW link shall be activated (default=1)
        speed: the speed in Mbps
        mode: the link mode [DISABLED, NORMAL, LEGACY or MASTER]
        report: enable reporting [default=0]

    Returns:
        Nothing
    """
    status = esl_set_active_link(esl_link, active_link)
    status = esl_set_speed(esl_link, speed)
    status = esl_set_mode(esl_link, mode)
    if report:
        status = esl_er_enable_reporting(esl_link, report)


def esl_set_speed(esl_link, speed):
    result = libesl_set_speed(esl_link, speed)
    if result:
        raise ESLError("Could not set speed to {}, ESL error code={} [{}]".format(speed, esl_error_codes[
            esl_link.contents.ESL_error], esl_link.contents.ESL_error))
    return result


def esl_set_mode(esl_link: ESL, mode: int) -> int:
    """
    Set the operating mode of the currently active SpaceWire link.

    After opening a connection, the link is disabled; it must then
    be enabled into one of its operational modes before data can
    be transferred.

    Args:
        esl_link (ESL): the ESL structure that defines the connection to the DSI
        mode (int): the link mode [DISABLED, NORMAL, LEGACY or MASTER]

    Returns:
        0 if the request has been queued, not 0 if not.

    """
    result = libesl_set_mode(esl_link, mode)
    if result:
        raise ESLError(
            "Could not set mode, ESL error code={} [{}]".format(esl_error_codes[esl_link.contents.ESL_error],
                                                                esl_link.contents.ESL_error))
    return result


def esl_send_timecode(esl_link: ESL, timecode: int) -> int:
    """
    Send a timecode over the SpaceWire link.

    The 8-bit timecode argument contains six-bit of system time (time-field) and two control flags.

    Args:
        esl_link (ESL): the ESL structure that defines the connection to the DSI
        timecode (int): an 8-bit timecode field

    Returns:
        0 if the request has been queued, not 0 if not.

    """
    result = libesl_send_timecode(esl_link, timecode)

    if result:
        raise ESLError(
            f"Could not send timecode, ESL error code={esl_error_codes[esl_link.contents.ESL_error]} "
            f"[{esl_link.contents.ESL_error}]"
        )

    libesl_flush(esl_link)

    return result


def esl_get_rx_timeout(esl_link):
    return esl_link.contents.rx_timeout


def esl_get_receive_speed(esl_link: ESL) -> int:
    """
    Gets the receive speed of the currently active link.

    Note that this function has the ability to cause frames to be dropped and the esl_request_rx_speed() function
    should be used instead.

    Args:
        esl_link (ESL): the ESL structure that defines the connection to the DSI

    Returns:
        the speed of the active link in Mbtis/s. In case of an error a value < 0 will be returned.
    """
    return libesl_get_receive_speed(esl_link)


def esl_set_log_file(esl_link, filename):
    result = libesl_set_log_file(esl_link, c_char_p(filename.encode()))
    if result:
        raise ESLError(f"Could not write to or open record file {filename}.")
    return result


def esl_set_record_file(esl_link, filename):
    result = libesl_set_record_file(esl_link, c_char_p(filename.encode()))
    if result:
        raise ESLError(f"Could not write to or open log file {filename}.")
    return result


def esl_get_manufacturer_string(esl_link):
    return libesl_get_manufacturer_string(esl_link).decode()


def esl_get_product_string(esl_link):
    return libesl_get_product_string(esl_link).decode()


def esl_read_packet_full(esl_link, buffer, buffer_length, rx_terminator, special_data_action, timeout: int = None):

    if timeout:
        saved_timeout = esl_get_rx_timeout(esl_link)
        esl_set_rx_timeout(esl_link, timeout)

    result = libesl_read_packet_full(esl_link, buffer, buffer_length, rx_terminator, special_data_action)

    if timeout:
        esl_set_rx_timeout(esl_link, saved_timeout)

    # This error handling is (or should be) done in the calling application, see for example egse.feesim.py
    # if result == -1:
    #     raise ESLError(
    #         f"Could not read full packet, "
    #         f"ESL error code = {esl_error_codes[esl_link.contents.ESL_error]} [{esl_link.contents.ESL_error}]"
    #     )

    return result


def esl_write_packet(esl_link: ESL, buffer, buffer_length: int, tx_terminator: int) -> int:
    """
    Queue data for transmission over the SpaceWire cable. If there is no room left in the buffer,
    the buffer is transmitted.

    Note, that even when the queued data is transmitted, the data added to it may not be.
    To guarantee transmission of this data you need to call the esl_flush() function.

    Args:
        esl_link (ESL): the ESL structure that defines the connection to the DSI
        buffer: the data to send
        buffer_length: the size of the buffer to send (the actual buffer size might be longer)
        tx_terminator: additional metadata about the frame we are transmitting (EOP, EEP, PART_EOP_EEP, EXTN)

    Returns:
        return_code: 0 on success, < 0 otherwise
    """
    # logger.debug(
    #     f"Calling esl_write_packet: "
    #     f"buffer={pp_packet(buffer)}, buffer_length={buffer_length}, tx_terminator=0x{tx_terminator:x} "
    #     f"[{get_terminator_name(tx_terminator) or get_extension_name(tx_terminator)}]."
    # )

    result = libesl_write_packet(esl_link, buffer, buffer_length, tx_terminator)

    # This error handling is (or should be) done in the calling application, see for example egse.feesim.py
    # if result == -1:
    #     raise ESLError(
    #         f"Could not write the packet, "
    #         f"ESL error code = {esl_error_codes[esl_link.contents.ESL_error]} [{esl_link.contents.ESL_error}]"
    #     )

    # logger.debug(f"Returning from esl_write_packet: buffer={pp_packet(buffer)}, result = {result}.")

    return result


def esl_er_enable_reporting(esl_link, flags):
    result = libesl_er_enable_reporting(esl_link, flags)
    if result:
        raise ESLError(
            f"Could not enable error reporting, "
            f"ESL error code = {esl_error_codes[esl_link.contents.ESL_error]} [{esl_link.contents.ESL_error}]"
        )
    return result


def esl_print_info(esl_link: ESL) -> None:
    """
    Prints information about the connected device to the console.

    Args:
        esl_link (ESL): the ESL structure that defines the connection to the DSI

    Returns:
        nothing
    """
    print("Manufacturer        {}".format(esl_get_manufacturer_string(esl_link)))
    print("Product             {}".format(esl_get_product_string(esl_link)))
    print("Number of links     {}".format(esl_get_number_of_links(esl_link)))

    # Pre-allocate the character buffer

    hwa = b'012345'

    esl_get_hwa(esl_link, hwa)
    serial_number = esl_hwa_to_serial_number_string(hwa)

    print(f"Serial number       {serial_number}")
    print(f"Hardware Address    0x{hwa[0]:02X}-{hwa[1]:02X}-{hwa[2]:02X}-{hwa[3]:02X}-{hwa[4]:02X}-{hwa[5]:02X}")


def esl_print_summary_of_structure(esl):
    print("EtherSpaceLink structure:")
    print("sock                {}".format(esl.contents.sock))
    print("tx_buffer_length    {}".format(esl.contents.tx_buffer_length))
    print("tx_buffer_content   {}".format(esl.contents.tx_buffer_content))
    print("rx_buffer_length    {}".format(esl.contents.rx_buffer_length))
    print("rx_buffer_content   {}".format(esl.contents.rx_buffer_content))
    print("rx_state            {}".format(esl.contents.rx_state))
    print("rx_count            {}".format(esl.contents.rx_count))
    print("rx_param            {}".format(esl.contents.rx_param))
    #print("rx_size             {}".format(esl.contents.rx_size))
    print("rx_timeout          {}".format(esl.contents.rx_timeout))
    #print("rx_final_terminator {}".format(esl.contents.rx_final_terminator))
    print("extn_count          {}".format(esl.contents.extn_count))
    print("number_of_slots     {}".format(esl.contents.number_of_slots))
    #print("id                  {}".format(esl.contents.id))


esl_get_version = libesl.EtherSpaceLink_get_version
esl_get_version.argtypes = []
esl_get_version.restype = c_char_p

libesl_open = libesl.EtherSpaceLink_open
libesl_open.argtypes = [c_char_p]
libesl_open.restype = esl_p

libesl_close = libesl.EtherSpaceLink_close
libesl_close.argtypes = [esl_p]

libesl_flush = libesl.EtherSpaceLink_flush
libesl_flush.argtypes = [esl_p]

esl_shutdown = libesl.EtherSpaceLink_shutdown
esl_shutdown.argtypes = [esl_p]

esl_link_connected = libesl.EtherSpaceLink_link_connected
esl_link_connected.argtypes = [esl_p]
esl_link_connected.restype = c_int

esl_set_active_link = libesl.EtherSpaceLink_set_active_link
esl_set_active_link.argtypes = [esl_p, c_int]
esl_set_active_link.restype = c_int

libesl_set_speed = libesl.EtherSpaceLink_set_speed
libesl_set_speed.argtypes = [esl_p, c_int]
libesl_set_speed.restype = c_int

libesl_set_mode = libesl.EtherSpaceLink_set_mode
libesl_set_mode.argtypes = [esl_p, c_int]
libesl_set_mode.restype = c_int

libesl_send_timecode = libesl.EtherSpaceLink_send_timecode
libesl_set_mode.argtypes = [esl_p, c_uint8]
libesl_set_mode.restype = c_int

esl_set_rx_timeout = libesl.EtherSpaceLink_set_rx_timeout
esl_set_rx_timeout.argtypes = [esl_p, c_int]

esl_set_rx_timeout_action = libesl.EtherSpaceLink_set_rx_timeout_action
esl_set_rx_timeout_action.argtypes = [esl_p, c_int]

libesl_set_log_file = libesl.EtherSpaceLink_set_log_file
libesl_set_log_file.argtypes = [esl_p, c_char_p]
libesl_set_log_file.restype = c_int

libesl_set_record_file = libesl.EtherSpaceLink_set_record_file
libesl_set_record_file.argtypes = [esl_p, c_char_p]
libesl_set_record_file.restype = c_int

esl_request_link_status = libesl.EtherSpaceLink_request_link_status
esl_request_link_status.argtypes = [esl_p]
esl_request_link_status.restype = c_int

libesl_get_receive_speed = libesl.EtherSpaceLink_get_receive_speed
libesl_get_receive_speed.argtypes = [esl_p]
libesl_get_receive_speed.restype = c_int

esl_get_esl_error = libesl.EtherSpaceLink_get_error
esl_get_esl_error.argtypes = [esl_p]
esl_get_esl_error.restype = c_int

esl_get_number_of_links = libesl.EtherSpaceLink_get_number_of_links
esl_get_number_of_links.argtypes = [esl_p]
esl_get_number_of_links.restype = c_int

libesl_get_manufacturer_string = libesl.EtherSpaceLink_get_manufacturer_string
libesl_get_manufacturer_string.argtypes = [esl_p]
libesl_get_manufacturer_string.restype = c_char_p

libesl_get_product_string = libesl.EtherSpaceLink_get_product_string
libesl_get_product_string.argtypes = [esl_p]
libesl_get_product_string.restype = c_char_p

esl_get_hwa = libesl.EtherSpaceLink_get_HWA
esl_get_hwa.argtypes = [esl_p, c_char_p]
esl_get_hwa.restype = c_int

esl_hwa_to_serial_number_string = libesl.EtherSpaceLink_HWA_to_serial_number_string
esl_hwa_to_serial_number_string.argtypes = [c_char_p]
esl_hwa_to_serial_number_string.restype = c_char_p

libesl_read_packet_full = libesl.EtherSpaceLink_read_packet_full
libesl_read_packet_full.argtypes = [esl_p, c_void_p, c_int, c_int_p, c_int]
libesl_read_packet_full.restype = c_int

libesl_write_packet = libesl.EtherSpaceLink_write_packet
libesl_write_packet.argtypes = [esl_p, c_void_p, c_size_t, c_uint32]
libesl_write_packet.restype = c_int

libesl_er_enable_reporting = libesl.EtherSpaceLink_ER_enable_reporting
libesl_er_enable_reporting.argtypes = [esl_p, c_int]
libesl_er_enable_reporting.restype = c_int


# Helper Functions ---------------------------------------------------------------------------------


def is_terminator_code(code):
    return True if code in esl_terminator_codes else False


def get_terminator_name(code):
    if code in esl_terminator_codes:
        return esl_terminator_codes[code]
    else:
        return None


def is_extension_code(code):
    return True if code in esl_extension_codes else False


def get_extension_name(code):
    if code in esl_extension_codes:
        return esl_extension_codes[code]
    else:
        return None


def get_protocol_id(packet) -> int:
    if isinstance(packet[1], bytes):
        value = int.from_bytes(packet[1], byteorder='big')
    else:
        value = packet[1]  # value assumed to be of type 'int'
    return value


def is_timecode(packet) -> bool:
    """Returns True if the packet is a timecode reported as an extension from the DSI."""
    return packet[0] == 0x91


RMAP_PROTOCOL_ID = 0x01
CCSDS_PROTOCOL_ID = 0x02
DATA_HK_PROTOCOL_ID = 0xF0


def pretty_print_packet(packet) -> str:

    from egse.fee import is_hk_data_packet

    msg = f"packet is of type {type(packet)}, with length {len(packet)}\n"

    # When the packet is of type ctypes.c_char_Array_24 (i.e. ctypes array of c_char)
    # then convert the packet into a bytes object.

    if hasattr(packet, 'raw'):
        packet = packet.raw

    # First check if this is a timecode packet because this is only 2 bytes long and reading the instruction field
    # will result in an IndexError otherwise.

    if is_timecode(packet):
        msg += (
            f"Time code received: 0x{packet[1]:02x}\n"
        )
    elif get_protocol_id(packet) == RMAP_PROTOCOL_ID:
        import egse.dsi.rmap
        instruction_field = egse.dsi.rmap.get_instruction_field(packet)
        if instruction_field == 0x4C:
            msg += pretty_print_read_request_packet(packet)
        elif instruction_field == 0x4C & 0x3F:
            msg += pretty_print_read_request_reply_packet(packet)
        elif instruction_field == 0x7C:
            msg += pretty_print_verified_write_request_packet(packet)
        elif instruction_field == 0x6C:
            msg += pretty_print_unverified_write_request_packet(packet)
        elif instruction_field == 0x3C & 0x3F:
            msg += pretty_print_write_request_reply_packet(packet)
        else:
            msg += (
                f"RMAP packet (to-be-implemented)\n"
                f'{pp_packet(packet)}'
            )
    elif get_protocol_id(packet) == CCSDS_PROTOCOL_ID:
        msg += (
            f"CCSDS Packet\n"
            f"Packet: {' '.join([hex(x) for x in packet[:min(80, len(packet))]])} [max. 80 bytes printed]."
        )
    elif get_protocol_id(packet) == DATA_HK_PROTOCOL_ID and is_hk_data_packet(packet):
        # FIXME: this puts an unnecessary dependency on the esl.py module. The HousekeepingPacket is PLATO specific
        #        and should not be in the esl.py module
        msg += (
            f"HK Packet:\n"
            f"{HousekeepingPacket(packet)}"
        )
    else:
        msg += (
            f"Extended Protocol Identifier is not supported.\n"
            f"Packet: {' '.join([hex(x) for x in packet[:min(80, len(packet))]])} [max. 80 bytes printed]."
        )

    return msg


def pretty_print_read_request_packet(packet):
    msg = (
        f"RMAP Read Request  ({len(packet)} bytes)\n"
        f"Logical address:   0x{packet[0]:0x}\n"
        f"Protocol ID:       0x{packet[1]:0x}\n"
        f"Instruction:       0x{packet[2]:0x}\n"
        f"Key:               0x{packet[3]:0x}\n"
        f"Initiator address: 0x{packet[4]:0x}\n"
        f"Transaction ID:    0x{packet[5:7].hex()}\n"
        f"Extended address:  0x{packet[7]:0x}\n"
        f"Address Field:     0x{packet[8:12].hex()}\n"
        f"Data Length:       0x{packet[12:15].hex()}\n"
        f"Header CRC:        0x{packet[15]:0x}\n"
    )
    return msg


def pretty_print_read_request_reply_packet(packet):
    data_length = int.from_bytes(packet[8:11], byteorder='big')
    msg = (
        f"RMAP Read Request Reply ({len(packet)} bytes)\n"
        f"Logical address:   0x{packet[0]:0x}\n"
        f"Protocol ID:       0x{packet[1]:0x}\n"
        f"Instruction:       0x{packet[2]:0x}\n"
        f"Status:            0x{packet[3]:0x}\n"
        f"Target address:    0x{packet[4]:0x}\n"
        f"Transaction ID:    0x{packet[5:7].hex()}\n"
        f"Reserved:          0x{packet[7]:0x}\n"
        f"Data Length:       {data_length}\n"
        f"Header CRC:        0x{packet[11]:0x}\n"
        f"data:              0x{packet[12:12 + min(32, data_length)].hex()}\n"
        f"                   note: maximum 32 bytes will be printed for the data.\n"
        f"Data CRC:          0x{packet[-1]:0x}\n"
    )
    return msg


def pretty_print_write_request_reply_packet(packet):
    data_length = int.from_bytes(packet[8:11], byteorder='big')
    msg = (
        f"RMAP Write Request Reply ({len(packet)} bytes)\n"
        f"Logical address:   0x{packet[0]:0x}\n"
        f"Protocol ID:       0x{packet[1]:0x}\n"
        f"Instruction:       0x{packet[2]:0x}\n"
        f"Status:            0x{packet[3]:0x}\n"
        f"Target address:    0x{packet[4]:0x}\n"
        f"Transaction ID:    0x{packet[5:7].hex()}\n"
        f"Header CRC:        0x{packet[7]:0x}\n"
    )
    return msg


def pretty_print_verified_write_request_packet(packet):
    msg = (
        f"RMAP Verified Write Request ({len(packet)} bytes)\n"
        f"Logical address:   0x{packet[0]:02x}\n"
        f"Protocol ID:       0x{packet[1]:02x}\n"
        f"Instruction:       0x{packet[2]:02x}\n"
        f"Key:               0x{packet[3]:02x}\n"
        f"Initiator address: 0x{packet[4]:02x}\n"
        f"Transaction ID:    0x{packet[5:7].hex()}\n"
        f"Address:           0x{packet[7:12].hex()}\n"
        f"Data Length:       0x04\n"
        f"Header CRC:        0x{packet[15]:02x}\n"
        f"data:              0x{packet[16:20].hex()}\n"
        f"Data CRC:          0x{packet[20]:02x}\n"
    )
    return msg


def pretty_print_unverified_write_request_packet(packet):
    data_length = int.from_bytes(packet[12:15], byteorder='big')
    msg = (
        f"RMAP Unverified Write Request ({len(packet)} bytes)\n"
        f"Logical address:   0x{packet[0]:02x}\n"
        f"Protocol ID:       0x{packet[1]:02x}\n"
        f"Instruction:       0x{packet[2]:02x}\n"
        f"Key:               0x{packet[3]:02x}\n"
        f"Initiator address: 0x{packet[4]:02x}\n"
        f"Transaction ID:    0x{packet[5:7].hex()}\n"
        f"Address:           0x{packet[7:12].hex()}\n"
        f"Data Length:       {data_length}\n"
        f"Header CRC:        0x{packet[15]:02x}\n"
        f"data:              {packet[16:16 + min(32, data_length)]}\n"
        f"                   note: maximum 32 bytes will be printed for the data.\n"
        f"Data CRC:          0x{packet[-1]:0x}\n"
    )
    return msg


def pp_packet(packet) -> str:
    """
    Returns a one-line representation of a SpW packet.

    Args:
        packet (bytes): the raw packet

    Returns:
        a one-line representation of a SpW packet
    """
    RMAP_PROTOCOL_ID = 0x01
    CCSDS_PROTOCOL_ID = 0x02

    if hasattr(packet, 'raw'):
        packet = packet.raw

    if get_protocol_id(packet) == RMAP_PROTOCOL_ID:
        msg = (
            f"RMAP: "
            f"0x{packet[0]:0x}:"
            f"0x{packet[1]:0x}:"
            f"0x{packet[2]:0x}:"
            f"0x{packet[3]:0x}:"
            f"0x{packet[4]:0x}:"
            f"0x{packet[5:7].hex()}:"
            f"0x{packet[7]:0x}:"
            f"0x{packet[8:12].hex()}:"
            f"0x{packet[12:15].hex()}:"
            f"0x{packet[15]:0x}"
        )
    elif get_protocol_id(packet) == CCSDS_PROTOCOL_ID:
        msg = (
            "CCSDS Packet"
        )
    else:
        msg = "Extended Protocol Identifier is not supported"

    return msg
