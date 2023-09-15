"""
This module contains functions to handle SpaceWire communication.
"""

import logging
from typing import Tuple

from egse.dsi import constants
from egse.dsi.esl import esl_close_connection
from egse.dsi.esl import esl_configure
from egse.dsi.esl import esl_flush
from egse.dsi.esl import esl_open_connection
from egse.dsi.esl import esl_read_packet
from egse.dsi.esl import esl_send_timecode
from egse.dsi.esl import esl_write_packet
from egse.dsi.rmap import rmap_configure
from egse.dsi.rmap import rmap_open_connection
from egse.dsi.rmap import rmap_read_request
from egse.dsi.rmap import rmap_write_request
from egse.settings import Settings
from egse.spw import SpaceWireInterface
from egse.spw import SpaceWirePacket

logger = logging.getLogger(__name__)

DSI_SETTINGS = Settings.load("DSI")

# Naming conventions:
#
# rx_buffer:
#     is used for any buffer (of type bytes) that is or was received over the SpaceWire interface.
# tx_buffer:
#     is used for any buffer (of type bytes) that will be transmitted over the SpaceWire interface.


def handle_extension_packet(rx_buffer: bytes, bytes_received: int):
    """
    Decide how to handle the extension packet that was received over the SpaceWire.

    The following extension packets are supported:

    * a timecode packet

    Args:
        rx_buffer (bytes): the packet that was received as a bytes object
        bytes_received (int): the length of the rx_buffer (allocated space might be larger)

    Returns:
        Nothing: yet.

    """
    logger.debug("*" * 80)
    logger.debug("Extension Packet returned by DSI")
    logger.debug(
        f"extension packet: {bin(int.from_bytes(rx_buffer, 'big'))} (length={bytes_received})"
    )
    logger.debug("*" * 80)


def handle_special_packet(rx_buffer: bytes, bytes_received: int):
    """

    Args:
        rx_buffer (bytes): the packet that was received as a bytes object
        bytes_received (int): the length of the rx_buffer (allocated space might be larger)

    Returns:
        Nothing: yet.

    """
    logger.debug("Special Packet returned by DSI")
    logger.debug(f"extension packet: {rx_buffer}")


class SpaceWireOverDSI(SpaceWireInterface):
    """
    The SpaceWireOverDSI implements the SpaceWire communication/transport over a Diagnostic
    SpaceWire Interface (DSI).
    """

    def __init__(self, dsi_address, dsi_port):
        self.dsi_address = dsi_address
        self.dsi_port = dsi_port
        self.esl_link = None
        self.rmap_link = None

    def connect(self):
        self.esl_link = esl_open_connection(self.dsi_address)
        self.rmap_link = rmap_open_connection(self.esl_link)
        # esl_print_info(self.esl_link)

    def disconnect(self):
        esl_close_connection(self.esl_link)

    def configure(self):
        esl_configure(
            self.esl_link,
            active_link=self.dsi_port,
            speed=DSI_SETTINGS.LINK_SPEED,
            mode=constants.ESL_LINK_MODE_NORMAL,
            report=constants.ESL_ER_REPORT_PARITY_ERROR
            | constants.ESL_ER_REPORT_TIME_CODE
            | constants.ESL_ER_REPORT_ESC_EOP
            | constants.ESL_ER_REPORT_ESC_EEP
            | constants.ESL_ER_REPORT_ESC_ESC
            | constants.ESL_ER_REPORT_TIMEOUT,
        )

        rmap_configure(
            self.rmap_link,
            target_key=constants.RMAP_TARGET_KEY,
            initiator_logical_address=DSI_SETTINGS.INITIATOR_LOGICAL_ADDRESS,
            target_logical_address=DSI_SETTINGS.TARGET_LOGICAL_ADDRESS,
        )

        # esl_print_summary_of_structure(self.esl_link)

    def flush(self):
        esl_flush(self.esl_link)

    def send_timecode(self, timecode: int):
        esl_send_timecode(self.esl_link, timecode)

    def read_packet(self, timeout: int = None) -> Tuple[int, bytes]:
        return esl_read_packet(self.esl_link, timeout=timeout)

    def write_packet(self, packet: bytes):
        esl_write_packet(self.esl_link, packet, len(packet), constants.ESL_EOP)

    def read_register(self, address: int, length: int = 4, strict: bool = True) -> bytes:
        terminator, rx_buffer = rmap_read_request(self.rmap_link, address, length)

        packet = SpaceWirePacket.create_packet(rx_buffer)
        rx_data = packet.data

        return rx_data

    def write_register(self, address: int, data: bytes):
        terminator, rx_buffer = rmap_write_request(self.rmap_link, address, data)

        # FIXME:
        #  So, what do we need to do with the terminator value and the rx_buffer?
        #  Is there some error checking needed here and what should than be the
        #  return value?

        return 0

    def read_memory_map(self, address: int, size: int):
        terminator, rx_buffer = rmap_read_request(self.rmap_link, address, size)

        packet = SpaceWirePacket.create_packet(rx_buffer)
        rx_data = packet.data

        return rx_data
