for board in range(6):
    for channel in range(4):
        print(f'Beaglebone Temperature Control;BBB_HEATERS;GSRON_HTR_I_{board}_{channel};GSRON_HTR_I_{board}_{channel};timestamp;;;;;Current of beaglebone {board} heater {channel};;Ampère;;;;;;;;')
        print(f'Beaglebone Temperature Control;BBB_HEATERS;GSRON_HTR_V_{board}_{channel};GSRON_HTR_V_{board}_{channel};timestamp;;;;;Voltage of beaglebone {board} heater {channel};;Volts;;;;;;;;')
