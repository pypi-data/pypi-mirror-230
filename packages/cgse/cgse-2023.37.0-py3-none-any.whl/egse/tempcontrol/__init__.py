"""
This package provides services for different kinds of temperature controllers.

The current on-going work is for support of the following devices:

* Keithley DAQ6510
* LakeShore Model 336
* National Instruments
* SRS PTC10 temperature regulator

"""
class TempError(Exception):
    pass

# The __pdoc__ dict is understood by pdoc3 and instructs to exclude the 'keys' from the documentation.
# See: https://pdoc3.github.io/pdoc/doc/pdoc/#overriding-docstrings-with-__pdoc__

# The following modules are excluded because they assume the gssw package is installed (SRON specific)

__pdoc__ = {
    'beaglebone': False,
    'spid': False,
}
