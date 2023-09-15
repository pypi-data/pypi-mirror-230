"""This script runs a dummy control server for test purposes."""
import logging

from egse.dummy import DummyControlServer
from egse.settings import Settings

logging.basicConfig(
    # filename="cs.log",
    # filemode='w',
    format=Settings.LOG_FORMAT_FULL,
    datefmt=Settings.LOG_FORMAT_DATE,
    level=logging.DEBUG
)

if __name__ == "__main__":
    cs = DummyControlServer()
    cs.serve()
