import logging
from prometheus_client import Gauge

from egse.control import ControlServer
from egse.metrics import define_metrics
from egse.protocol import CommandProtocol
from egse.settings import Settings
from egse.synoptics import SynopticsManagerProxy

from egse.system import format_datetime
from egse.zmq_ser import bind_address

from egse.filterwheel.eksma.fw8smc4 import (FilterWheel8SMC4Controller, FilterWheel8SMC4Interface,
                                            FilterWheel8SMC4Simulator)
from egse.filterwheel.eksma.fw8smc4_devif import FilterWheel8SMC4Command

logger = logging.getLogger(__name__)

DEVICE_SETTINGS = Settings.load(filename="fw8smc4.yaml")
SITE_ID = Settings.load("SITE").ID


class FilterWheel8SMC4Protocol(CommandProtocol):
    def __init__(self, control_server: ControlServer):
        super().__init__()
        self.control_server = control_server

        if Settings.simulation_mode():
            self.filterwheel = FilterWheel8SMC4Simulator()
        else:
            self.filterwheel = FilterWheel8SMC4Controller()

        self.filterwheel.connect()

        self.load_commands(DEVICE_SETTINGS.Commands, FilterWheel8SMC4Command, FilterWheel8SMC4Interface)

        self.build_device_method_lookup_table(self.filterwheel)

        # self.fwc_calibration = GlobalState.setup.gse.ogse.calibration.fwc_calibration     TODO

        self.synoptics = SynopticsManagerProxy()
        self.metrics = define_metrics(origin="FW8SMC4", use_site=True)

    def get_bind_address(self):
        return bind_address(
            self.control_server.get_communication_protocol(),
            self.control_server.get_commanding_port(),
        )

    def get_status(self):
        return super().get_status()

    def get_housekeeping(self) -> dict:

        metrics_dict = self.metrics
        hk_dict = dict()
        hk_dict["timestamp"] = format_datetime()
        try:
            # relative_intensity = self.filterwheel.get_relative_intensity()      # TODO Use the correct command name

            # hk_dict["G{SITE_ID}_FW8SMC4_REL_INTENSITY"] = relative_intensity                          # TODO
            # hk_dict["G{SITE_ID}_FW8SMC4_FWC_FRACTION"] = relative_intensity / self.fwc_calibration,   # TODO

            # self.synoptics.store_th_synoptics(hk_dict)    TODO Uncomment when the relative intensity + FWC fraction are available
            # TODO Update the TM dictionary (entry for the HK + for the synoptics)

            filterwheel_motor_positions = self.filterwheel.get_position()
            filterwheel_status = self.filterwheel.get_status()

            hk_values = [filterwheel_motor_positions[0], filterwheel_motor_positions[1], filterwheel_status[2], filterwheel_status[3], filterwheel_status[4]]
            hk_dict.update({hk_name: hk_value for hk_name, hk_value in zip(metrics_dict.keys(), hk_values)})

            for hk_name in metrics_dict.keys():
                metrics_dict[hk_name].set(hk_dict[hk_name])

            # Send the HK acquired so far to the Synoptics Manager
            self.synoptics.store_th_synoptics(hk_dict)
        except Exception as exc:
            logger.warning(f'failed to get HK ({exc})')

        return hk_dict
