from egse.control import ControlServer
from egse.protocol import CommandProtocol
from egse.settings import Settings
from datetime import datetime
from prometheus_client import Gauge

from egse.tempcontrol.spid.spid_controller import PidController
from egse.tempcontrol.spid.spid import PidInterface, PidSimulator, PidCommand
from egse.system import format_datetime
from egse.zmq_ser import bind_address
from egse.confman import ConfigurationManagerProxy


COMMAND_SETTINGS = Settings.load(filename='spid.yaml')


class PidProtocol(CommandProtocol):

    def __init__(self, control_server:ControlServer):

        super().__init__()
        self.control_server = control_server

        if Settings.simulation_mode():
            self.pid = PidSimulator()
        else:
            self.pid = PidController()

        self.load_commands(COMMAND_SETTINGS.Commands, PidCommand, PidInterface)

        self.build_device_method_lookup_table(self.pid)

        # Get PID channels form the setup
        with ConfigurationManagerProxy() as cm:
            heaters = cm.get_setup().gse.spid.configuration.heaters

        # Get the list of PID channe    ls [pid_idx, agilent_idx, agilent_ch, bbb_idx, bbb_ch, P, I]
        self.channels = [channel for heater in heaters.values() for channel in heater]
    

        self.gauges_enabled = [Gauge(f'GSRON_PID_CH{channel[0]}_ENABLED', '') for channel in self.channels]
        self.gauges_setpoint = [Gauge(f'GSRON_PID_CH{channel[0]}_SETPOINT', '') for channel in self.channels]
        self.gauges_input = [Gauge(f'GSRON_PID_CH{channel[0]}_INPUT', '') for channel in self.channels]
        self.gauges_error = [Gauge(f'GSRON_PID_CH{channel[0]}_ERROR', '') for channel in self.channels]
        self.gauges_output = [Gauge(f'GSRON_PID_CH{channel[0]}_OUTPUT', '') for channel in self.channels]
        self.gauges_isum = [Gauge(f'GSRON_PID_CH{channel[0]}_ISUM', '') for channel in self.channels]


    def get_bind_address(self):

        return bind_address(self.control_server.get_communication_protocol(),
                            self.control_server.get_commanding_port())


    def get_status(self):

        status_info = super().get_status()
        now = datetime.now()
        enabled     = {f"{ch[3]}_{ch[4]}" : self.pid.running[ch[0]] for ch in self.channels}
        setpoint    = [self.pid.setpoints[ch[0]] for ch in self.channels]
        temperature = [self.pid.temperature[ch[0]] for ch in self.channels]
        timestamp   = [self.pid.timestamp[ch[0]] for ch in self.channels]
        error       = [self.pid.errors[ch[0]] for ch in self.channels]
        isum        = [self.pid.isum[ch[0]] for ch in self.channels]
        t_input      = [self.pid.inputs[ch[0]] for ch in self.channels]
        output      = [self.pid.outputs[ch[0]] for ch in self.channels]
        pid_const   = [[self.pid.pids[ch[0]].Kp, self.pid.pids[ch[0]].Ki, self.pid.pids[ch[0]].Kd] for ch in self.channels]

        
        status_info['Enabled']      = enabled
        status_info['Setpoint']     = setpoint
        status_info['Temperature']  = temperature
        status_info['Timestamp']    = timestamp
        status_info['Error']        = error
        status_info['Isum']         = isum
        status_info['Input']        = t_input
        status_info['Output']       = output
        status_info['PidConst']     = pid_const
        
        return status_info


    def get_housekeeping(self) -> dict:

        hk_dict = {'timestamp': format_datetime()}

        for channel in self.channels:

            hk_dict[f'GSRON_PID_CH{channel[0]}_ENABLED'] = int(self.pid.running[channel[0]])
            hk_dict[f'GSRON_PID_CH{channel[0]}_SETPOINT'] = self.pid.setpoints[channel[0]]
            hk_dict[f'GSRON_PID_CH{channel[0]}_INPUT'] = self.pid.inputs[channel[0]]
            hk_dict[f'GSRON_PID_CH{channel[0]}_ERROR'] = self.pid.errors[channel[0]]
            hk_dict[f'GSRON_PID_CH{channel[0]}_OUTPUT'] = self.pid.outputs[channel[0]]
            hk_dict[f'GSRON_PID_CH{channel[0]}_ISUM'] = self.pid.pids[channel[0]].integral

            self.gauges_enabled[channel[0]].set(hk_dict[f'GSRON_PID_CH{channel[0]}_ENABLED'])
            self.gauges_setpoint[channel[0]].set(hk_dict[f'GSRON_PID_CH{channel[0]}_SETPOINT'])
            self.gauges_input[channel[0]].set(hk_dict[f'GSRON_PID_CH{channel[0]}_INPUT'])
            self.gauges_error[channel[0]].set(hk_dict[f'GSRON_PID_CH{channel[0]}_ERROR'])
            self.gauges_output[channel[0]].set(hk_dict[f'GSRON_PID_CH{channel[0]}_OUTPUT'])
            self.gauges_isum[channel[0]].set(hk_dict[f'GSRON_PID_CH{channel[0]}_ISUM'])

        return hk_dict
    
    def quit(self):
        self.pid.disconnect()
        super().quit()
