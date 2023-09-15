from enum import IntEnum


class MessageIdentifier(IntEnum):
    """
    The first item in a multipart message that can be used to subscribe, filter and identify
    messages.
    """

    # ALL shall not be used in the multipart message itself, but exists as an indicator for
    # subscribing to all messages. The ALL shall be converted into b'' when subscribing.

    ALL = 0x00

    # Synchronisation to DPU Processor at time of reception

    SYNC_TIMECODE = 0x80
    SYNC_HK_PACKET = 0x81
    SYNC_DATA_PACKET = 0x82
    SYNC_ERROR_FLAGS = 0x85
    SYNC_HK_DATA = 0x86

    N_FEE_REGISTER_MAP = 0x83
    NUM_CYCLES = 0x84

    # Sending out all kinds of information

    HDF5_FILENAMES = 0x90
