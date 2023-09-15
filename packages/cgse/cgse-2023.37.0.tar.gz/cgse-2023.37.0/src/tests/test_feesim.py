"""
Testing the FEE Simulator:

Pre-requisites:

* start up the feesim as a process.

"""
import pytest
import timeit
import ctypes
import logging
import shlex
import subprocess

from contextlib import contextmanager
from ctypes import c_int

import egse.dsi.esl
import egse.dsi.constants

from egse.dsi.esl import esl_connection, ESLError
from egse.dsi.rmap import rmap_connection, rmap_read
from egse.dsi import constants
from egse.fee.feesim import FEESimulator
from egse.settings import Settings
from egse.system import ping

logger = logging.getLogger(__name__)

TIMEOUT_MS = 1000                # Timeout in milli seconds

dsi_settings = Settings.load("DSI")

dsi_available = True if ping(dsi_settings.DSI_FEE_IP_ADDRESS) else False


@contextmanager
def fee_simulator():
    """
    Context manager that starts the FEE Simulator in a sub-process.
    """

    cmd_line = f'python -m egse.fee.feesim --zeromq'
    args = shlex.split(cmd_line)
    logger.info(args)
    feesim = subprocess.Popen(args)
    try:
        yield feesim
    finally:
        feesim.terminate()


@pytest.mark.skip(reason="I'm working on this test...")
@pytest.mark.skipif(not dsi_available,
                    reason="requires DSI to be connected")
def test_mode_setting():

    with fee_simulator() as feesim:
        logger.info(f'FEE Simulator PID: {feesim.pid}')

        with esl_connection(dsi_settings.DSI_DPU_IP_ADDRESS) as esl_link, rmap_connection(esl_link) as rmap_link:

            status = egse.dsi.esl.esl_set_active_link(esl_link, 1)
            status = egse.dsi.esl.esl_set_speed(esl_link, dsi_settings.LINK_SPEED)
            status = egse.dsi.esl.esl_set_mode(esl_link, egse.dsi.constants.ESL_LINK_MODE_NORMAL)

            logger.info(f'Receive Timeout = {egse.dsi.esl.esl_get_receive_timeout(esl_link)} ms')
            egse.dsi.esl.esl_set_receive_timeout(esl_link, 2 * 1000)
            logger.info(f'Receive Timeout = {egse.dsi.esl.esl_get_receive_timeout(esl_link)} ms')

            egse.dsi.rmap.rmap_set_target_key(rmap_link, egse.dsi.constants.RMAP_TARGET_KEY)
            egse.dsi.rmap.rmap_set_target_logical_address(rmap_link, egse.dsi.constants.RMAP_TARGET_LOGICAL_ADDRESS_DEFAULT)

            rxbuf = ctypes.create_string_buffer(dsi_settings.RX_BUFFER_LENGTH)
            txbuf = ctypes.create_string_buffer(dsi_settings.TX_BUFFER_LENGTH)
            status = c_int(0)
            status_p = ctypes.pointer(status)

            # The following lines will run the read_write test count times.
            # I commented out the print statements so that the terminal output doesn't slow down the process.
            # Be careful also to set the logging level to INFO instead of DEBUG in the different parts.
            #
            # timeit (number=1000) returned about 16 sec to run over an ssh tunnel and about 14s without ssh tunneling

            count = 2
            wrapped = wrapper(do_read_write_test, rmap_link, rxbuf, txbuf, status_p)
            logger.info("{} runs took {} seconds".format(count, timeit.timeit(wrapped, number=count)))

            egse.dsi.esl.esl_close_connection(esl_link)

            while True:
                try:
                    feesim.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    continue
                break


def do_read_write_test(rmap_link, rxbuf, txbuf, status_p):

    try:
        data_length = rmap_read(rmap_link, 0, 16, TIMEOUT_MS)
        logger.info("rmap_read returned {} bytes, {}".format(data_length, rxbuf[:data_length]))

        # Change the 8 bytes [2:10] of the buffer and send an RMAP write command
        rxbuf[2:10] = [0xFF - i for i in range(8)]
        status = egse.dsi.rmap.rmap_write(rmap_link, 0, rxbuf, 8, status_p)

        data_length = egse.dsi.rmap.rmap_read(rmap_link, 0, txbuf, 16, status_p)
        logger.info("rmap_read returned {} bytes, {}".format(data_length, txbuf[:data_length]))

        # Clear the buffers

        rxbuf[:20] = [0 for i in range(20)]
        txbuf[:20] = [0 for i in range(20)]

        status = egse.dsi.rmap.rmap_write(rmap_link, 0, rxbuf, 8, status_p)

    except egse.dsi.rmap.RMAPError as re:
        logger.error("{}, status = {}".format(re, status_p.contents.value))


def wrapper(func, *args, **kwargs):
    """Allows a function to run with timeit."""
    def wrapped():
        return func(*args, **kwargs)
    return wrapped


@pytest.mark.skip(reason="I'm working on this test...")
@pytest.mark.skipif(not dsi_available,
                    reason="requires DSI to be connected")
def test_fee_sim_constructor(mocker):

    mock_esl_connection = mocker.patch('egse.feesim.esl_connection')
    mock_rmap_connection = mocker.patch('egse.feesim.rmap_connection')
    mock_esl_set_active_link = mocker.patch('egse.dsi.esl.esl_set_active_link')
    mock_esl_set_speed = mocker.patch('egse.dsi.esl.esl_set_speed')
    mock_esl_er_enable_reporting = mocker.patch('egse.dsi.esl.esl_er_enable_reporting')

    mock_esl_set_mode = mocker.patch('egse.dsi.esl.esl_set_mode')
    mock_rmap_set_initiator_logical_address = mocker.patch('egse.dsi.rmap.rmap_set_initiator_logical_address')
    mock_rmap_set_target_key = mocker.patch('egse.dsi.rmap.rmap_set_target_key')
    mock_rmap_set_target_logical_address = mocker.patch('egse.dsi.rmap.rmap_set_target_logical_address')
    mock_rmap_set_target_spw_address = mocker.patch('egse.dsi.rmap.rmap_set_target_spw_address')
    mock_esl_read_packet = mocker.patch('egse.dsi.esl.esl_read_packet')

    cm_mock = mocker.MagicMock()
    cm_mock.__enter__ = mocker.MagicMock(return_value=None)
    cm_mock.__exit__ = mocker.MagicMock(return_value=None)
    mock_esl_connection.return_value = cm_mock

    # Can we set side_effect here with a generator to return different values?

    def generate_normal_packets(esl):
        return constants.ESL_PART_EOP_EEP, bytes('Hello, World!'.encode())

    mock_esl_read_packet.side_effect = generate_normal_packets

    dsi_address = 'localhost'
    dsi_port = 1
    fee_sim = FEESimulator(dsi_address, dsi_port)
    assert fee_sim.current_state == egse.feesim.states.ST_ON
    assert fee_sim.decode_current_state() == 'ST_ON'

    with pytest.raises(ESLError):
        fee_sim.run()
