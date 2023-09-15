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

# TODO: turn of vacscan filament
# TODO: close gate valve

log.info('Turn of IGM402 filament')
igm402.set_filament_enable(enable=False)

log.info('Shut down TC400')
tc400.set_pumpingstation(enable=False)

log.info('Waiting for tc400 to reach 50 Hz...')
while (tc400.get_active_speed() > 50):
    sleep(1)

log.info('Shut down ACP40')
acp40.set_enable(enable=False)

log.info('Done')
