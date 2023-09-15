from prometheus_client import Gauge

from egse.control import ControlServer
from egse.powermeter.thorlabs.pm100a import ThorlabsPM100Controller
from egse.powermeter.thorlabs.pm100a import ThorlabsPM100Interface
from egse.powermeter.thorlabs.pm100a import ThorlabsPM100Simulator
from egse.powermeter.thorlabs.pm100a_devif import ThorlabsPM100Command
from egse.protocol import CommandProtocol
from egse.settings import Settings
from egse.synoptics import SynopticsManagerProxy
from egse.system import format_datetime
from egse.zmq_ser import bind_address

COMMAND_SETTINGS = Settings.load(filename="pm100a.yaml")
SITE_ID = Settings.load("SITE").ID

gauge_power = Gauge(f"G{SITE_ID}_PM100A_POWER", "")
gauge_average = Gauge(f"G{SITE_ID}_PM100A_AVERAGE", "")
gauge_correction_wavelength = Gauge(f"G{SITE_ID}_PM100A_COR_WAVELENGTH", "")
gauge_autorange = Gauge(f"G{SITE_ID}_PM100A_AUTORANGE", "")
gauge_power_range = Gauge(f"G{SITE_ID}_PM100A_POWER_RANGE", "")
gauge_autozero = Gauge(f"G{SITE_ID}_PM100A_AUTOZERO", "")
gauge_magnitude = Gauge(f"G{SITE_ID}_PM100A_MAGNITUDE", "")


class ThorlabsPM100Protocol(CommandProtocol):
    def __init__(self, control_server: ControlServer):
        super().__init__()
        self.control_server = control_server

        if Settings.simulation_mode():
            self.thorlabs = ThorlabsPM100Simulator()
        else:
            self.thorlabs = ThorlabsPM100Controller()

        self.load_commands(COMMAND_SETTINGS.Commands, ThorlabsPM100Command, ThorlabsPM100Interface)

        self.build_device_method_lookup_table(self.thorlabs)

        self.synoptics = SynopticsManagerProxy()

    def get_bind_address(self):
        return bind_address(
            self.control_server.get_communication_protocol(),
            self.control_server.get_commanding_port(),
        )

    def get_status(self):
        status_dict = super().get_status()
        status_dict['pm100a_power'] = self.thorlabs.get_value()
        return status_dict

    def get_housekeeping(self) -> dict:
        _range = self.thorlabs.get_range()
        _autozero = self.thorlabs.get_autozero()

        hk_dict = dict()
        hk_dict["timestamp"] = format_datetime()

        hk_dict[f"G{SITE_ID}_PM100A_POWER"] = self.thorlabs.get_value()

        # Send the HK acquired so far to the Synoptics Manager
        self.synoptics.store_th_synoptics(hk_dict)

        hk_dict[f"G{SITE_ID}_PM100A_AVERAGE"] = self.thorlabs.get_average()
        hk_dict[f"G{SITE_ID}_PM100A_COR_WAVELENGTH"] = self.thorlabs.get_wavelength()
        hk_dict[f"G{SITE_ID}_PM100A_AUTORANGE"] = _range["auto"]
        hk_dict[f"G{SITE_ID}_PM100A_POWER_RANGE"] = _range["range"]
        hk_dict[f"G{SITE_ID}_PM100A_AUTOZERO"] = _autozero["set"]
        hk_dict[f"G{SITE_ID}_PM100A_MAGNITUDE"] = _autozero["magnitude (W)"]

        gauge_power.set(hk_dict[f"G{SITE_ID}_PM100A_POWER"])
        gauge_average.set(hk_dict[f"G{SITE_ID}_PM100A_AVERAGE"])
        gauge_correction_wavelength.set(hk_dict[f"G{SITE_ID}_PM100A_COR_WAVELENGTH"])
        gauge_autorange.set(hk_dict[f"G{SITE_ID}_PM100A_AUTORANGE"])
        gauge_power_range.set(hk_dict[f"G{SITE_ID}_PM100A_POWER_RANGE"])
        gauge_autozero.set(hk_dict[f"G{SITE_ID}_PM100A_AUTOZERO"])
        gauge_magnitude.set(hk_dict[f"G{SITE_ID}_PM100A_MAGNITUDE"])

        return hk_dict
