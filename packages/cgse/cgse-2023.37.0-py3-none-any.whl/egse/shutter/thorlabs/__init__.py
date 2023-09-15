"""
This module defines the basic classes to access the Thorlabs Shutter KSC01 controller.

The main entry point for the user of this package is through the `ThorlabsPM100Proxy` class:

```python
>>> from egse.shutter.thorlabs.ksc101 import ShutterKSC101Proxy
```

This class will connect to the control server of the Thorlabs KSC101 Shutter Controller and provides all commands to
control and monitor the shutter status. The control server is a small server application
that is started as shown below. The control server directly connects to the Shutter Controller through an USB
interface. When you have now hardware available, the control server can be started in simulator mode by appending the
`--sim` string to the command below.

```bash
$ python -m egse.shutter.thorlabs.ksc101_cs
```
"""