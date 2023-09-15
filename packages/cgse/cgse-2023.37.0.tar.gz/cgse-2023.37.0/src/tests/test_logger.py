import logging

from egse.logger import egse_logger, create_new_zmq_logger


def test_logging_exception():

    try:
        raise ValueError("incorrect value entered.")
    except ValueError as exc:
        egse_logger.exception("Reporting a ValueError")


def test_logging_error():

    try:
        raise ValueError("incorrect value entered.")
    except ValueError as exc:
        egse_logger.error("Reporting a ValueError")
        egse_logger.error("Reporting a ValueError with exc_info", exc_info=True)


def test_create_new_zmq_logger():

    camtest_logger = create_new_zmq_logger("camtest")

    camtest_logger.info("First message with ZeroMQ handler in camtest logger")

    logger = logging.getLogger("camtest.sub_level")

    logger.info("Message from sub_level logger should be categorised under camtest_logger")

    # See what happens if we call the function twice with the same logger

    camtest_logger = create_new_zmq_logger("camtest")

    # If the following message appears twice in the general.log logfile then a second handler
    # was created by the create_new_zmq_logger function.

    camtest_logger.info("Created the zmq handler twice?")
