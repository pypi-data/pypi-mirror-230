"""
Content of the UI for the mechanical position at CSL.

This module defines the initialisation part with the following buttons:

* Set the Hexapod ID
* Home the Hexapod

"""
from pathlib import Path

from gui_executor.exec import StatusType
from gui_executor.exec import exec_task
from gui_executor.exec import exec_recurring_task
from gui_executor.utils import read_id
from gui_executor.utils import write_id

from egse.csl import HexapodID
from egse.csl import ID_FILE
from egse.csl import get_endpoint_hexapod
from egse.hexapod import HexapodError
from egse.hexapod.symetrie.puna import PunaController

UI_MODULE_DISPLAY_NAME = "1 - Initialisation"

HERE = Path(__file__).parent.resolve()


@exec_recurring_task(status_type=StatusType.NORMAL)
def show_hexapod_status():

    hexapod = None
    hexapod_name, hexapod_id, hostname, port = get_endpoint_hexapod()
    try:
        from egse.hexapod.symetrie import ControllerFactory
        factory = ControllerFactory()
        hexapod = factory.create(hexapod_name, device_id=hexapod_id)
        hexapod.connect()
        in_position = hexapod.is_in_position()
        homing_done = hexapod.is_homing_done()

        return f"{'' if homing_done else 'NOT '}HOMED — {'IN POSITION' if in_position else 'MOVING...'}"

    except (ConnectionError, HexapodError) as exc:
        print(exc)
        return "Connection Error"
    finally:
        if hexapod is not None:
            hexapod.disconnect()


@exec_recurring_task(status_type=StatusType.PERMANENT)
def show_hexapod_id():

    return f"Hexapod ID = {read_id(ID_FILE)}"


@exec_task(display_name="Set Hexapod ID")
def set_id(hexapod_id: HexapodID):
    """Set the Hexapod Identifier for the Hexapod that is connected to this position."""
    write_id(hexapod_id, ID_FILE)


@exec_task(display_name="Check connection", immediate_run=True,
           icons=(HERE/"icons/hexapod-connected.svg", HERE/"icons/hexapod-connected-selected.svg"))
def check_connection():
    """Check the connection to the hexapod."""

    hexapod = None
    hexapod_name, hexapod_id, hostname, port = get_endpoint_hexapod()
    try:
        from egse.hexapod.symetrie import ControllerFactory
        factory = ControllerFactory()
        hexapod = factory.create(hexapod_name, device_id=hexapod_id)
        hexapod.connect()
        print(f"[green]Successfully connected to Hexapod with ID = {read_id(ID_FILE)}.[/]")
    except ConnectionError as exc:
        print("[red]Couldn't connect to the Hexapod Controller. "
              "Check if the Controller is switched on and no error is reported on the front panel of the controller.[/]")
    finally:
        if hexapod is not None:
            hexapod.disconnect()


@exec_task(display_name="Homing", icons=(HERE/"icons/hexapod-homing.svg", HERE/"icons/hexapod-homing-selected.svg"))
def goto_home_position():
    """ Move the hexapod to the home position."""

    hexapod = None
    hexapod_name, hexapod_id, hostname, port = get_endpoint_hexapod()
    try:
        from egse.hexapod.symetrie import ControllerFactory
        factory = ControllerFactory()
        hexapod = factory.create(hexapod_name, device_id=hexapod_id)
        hexapod.connect()
        hexapod.homing()
    except ConnectionError as exc:
        print("[red]Couldn't connect to the Hexapod Controller. "
              "Check if the Controller is switched on and no error is reported on the front panel of the controller.[/]")
    finally:
        if hexapod is not None:
            hexapod.disconnect()
