import logging

from egse.control import ControlServer
from egse.metrics import define_metrics
from egse.protocol import CommandProtocol
from egse.settings import Settings

from egse.system import format_datetime
from egse.zmq_ser import bind_address

from egse.tempcontrol.lakeshore.lsci import (LakeShoreController, LakeShoreInterface, LakeShoreSimulator)
from egse.tempcontrol.lakeshore.lsci_devif import LakeShoreCommand

from egse.synoptics import SynopticsManagerProxy

logger = logging.getLogger(__name__)

COMMAND_SETTINGS = Settings.load(filename="lsci.yaml")
SITE_ID = Settings.load("SITE").ID


class LakeShoreProtocol(CommandProtocol):
    def __init__(self, control_server: ControlServer, device_index):
        super().__init__()
        self.control_server = control_server
        self.device_index = device_index
        if Settings.simulation_mode():
            self.lakeshore = LakeShoreSimulator()
        else:
            self.lakeshore = LakeShoreController(device_index)

        self.load_commands(COMMAND_SETTINGS.Commands, LakeShoreCommand, LakeShoreInterface)

        self.build_device_method_lookup_table(self.lakeshore)
        
        self.synoptics = SynopticsManagerProxy()
        
        self.metrics = define_metrics(origin="LSCI", use_site=True)

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
            hk_dict[f"G{SITE_ID}_LSCI_{self.device_index}_TEMP_A"] = self.lakeshore.get_temperature()
            pidParams = self.lakeshore.get_params_pid(1)
            hk_dict[f"G{SITE_ID}_LSCI_{self.device_index}_P_VALUE"] = pidParams[0]
            hk_dict[f"G{SITE_ID}_LSCI_{self.device_index}_I_VALUE"] = pidParams[1]
            hk_dict[f"G{SITE_ID}_LSCI_{self.device_index}_D_VALUE"] = pidParams[2]
            hk_dict[f"G{SITE_ID}_LSCI_{self.device_index}_HEATER_VALUE"] = self.lakeshore.get_heater(1)
            hk_dict[f"G{SITE_ID}_LSCI_{self.device_index}_SET_POINT_VALUE"] = self.lakeshore.get_setpoint(1)

            for hk_name in metrics_dict.keys():
                index_lsci = hk_name.split("_")
                if(len(index_lsci) > 2):
                    if int(index_lsci[2]) ==  int(self.device_index):
                        metrics_dict[hk_name].set(hk_dict[hk_name])

            # Send the HK acquired so far to the Synoptics Manager
            self.synoptics.store_th_synoptics(hk_dict)

        except Exception as exc:
            logger.warning(f'failed to get HK ({exc})')
        return hk_dict
