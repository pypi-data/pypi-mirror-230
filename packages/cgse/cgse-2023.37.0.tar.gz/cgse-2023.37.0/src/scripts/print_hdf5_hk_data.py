from __future__ import annotations
from pathlib import Path

import click
import rich
from rich.console import Console
from rich.table import Table

from egse import h5
from egse.fee.nfee import HousekeepingData

@click.command()
@click.argument('filename')
def print_hk_data(filename: str | Path):
    """Prints the updated HK data that is saved in the HDF5 file."""

    filename = Path(filename)

    if filename.exists():
        console = Console(width=80)
        try:
            with h5.get_file(filename, mode='r') as hdf5_file:
                rich.print(f"HK data from {filename}", end='')
                if "/obsid" in hdf5_file:
                    obsid = h5.get_data(hdf5_file["/obsid"]).item().decode()
                    if obsid != 'None':
                        rich.print(f", OBSID = {obsid}\n")
                    else:
                        rich.print()

                # TODO:
                #    Make a table with 5 columns where the first column is the parameter name
                #    the next columns the values for each frame
                #    Detect specific names and convert the values (use dictionary dispatching?)

                tmp_hk_data = {}
                tmp_frame_numbers = []

                for frame_number in {0, 1, 2, 3}:
                    if (key := f"/{frame_number}/hk_data") in hdf5_file:
                        tmp_frame_numbers.append(frame_number)
                        hk_data = h5.get_data(hdf5_file[key])
                        hk_data = HousekeepingData(hk_data)
                        # rich.print(hk_data)
                        for par_name in hk_data:
                            if par_name not in tmp_hk_data:
                                tmp_hk_data[par_name] = []
                            tmp_hk_data[par_name].append(hk_data[par_name])

                table = Table(title=f"Housekeeping Data for {obsid}", expand=False)
                table.add_column("Parameter")

                for fn in tmp_frame_numbers:
                    table.add_column(f"Frame {fn}")

                for k, v in tmp_hk_data.items():
                    table.add_row(str(k), *[f"0x{x:0x}" for x in v])

                console.print(table)

        except OSError as exc:
            rich.print(f"{filename=!s}, {exc}")
    else:
        rich.print(f"no such file {filename!s}")


if __name__ == "__main__":
    print_hk_data()
