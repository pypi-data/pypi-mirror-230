import logging

import pytest
import rich

import numpy as np

from egse.dpu.ccd_ui import ImageCreator
from egse.fee import n_fee_mode
from egse.fee.fee import create_pattern_data
from egse.fee.fee import generate_data_packets
from egse.fee.nfee import HousekeepingData
from egse.spw import DataDataPacket
from egse.spw import DataPacketHeader
from egse.spw import DataPacketType
from egse.spw import SpaceWirePacket
from egse.state import GlobalState
from egse.system import Timer


def test_housekeeping_data(setup_environment):
    data = b'P\xf0\x00\x90\x00\xb2\x00D\x00\x00\x80\x00\x80\x00\x80\x00\x80\x00\x80\x00\x80\x00' \
           b'\x7f\xff\x7f\xff\x7f\xff\x7f\xff\x7f\xff\x7f\xff\x7f\xff\x7f\xff\x7f\xff\x80\x15' \
           b'\x80U\x80V\x80V\x80W\x80X\x80W\x80X\x80X\x80X\x80W\x80X\x80X9\xbf\xfc\x8a\xfa\xe9' \
           b'\x82\x1a\x1ej\x1a\x9f\xe7]\x19y\xe7n\x1a\x8c\xdf5\x1a\x80S\xbf@\xba\x07D\xfb|:\xec\n' \
           b'\xb5\n2\x82w\x80Y\x94\xca\x80V\x80X\x94\xc1\x80U\x80Y\x94\xc1\x80X\x80X\x94\xba\x80V' \
           b'\x80W\x80Y\x80Y\x80Z\x00\r\x00\x01\x00D\x00\x00\x00\x00\x00\x0c\x00\x00\x00\x18'

    assert len(data) == 154

    n_fee_side = GlobalState.setup.camera.fee.ccd_sides.enum

    packet = SpaceWirePacket.create_packet(data)
    n_fee_data = HousekeepingData(packet.data)

    print()
    rich.print(f"{len(packet.data)=}")
    rich.print(packet.header_as_bytes())
    rich.print(n_fee_data)

    header = DataPacketHeader(packet.header_as_bytes())

    assert header.logical_address == 0x50
    assert header.protocol_id == 0xF0
    assert header.length == len(data) - 10
    assert header.type == 0xB2
    assert header.frame_counter == 0x44
    assert header.sequence_counter == 0x00

    header.logical_address = 0x42
    header.protocol_id = 0x23
    header.length = 222
    header.type = b'\x03\xF1'
    header.frame_counter = 31
    header.sequence_counter = 75

    assert header.logical_address == 0x42
    assert header.protocol_id == 0x23
    assert header.length == 222
    assert header.type == 1009
    assert header.frame_counter == 0x1F
    assert header.sequence_counter == 0x4B

    data_packet_type = DataPacketType(0xB2)
    rich.print(data_packet_type)

    assert data_packet_type.ccd_side == n_fee_side.E_SIDE
    data_packet_type.ccd_side = n_fee_side.F_SIDE
    assert data_packet_type.ccd_side == n_fee_side.F_SIDE

    assert data_packet_type.ccd_number == 3
    data_packet_type.ccd_number = 2
    assert data_packet_type.ccd_number == 2

    assert data_packet_type.frame_number == 0
    data_packet_type.frame_number = 3
    assert data_packet_type.frame_number == 3
    data_packet_type.frame_number = 2
    assert data_packet_type.frame_number == 2
    data_packet_type.frame_number = 1
    assert data_packet_type.frame_number == 1


def test_housekeeeping_data_setitem(setup_environment):

    hk_data = HousekeepingData()

    with Timer(precision=9):
        hk_data["TOU_SENSE_1"] = 0x8000
        hk_data["TOU_SENSE_2"] = 0x8000
        hk_data["TOU_SENSE_3"] = 0x8000
        hk_data["TOU_SENSE_4"] = 0x8000
        hk_data["TOU_SENSE_5"] = 0x8000
        hk_data["TOU_SENSE_6"] = 0x8000

        hk_data["CCD1_TS"] = 0x7FFF
        hk_data["CCD2_TS"] = 0x7FFF
        hk_data["CCD3_TS"] = 0x7FFF
        hk_data["CCD4_TS"] = 0x7FFF

        hk_data["PRT1"] = 0x7FFF
        hk_data["PRT2"] = 0x7FFF
        hk_data["PRT3"] = 0x7FFF
        hk_data["PRT4"] = 0x7FFF
        hk_data["PRT5"] = 0x7FFF

        hk_data["ZERO_DIFF_AMP"] = 0x8015

        # hk_data["CCD1_VOD_MON"] = 0x8055
        hk_data["CCD1_VOG_MON"] = 0x8056
        hk_data["CCD1_VRD_MON_E"] = 0x8056
        # hk_data["CCD2_VOD_MON"] = 0x8057
        hk_data["CCD2_VOG_MON"] = 0x8058
        hk_data["CCD2_VRD_MON_E"] = 0x8057
        # hk_data["CCD3_VOD_MON"] = 0x8058
        hk_data["CCD3_VOG_MON"] = 0x8058
        hk_data["CCD3_VRD_MON_E"] = 0x8058
        # hk_data["CCD4_VOD_MON"] = 0x8057
        hk_data["CCD4_VOG_MON"] = 0x8058
        hk_data["CCD4_VRD_MON_E"] = 0x8058

        hk_data["VCCD"] = 0x39BF
        hk_data["VRCLK_MON"] = 0xFC8A
        hk_data["VICLK"] = 0xFAE9
        # hk_data["VRCLK_LOW"] = 0x821A

        # hk_data["5VB_POS_MON"] = 0x1E6A
        hk_data["5VB_NEG_MON"] = 0x1A9F
        hk_data["3V3B_MON"] = 0xE75D
        hk_data["2V5A_MON"] = 0x1979
        hk_data["3V3D_MON"] = 0xE76E
        hk_data["2V5D_MON"] = 0x1A8C
        hk_data["1V5D_MON"] = 0xDF35
        hk_data["5VREF_MON"] = 0x1A80

        hk_data["VCCD_POS_RAW"] = 0x53BF
        hk_data["VCLK_POS_RAW"] = 0x40BA
        hk_data["VAN1_POS_RAW"] = 0x0744
        hk_data["VAN3_NEG_MON"] = 0xFB7C
        hk_data["VAN2_POS_RAW"] = 0x3AEC
        hk_data["VDIG_RAW"] = 0x0AB5
        # hk_data["VDIG_RAW_2"] = 0x0A32
        # hk_data["VICLK_LOW"] = 0x8277

        hk_data["CCD1_VRD_MON_F"] = 0x8059
        hk_data["CCD1_VDD_MON"] = 0x94CA
        hk_data["CCD1_VGD_MON"] = 0x8056
        hk_data["CCD2_VRD_MON_F"] = 0x8058
        hk_data["CCD2_VDD_MON"] = 0x94C1
        hk_data["CCD2_VGD_MON"] = 0x8055
        hk_data["CCD3_VRD_MON_F"] = 0x8059
        hk_data["CCD3_VDD_MON"] = 0x94C1
        hk_data["CCD3_VGD_MON"] = 0x8058
        hk_data["CCD4_VRD_MON_F"] = 0x8058
        hk_data["CCD4_VDD_MON"] = 0x94BA
        hk_data["CCD4_VGD_MON"] = 0x8056

        hk_data["IG_HI_MON"] = 0x8057
        # hk_data["IG_LO_MON"] = 0x8059
        hk_data["TSENSE_A"] = 0x8059
        hk_data["TSENSE_B"] = 0x805A

        hk_data["spw_timecode"] = 0x000D
        hk_data["rmap_target_status"] = 0x0000
        hk_data["rmap_target_indicate"] = 0x0000
        hk_data["spw_link_escape_error"] = 0x0000
        hk_data["spw_credit_error"] = 0x0000
        hk_data["spw_parity_error"] = 0x0000
        hk_data["spw_link_disconnect"] = 0x0000
        hk_data["spw_link_running"] = 0x0001

        hk_data["frame_counter"] = 0x0000
        hk_data["op_mode"] = 0x0000
        hk_data["frame_number"] = 0x0000

        hk_data["error_flags"] = 0x000C

        hk_data["FPGA minor version"] = 0x0018
        hk_data["FPGA major version"] = 0x0000
        hk_data["Board ID"] = 0x0000

    rich.print(hk_data)


def test_generate_data_packets_full_ccd():
    ccd_side = GlobalState.setup.camera.fee.ccd_sides.enum.E_SIDE
    ccd_id = 0  # ccd number [0-3]
    timecode = 62

    header = DataPacketHeader()

    packet_type = header.type_as_object
    packet_type.ccd_side = ccd_side
    packet_type.ccd_number = ccd_id
    packet_type.last_packet = False
    packet_type.frame_number = 2
    packet_type.mode = n_fee_mode.FULL_IMAGE_PATTERN_MODE
    header.type = packet_type

    # The pattern data includes 30 lines of parallel overscan data

    with Timer("Generate pattern data", log_level=logging.WARNING):
        data = create_pattern_data(timecode, ccd_id, ccd_side)

    # Generate a full image frame without parallel overscan

    v_start = 0
    v_end = 4509

    nr_lines = 0
    image = np.empty((0,), dtype=np.uint16)

    with Timer("Generate data packets", log_level=logging.WARNING):
        for packet in generate_data_packets(data, header, v_start, v_end):
            image = np.concatenate((image, packet.data_as_ndarray))
            nr_lines += len(packet.data_as_ndarray) // 2295

    image = image.reshape(nr_lines, 2295)
    logging.info(f"{image.shape = }")
    assert image.shape == (4510, 2295)


def test_generate_data_packets_including_overscan():
    ccd_side = GlobalState.setup.camera.fee.ccd_sides.enum.E_SIDE
    ccd_id = 0  # ccd number [0-3]
    timecode = 62

    header = DataPacketHeader()

    packet_type = header.type_as_object
    packet_type.ccd_side = ccd_side
    packet_type.ccd_number = ccd_id
    packet_type.last_packet = False
    packet_type.frame_number = 2
    packet_type.mode = n_fee_mode.FULL_IMAGE_PATTERN_MODE
    header.type = packet_type

    # The pattern data includes 30 lines of parallel overscan data

    with Timer("Generate pattern data"):
        data = create_pattern_data(timecode, ccd_id, ccd_side)

    # Generate CCD lines + parallel overscan lines

    LAST_IMAGE_LINE = 4509

    nr_ccd_lines = 10
    nr_overscan_lines = 50

    v_start = LAST_IMAGE_LINE - nr_ccd_lines + 1
    v_end = LAST_IMAGE_LINE + nr_overscan_lines

    ccd_lines_count = 0
    overscan_lines_count = 0
    image_ccd = np.empty((0,), dtype=np.uint16)
    image_overscan = np.empty((0,), dtype=np.uint16)

    image = ImageCreator(nr_ccd_lines + nr_overscan_lines, 2295)

    with Timer("Generate data packets"):
        for packet in generate_data_packets(data, header, v_start, v_end):
            if isinstance(packet, DataDataPacket):
                # image_ccd = np.concatenate((image_ccd, packet.data_as_ndarray))
                image.add_data(packet)
                ccd_lines_count += len(packet.data_as_ndarray) // 2295
            else:
                # image_overscan = np.concatenate((image_overscan, packet.data_as_ndarray))
                image.add_data(packet)
                overscan_lines_count += len(packet.data_as_ndarray) // 2295

    logging.info(f"{ccd_lines_count=}, {overscan_lines_count=}")

    image = image.get_image(ccd_side)  # this returns the transposed image
    logging.info(f"{image.shape = }")
    assert image.shape == (2295, nr_ccd_lines+nr_overscan_lines)

    image_ccd = image[:, 0:nr_ccd_lines]
    logging.info(f"{image_ccd.shape = }")
    assert image_ccd.shape == (2295, nr_ccd_lines)

    image_overscan = image[:, nr_ccd_lines:nr_ccd_lines+nr_overscan_lines]
    logging.info(f"{image_overscan.shape = }")
    assert image_overscan.shape == (2295, nr_overscan_lines)
