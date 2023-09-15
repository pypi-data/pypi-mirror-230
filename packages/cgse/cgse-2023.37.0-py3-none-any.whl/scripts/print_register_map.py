from __future__ import annotations
from pathlib import Path

import click
import rich

from egse import h5
from egse.reg import RegisterMap

@click.command()
@click.argument('filename')
def print_register_map(filename: str | Path):
    """Prints the Register Map that is saved in the HDF5 file."""

    filename = Path(filename)

    if filename.exists():
        try:
            with h5.get_file(filename, mode='r') as hdf5_file:
                rich.print(f"Register Map from {filename}", end='')
                if "/obsid" in hdf5_file:
                    obsid = h5.get_data(hdf5_file["/obsid"]).item().decode()
                    if obsid != 'None':
                        rich.print(f", OBSID = {obsid}\n")
                    else:
                        rich.print()

                if "/register" in hdf5_file:
                    reg_data = h5.get_data(hdf5_file["/register"])
                    reg_map = RegisterMap("N-FEE", memory_map=reg_data)
                    rich.print(reg_map)
        except OSError as exc:
            rich.print(f"{filename=!s}, {exc}")
    else:
        rich.print(f"no such file {filename!s}")


if __name__ == "__main__":
    print_register_map()
