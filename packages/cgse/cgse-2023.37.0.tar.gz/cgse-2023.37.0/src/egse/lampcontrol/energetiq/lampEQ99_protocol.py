from egse.control import ControlServer
from egse.metrics import define_metrics
from egse.protocol import CommandProtocol
from egse.settings import Settings

from egse.lampcontrol.energetiq.lampEQ99 import LampEQ99Controller, LampEQ99Interface, LampEQ99Simulator
from egse.lampcontrol.energetiq.lampEQ99_devif import LampEQ99Command
from egse.synoptics import SynopticsManagerProxy
from egse.system import format_datetime
from egse.zmq_ser import bind_address
from egse.lampcontrol.energetiq.lampEQ99_encode_decode_errors import encode_lamp_errors

COMMAND_SETTINGS = Settings.load(filename="eq99.yaml")
SITE_ID = Settings.load("SITE").ID

class LampEQ99Protocol(CommandProtocol):
    def __init__(self, control_server: ControlServer):
        super().__init__()
        self.control_server = control_server

        if Settings.simulation_mode():
            self.lamp = LampEQ99Simulator()
        else:
            self.lamp = LampEQ99Controller()

        self.load_commands(COMMAND_SETTINGS.Commands, LampEQ99Command, LampEQ99Interface)

        self.build_device_method_lookup_table(self.lamp)

        self.metrics = define_metrics("EQ99")
        self.synoptics = SynopticsManagerProxy()

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

        _enable = self.lamp.get_lamp()
        _status = self.lamp.get_lamp_status()
        _time = self.lamp.get_lamp_time()

        errors = self.lamp.lamp_errors()
        list_code_errors = [int(error) for error in errors[len("Error Message: "):].split(",")[::2]]
        _encoded_errors = encode_lamp_errors(list_code_errors)

        _data = [_enable, _status, _time, _encoded_errors]

        # TODO Incl. the laser status

        for idx, key in enumerate([f"G{SITE_ID}_LAMP_ON", f"G{SITE_ID}_LAMP_STATUS", f"G{SITE_ID}_LAMP_ON_TIME", f"G{SITE_ID}_LAMP_ERRORS"]):
            result[key] = _data[idx]

        # TODO Incl. laser status ("G{SITE_ID}_LASER_ON") -> also update the TM dictionary

        for key, value in result.items():
            if key != "timestamp":
                self.metrics[key].set(value)

        self.synoptics.store_th_synoptics(result)

        return result
