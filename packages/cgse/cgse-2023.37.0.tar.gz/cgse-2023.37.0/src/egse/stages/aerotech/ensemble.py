import enum
import logging
import time

from prometheus_client import Gauge

from egse.control import ControlServer
from egse.command import ClientServerCommand
from egse.protocol import CommandProtocol
from egse.proxy import Proxy
from egse.settings import Settings
from egse.zmq_ser import bind_address
from egse.system import format_datetime
from egse.stages.aerotech.ensemble_interface import EnsembleInterface
from egse.stages.aerotech.ensemble_controller import EnsembleController
from egse.stages.aerotech.ensemble_simulator import EnsembleSimulator
from egse.zmq_ser import connect_address

PLANESTATUS = {
    0: "MotionActive",
    1: "ProfilingActive",
    2: "AccelPhase",
    3: "DecelPhase",
    4: "MotionAbort",
    5: "HoldMode"
}

AXISFAULT = {
    0:  "PositionError",
    1:  "OverCurrent",
    2:  "CwEOTLimit",
    3:  "CcwEOTLimit",
    4:  "CwSoftLimit",
    5:  "CcwSoftLimit",
    6:  "AmplifierFault",
    7:  "PositionFbk",
    8:  "VelocityFbk",
    9:  "HallFault",
    10: "MaxVelocity",
    11: "EstopFault",
    12: "VelocityError",
    15: "ExternalFault",
    17: "MotorTemp",
    18: "AmplifierTemp",
    19: "EncoderFault",
    20: "CommLost",
    23: "FbkScalingFault",
    24: "MrkSearchFault",
    27: "VoltageClamp",
    28: "PowerSupply",
    30: "Internal"
}
AXISSTATUS = {
    0:  "Enabled",
    1:  "Homed",
    2:  "InPosition",
    3:  "MoveActive",
    4:  "AccelPhase",
    5:  "DecelPhase",
    6:  "PositionCapture",
    7:  "CurrentClamp",
    8:  "BreakOutput",
    9:  "MotionIsCw",
    10: "MsSlControl",
    11: "CalActivate",
    12: "CalEnabled",
    13: "JoystickControl",
    14: "Homing",
    15: "MasterSuppress",
    16: "GantryActive",
    17: "GantryMaster",
    18: "AutofocusActive",
    19: "CommandFilterDone",
    20: "InPosition2",
    21: "ServoControl",
    22: "CwEOTLimit",
    23: "CcwEOTLimit",
    24: "HomeLimit",
    25: "MarketInput",
    26: "HallAInput",
    27: "HallBInput",
    28: "HallCInput",
    29: "SinEncErr",
    30: "CSinEncErr",
    21: "ESTOPInput"
}

LOGGER = logging.getLogger(__name__)

DEVICE_SETTINGS = Settings.load(filename="ensemble.yaml")
CTRL_SETTINGS = Settings.load("Aerotech Ensemble Control Server")


class EnsembleCommand(ClientServerCommand):
    pass


class EnsembleProtocol(CommandProtocol):

    def __init__(self, control_server: ControlServer):

        super().__init__()
        self.control_server = control_server

        if Settings.simulation_mode():
            self.dev = EnsembleSimulator()
        else:
            self.dev = EnsembleController()

        self.gauge_actual_position_x     = Gauge('GSRON_ENSEMBLE_ACT_POS_X', '')
        self.gauge_actual_position_y     = Gauge('GSRON_ENSEMBLE_ACT_POS_Y', '')
        self.gauge_command_position_x    = Gauge('GSRON_ENSEMBLE_CMD_POS_X', '')
        self.gauge_command_position_y    = Gauge('GSRON_ENSEMBLE_CMD_POS_Y', '')
        self.gauge_error_position_x      = Gauge('GSRON_ENSEMBLE_ERR_POS_X', '')
        self.gauge_error_position_y      = Gauge('GSRON_ENSEMBLE_ERR_POS_Y', '')
        self.gauge_actual_current_x      = Gauge('GSRON_ENSEMBLE_ACT_CUR_X', '')
        self.gauge_actual_current_y      = Gauge('GSRON_ENSEMBLE_ACT_CUR_Y', '')
        self.gauge_command_current_x     = Gauge('GSRON_ENSEMBLE_CMD_CUR_X', '')
        self.gauge_command_current_y     = Gauge('GSRON_ENSEMBLE_CMD_CUR_Y', '')

        self.gauge_actual_velocity_x     = Gauge('GSRON_ENSEMBLE_ACT_VEL_X', '')
        self.gauge_actual_velocity_y     = Gauge('GSRON_ENSEMBLE_ACT_VEL_Y', '')
        self.gauge_command_velocity_x    = Gauge('GSRON_ENSEMBLE_CMD_VEL_X', '')
        self.gauge_command_velocity_y    = Gauge('GSRON_ENSEMBLE_CMD_VEL_Y', '')

        self.gauge_power_x               = Gauge('GSRON_ENSEMBLE_POWER_X', '')
        self.gauge_power_y               = Gauge('GSRON_ENSEMBLE_POWER_Y', '')
        self.gauge_status_x              = [
            Gauge(f'GSRON_ENSEMBLE_STATUS_X_{status}', '') for status in AXISSTATUS.values()]
        self.gauge_status_y              = [
            Gauge(f'GSRON_ENSEMBLE_STATUS_Y_{status}', '') for status in AXISSTATUS.values()]
        self.gauge_fault_x               = [
            Gauge(f'GSRON_ENSEMBLE_FAULT_X_{fault}', '') for fault in AXISFAULT.values()]
        self.gauge_fault_y               = [
            Gauge(f'GSRON_ENSEMBLE_FAULT_Y_{fault}', '') for fault in AXISFAULT.values()]
        self.gauge_status_plane          = [
            Gauge(f'GSRON_ENSEMBLE_STATUS_PLANE_{status}', '') for status in PLANESTATUS.values()]
        
        self.load_commands(DEVICE_SETTINGS.Commands, EnsembleCommand, EnsembleInterface)
        self.build_device_method_lookup_table(self.dev)


    # move to parent class?
    def get_bind_address(self):

        return bind_address(
            self.control_server.get_communication_protocol(),
            self.control_server.get_commanding_port(),
        )


    def get_status(self):

        status_dict = super().get_status()

        status_dict["alpha"] = self.dev.get_actual_position(axis="X")   # [degrees]
        status_dict["beta"] = self.dev.get_actual_position(axis="Y")    # [degrees]

        return status_dict


    def get_housekeeping(self) -> dict:

        result = dict()

        result["timestamp"] = format_datetime()
        try:
            result["GSRON_ENSEMBLE_STATUS_PLANE"]   = self.dev.get_plane_status()
            result["GSRON_ENSEMBLE_STATUS_X"]       = self.dev.get_status(axis='X')
            result["GSRON_ENSEMBLE_STATUS_Y"]       = self.dev.get_status(axis='Y')
            result["GSRON_ENSEMBLE_FAULT_X"]        = self.dev.get_fault(axis='X')
            result["GSRON_ENSEMBLE_FAULT_Y"]        = self.dev.get_fault(axis='Y')
            result["GSRON_ENSEMBLE_ACT_POS_X"]      = self.dev.get_actual_position(axis='X')
            result["GSRON_ENSEMBLE_ACT_POS_Y"]      = self.dev.get_actual_position(axis='Y')
            result["GSRON_ENSEMBLE_CMD_POS_X"]      = self.dev.get_command_position(axis='X')
            result["GSRON_ENSEMBLE_CMD_POS_Y"]      = self.dev.get_command_position(axis='Y')
            result["GSRON_ENSEMBLE_ERR_POS_X"]      = self.dev.get_error_position(axis='X')
            result["GSRON_ENSEMBLE_ERR_POS_Y"]      = self.dev.get_error_position(axis='Y')
            result["GSRON_ENSEMBLE_ACT_CUR_X"]      = self.dev.get_actual_current(axis='X')
            result["GSRON_ENSEMBLE_ACT_CUR_Y"]      = self.dev.get_actual_current(axis='Y')
            result["GSRON_ENSEMBLE_CMD_CUR_X"]      = self.dev.get_command_current(axis='X')
            result["GSRON_ENSEMBLE_CMD_CUR_Y"]      = self.dev.get_command_current(axis='Y')
            result["GSRON_ENSEMBLE_CMD_VEL_X"]      = self.dev.get_command_velocity(axis='X')
            result["GSRON_ENSEMBLE_CMD_VEL_Y"]      = self.dev.get_command_velocity(axis='Y')
            result["GSRON_ENSEMBLE_ACT_VEL_X"]      = self.dev.get_actual_velocity(axis='X')
            result["GSRON_ENSEMBLE_ACT_VEL_Y"]      = self.dev.get_actual_velocity(axis='Y')

            # calculate the power dissipated
            result["GSRON_ENSEMBLE_POWER_X"]        = float(result["GSRON_ENSEMBLE_ACT_CUR_X"]) * 60.0 * (3/2)
            result["GSRON_ENSEMBLE_POWER_Y"]        = float(result["GSRON_ENSEMBLE_ACT_CUR_Y"]) * 60.0 * (3/2)

            # LOGGER.debug(f"PACT: {result['GSRON_ENSEMBLE_ACT_POS_Y']}, \
            #                PCMD: {result['GSRON_ENSEMBLE_CMD_POS_Y']}, \
            #                IACT: {result['GSRON_ENSEMBLE_ACT_CUR_Y']}, \
            #                ICMD: {result['GSRON_ENSEMBLE_CMD_CUR_Y']}")

        except Exception as exc:
            LOGGER.error(f"Exception getting HK: {exc}")

        self.gauge_actual_position_x.set(result["GSRON_ENSEMBLE_ACT_POS_X"])
        self.gauge_actual_position_y.set(result["GSRON_ENSEMBLE_ACT_POS_Y"])
        self.gauge_command_position_x.set(result["GSRON_ENSEMBLE_CMD_POS_X"])
        self.gauge_command_position_y.set(result["GSRON_ENSEMBLE_CMD_POS_Y"])
        self.gauge_actual_current_x.set(result['GSRON_ENSEMBLE_ACT_CUR_X'])
        self.gauge_actual_current_y.set(result['GSRON_ENSEMBLE_ACT_CUR_Y'])
        self.gauge_command_current_x.set(result["GSRON_ENSEMBLE_CMD_CUR_X"])
        self.gauge_command_current_y.set(result["GSRON_ENSEMBLE_CMD_CUR_Y"])
        self.gauge_actual_velocity_x.set(result["GSRON_ENSEMBLE_ACT_VEL_X"])
        self.gauge_actual_velocity_y.set(result["GSRON_ENSEMBLE_ACT_VEL_Y"])
        self.gauge_command_velocity_x.set(result["GSRON_ENSEMBLE_CMD_VEL_X"])
        self.gauge_command_velocity_y.set(result["GSRON_ENSEMBLE_CMD_VEL_Y"])

        self.gauge_power_x.set(result["GSRON_ENSEMBLE_POWER_X"])
        self.gauge_power_y.set(result["GSRON_ENSEMBLE_POWER_Y"])

        for idx, _ in enumerate(AXISSTATUS):
            self.gauge_status_x[idx].set((result["GSRON_ENSEMBLE_STATUS_X"] >> idx) & 0b1)
            self.gauge_status_y[idx].set((result["GSRON_ENSEMBLE_STATUS_Y"] >> idx) & 0b1)

        for idx, _ in enumerate(AXISFAULT):
            self.gauge_fault_x[idx].set((result["GSRON_ENSEMBLE_FAULT_X"] >> idx) & 0b1)
            self.gauge_fault_y[idx].set((result["GSRON_ENSEMBLE_FAULT_Y"] >> idx) & 0b1)
        
        for idx, _ in enumerate(PLANESTATUS):
            self.gauge_status_plane[idx].set((result['GSRON_ENSEMBLE_STATUS_PLANE'] >> idx) & 0b1)
        
        # Check X axis EoT limits
        if result['GSRON_ENSEMBLE_FAULT_X'] & 0x04:
            LOGGER.warning("X axis clockwise End-of-Travel limit has been reached")
        if result['GSRON_ENSEMBLE_FAULT_X'] & 0x08:
            LOGGER.warning("X axis counterclockwise End-of-Travel limit has been reached")
        
        # Check Y axis EoT limits 
        if result['GSRON_ENSEMBLE_FAULT_Y'] & 0x04:
            LOGGER.warning("Y axis clockwise End-of-Travel limit has been reached")
        if result['GSRON_ENSEMBLE_FAULT_Y'] & 0x08:
            LOGGER.warning("Y axis counterclockwise End-of-Travel limit has been reached")

        return result


class EnsembleProxy(Proxy, EnsembleInterface):

    def __init__(self):
        super().__init__(
            connect_address(
                CTRL_SETTINGS.PROTOCOL, CTRL_SETTINGS.HOSTNAME, CTRL_SETTINGS.COMMANDING_PORT), timeout=500000)
