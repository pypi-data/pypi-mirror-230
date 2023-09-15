#!/usr/bin/env python3

from egse.tempcontrol.beaglebone.beaglebone import BeagleboneProxy

bbb = BeagleboneProxy()

for device in range(4):
    for channel in range(4):
        bbb.set_enable(device, channel, False)
        #print(bbb.get_current(device, channel))
