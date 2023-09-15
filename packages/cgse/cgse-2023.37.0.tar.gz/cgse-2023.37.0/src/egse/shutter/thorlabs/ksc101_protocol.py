from egse.control import ControlServer
from egse.metrics import define_metrics
from egse.protocol import CommandProtocol
from egse.settings import Settings

from egse.shutter.thorlabs.ksc101 import ShutterKSC101Controller
from egse.shutter.thorlabs.ksc101 import ShutterKSC101Interface
from egse.shutter.thorlabs.ksc101 import ShutterKSC101Simulator
from egse.shutter.thorlabs.ksc101_devif import ShutterKSC101Command
from egse.synoptics import SynopticsManagerProxy
from egse.system import format_datetime
from egse.zmq_ser import bind_address

COMMAND_SETTINGS = Settings.load(filename="ksc101.yaml")


class ShutterKSC101Protocol(CommandProtocol):
    def __init__(self, control_server: ControlServer):
        super().__init__()
        self.control_server = control_server

        if Settings.simulation_mode():
            self.shutter = ShutterKSC101Simulator()
        else:
            self.shutter = ShutterKSC101Controller()

        self.load_commands(COMMAND_SETTINGS.Commands, ShutterKSC101Command, ShutterKSC101Interface)

        self.build_device_method_lookup_table(self.shutter)

        self.synoptics = SynopticsManagerProxy()
        self.metrics = define_metrics("KSC101")

    def get_bind_address(self):
        return bind_address(
            self.control_server.get_communication_protocol(),
            self.control_server.get_commanding_port(),
        )

    def get_status(self):
        return super().get_status()

    def get_housekeeping(self) -> dict:

        result = dict()
        result["timestamp"] = format_datetime()

        _enable = self.shutter.get_enable()
        _mode = self.shutter.get_mode()
        _cycles = self.shutter.get_cycle()

        _parameters = list()
        for v in _cycles.values():
            _parameters.append(v)

        _status = [_enable, _mode, _cycles, _parameters[0], _parameters[1], _parameters[2]]

        for idx, key in enumerate(["GIAS_KSC101_ENABLE", "GIAS_KSC101_MODE", "GIAS_KSC101_CYCLE_CONFIG"]):
            result[key] = _status[idx]

        for key, value in result.items():
            if key != "timestamp" and key != "GIAS_KSC101_CYCLE_CONFIG":
                # TODO Prometheus doesn't seem to be able to deal with dictionaries (GIAS_KSC101_CYCLE_CONFIG)
                self.metrics[key].set(value)

        self.synoptics.store_th_synoptics(result)

        return result

