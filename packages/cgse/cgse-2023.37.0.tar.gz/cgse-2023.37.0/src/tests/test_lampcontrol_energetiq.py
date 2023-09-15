from functools import lru_cache

import pytest

from egse.exceptions import DeviceNotFoundError
from egse.lampcontrol import LampError
from egse.lampcontrol.energetiq.lampEQ99 import LampEQ99Controller
from egse.lampcontrol.energetiq.lampEQ99 import LampEQ99Simulator


@pytest.fixture
@lru_cache
def lamp():
    try:
        lamp = LampEQ99Controller()
        lamp.connect()
        lamp.disconnect()
        return lamp
    except (LampError, DeviceNotFoundError):
        return LampEQ99Simulator()


@pytest.mark.skip
def test_connection(lamp):

    print("***connection test started***")
    lamp.connect()

    try:
        _id = lamp.get_id()
        print("Is_connected?:", lamp.is_connected())

        lamp._beep()
        print("Well connected to:", _id)

    except LampError:
        assert False
    finally:
        print("*** end of test sequence ***")
        lamp.disconnect()


def test_errors(lamp):

    print("***error test started***")
    lamp.connect()
    print("Is_connected?:", lamp.is_connected())

    try:

        _errors = lamp.lamp_errors()
        print("There are currently the following errors in the system:", _errors)
        lamp.set_lamp(1) #this will create an error as no lamp is present

        print("Turning on the lamp without controller will generate a 603 error if the Lamp is not connectd to the controller (otherwise check):")

        _errors = lamp.lamp_errors()
        print(_errors)
        print("Resetting the lamp device")

        lamp.ldls_reset()

    except LampError:
        assert False
    finally:
        print("*** end of test sequence ***")
        lamp.disconnect()


@pytest.mark.skip
def test_status(lamp):

    print("***status test started***")
    lamp.connect()

    try:
        enable_state = lamp.get_lamp()
        print(enable_state)

        _status = lamp.get_lamp_status()
        print(_status)

    except LampError:
        assert False
    finally:
        print("*** end of test sequence ***")
        lamp.disconnect()


@pytest.mark.skip
def test_settings(lamp):

    print("***setting test started***")
    lamp.connect()

    try:
        print("trying to set lamp Runtime to 5 hours")
        lamp.set_lamp_time(5)
        print("Runtime has been set to:", lamp.get_lamp_time())

        print("trying to reset lamp Runtime to zero")
        lamp.set_lamp_time(0)
        print("Runtime has been set to:", lamp.get_lamp_time())

    except LampError:
        assert False
    finally:
        print("*** end of test sequence ***")
        lamp.disconnect()
