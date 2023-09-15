"""
Device control for the NI photodiode meter model cdaq9184 that will be used during IAS TVAC.

This package contains the classes and modules to work with the Thorlabs Power meter Controller.

The main entry point for the user of this package is through the `cdaq9184Proxy` class:

```python
>>> from egse.powermeter.ni.cdaq9184 import cdaq9184Proxy
```

This class will connect to the control server of the CDAQ 9184 Controller and provides all
commands to
control and monitor the photodiode sensor readout and status. The control server is a small
server application
that is started as shown below. The control server directly connects to the cdaq9184 readout Controller
through an Ethernet
interface. When you have now hardware available, the control server can be started in simulator
mode by appending the
`--sim` string to the command below.

CDAQ9184 has 4 NI slots that will be equipped with NI9226, NI9239 and NI9219 compact daqs.

NI9239 will read the voltage signal from the 2x photodiodes inside the integrating sphere.
Current to voltage is converted and pre amplified by TIAs.
NI9226 will read 3x PT100 4 wire sensors: 2x on each collimator extremity, 1x on the integrating sphere in order
to perform thermal drift compensations of the photodiodes' signals.
In the final config NI9219 stays as a backup daq, to be used whenever needed -but the code does not read now any
output from it-.

All these signals can be read (mean and dev from 5 samples acquired at 100Hz) and will be required to monitor the
flux of the OGSE if an integrating sphere is used in the setup. It can then provide the capability to perform
Long term stability test as well as to monitor the full flux range from cam_tvpt_080_dynamic_range.py (tbc).

```bash
$ python -m egse.powermeter.ni.cdaq9184_cs
```
"""
