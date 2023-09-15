"""
Device control for the Symétrie's Gimbal

This package contains the modules and classes to work with the gimbal from [Symétrie](www.symetrie.fr).

The main entry point for the user of this package is through the terminal commands to start the
control server for the gimbal, along with the corresponding interactive GUI.

The following command starts the control server for the Gimbal in the background:

    $ gimbal_cs start-bg

The GUI can be started with the following command:

    $ gimbal_ui

For developers, the `GimbalProxy` class is the main interface to command the
hardware.

    >>> from egse.gimbal.symetrie.gimbal import GimbalProxy
    >>> gimbal = GimbalProxy()

This class will connect to its control server and provide all commands to
control the gimbal and monitor its position and status.

"""
