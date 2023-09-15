"""
This package provides support for the Keithley instrumentation for temperature control.

We support in this package the following device:

* Keithley DAQ6510 Data Acquisition and Multimeter System

## Keithley DAQ6510

The main entry point for the user of this package is through the `DAQ6510Proxy` class:

    >>> from egse.tempcontrol.keithley.daq6510 import DAQ6510Proxy

This class will connect to the control server of the DAQ6510 Controller and
provides all commands to control and monitor the temperature and other sensors that are
connected in the slots. The control server is a small server application that is started as shown
below. The control server directly connects to the DAQ6510 Controller through an
Ethernet interface. When you have no hardware available, the control server can
be started in simulation mode by appending the `--sim` string to the command below.

    $ python -m egse.tempcontrol.keithley.daq6501_cs

We have also provided a graphical user interface (GUI) to monitor and manipulate the
temperature sensors. The GUI is currently a very preliminary and simple stripchart that
plots the temperature of just one channel. Below is a screenshot of this GUI connected to the
DAQ6510 Control Server in simulation mode. The simulation does a random walk.

![DAQ6510 GUI screenshot](../../../../img/screenshot-daq6510_ui.png)

Make sure that when executing above applications from the Terminal, you have
properly set your Python environment and the `PYTHONPATH` environment variable.

"""
