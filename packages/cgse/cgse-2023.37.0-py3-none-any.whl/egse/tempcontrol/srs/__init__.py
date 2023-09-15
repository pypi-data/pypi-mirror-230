"""
Device control for the SRS/PTC10 that controls the SRS temperature control system of the MaRi.

The main entry point for the user of this package is through the `Eq99Proxy` class:

```python
>>> from egse.tempcontrol.srs.ptc10 import ptc10Proxy
```

This class will connect to the control server of the filter wheel and provides all commands to
control this device and monitor its settings and status.

We have also provided a graphical user interface (GUI) to monitor and manipulate the filter wheel.
For this, execute the following command from the terminal. We assume hereby that your environment
and `PYTHONPATH` are set up properly.

```bash
$ python -m egse.tempcontrol.srs.ptc10_cs
```


"""