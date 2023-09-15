#! /usr/bin/env python3

import glob
import logging
import os
from datetime import datetime
from enum import IntEnum
from pathlib import Path
from typing import List

import click
import pandas as pd
from pandas import DataFrame
from rich import print
from rich.console import Console
from rich.progress import track
from rich.table import Table

from egse import h5
from egse.setup import load_setup
from egse.bits import beautify_binary
from egse.fee import convert_ccd_order_value
from egse.fee import n_fee_mode
from egse.fee.nfee import HousekeepingData
from egse.reg import RegisterMap
from egse.spw import SpaceWirePacket
from egse.storage.persistence import CSV2

MODULE_LOGGER = logging.getLogger("egse.create_hdf5_report")

df_awg2: DataFrame
"""Holds the AEU AWG2 HK data to determine external sync period."""

sync_mode = {0: 'ext', 1: 'int'}
"""Decodes N-FEE internal or external sync mode."""

reg_map = RegisterMap("N-FEE")
"""Holds the register map of the N-FEE."""

setup = load_setup()
sensor_sel = setup.camera.fee.sensor_sel.enum
"""Decodes N-FEE E-side and F-side information."""

def load_aeu_awg2_data(location: Path):
    try:
        awg_fn = glob.glob(str(location / '*_AEU-AWG2.csv'))[0]
    except IndexError as exc:
        raise FileNotFoundError(
            "The AEU AWG2 CSV file is not found, cannot determine correct external sync period."
        ) from exc

    print(f"Loading {awg_fn}...")
    converters = {
         "timestamp": lambda x: datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%f+0000"),
    }
    return pd.read_csv(location / awg_fn, index_col="timestamp", converters=converters)


def get_external_sync_period(timestamp: str):
    if timestamp == 'N/A':
        return float('nan')
    dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f+0000")
    try:
        idx = df_awg2.index.get_loc(dt, method="nearest")
    except AttributeError:
        return 0.0
    return df_awg2.iloc[idx]['GAEU_EXT_CYCLE_TIME']


def extract_register_values(filename: Path):
    with h5.get_file(filename, mode='r', locking=False) as hdf5_file:

        if "/obsid" in hdf5_file:
            obsid = h5.get_data(hdf5_file["/obsid"]).item().decode()
        else:
            obsid = ''

        if "/0/timecode" in hdf5_file:
            timecode = h5.get_data(hdf5_file["/0/timecode"])
            timestamp = h5.get_attribute_value(hdf5_file["/0/timecode"], "timestamp")
        else:
            timestamp = 'N/A'

        if "/register" not in hdf5_file:
            raise RuntimeError(f'no register map in this HDF5 file ({filename.name})')

        reg_data = h5.get_data(hdf5_file["/register"])
        reg_map.set_data(0x0000_0000, bytearray(reg_data.tobytes()), 0x800)
        v_start = reg_map['v_start']
        v_end = reg_map['v_end']
        digitise_en = reg_map['digitise_en']
        dg_en = reg_map['DG_en']
        n_final_dump = reg_map['n_final_dump']
        sync_sel = sync_mode[reg_map['sync_sel']]
        if sync_sel == 'ext':
            sync_period = get_external_sync_period(timestamp)
            n_frames = 4
        else:
            sync_period = reg_map['int_sync_period'] / 1000.0
            n_frames = 1
        sensor = sensor_sel(reg_map['sensor_sel']).name
        ccd_readout_order = convert_ccd_order_value(reg_map['ccd_readout_order'])

        charge_injection_en = reg_map['charge_injection_en'] or ''
        charge_inject_width = reg_map['charge_injection_width'] if charge_injection_en else ''
        charge_inject_gap = reg_map['charge_injection_gap'] if charge_injection_en else ''

        ccd_vgd_config_19 = reg_map[('reg_19_config', 'ccd_vgd_config')]
        ccd_vgd_config_20 = reg_map[('reg_20_config', 'ccd_vgd_config')]
        ccd_vgd_config = (ccd_vgd_config_20 << 4) + ccd_vgd_config_19

        try:
            mode = n_fee_mode(reg_map['ccd_mode_config']).name
        except ValueError:
            mode = f"[bold red]INVALID ({reg_map['ccd_mode_config']})[/]"

        has_error_flags = ''
        all_error_flags_value = [0, 0, 0, 0]
        all_error_flags_str = [" "*5, " "*5, " "*5, " "*5]

        for count in range(n_frames):
            if f"/{count}/hk_data" in hdf5_file:
                hk_data = hdf5_file[f"/{count}/hk_data"][...]
            elif f"/{count}/hk" in hdf5_file:
                hk_packet = SpaceWirePacket.create_packet(hdf5_file[f"/{count}/hk"][...])
                hk_data = hk_packet.data
            else:
                continue
            if error_flags := HousekeepingData(hk_data)['error_flags']:
                all_error_flags_value[count] = error_flags
                # error_flags = beautify_binary(error_flags, group=4, size=12)
                error_flags = f"0x{error_flags:03X}"
                all_error_flags_str[count] = error_flags
                has_error_flags = 'x'

        # Since Rich Table cannot render a List, convert it to a string
        all_error_flags_str = ", ".join(all_error_flags_str) if has_error_flags else ''

    return (
            obsid,
            timestamp[:19],
            filename.name,
            str(v_start),
            str(v_end),
            str(n_final_dump),
            str(digitise_en),
            str(dg_en),
            sync_sel,
            f"{sync_period:.3f}",
            mode,
            sensor,
            str(ccd_readout_order),
            str(charge_injection_en),
            str(charge_inject_width),
            str(charge_inject_gap),
            hex(ccd_vgd_config),
            str(all_error_flags_value),
            all_error_flags_str,
            has_error_flags,
    )


@click.command()
@click.argument('location')
@click.option('--output-file', '-o', help="full path name for the report file")
@click.option('--csv-format', is_flag=True, help="output format in CVS instead of TXT")
def cli(location, output_file, csv_format):
    """
    Script to extract parameter values from the register map in the HDF5 files that are
    generated by the DPU Processor.

    * location - the folder that contains the HDF5 files to be checked

    """
    global df_awg2

    location = Path(location)
    output_file = output_file or ("report.csv" if csv_format else "report.txt")

    files = glob.glob(str(location / '*_SPW_*.hdf5'))
    n_files = len(files)

    # Read the AEU AWG2 data file to determine the external sync period

    try:
        df_awg2 = load_aeu_awg2_data(location)
    except FileNotFoundError:
        df_awg2 = None

    # Extract all the parameters from the HDF5 register map

    data = []
    errors = []

    print(f"Number of files: {n_files}")

    for filename in track(sorted(files), description=f"Extracting register from {n_files} files"):
        # for filename in sorted(files):
        try:
            row = extract_register_values(Path(filename))
            data.append(list(row))
            if row[-1] == 'x':  # the last element is the has_error_flags, the first is the OBSID
                errors.append(row[0])
        except Exception as exc:
            print(f"[red]ERROR[/]: {Path(filename).name}: {exc!s}")
            MODULE_LOGGER.error(f"{exc!s}", exc_info=True)

    if csv_format:
        print_csv(output_file, data, errors)
    else:
        print_table(output_file, data, errors)

def exclude_items(*indices):
    """
    Returns a function that excludes the items of its operand at the given indices and returns a tuple
    containing the other elements of the operand using the `__getitem__` method of the operand.

    Args:
        *indices: indices of items that shall be excluded, can be a negative index also.

    """
    def func(obj):
        size = len(obj)
        pos_indices = [idx if idx > 0 else size + idx for idx in indices]
        return tuple(obj[idx] for idx in range(size) if idx not in pos_indices)
    return func

def print_csv(output_file: str, data: List, errors: List):
    header = [
        "obsid",
        "timestamp",
        "HDF5 filename",
        "v_start",
        "v_end",
        "n_final_dump",
        "digitise",
        "DG",
        "sync",
        "sync period",
        "mode",
        "sensor",
        "CCD order",
        "CI",
        "CI width",
        "CI gap",
        "VGD",
        "error_flags",
    ]

    prep = {"column_names": header, "mode": 'w', "quote_char": '\"'}
    with CSV2(output_file, prep=prep) as csv:
        for row in data:
            csv.create(row[:-2])  # remove last two values, i.e. all_error_flags_str and has_error_flags


def print_table(output_file: str, data: List, errors: List):
    table = Table(title="HDF5 & Register Map", min_width=180)

    table.add_column("obsid")
    table.add_column("timestamp", width=20)
    table.add_column("HDF5 filename", no_wrap=True)
    table.add_column("v_start", justify="right")
    table.add_column("v_end", justify="right")
    table.add_column("n_final_dump", justify="right")
    table.add_column("digitise", justify="right")
    table.add_column("DG", justify="right")
    table.add_column("sync")
    table.add_column("sync period")
    table.add_column("mode")
    table.add_column("sensor")
    table.add_column("CCD order")
    table.add_column("CI")
    table.add_column("CI width")
    table.add_column("CI gap")
    table.add_column("VGD")
    table.add_column("error_flags")

    # We don't need the error_flags-by-value, we need the error_flags-by-str/bin
    # and, do not use the last element which is the has_error_flags. So, all rows
    # should exclude element -3 and -1
    snip = exclude_items(-1, -3)

    for row in data:
        table.add_row(*snip(row))

    with Console().status("Saving report...", spinner='clock'):
        with open(output_file, "wt") as report_file:
            console = Console(file=report_file, width=300)
            if errors:
                console.print(f"Observations with N-FEE errors: {', '.join(set(errors))}")
            console.print(table)


if __name__ == "__main__":
    cli()
