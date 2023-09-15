import logging

import pyvisa
from ThorlabsPM100 import ThorlabsPM100

from egse.command import ClientServerCommand
from egse.exceptions import DeviceNotFoundError
from egse.settings import Settings

logger = logging.getLogger(__name__)

ctrl_settings = Settings.load("Thorlabs PM100 Controller")


class ThorlabsError(Exception):
    """Base exception for all Thorlabs errors."""

    pass


class ThorlabsPM100Command(ClientServerCommand):
    def get_cmd_string(self, *args, **kwargs) -> str:
        out = super().get_cmd_string(*args, **kwargs)
        return out + "\n"


class ThorlabsPM100USBInterface:
    def __init__(self):
        self._visa_rm = pyvisa.ResourceManager()
        self._visa_inst = None
        self._power_meter = None
        self._is_connected = False

    def connect(self):
        # FIXME: Learn how to find resources with VISA and select the correct resource, based on
        #  vendor 0x1313 (=4883)
        #  and product id 0x8079 (=32889)
        try:
            self._visa_inst = self._visa_rm.open_resource(ctrl_settings.VISA_RESOURCE)

        except (ValueError, Exception) as exc:
            logger.warning(f"Could not open USB device P1001855: {exc}")
            raise DeviceNotFoundError("Could not open USB device P1001855.") from exc
        self._power_meter: ThorlabsPM100 = ThorlabsPM100(inst=self._visa_inst)

        self._is_connected = True


    def disconnect(self):
        self._visa_inst.close()
        self._power_meter = None
        self._is_connected = False

    def is_connected(self):
        """Return True if the device is connected."""
        if not self._is_connected:
            return False

        try:
            self.get_id()
        except OSError:  # FIXME: Check which errors are actually thrown here
            self.disconnect()
            return False

        return True

    def info(self):
        return f"Thorlabs PM100A Power Meter: {self.get_id()}."

    def get_response(self, cmd_string):
        logger.debug(f"get_response() called with {cmd_string}")
        return NotImplemented

    def get_value(self):
        return self._power_meter.read

    def get_average(self):
        return self._power_meter.sense.average.count

    def set_average(self, average: int):
        "Sets the averaging rate (1 sample takes approx. 3ms)"
        self._power_meter.sense.average.count = average

    def get_id(self):
        return self._power_meter.system.sensor.idn

    def get_wavelength(self):
        return self._power_meter.sense.correction.wavelength

    def get_range(self):
        range = self._power_meter.sense.power.dc.range.upper
        auto = self._power_meter.sense.power.dc.range.auto
        return {"range": range, "auto": auto}

    def get_diameter(self):
        return self._power_meter.sense.correction.beamdiameter

    def get_autozero(self):
        zero = self._power_meter.sense.correction.collect.zero.state
        magnitude = self._power_meter.sense.correction.collect.zero.magnitude
        return {"set": zero, "magnitude (W)": magnitude}

    def set_wavelength(self, wave: int):
        self._power_meter.sense.correction.wavelength = wave

    def autorange(self, auto: int):
        self._power_meter.sense.power.dc.range.auto = auto

    def range(self, range: float):
        self._power_meter.sense.power.dc.range.upper = range

    def set_diameter(self, diameter: float):
        self._power_meter.sense.correction.beamdiameter = diameter

    def set_zero(self, autozero: bool):
        if autozero:
            self._power_meter.sense.correction.collect.zero.initiate()
        else:
            self._power_meter.sense.correction.collect.zero.abort()

    @property
    def power_meter(self):
        return self._power_meter

    @property
    def instrument(self):
        return self._visa_inst
