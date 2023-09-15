import logging

from egse.control import ControlServer
from egse.device import DeviceTimeoutError
from egse.hk import read_conversion_dict
from egse.metrics import define_metrics
from egse.protocol import CommandProtocol
from egse.settings import Settings
from egse.state import GlobalState
from egse.synoptics import SynopticsManagerProxy
from egse.system import format_datetime
from egse.tempcontrol.keithley.daq6510 import DAQ6510Controller
from egse.tempcontrol.keithley.daq6510 import DAQ6510Interface
from egse.tempcontrol.keithley.daq6510 import DAQ6510Simulator
from egse.tempcontrol.keithley.daq6510_devif import DAQ6510Command
from egse.zmq_ser import bind_address

COMMAND_SETTINGS = Settings.load(filename="daq6510.yaml")

MODULE_LOGGER = logging.getLogger(__name__)


class DAQ6510Protocol(CommandProtocol):
    def __init__(self, control_server: ControlServer):
        super().__init__()
        self.control_server = control_server

        if Settings.simulation_mode():
            self.daq = DAQ6510Simulator()
        else:
            self.daq = DAQ6510Controller()

        try:
            self.daq.connect()
        except (ConnectionError, DeviceTimeoutError) as exc:
            MODULE_LOGGER.warning(
                f"Couldn't establish a connection to the DAQ6510, check the log messages.")

        self.load_commands(COMMAND_SETTINGS.Commands, DAQ6510Command, DAQ6510Interface)
        self.build_device_method_lookup_table(self.daq)

        self.channels = GlobalState.setup.gse.DAQ6510.channels

        self.hk_conversion_table = read_conversion_dict(self.control_server.get_storage_mnemonic())

        self.synoptics = SynopticsManagerProxy()
        self.metrics = define_metrics(origin="DAS-DAQ6510", use_site=True)

    def get_bind_address(self):
        return bind_address(
            self.control_server.get_communication_protocol(),
            self.control_server.get_commanding_port(),
        )

    def get_status(self):
        return super().get_status()

    def get_housekeeping(self) -> dict:

        hk_dict = dict()
        hk_dict["timestamp"] = format_datetime()

        # # TODO I guess we have to do something along those lines
        # # (We'll have to increase the HK delay, cfr. Agilents)
        # measurement = self.daq.perform_measurement(channel_list=self.channels)
        # temperatures = convert_hk_names(measurement, self.hk_conversion_table)
        # hk_dict.update(temperatures)
        #
        # self.synoptics.store_th_synoptics(hk_dict)
        #
        # for key, value in hk_dict.items():
        #     if key != "timestamp":
        #         self.metrics[key].set(value)

        return hk_dict

    def quit(self):
        self.synoptics.disconnect_cs()
