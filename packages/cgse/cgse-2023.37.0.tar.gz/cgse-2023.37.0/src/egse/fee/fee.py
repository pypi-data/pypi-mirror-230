"""
This module contains functions and classes that are typically used by the FEE.
"""
import ctypes
import logging
from pathlib import Path

import numpy as np

from egse import h5
from egse.bits import beautify_binary
from egse.decorators import static_vars
from egse.dsi import constants
from egse.dsi.esl import ESL
from egse.dsi.esl import ESLError
from egse.dsi.esl import esl_flush
from egse.dsi.esl import esl_get_esl_error
from egse.dsi.esl import esl_read_packet
from egse.dsi.esl import esl_write_packet
from egse.dsi.esl import get_extension_name
from egse.dsi.esl import get_terminator_name
from egse.dsi.esl import is_extension_code
from egse.dsi.esl import is_terminator_code
from egse.dsi.esl import pretty_print_packet
from egse.dsi.rmap import CheckError
from egse.dsi.rmap import ESL_RMAP
from egse.dsi.rmap import check_data_crc
from egse.dsi.rmap import check_header_crc
from egse.dsi.rmap import check_initiator_logical_address
from egse.dsi.rmap import check_instruction
from egse.dsi.rmap import check_key
from egse.dsi.rmap import check_protocol_id
from egse.dsi.rmap import check_target_logical_address
from egse.dsi.rmap import create_rmap_read_reply_packet
from egse.dsi.rmap import get_address
from egse.dsi.rmap import get_data_length
from egse.dsi.rmap import get_instruction_field
from egse.dsi.rmap import get_transaction_identifier
from egse.dsi.rmap import is_command
from egse.dsi.rmap import is_increment
from egse.dsi.rmap import is_write
from egse.dsi.rmap import rmap_crc_check
from egse.dsi.spw import handle_extension_packet
from egse.dsi.spw import handle_special_packet
from egse.settings import Settings
from egse.spw import DataPacketHeader
from egse.spw import PacketType
from egse.spw import SpaceWirePacket
from egse.state import GlobalState
from egse.system import Timer

fee_settings = Settings.load("FEE")
dsi_settings = Settings.load("DSI")
site_settings = Settings.load("SITE")

LOGGER = logging.getLogger(__name__)

DATA_DIR = (Path(__file__).parent / "../../data").resolve()


def create_pattern_data(timecode: int, ccd_id: int, ccd_side: int) -> np.ndarray:
    """
    Create pattern data as a two-dimensional ND array. The pattern data is generated as described
    in PLATO-LESIA-PL-TN-023 - SimuCam pattern requirement.

    The pattern is build up like this: each pixel is a 16-bit number with the following structure:

        * Bits [15:13] = time-code % 8
        * Bits [12:11] = CCD number [1, 2, 3, 4]  should be [0-3]!
        * Bit [10] = CCD side: 0 = left side, 1 = right side
        * Bits [9:5] = Y-coordinate % 32
        * Bits [4:0] = X-coordinate % 32

    The total image data size of a full frame CCD is:

        x = 4590 = 2 x (25 [serial prescan] + 2255 + 15 [serial overscan])
        y = 4540 = 4510 + 30 [parallel overscan]

    This function creates each side of the CCD separately, so each half can be treated individually
    as is done in the N-FEE. The two sides can easily be concatenated to form the full image:

        data = np.concatenate((data_left, data_right), axis=1)

    Args:
        timecode (int): the timecode for this readout
        ccd_id (int): the CCD number [0-3]
        ccd_side (int): the CCD side, 0 = left = E-side, 1 = right = F-side
    Returns:
        A two-dimensional ND array representing half of a CCD.
    """

    ccd_number = ccd_id  # save for later use

    timecode = (timecode % 8) << 13  # timecode is 3 bits at [15:13]
    ccd_id = (ccd_id & 0b0011) << 11  # ccd_id is 2 bits at [12:11]
    ccd_side = (ccd_side & 0b0001) << 10  # ccd_side is 1 bit at [10]

    x_size = 25 + 2255 + 15
    y_size = 4510 + 30

    rows, cols = np.indices((y_size, x_size), dtype=np.uint16)
    cols %= 32
    rows %= 32

    data = rows * 16 + cols + timecode + ccd_side + ccd_id

    # We leave set the msb because of the bit flipt for N-FEE EM

    data[50:300, 100:105] = ccd_number | 0b10000000_00000000
    data[100:105, 50:500] = ccd_number | 0b10000000_00000000
    data[300:305, 50:150] = ccd_number | 0b10000000_00000000
    data[50:150, 500:505] = ccd_number | 0b10000000_00000000

    # We unset the msb because of the bit flip for N-FEE EM

    data[110, 110] = 0x7FFF

    return data


def generate_data_packets(data: np.ndarray, header: DataPacketHeader,
                          v_start: int, v_end: int):
    """
    This generator function creates and returns the SpaceWire packets to send to the DPU Processor.

    Args:
        data (ndarray): the full frame image data
        header (DataPacketHeader): the data packet header
        v_start (int): the first row to be transmitted
        v_end (int): the last row to be transmitted

    Returns:

    """
    # steps:
    # * reshape data to 1D array
    # * update header with length, last_packet
    # * increment sequence number?
    # * convert data part into bytes object
    # * concatenate header and data -> bytes
    # * yield the packet

    N_FEE_SIDE = GlobalState.setup.camera.fee.ccd_sides.enum

    MAX_PACKET_SIZE = 32140  # this is a register value reg_4_config
    HEADER_LENGTH = 10
    H_END = 2294
    MAX_CCD_LINE = 4509
    MAX_OVERSCAN_LINE = MAX_CCD_LINE + 30

    nr_rows_in_packet = row_offset = (MAX_PACKET_SIZE - HEADER_LENGTH) // (H_END + 1) // 2

    y_size, x_size = data.shape
    h_end = x_size - 1
    v_end_ccd = min(MAX_CCD_LINE, v_end)

    ccd_side = header.type_as_object.ccd_side

    # F-side is read out starting from the right, so we flip the data left to right
    # before sending, which simulates the reverse readout.

    data = np.fliplr(data) if ccd_side == N_FEE_SIDE.RIGHT_SIDE else data

    header.length = nr_rows_in_packet * ((h_end + 1) * 2)
    LOGGER.debug(f"{header.length = }, {nr_rows_in_packet = }, {h_end = }")

    for idx in range(v_start, v_end_ccd + 1, nr_rows_in_packet):
        if idx + nr_rows_in_packet > v_end_ccd:
            row_offset = v_end_ccd - idx + 1
            header.length = row_offset * ((h_end + 1) * 2)
            header.last_packet = True
        # LOGGER.debug(f"{idx=}, {row_offset=}")
        chunk = bytearray(data[idx:idx+row_offset, :])
        chunk[0::2], chunk[1::2] = chunk[1::2], chunk[0::2]
        packet_data = header.data_as_bytes() + chunk
        # LOGGER.debug(f"{len(packet_data)=}, {len(chunk)=}")
        yield SpaceWirePacket.create_packet(packet_data)

    # reset the header for the overscan lines

    header.packet_type = PacketType.OVERSCAN_DATA
    header.last_packet = False
    header.length = nr_rows_in_packet * ((h_end + 1) * 2)

    v_end_overscan = min(MAX_OVERSCAN_LINE, v_end)

    # reset the row_offset

    row_offset = nr_rows_in_packet

    for idx in range(MAX_CCD_LINE+1, v_end_overscan + 1, nr_rows_in_packet):
        if idx + nr_rows_in_packet > v_end_overscan:
            row_offset = v_end_overscan - idx + 1
            header.length = row_offset * ((h_end + 1) * 2)
            header.last_packet = True
        LOGGER.debug(f"{idx=}, {row_offset=}")
        chunk = bytearray(data[idx:idx+row_offset, :])
        chunk[0::2], chunk[1::2] = chunk[1::2], chunk[0::2]
        packet_data = header.data_as_bytes() + chunk
        LOGGER.debug(f"{len(packet_data)=}, {len(chunk)=}")
        yield SpaceWirePacket.create_packet(packet_data)

def read_exposure(image_count):
    """
    Private method to extract an exposure from the PlatoSim HDF5 file.

    This method uses an internal counter to read the next exposure from the
    HDF5 file. When no exposures are available, an empty numpy array is returned.
    """

    platosim_filename = DATA_DIR / fee_settings.PLATOSIM_FILENAME
    platosim_hdf5file = h5.get_file(platosim_filename, "r")

    # Construct the image name that was used to store the image
    image_name = "image{0:06d}".format(image_count)

    # Copy the contents of the Image into a numpy array
    try:
        dataset = platosim_hdf5file["Images"][image_name]
        image = np.zeros(dataset.shape, dataset.dtype)
        LOGGER.info("image shape {} and type {}".format(dataset.shape, dataset.dtype))
        dataset.read_direct(image)
        return image
    except KeyError as msg:
        LOGGER.error("KeyError: {}".format(msg))
        LOGGER.error("Cannot read exposure {} from the HDF5 file".format(image_name))
        return np.array([])
    except TypeError as msg:
        LOGGER.error("TypeError: {}".format(msg))
        LOGGER.error(
            "Somehow the shape and/or the data type of the image are wrong in the HDF5 file."
        )
        return np.array([])


def is_data_packet(packet):
    return packet[0] == 0x50 and packet[1] == 0xF0


def is_hk_data_packet(packet):
    packet_type = int.from_bytes(packet[4:6], "big")

    return (packet_type & 0b0011) == 2


def is_data_data_packet(packet):
    packet_type = int.from_bytes(packet[4:6], "big")

    return (packet_type & 0b0011) == 0


def is_overscan_data_packet(packet):
    packet_type = int.from_bytes(packet[4:6], "big")

    return (packet_type & 0b0011) == 1


def is_last_packet(packet):

    # Note that this bit is only set when in readout mode and when data is sent.
    # It's currently not clear if the HK data packet will then also have the bit set (as there is
    # only one HK packet) or if it is only the last data packet.

    # bit 7 of the Data Packet Field: Type
    packet_type = int.from_bytes(packet[4:6], "big")

    LOGGER.log(5, f"Packet Type Field: 0b{beautify_binary(packet_type, size=16)}")

    return packet_type & 0b10000000


def get_mode(packet):
    # bit [8:12] of the Data Packet Field: Type
    packet_type = int.from_bytes(packet[4:6], "big")

    mode = (packet_type & 0b111100000000) >> 8
    return mode


def get_data(packet) -> bytes:
    """Return the data from the HK or Data packet.

    Raises:
        ValueError: if there is no data section in the packet (TODO: not yet implemented)
    """
    if not is_data_packet(packet):
        LOGGER.debug(f"0x{packet.hex()}")
        raise ValueError("Trying to read data from a packet that is not a data packet.")

    length = int.from_bytes(packet[2:4], "big")
    data = packet[10:]

    LOGGER.debug(f"length field={length}, packet length={len(packet)}, data length={len(data)}")

    return data


@static_vars(timecode=0)
def increment_timecode() -> int:
    if increment_timecode.timecode == 0x3F:
        increment_timecode.timecode = 0
    else:
        increment_timecode.timecode += 1

    return increment_timecode.timecode


def process_rmap_commands(esl_link: ESL, rmap_link: ESL_RMAP):
    total_received = 0
    packet = bytes()

    terminator, rx_buffer = esl_read_packet(esl_link)
    bytes_received = len(rx_buffer)

    if is_terminator_code(terminator):
        LOGGER.debug(
            f"bytes received={bytes_received}, terminator={terminator} "
            f"[{get_terminator_name(terminator)}]"
        )
    elif is_extension_code(terminator):
        LOGGER.debug(
            f"bytes received={bytes_received}, terminator={terminator} "
            f"[{get_extension_name(terminator)}]"
        )
    else:
        LOGGER.debug(f"bytes received={bytes_received}, terminator={terminator}")

    # TODO:
    #   When the link is  closed from the other end (dpusim) just one byte (b'\x08') is received.
    #   So, we should try to restart the link...

    if bytes_received == 1:
        LOGGER.warning("Link was closed from the initiator side, terminating.")
        return

    # First check if we encountered any errors or shutdown,
    # if True then break the main while loop and end the connection
    #
    # FIXME:
    #   We need better handling of exceptional conditions here since the FEE Simulator can never
    #   die.
    #       - what shall we do when a shutdown is received?
    #       - what shall we do when a timeout has occured?
    #       - what shall we do with a buffer overflow? When can this happen?
    #       - some errors are related to the virtual DSI, how do we solve those?

    if bytes_received < 0:
        error = esl_get_esl_error(esl_link)
        if error == constants.ESL_ERROR_TIMEOUT:
            LOGGER.debug("Received a timeout, continuing...")
            return
        # FIXME: We should handle all these cases in a simpler way
        if error == constants.ESL_ERROR_RECEIVER_SHUTDOWN:
            LOGGER.info("Shutdown detected.")
            return
        if error == constants.ESL_ERROR_BUFFER_OVERFLOW:
            # FIXME: Can we recover from this situation?
            LOGGER.error("Insufficient buffer to read full packet, bailing out.")
            return
        if error == constants.ESL_ERROR_RECFILE_WRITE:
            LOGGER.error("Write error on record file, bailing out.")
            return

        LOGGER.error(
            f"read_packet: returned error, "
            f"ESL error = {constants.esl_error_codes[error]} [{error}]"
        )
        return

    # When we receive an unknown terminator we just ignore, log the error and continue...

    if terminator not in (
        constants.ESL_EXTN,
        constants.ESL_SPECIAL,
        constants.ESL_PART_EOP_EEP,
        constants.ESL_PART_EXTN,
        constants.ESL_PART_SPECIAL,
        constants.ESL_EEP,
        constants.ESL_EOP,
    ):
        LOGGER.error(f"Unknown terminator [{terminator}] received.")
        return

    if terminator == constants.ESL_EXTN:
        handle_extension_packet(rx_buffer, bytes_received)

    if terminator == constants.ESL_SPECIAL:
        handle_special_packet(rx_buffer, bytes_received)

    if terminator in (
        constants.ESL_PART_EOP_EEP,
        constants.ESL_PART_EXTN,
        constants.ESL_PART_SPECIAL,
    ):
        LOGGER.debug("Partial Data Packet received.")

        total_received += bytes_received
        packet += rx_buffer[:bytes_received]

        # FIXME:
        #   at this point we need to go for the next part of the packet
        #   continue was used in the while loop before splitting off this code. We now do a
        #   return, but we loose information on the total packet size etc.
        return

    if terminator == constants.ESL_EEP:
        LOGGER.debug("Error End of Packet returned by DSI")

    if terminator == constants.ESL_EOP:
        LOGGER.debug("Normal End of Packet returned by DSI")

        total_received += bytes_received
        packet += rx_buffer[:bytes_received]

        LOGGER.debug(f"total_received={total_received}")
        LOGGER.debug("Pretty Print Received Packet:\n" + pretty_print_packet(packet))

        # Deal with RMAP request packet
        # FIXME: shouldn't this all be checked on packet instead of rx_buffer?

        try:
            # Run a number of checks on the received packet

            check_target_logical_address(rmap_link, rx_buffer, dsi_settings.TARGET_LOGICAL_ADDRESS)
            check_protocol_id(rx_buffer)
            check_instruction(rx_buffer)
            check_key(rmap_link, rx_buffer)
            check_initiator_logical_address(rx_buffer, dsi_settings.INITIATOR_LOGICAL_ADDRESS)
            check_header_crc(rx_buffer)

            # Extract information from the packet that we need further on

            tid = get_transaction_identifier(rx_buffer)
            address = get_address(rx_buffer)
            data_length = get_data_length(rx_buffer)
        except CheckError as ce:
            LOGGER.error(f"{ce.message}, status = {ce.status}")
            status = ce.status
            # FIXME:
            #   Something is wrong with the packet here, do proper exception handling.
            #   We are not anymore in the while loop after we have split off this code,
            #   so continue doesn't work anymore...
            # continue
            raise ce

        # Do something with the packet received

        instruction_field = get_instruction_field(packet)

        if is_command(instruction_field):

            status = constants.RMAP_SUCCESS

            if (
                not dsi_settings.RMAP_BASE_ADDRESS
                <= address
                < (dsi_settings.RMAP_BASE_ADDRESS + dsi_settings.RMAP_MEMORY_SIZE)
            ):
                LOGGER.error(f"ERROR: Access outside of RMAP memory area, address=0x{address:010X}")
                status = constants.RMAP_GENERAL_ERROR

            # Handling an RMAP Write Command
            #
            # - Send a reply
            # - Check Data CRC before writing
            # - Write the data into memory

            if is_write(instruction_field):

                LOGGER.debug("RMAP write command received, sending reply packet...")

                # FIXME: need some work here!!!!

                # Create the target memory map and fill it with a pattern.
                # This is just to simplify checking the correct write command.
                # TODO: this should be replaced with the RegistryMap

                rmap_target_memory = ctypes.create_string_buffer(
                    bytes([x & 0xFF for x in range(dsi_settings.RMAP_MEMORY_SIZE)])
                )

                tx_buffer = ctypes.create_string_buffer(dsi_settings.TX_BUFFER_LENGTH)

                tx_buffer[7] = rmap_crc_check(tx_buffer, 0, 7)

                result = esl_write_packet(esl_link, tx_buffer, 8, constants.ESL_EOP)

                esl_flush(esl_link)

                # When no errors, then write the data into memory at the given position

                if status == constants.RMAP_SUCCESS:

                    # Check the Data CRC

                    try:
                        check_data_crc(rx_buffer)
                    except CheckError as ce:
                        LOGGER.error(f"{ce}, status = {ce.status}")
                        raise ce

                    # Write the data into the target memory map

                    # FIXME: I do not understand why this is !!!!

                    if is_increment(instruction_field):
                        # change this code to work with RegisterMap
                        # rmap_target_memory[address:address + data_length] = get_data(rx_buffer)
                        pass
                    else:
                        # change this code to work with RegisterMap
                        # Overwrite all the data into the same memory address, why?
                        # for b in get_data(rx_buffer):
                        #    rmap_target_memory[address] = b
                        pass

            # Handling an RMAP Read Command

            else:
                if status:
                    data_length = 0

                LOGGER.warning(
                    "Commented out this code, work needs to be done on RMAP read command"
                )
                # data = self.register_map.get_data(address, data_length)
                data = b"\x00\x01\x02\x03"

                tx_buffer = create_rmap_read_reply_packet(
                    rmap_link, instruction_field, tid, status, data, data_length
                )

                result = esl_write_packet(esl_link, tx_buffer, len(tx_buffer), constants.ESL_EOP)

                result = esl_flush(
                    esl_link
                )  # FIXME: This will mask previous ESL_error if there was one

                if result:
                    raise ESLError(
                        f"Could not write the packet, "
                        f"ESL error code = {constants.esl_error_codes[esl_link.contents.ESL_error]} "
                        f"[{esl_link.contents.ESL_error}]"
                    )

        else:
            LOGGER.warning("The packet is not an RMAP read/write command.")

        total_received = 0
        packet = bytes()

    LOGGER.debug("Going for the next SpaceWire packet...")


if __name__ == "__main__":

    import numpy as np
    import matplotlib.pyplot as plt
    from egse.fee import n_fee_mode

    fig, (ax1, ax2, ax3) = plt.subplots(3)

    header = DataPacketHeader()

    timecode = 0
    ccd_side = 0
    ccd_id = 2

    data_left = create_pattern_data(timecode, ccd_id, ccd_side)

    print(f"{data_left[0, 0]=:016b}, {data_left[0, 1]=:016b}, {data_left[0, 2278]=:016b}, {data_left[0, 2279]=:016b}")
    print(f"{data_left[1, 0]=:016b}, {data_left[1, 1]=:016b}, {data_left[1, 2278]=:016b}, {data_left[1, 2279]=:016b}")
    print(f"{data_left[4538, 0]=:016b}, {data_left[4538, 1]=:016b}, {data_left[4538, 2278]=:016b}, {data_left[4538, 2279]=:016b}")
    print(f"{data_left[4539, 0]=:016b}, {data_left[4539, 1]=:016b}, {data_left[4539, 2278]=:016b}, {data_left[4539, 2279]=:016b}")

    v_start = 0
    v_end = 4509  # remember that v_end is inclusive

    data_left = create_pattern_data(62, 0, 0)
    data_right = create_pattern_data(62, 0, 1)

    data = np.concatenate((data_left, data_right), axis=1)
    data = data[v_start:v_end+1, :]

    LOGGER.info(f"{data.shape=}")

    ax1.imshow(data, origin='lower')

    # now generate the packet for the first 10 lines and glue the data together again to
    # be displayed

    packet_type = header.type_as_object
    packet_type.ccd_side = ccd_side
    packet_type.ccd_number = ccd_id
    packet_type.last_packet = False
    packet_type.frame_number = 2
    packet_type.mode = n_fee_mode.FULL_IMAGE_PATTERN_MODE
    header.type = packet_type

    nr_lines = 0
    image_left = np.empty((0,), dtype=np.uint16)

    with Timer("Generate left side data packets") as timer:
        for packet in generate_data_packets(data_left, header, v_start, v_end):
            image_left = np.concatenate((image_left, packet.data_as_ndarray))
            nr_lines += len(packet.data_as_ndarray) // 2295

    image_left = image_left.reshape(nr_lines, 2295)
    LOGGER.info(f"{image_left.shape = }")

    nr_lines = 0
    image_right = np.empty((0,), dtype=np.uint16)

    with Timer("Generate right side datapackets"):
        for packet in generate_data_packets(data_right, header, v_start, v_end):
            image_right = np.concatenate((image_right, packet.data_as_ndarray))
            nr_lines += len(packet.data_as_ndarray) // 2295

    image_right = image_right.reshape(nr_lines, 2295)
    LOGGER.info(f"{image_right.shape = }")

    image = np.concatenate((image_left, image_right), axis=1)

    ax2.imshow(image, origin='lower')

    x = data - image

    print(f"{np.count_nonzero(x)=}")

    ax3.imshow(x, origin='lower')
    plt.show()
