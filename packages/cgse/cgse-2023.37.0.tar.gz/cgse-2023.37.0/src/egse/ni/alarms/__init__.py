"""
Device control for the NI cdaq9375 that will be used at IAS for alarm manager.

This package contains the classes and modules to work with the Labview code running on Windows Keynes dealing with
CDAQ9375 .

The main entry point for the user of this package is through the `cdaq9375Proxy` class:

```python
>>> from egse.ni.alarms.cdaq9375 import cdaq9375Proxy
```

This class will connect to the control server of the CDAQ 9375 Controller and provides all
commands to
get alarms from the 2 EGSE UPS and from TVAC and send EGSE alarms to TVAC. The control server is a small
server application
that is started as shown below. The control server directly connects to the cdaq9375 readout Controller
through an Ethernet
interface. When you have no hardware available, the control server can be started in simulator
mode by appending the
`--sim` string to the command below.

```bash
$ python -m egse.ni.alarms.cdaq9375_cs
```
"""
