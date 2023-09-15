import pytest
from ThorlabsPM100 import ThorlabsPM100
from pyvisa.resources.usb import USBInstrument

from egse.exceptions import DeviceNotFoundError
from egse.powermeter.thorlabs.pm100a import ThorlabsPM100Controller
from egse.powermeter.thorlabs.pm100a_devif import ThorlabsError


def connect_to_pm100():
    try:
        pw = ThorlabsPM100Controller()
        pw.info()
    except (DeviceNotFoundError, ThorlabsError):
        return False
    pw.disconnect()
    return True


pm100_available = True if connect_to_pm100() else False


@pytest.mark.skipif(not pm100_available,
                    reason="requires Thorlabs PM100 to be connected")
def test_pm100_controller():

    pw = ThorlabsPM100Controller()
    pw.connect()
    assert isinstance(pw.get_value(), float)
    assert pw.get_id() == 'S121C,13112508,25-Nov-2013,1,18,289'
    assert isinstance(pw.power_meter, ThorlabsPM100)
    assert isinstance(pw.instrument, USBInstrument)

    pw.power_meter.sense.correction.wavelength = 400
    assert pw.power_meter.sense.correction.wavelength == 400
    pw.power_meter.sense.correction.wavelength = 800
    assert pw.power_meter.sense.correction.wavelength == 800
    pw.power_meter.system.beeper.immediate()

    pw.disconnect()

