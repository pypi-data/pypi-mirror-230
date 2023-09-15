"""
The Gimbal package provides the components to interact with the gimbal of
Symétrie, i.e.

* The Gimbal commanding concept with Command, and CommandProtocol
* The client server access through Proxy and ControlServer
* The interface to the hardware controller: HexapodController and its simulator

This package also contains the Gimbal GUI which can be used to monitor the
gimbal positions in different reference frames and apply simple movements.

"""


class GimbalError(Exception):
    """A Gimbal specific error."""
    pass


# These are the classes and function that we would like to export. This is mainly
# to simplify import statements in scripts. The user can now use the following:
#
#    >>> from egse.gimbal import GimbalProxy
#
# while she previously had to import the class as follows:
#
#    >>> from egse.gimbal.gimbalProxy import GimbalProxy
#

__all__ = [
    'GimbalError',
]
