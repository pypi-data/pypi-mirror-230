"""
This module is a mix-in for device simulator classes.
All non device specific things are handled in this class.
"""

from egse.device import DeviceInterface


class Simulator(DeviceInterface):

    def __init__(self):
        self._connected = False


    def connect(self):
        """ Connect to the device controller. """
        self._connected = True


    def disconnect(self):
        """ Disconnect from the device controller. """
        self._connected = False


    def reconnect(self):
        """ Reconnect the device controller. """
        self._connected = True


    def is_connected(self):
        """ Check if the device is connected.

            True if the device is connected and responds to a command, False otherwise.
        """
        return self._connected


    def is_simulator(self):
        """ Ask if the device class is a Simulator instead of the real Controller. """

        return True
