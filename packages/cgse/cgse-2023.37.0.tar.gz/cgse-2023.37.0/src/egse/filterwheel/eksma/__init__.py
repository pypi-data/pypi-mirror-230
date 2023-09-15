"""
Device control for the Thorlabs Filter Wheel.

This package contains the modules and classes to work with the 8SMC4 Filter Wheel from Thorlabs.

The main entry point for the user of this package is through the `FW8SMC4Proxy` class:

```python
>>> from egse.filterwheel.eksma.fw8smc4 import FilterWheel8SMC4Proxy
```

This class will connect to the control server of the filter wheel and provides all commands to
control this device and monitor its settings and status.

We have also provided a graphical user interface (GUI) to monitor and manipulate the filter wheel.
For this, execute the following command from the terminal. We assume hereby that your environment
and `PYTHONPATH` are set up properly.

```bash
$ python -m egse.filterwheel.eksma.fw8smc4_cs
```


"""
