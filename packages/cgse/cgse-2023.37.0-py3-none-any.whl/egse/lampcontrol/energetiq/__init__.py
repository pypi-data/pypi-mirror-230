"""
Device control for the EQ-99 Manager that controls the Hamamatsu Lamp.

The main entry point for the user of this package is through the `Eq99Proxy` class:

```python
>>> from egse.lampcontrol.energetiq.lampEQ99 import LampEQ99Proxy
```

This class will connect to the control server of the filter wheel and provides all commands to
control this device and monitor its settings and status.

We have also provided a graphical user interface (GUI) to monitor and manipulate the filter wheel.
For this, execute the following command from the terminal. We assume hereby that your environment
and `PYTHONPATH` are set up properly.

```bash
$ python -m egse.lampcontrol.energetiq.eq99_cs
```


"""
