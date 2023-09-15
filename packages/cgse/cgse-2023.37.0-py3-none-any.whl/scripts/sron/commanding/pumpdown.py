#!/usr/bin/env python3

import logging
from time import sleep

from egse.vacuum.instrutech.igm402 import Igm402Proxy
from egse.vacuum.pfeiffer.tc400 import Tc400Proxy
from egse.vacuum.pfeiffer.acp40 import Acp40Proxy

log = logging.getLogger(__name__)
logging.basicConfig()

igm402 = Igm402Proxy()
tc400 = Tc400Proxy()
acp40 = Acp40Proxy()

# TODO: check vessel door interlock
# TODO: open gate valve

log.info('Starting ACP40')
acp40.set_enable(enable=True)

log.info('Waiting for pressure to reach 6E-0 mbar...')
while (igm402.get_cgn_pressure(index=1) > 6E-0):
    sleep(1)
log.info('Starting TC400')
tc400.set_pumpingstation(enable=True)
tc400.set_motorpump(enable=True)

log.info('Waiting for pressure to reach 1.1E-3 mbar...')
while (igm402.get_cgn_pressure(index=1) > 1.1E-3):
    last_error = tc400.get_last_error()
    if last_error != 0:
        log.error(f'TC400 error: {last_error}')
        tc400.set_pumpingstation(enable=False)
        exit()
    sleep(1)

# log.info('Turn on ionization gauge')
igm402.set_filament_enable(enable=True)

log.info('Waiting for pressure to reach 1E-5 mbar...')
while (igm402.get_ion_gauge_pressure() > 1E-5):
    sleep(1)

log.info('Ready for cooling')
