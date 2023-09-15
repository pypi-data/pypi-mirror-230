"""
Device control for the Thorlabs Power meter model PM100A that will be used during IAS TVAC.

This package contains the classes and modules to work with the Thorlabs Power meter Controller.

The main entry point for the user of this package is through the `ThorlabsPM100Proxy` class:

```python
>>> from egse.powermeter.thorlabs.pm100a import ThorlabsPM100Proxy
```

This class will connect to the control server of the Thorlabs PM100 Controller and provides all
commands to
control and monitor the photodiode sensor readout and status. The control server is a small
server application
that is started as shown below. The control server directly connects to the Powermeter Controller
through an Ethernet
interface. When you have now hardware available, the control server can be started in simulator
mode by appending the
`--sim` string to the command below.

```bash
$ python -m egse.powermeter.thorlabs.pm100a_cs
```
"""
