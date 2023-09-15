#!/usr/bin/env python3

import logging
import time

from argparse import ArgumentParser

from egse.tempcontrol.beaglebone.beaglebone import BeagleboneProxy

log = logging.getLogger(__name__)
logging.basicConfig()

parser = ArgumentParser()
parser.add_argument('device', type=int, help='beaglebone device index [0, 1]')
parser.add_argument('channel', type=int, help='beaglebone pwm channel [0, 3]')
parser.add_argument('setpoint', type=int, help='pwm duty cycle in %%')
args = parser.parse_args()

assert args.device in [0, 1, 2, 3], 'device index must be in [0 - 3]'
assert args.channel in [0, 1, 2, 3], 'pwm channel must be in [0 - 3]'
assert args.setpoint in range(0, 101), 'pwm duty cycle must be in [0 - 100]'

try:
    beaglebone = BeagleboneProxy()
except Exception as e:
    log.error(f'could not connect to beaglebone control server ({e})')
else:
    log.info('connected to beaglebone control server')

try:
    beaglebone.set_period(args.device, args.channel, 10000)
    beaglebone.set_duty_cycle(args.device, args.channel, (args.setpoint * 100))
    if args.setpoint == 0:
        beaglebone.set_enable(args.device, args.channel, False)
    else:
        beaglebone.set_enable(args.device, args.channel, True)
except Exception as e:
    log.error(f'could not set duty cycle ({e})')

while True:
    time.sleep(1)
    print(beaglebone.get_voltage(args.device, args.channel), 'V')
    print(beaglebone.get_current(args.device, args.channel), 'A')
    print(beaglebone.get_power(args.device, args.channel), 'W')
