"""
This module defines all the classes and functions that interact with and control
the HUBER stages.

The main entry point for the user of this package is through the `HuberSMC9300Proxy class:

```python
>>> from egse.stages.huber.smc9300 import HuberSMC9300Proxy
```

This class will connect to the control server of the HUBER Stages and provides all commands to
control the stages and monitor its positions and status. The control server can be started from
a terminal with:

```bash
$ smc9300_cs start
```

We have also provided a graphical user interface (GUI) to monitor and manipulate the stages.
For this, execute the following command from the terminal.

```bash
$ smc9300_ui
```

"""
from egse.control import is_control_server_active
from egse.settings import Settings
from egse.zmq_ser import connect_address

CTRL_SETTINGS = Settings.load("Huber Control Server")


def is_smc9300_cs_active(timeout: float = 2.0):
    """
    Checks whether the HUBER SMC9300 Control Server is running.

    Args:
        timeout (float): Timeout when waiting for a reply [seconds, default=2.0]

    Returns:
        True if the SMC9300 CS is running and replied with the expected answer.
    """

    endpoint = connect_address(
        CTRL_SETTINGS.PROTOCOL, CTRL_SETTINGS.HOSTNAME, CTRL_SETTINGS.COMMANDING_PORT
    )

    return is_control_server_active(endpoint, timeout)
