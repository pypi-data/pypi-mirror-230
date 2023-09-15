""" Content of the UI for the mechanical position at CSL.  This basically needs two buttons to command the hexapod:
    - a button to go to the home position;
    - a button to go to the retracted position.
"""
from pathlib import Path

from gui_executor.exec import exec_ui

from egse.csl import get_endpoint_hexapod
from egse.hexapod.symetrie.puna import PunaController

UI_MODULE_DISPLAY_NAME = "2 - Commanding"

ID_FILE = Path('~').expanduser() / "id.txt"

HERE = Path(__file__).parent.resolve()


@exec_ui(display_name="Zero position",
         icons=(HERE/"icons/hexapod-zero.svg", HERE/"icons/hexapod-zero-selected.svg"))
def goto_zero_position():
    """ Move the hexapod to the zero position."""

    hexapod = None
    hexapod_name, hexapod_id, hostname, port = get_endpoint_hexapod()
    try:
        from egse.hexapod.symetrie import ControllerFactory
        factory = ControllerFactory()
        hexapod = factory.create(hexapod_name, device_id=hexapod_id)
        hexapod.connect()
        hexapod.goto_zero_position()
    except ConnectionError as exc:
        print("[red]Couldn't connect to the Hexapod Controller. "
              "Check if the Controller is switched on and no error is reported on the front panel of the controller.[/]")
    finally:
        if hexapod is not None:
            hexapod.disconnect()


@exec_ui(display_name="Retracted position",
         icons=(HERE/"icons/hexapod-retract.svg", HERE/"icons/hexapod-retract-selected.svg"))
def goto_retracted_position():
    """ Move the hexapod to the retracted position."""

    hexapod = None
    hexapod_name, hexapod_id, hostname, port = get_endpoint_hexapod()
    try:
        from egse.hexapod.symetrie import ControllerFactory
        factory = ControllerFactory()
        hexapod = factory.create(hexapod_name, device_id=hexapod_id)
        hexapod.connect()
        hexapod.goto_retracted_position()
    except ConnectionError as exc:
        print("[red]Couldn't connect to the Hexapod Controller. "
              "Check if the Controller is switched on and no error is reported on the front panel of the controller.[/]")
    finally:
        if hexapod is not None:
            hexapod.disconnect()


@exec_ui(display_name="Emergency stop", icons=(HERE / "icons/stop.svg", HERE / "icons/stop.svg"), immediate_run=True)
def emergency_stop():
    """ Emergency stop of the hexapod."""

    hexapod = None
    hexapod_name, hexapod_id, hostname, port = get_endpoint_hexapod()
    try:
        from egse.hexapod.symetrie import ControllerFactory
        factory = ControllerFactory()
        hexapod = factory.create(hexapod_name, device_id=hexapod_id)
        hexapod.connect()
        hexapod.stop()
    except ConnectionError as exc:
        print("[red]Couldn't connect to the Hexapod Controller. "
              "Check if the Controller is switched on and no error is reported on the front panel of the controller.[/]")
    finally:
        if hexapod is not None:
            hexapod.disconnect()
