"""
The TCS EGSE (Thermal Control System) is responsible for the thermal control of the PLATO Camera
Telescope Optical Unit (TOU).
"""

from .tcs import OperatingMode
from .tcs import ClosedLoopMode
from .tcs import TCSError

__all__ = [
    "TCSError",
    "OperatingMode",
    "ClosedLoopMode",
]
