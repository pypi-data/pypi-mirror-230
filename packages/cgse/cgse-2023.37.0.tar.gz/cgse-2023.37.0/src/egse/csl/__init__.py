from enum import Enum
from pathlib import Path
from executor import ExternalCommand
from gui_executor.utils import read_id

from egse.settings import Settings

HERE = Path(__file__).parent.resolve()
HOME_DIR = Path('~').expanduser()
ID_FILE = HOME_DIR / "hexapod_id.txt"

HEXAPODS = Settings.load(location=HOME_DIR,
                         filename="mech_pos_settings.yaml",
                         group_name="Hexapod",
                         add_local_settings=False)


class HexapodID(str, Enum):
    H_1A = "1A"
    H_1B = "1B"
    H_2A = "2A"
    H_2B = "2B"


def get_endpoint_hexapod(hexapod_id: str = None):
    """Returns the hostname and port number for the Hexapod."""

    hexapod_id = hexapod_id or read_id(ID_FILE)

    hostname = HEXAPODS[f"H_{hexapod_id}"]["HOSTNAME"]
    port = HEXAPODS[f"H_{hexapod_id}"]["PORT"]

    print(f"{hexapod_id=}, {hostname=}, {port=}")

    return "PUNA", hexapod_id, hostname, port


def mechanical_position_ui():
    """ Definition of the UI for the mechanical position at CSL.

    This UI is built using the gui-executor code, and uses the definitions from this module.
    """
    logo_path = HERE / "icons/logo-puna.svg"
    cmd = ExternalCommand(
        f"gui-executor --module-path egse.csl --logo {logo_path} --single "
        f"--kernel-name plato-common-egse  "
        f"--app-name 'CSL Operator GUI (M-position)'",
        asynchronous=True
    )
    cmd.start()
