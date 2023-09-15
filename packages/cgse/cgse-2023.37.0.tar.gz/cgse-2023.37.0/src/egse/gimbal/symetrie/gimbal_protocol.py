import logging

from egse.command import ClientServerCommand
from egse.control import ControlServer
from egse.device import DeviceConnectionState
from egse.gimbal.symetrie.gimbal import GimbalController
from egse.gimbal.symetrie.gimbal import GimbalInterface
from egse.gimbal.symetrie.gimbal import GimbalSimulator
from egse.hk import read_conversion_dict, convert_hk_names
from egse.protocol import CommandProtocol
from egse.settings import Settings
from egse.system import format_datetime
from egse.zmq_ser import bind_address
from egse.metrics import define_metrics

logger = logging.getLogger(__name__)

ctrl_settings = Settings.load("Gimbal Control Server")
gimbal_settings = Settings.load(filename="gimbal.yaml")


class GimbalCommand(ClientServerCommand):
    pass


class GimbalProtocol(CommandProtocol):
    def __init__(self, control_server: ControlServer):
        super().__init__()
        self.control_server = control_server

        self.hk_conversion_table = read_conversion_dict(self.control_server.get_storage_mnemonic(), use_site=True)

        if Settings.simulation_mode():
            self.gimbal = GimbalSimulator()
        else:
            self.gimbal = GimbalController()
            self.gimbal.add_observer(self)

        try:
            self.gimbal.connect()
        except ConnectionError as exc:
            logger.warning(
                f"Couldn't establish a connection to the Gimbal, check the log messages.")

        self.load_commands(gimbal_settings.Commands, GimbalCommand, GimbalInterface)
        self.build_device_method_lookup_table(self.gimbal)

        self.metrics = define_metrics(origin="GIMBAL", use_site=True)

    def get_bind_address(self):
        return bind_address(
            self.control_server.get_communication_protocol(),
            self.control_server.get_commanding_port(),
        )

    def get_status(self):

        status = super().get_status()

        if self.state == DeviceConnectionState.DEVICE_NOT_CONNECTED and not Settings.simulation_mode():
            return status

        mach_positions = self.gimbal.get_machine_positions()
        user_positions = self.gimbal.get_user_positions()
        actuator_length = self.gimbal.get_actuator_length()

        status.update({"mach": mach_positions, "user": user_positions, "alength": actuator_length})

        return status

    def get_housekeeping(self) -> dict:

        metrics_dict = self.metrics

        result = dict()
        result["timestamp"] = format_datetime()

        if self.state == DeviceConnectionState.DEVICE_NOT_CONNECTED and not Settings.simulation_mode():
            return result

        mach_positions = self.gimbal.get_machine_positions()
        user_positions = self.gimbal.get_user_positions()
        actuator_length = self.gimbal.get_actuator_length()

        # The result of the previous calls might be None when e.g. the connection
        # to the device gets lost.

        if mach_positions is None or user_positions is None or actuator_length is None:
            if not self.gimbal.is_connected():
                logger.warning("Gimbal disconnected.")
                self.update_connection_state(DeviceConnectionState.DEVICE_NOT_CONNECTED)
            return result

        for idx, key in enumerate(
            ["user_r_x", "user_r_y"]
        ):
            result[key] = user_positions[idx]

        for idx, key in enumerate(
            ["mach_r_x", "mach_r_y"]
        ):
            result[key] = mach_positions[idx]

        for idx, key in enumerate(
            ["alen_r_x", "alen_r_y"]
        ):
            result[key] = actuator_length[idx]

        # TODO:
        #   the get_general_state() method should be refactored as to return a dict instead of a
        #   list. Also, we might want to rethink the usefulness of returning the tuple,
        #   it the first return value ever used?

        _, _ = self.gimbal.get_general_state()

        result["Homing done"] = self.gimbal.is_homing_done()
        result["In position"] = self.gimbal.is_in_position()
        temperatures = self.gimbal.get_motor_temperatures()
        result["Temp_X"] = temperatures[0]
        result["Temp_Y"] = temperatures[1]
        hk_dict = convert_hk_names(result, self.hk_conversion_table)

        for hk_name in metrics_dict.keys():
            metrics_dict[hk_name].set(hk_dict[hk_name])    
            
        return hk_dict
    
    def is_device_connected(self):
        # FIXME(rik): There must be another way to check if the socket is still alive...
        #             This will send way too many VERSION requests to the controllers.
        #             According to SO [https://stackoverflow.com/a/15175067] the best way
        #             to check for a connection drop / close is to handle the exceptions
        #             properly.... so, no polling for connections by sending it a simple
        #             command.
        return self.gimbal.is_connected()
