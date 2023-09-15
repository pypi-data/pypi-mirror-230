#!/usr/bin/env python3

from argparse import ArgumentParser
from egse.tempcontrol.spid.spid import PidProxy

parser = ArgumentParser()
parser.add_argument('channel', type=int, help='channel index')
parser.add_argument('setpoint', type=float, help='temperature setpoint')
parser.add_argument('enable', type=bool, help="Enable controller")

args = parser.parse_args()

p = PidProxy()

if args.enable:
    p.set_temperature(args.channel, args.setpoint)
    p.enable(args.channel)
else:
    p.disable(args.channel)
