import logging
import sys
import time

from egse.control import ControlServer
from egse.device import DeviceConnectionState
from egse.hk import convert_hk_names
from egse.hk import read_conversion_dict
from egse.metrics import define_metrics
from egse.process import SubProcess
from egse.protocol import DynamicCommandProtocol
from egse.settings import Settings
from egse.stages.huber.smc9300 import HuberSMC9300Controller
from egse.stages.huber.smc9300 import HuberSMC9300Interface
from egse.system import format_datetime
from egse.zmq_ser import bind_address

HUBER_SETTINGS = Settings.load(filename="smc9300.yaml")
STAGES_SETTINGS = Settings.load("Huber Controller")

MODULE_LOGGER = logging.getLogger(__name__)


class HuberSMC9300Protocol(DynamicCommandProtocol):
    def __init__(self, control_server: ControlServer):
        super().__init__(control_server)

        self.huber_sim: SubProcess
        self.huber = HuberSMC9300Interface

        storage_mnemonic = self.get_control_server().get_storage_mnemonic()

        self.hk_conversion_table = read_conversion_dict(storage_mnemonic, use_site=True)

        if Settings.simulation_mode():
            # In simulation mode, we start the simulator process and have the control server
            # connect to that process instead of the hardware.
            self.huber_sim = SubProcess("SMC9300 Simulator",
                                        [sys.executable, "-m", "egse.stages.huber.smc9300_sim", "start"])
            self.huber_sim.execute(detach_from_parent=True)
            time.sleep(2.0)  # Allow the simulator time to start up
            self.huber = HuberSMC9300Controller(hostname="localhost")
        else:
            self.huber_sim = None
            self.huber = HuberSMC9300Controller()

        self.huber.add_observer(self)

        try:
            self.huber.connect()
        except ConnectionError as exc:
            MODULE_LOGGER.warning(
                "Couldn't establish a connection to the HUBER Stages, check the log messages.")
            MODULE_LOGGER.debug(f"{exc = }")

        self.metrics = define_metrics(storage_mnemonic, use_site=True)

    def quit(self):
        if self.huber_sim is not None:
            self.huber_sim.quit()

    def get_bind_address(self):
        return bind_address(
            self.get_control_server().get_communication_protocol(),
            self.get_control_server().get_commanding_port(),
        )

    def get_device(self):
        return self.huber

    # @timer()  # 20220621: takes about 50ms
    def get_status(self):

        status = super().get_status()

        # Position of the stages:
        #   - Commanded angle of the big rotation stage [degrees]
        #   - Commanded angle of the small rotation stage [degrees]
        #   - Commanded distance for the translation stage [mm]

        status["big_rotation_stage_position"] = self.huber.get_current_position(STAGES_SETTINGS.BIG_ROTATION_STAGE)
        status["small_rotation_stage_position"] = self.huber.get_current_position(STAGES_SETTINGS.SMALL_ROTATION_STAGE)
        status["translation_stage_position"] = self.huber.get_current_position(STAGES_SETTINGS.TRANSLATION_STAGE)

        return status

    # @timer()  # 20220621: takes less than 200ms
    def get_housekeeping(self) -> dict:

        response = {"timestamp": format_datetime()}

        if self.state == DeviceConnectionState.DEVICE_CONNECTED or Settings.simulation_mode():
            response.update({
                "axis 1 - cur_pos": self.huber.get_current_position(axis=1),
                "axis 2 - cur_pos": self.huber.get_current_position(axis=2),
                "axis 3 - cur_pos": self.huber.get_current_position(axis=3),
                "axis 1 - enc_pos": self.huber.get_current_encoder_position(axis=1),
                "axis 2 - enc_pos": self.huber.get_current_encoder_position(axis=2),
                "axis 3 - enc_pos": self.huber.get_current_encoder_position(axis=3),
                "axis 1 - enc_cnt": self.huber.get_current_encoder_counter_value(axis=1),
                "axis 2 - enc_cnt": self.huber.get_current_encoder_counter_value(axis=2),
                "axis 3 - enc_cnt": self.huber.get_current_encoder_counter_value(axis=3),
            })

        hk = convert_hk_names(response, self.hk_conversion_table)

        for key, value in hk.items():
            if key != "timestamp":
                self.metrics[key].set(value)

        return hk
