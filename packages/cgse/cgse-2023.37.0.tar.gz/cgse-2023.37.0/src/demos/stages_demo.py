"""
A simple demo script for sending commands to the HUBER Stages.

Run this script from the Terminal as:
```
export PYTHONPATH=....
cd src/demo
python stages_demo.py
```
"""

import logging

from egse.settings import Settings
from egse.stages.huber.smc9300 import HuberSMC9300Proxy as Stages
from egse.stages.huber.smc9300 import HuberSMC9300Simulator as Stages

logging.basicConfig(level=logging.DEBUG)

ctrl_settings = Settings.load("Huber Controller")

stages = Stages()

stages.goto(ctrl_settings.BIG_ROTATION_STAGE, 20)
print(stages.get_current_position(ctrl_settings.BIG_ROTATION_STAGE))

stages.goto(ctrl_settings.BIG_ROTATION_STAGE, 20, False)
print(stages.get_current_position(ctrl_settings.BIG_ROTATION_STAGE))

stages.goto(ctrl_settings.BIG_ROTATION_STAGE, 10, wait=True)
print(stages.get_current_position(ctrl_settings.BIG_ROTATION_STAGE))

stages.goto(ctrl_settings.BIG_ROTATION_STAGE, position=5, wait=True)
print(stages.get_current_position(ctrl_settings.BIG_ROTATION_STAGE))

stages.goto(axis=ctrl_settings.BIG_ROTATION_STAGE, position=5, wait=True)
print(stages.get_current_position(ctrl_settings.BIG_ROTATION_STAGE))

