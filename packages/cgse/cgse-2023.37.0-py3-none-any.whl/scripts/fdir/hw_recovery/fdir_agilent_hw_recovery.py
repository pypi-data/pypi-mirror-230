import logging
from argparse import ArgumentParser

import sys
from numpy import mean
from time import time

from egse.hk import get_housekeeping
from egse.state import GlobalState
from egse.system import EPOCH_1958_1970
from egse.tempcontrol.beaglebone.beaglebone import BeagleboneProxy
from egse.tempcontrol.spid.spid import PidProxy

# This script is triggered when one of the agilent DAQs becomes unresponsive.
# This script is called with the agilent index as argument.
# All PID channels driven by a sensor connected to the DAQ are disabled.
# All corresponding heaters are set to the last value given by the PID.

log = logging.getLogger(__name__)
logging.basicConfig()

log.info(f'running {__name__}')

parser = ArgumentParser()
parser.add_argument('device_index', type=int, help='DAQ device index [0 - 3]')
args = parser.parse_args()

# Try to get the setup from the SM.
setup = GlobalState.setup

# Try to get device proxies.
bb_proxy = BeagleboneProxy()
pid_proxy = PidProxy()

if not bb_proxy.is_cs_connected():
    log.crticial("Could not connect to Beaglebone proxy")
    sys.exit("Could not connect to Beaglebone proxy")
if not pid_proxy.is_cs_connected():
    log.crticial("Could not connect to PID proxy")
    sys.exit("Could not connect to PID proxy")

pid_channels = []
for l in setup.gse.spid.configuration.heaters.values():
    pid_channels.extend(l)

# Turn off all PID channels controlled by this DAQ and set the heater power to the last value.
for (channel, agilent_idx, _, beaglebone_idx, beaglebone_ch, _, _, _) in pid_channels:

    if agilent_idx == args.device_index:

        # Calculate the average duty cycle over the last minute before shutting down
        hk_name = f"GSRON_PID_CH{channel}_OUTPUT"
        timestamp, values = get_housekeeping(hk_name=hk_name, time_window=60)
        if time() - (float(timestamp[-1]) - EPOCH_1958_1970) > 30:
            sys.exit("Retrieved duty cycles are more than a minute old")
             
        values = [float(val) for val in values]
        duty_cycle = mean(values)
        
            # Read heater power before disabling PID channel.
        pid_proxy.disable(channel=channel)
        log.info(f'Disabled PID channel {channel}')

        # Set heater power to last value.

        bb_proxy.set_duty_cycle(beaglebone_idx, beaglebone_ch, int(duty_cycle * 10000))
        bb_proxy.set_enable(beaglebone_idx, beaglebone_ch, True)
        log.info(f'Set heater {beaglebone_idx}.{beaglebone_ch} to (fixed) {duty_cycle * 100} %')

    else:
        log.info(f"PID channel #{channel} not associated with DAQ #{args.device_index}")

log.info(f'finished {__name__}')
