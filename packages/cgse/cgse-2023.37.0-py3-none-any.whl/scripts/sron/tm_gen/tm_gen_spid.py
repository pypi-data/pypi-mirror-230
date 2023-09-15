from egse.state import GlobalState

setup = GlobalState.setup

channels = []
for category, channels in setup.gse.spid.configuration.heaters.items():
    for channel in channels:
        print(f'PID Controller;SPID;GSRON_PID_CH{channel[0]}_ENABLED;GSRON_PID_CH{channel[0]}_ENABLED;timestamp;;;;;{category};;;;;;;;;;')
        print(f'PID Controller;SPID;GSRON_PID_CH{channel[0]}_SETPOINT;GSRON_PID_CH{channel[0]}_SETPOINT;timestamp;;;;;{category};;DegCelsius;;;;;;;;')
        print(f'PID Controller;SPID;GSRON_PID_CH{channel[0]}_INPUT;GSRON_PID_CH{channel[0]}_INPUT;timestamp;;;;;{category};;DegCelsius;;;;;;;;')
        print(f'PID Controller;SPID;GSRON_PID_CH{channel[0]}_ERROR;GSRON_PID_CH{channel[0]}_ERROR;timestamp;;;;;{category};;DegCelsius;;;;;;;;')
        print(f'PID Controller;SPID;GSRON_PID_CH{channel[0]}_OUTPUT;GSRON_PID_CH{channel[0]}_OUTPUT;timestamp;;;;;{category};;;;;;;;;;')
        print(f'PID Controller;SPID;GSRON_PID_CH{channel[0]}_ISUM;GSRON_PID_CH{channel[0]}_ISUM;timestamp;;;;;{category};;;;;;;;;;')
