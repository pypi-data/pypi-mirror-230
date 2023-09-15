import logging
import sys

from time import time

from egse.hk import get_housekeeping
from egse.system import EPOCH_1958_1970
from egse.vacuum.beaglebone.beaglebone import BeagleboneProxy
from egse.vacuum.instrutech.igm402 import Igm402Proxy
# This script is run when the pressure in the vessel is too high.
# Indicating something wrong with the pump(s) or a leak.
# First the gate valve is closed. Then the LN2 valve. and finally the IGM402 filament is disabled.

MAXPRESSURE = 1.5E-6

log = logging.getLogger(__name__)
logging.basicConfig()

log.info(f'Running {__name__}')

# Try to connect to the Beaglebone Valve controller and IGM402 pressure gauge proxy

valves = BeagleboneProxy()
igm402 = Igm402Proxy()
if not valves.is_cs_connected():
    log.critical(f"Could not connect to Beaglebone Black proxy")
    sys.exit(f"Could not connect to Beaglebone Black proxy")
if not igm402.is_cs_connected():
    log.critical(f"Could not connect to IGM402 proxy")
    sys.exit(f"Could not connect to IGM402 proxy")    


# Get the most recent values from the housekeeping
igm402Timestamp, igm402Value = get_housekeeping("GSRON_IGM402_IG_P") 
tpg261Timestamp, tpg261Value, = get_housekeeping("GSRON_TPG261_P_1")

igm402Age = time() - (float(igm402Timestamp) - EPOCH_1958_1970)
tpg261Age = time() - (float(tpg261Timestamp) - EPOCH_1958_1970)

# Ensure that these values are not too old
if igm402Age > 60:
    raise Exception(f"IGM402 HK is more than 60 seconds old")

if tpg261Age > 60:
    raise Exception(f"TPG261 HK is more than 60 seconds old")
log.info(f"IGM402 - Current value: {igm402Value}, Max: {MAXPRESSURE}")
log.info(f"TPG261 - Current value: {tpg261Value}, Max: {MAXPRESSURE}")

# Make sure that both pressure gauges are exeecuding their limits
if float(igm402Value) > float(MAXPRESSURE):
    if float(tpg261Value) > float(MAXPRESSURE):
        # Close the gate valve
        log.info("Closing Gate valve")
        # log.debug("set_valve, MV001, False")
        valves.set_valve('MV001', False)

        # Close the LN2 valves
        log.info("Closing the LN2 valves")
        for i in range(1, 5):
            # log.debug(f"set_valve, MV01{i}, False")
            valves.set_valve(f"MV01{i}", False)

        log.info("Turning off IG filament")
        # log.debug("set_filament_enable, False")
        igm402.set_filament_enable(False)
    else:
        log.info(f"TPG261 is still in a safe range: {tpg261Value}")
else:
    log.info(f"IGM402 is still in a safe range: {igm402Value}")
    
log.info(f'Finished {__name__}')
