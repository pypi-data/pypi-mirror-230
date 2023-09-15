"""
This package defines all classes and functions that work with
stages, stepper motors, and multi-axes motion controllers.
"""


class StagesError(Exception):
    """A Stages specific error."""
    pass


__all__ = ['StagesError']
