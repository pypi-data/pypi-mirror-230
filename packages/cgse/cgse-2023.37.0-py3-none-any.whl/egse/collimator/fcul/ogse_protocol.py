import logging
import sys
import time

from egse.collimator.fcul.ogse import OGSEController
from egse.collimator.fcul.ogse import OGSEInterface
from egse.control import ControlServer
from egse.control import Failure
from egse.device import DeviceConnectionError
from egse.device import DeviceTimeoutError
from egse.metrics import define_metrics
from egse.metrics import update_metrics
from egse.process import SubProcess
from egse.protocol import DynamicCommandProtocol
from egse.settings import Settings
from egse.state import GlobalState
from egse.synoptics import SynopticsManagerProxy
from egse.system import format_datetime

DEVICE_SETTINGS = Settings.load(filename="ogse.yaml")
SITE = Settings.load("SITE")

MODULE_LOGGER = logging.getLogger(__name__)


class OGSEProtocol(DynamicCommandProtocol):
    def __init__(self, control_server: ControlServer):
        super().__init__(control_server)

        self.ogse_sim: SubProcess
        self.device = OGSEInterface

        self.fwc_calibration = GlobalState.setup.gse.ogse.calibration.fwc_calibration

        if Settings.simulation_mode():
            # In simulation mode, we start the simulator process and have the control server
            # connect to that process instead of the hardware.
            self.ogse_sim = SubProcess("OGSE Simulator",
                                       [sys.executable, "-m", "egse.collimator.fcul.ogse_sim", "start"])
            self.ogse_sim.execute(detach_from_parent=True)
            time.sleep(2.0)  # Allow the simulator time to start up
            self.device = OGSEController(hostname="localhost")
        else:
            self.ogse_sim = None
            self.device = OGSEController()

        self.device.add_observer(self)

        try:
            self.device.connect()
        except DeviceConnectionError as exc:
            MODULE_LOGGER.warning(
                "Couldn't establish a connection to the OGSE, check the log messages.")
            MODULE_LOGGER.debug(f"{exc = }")
        except ValueError as exc:
            MODULE_LOGGER.warning(exc)
        except DeviceTimeoutError as exc:
            MODULE_LOGGER.warning(exc)

        self.synoptics = SynopticsManagerProxy()
        self.metrics = define_metrics(origin="OGSE", dashboard="GOGSE_MON", use_site=True)

    def quit(self):
        if self.synoptics is not None:
            MODULE_LOGGER.info("Disconnecting from Synoptics Manager...")
            self.synoptics.disconnect_cs()

        if self.ogse_sim is not None:
            MODULE_LOGGER.info("Terminating the OGSE Simulator...")
            self.ogse_sim.quit()

    def get_device(self):
        return self.device

    def get_status(self):
        return super().get_status()

    def get_housekeeping(self) -> dict:

        hk = {"timestamp": format_datetime()}

        ogse_status = self.device.status()

        if isinstance(ogse_status, Failure):
            MODULE_LOGGER.info(
                "Failure detected while requesting the status of the OGSE. "
                "No housekeeping generated. Check the log file for more information on the cause."
            )
            MODULE_LOGGER.error(f"Failure: {ogse_status}", exc_info=False)
            return hk

        ogse_laser = self.device.get_laser()

        hk[f"G{SITE.ID}_OGSE_LDLS_LAMP"] = ogse_status["lamp"] == "ON"
        hk[f"G{SITE.ID}_OGSE_LDLS_LASER"] = ogse_laser == "laser: ON"
        hk[f"G{SITE.ID}_OGSE_PM_CH1_PWR"] = ogse_status["power1"]
        hk[f"G{SITE.ID}_OGSE_PM_CH2_PWR"] = ogse_status["power2"]
        hk[f"G{SITE.ID}_OGSE_REL_INTENSITY"] = ogse_status["att_factor"]
        hk[f"G{SITE.ID}_OGSE_FWC_FRACTION"] = ogse_status["att_factor"] / self.fwc_calibration

        # Send the HK acquired so far to the Synoptics Manager

        hk_for_synoptics = hk.copy()

        # The GOGSE_SHUTTER_OPEN parameter is not in the CSL OGSE HK but is included in the synoptics

        if "CSL" in SITE.ID:
            hk_for_synoptics[f"G{SITE.ID}_OGSE_SHUTTER_OPEN"] = True

        self.synoptics.store_th_synoptics(hk_for_synoptics)

        hk[f"G{SITE.ID}_OGSE_LDLS_INTERLOCK"] = ogse_status["interlock"] == "ON"
        hk[f"G{SITE.ID}_OGSE_LDLS_POWER"] = ogse_status["power"] == "ON"
        hk[f"G{SITE.ID}_OGSE_LDLS_PSU"] = ogse_status["psu"] == "ON"
        hk[f"G{SITE.ID}_OGSE_PM_CH1_TEMP"] = ogse_status["temp1"]
        hk[f"G{SITE.ID}_OGSE_PM_CH2_TEMP"] = ogse_status["temp2"]
        hk[f"G{SITE.ID}_OGSE_LDLS_LAMP_FAULT"] = self.device.get_lamp_fault() == "lamp-fault: NO-ERROR"
        hk[f"G{SITE.ID}_OGSE_LDLS_CTRL_FAULT"] = self.device.get_controller_fault() == "controller-fault: NO-ERROR"
        hk[f"G{SITE.ID}_OGSE_LDLS_OPERATE"] = self.device.get_operate() == "operate: ON"
        hk[f"G{SITE.ID}_OGSE_FW_MOVING"] = ogse_status["att_moving"]

        pm_status = self.device.pm_status()

        hk[f"G{SITE.ID}_OGSE_PM_CH1_STATUS"] = pm_status["pm1"] == "OK"
        hk[f"G{SITE.ID}_OGSE_PM_CH2_STATUS"] = pm_status["pm2"] == "OK"

        update_metrics(self.metrics, {name: hk[name] for name in hk if name in self.metrics})

        return hk
