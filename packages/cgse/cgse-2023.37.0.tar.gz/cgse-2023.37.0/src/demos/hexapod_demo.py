"""
A simple demo script for sending commands to the PUNA Hexapod from Symetrie.

Run this script from the Terminal as:
```
export PYTHONPATH=....
cd src/demo
python hexapod_demo.py
```
"""

import logging
logging.basicConfig(level=logging.INFO)

from egse.hexapod.symetrie.puna import PunaProxy as Hexapod
from egse.hexapod.symetrie.puna import PunaSimulator as Hexapod

hexapod = Hexapod()

if not hexapod.is_simulator():
    print(hexapod.get_commands())

hexapod.goto_zero_position()
print(f"Before move_absolute: {hexapod.get_user_positions()}")
hexapod.move_absolute(0.0, 0.0, 1.0, 0.0, 0.0, 45.0)
print(f"After move_absolute: {hexapod.get_user_positions()}")

hexapod.log_positions()
