"""
Device control for the LakeShore Temperature Controller Model 336.

This package contains the classes and modules to work with the LakeShore Temperature Controller.

The main entry point for the user of this package is through the `LakeShore336Proxy` class:

```python
>>> from egse.tempcontrol.lakeshore.lsci336 import LakeShore336Proxy
```

This class will connect to the control server of the LakeShore 336 Controller and
provides all commands to control and monitor the temperature sensors, heaters and
status. The control server is a small server application that is started as shown
below. The control server directly connects to the LakeShore Controller through an
Ethernet interface. When you have now hardware available, the control server can
be started in simulator mode by appending the `--sim` string to the command below.

```bash
$ python -m egse.tempcontrol.lakeshore.lsci336_cs
```

We have also provided a graphical user interface (GUI) to monitor and manipulate the
temperature sensors. The GUI is currently a very preliminary and simple stripchart that
plots the temperature of channel A. Below is a screenshot of this GUI connected to the
LakeShore 336 Control Server in simulation mode. The simulation does a random walk.

![LakeShore GUI screenshot](../../../../img/screenshot-lsci336_ui.png)

Make sure that when executing above applications from the Terminal, you have
properly set your Python environment and the `PYTHONPATH` environment variable.

"""
