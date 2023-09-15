import glob
import logging
from pathlib import Path
from typing import Optional
from typing import Union

import click
import rich
from h5py import File
from rich.progress import track

from egse import h5
from egse.bits import beautify_binary
from egse.fee import n_fee_mode
from egse.fee.nfee import HousekeepingData
from egse.reg import RegisterMap
from egse.spw import SpaceWirePacket

MODULE_LOGGER = logging.getLogger("egse.check_hdf5_file")


def check_if_top_level_groups_complete(hdf5_file: File, indent: str) -> (str, bool):

    msg = ""
    error = False

    # Check for internal or external sync

    if "/register" in hdf5_file:
        reg_data = h5.get_data(hdf5_file["/register"])
        reg_map = RegisterMap("N-FEE", memory_map=reg_data)
        sync_sel = reg_map["sync_sel"]
        if sync_sel and ("/1" in hdf5_file or "/2" in hdf5_file or "/3" in hdf5_file):
            msg += indent + (
                   "[bold red]ERROR[/]: internal sync contains more than one readout period\n")
            error = True
        if not sync_sel and (
            missing := [idx for idx in range(4) if f"/{idx}" not in hdf5_file]
        ):
            msg += indent + f"[bold red]ERROR[/]: missing readouts for external sync {missing}\n"
            error = True

    return msg, error


def check_hdf5_file(filename: Union[str, Path], requested_obsid: Union[int, str], error_flags_only=False, errors_only=False):

    filename = Path(filename)

    if filename.exists():
        try:

            with h5.get_file(filename, mode='r') as hdf5_file:

                has_error = False
                indent = "  "
                full_msg = f"Analysing {filename!s}\n"
                full_msg += indent + f"Top level groups: {list(hdf5_file.keys())}\n"
                error_msg = ""
                obsid = ''

                msg, error = check_if_top_level_groups_complete(hdf5_file, indent)
                full_msg += msg
                has_error = error or has_error

                if "/obsid" in hdf5_file:
                    obsid = h5.get_data(hdf5_file["/obsid"]).item().decode()
                    if obsid == 'None':
                        full_msg += indent + "no observation running\n"
                    else:
                        full_msg += indent + f"OBSID = {obsid}\n"

                if requested_obsid is not None and str(requested_obsid) not in obsid:
                    return

                if "/0/timecode" in hdf5_file:
                    timecode = h5.get_data(hdf5_file["/0/timecode"])
                    timestamp = h5.get_attribute_value(hdf5_file["/0/timecode"], "timestamp")
                    full_msg += indent + f"{timecode=!s}, {timestamp=}\n"

                if "/register" in hdf5_file:
                    reg_data = h5.get_data(hdf5_file["/register"])
                    reg_map = RegisterMap("N-FEE", memory_map=reg_data)
                    v_start = reg_map['v_start']
                    v_end = reg_map['v_end']
                    digitise_en = reg_map['digitise_en']
                    dg_en = reg_map['DG_en']
                    sync_sel = reg_map['sync_sel']
                    try:
                        mode = n_fee_mode(reg_map['ccd_mode_config']).name
                    except ValueError:
                        mode = f"[bold red]INVALID ({reg_map['ccd_mode_config']})[/]"
                        has_error = True
                    full_msg += indent + f"register: {v_start=}, {v_end=}, {digitise_en=}, {dg_en=}, {sync_sel=}, {mode=}\n"
                else:
                    full_msg += indent + '[red]no register map in this HDF5 file[/red]\n'
                    has_error = True

                if "/0/data" in hdf5_file and h5.has_attributes(hdf5_file['/0/data']):
                    v_start = h5.get_attribute_value(hdf5_file['/0/data'], "v_start")
                    v_end = h5.get_attribute_value(hdf5_file['/0/data'], "v_end")
                    full_msg += indent + f"data: {v_start=}, {v_end=}\n"

                for count in range(4):
                    if f"/{count}/hk" in hdf5_file:
                        hk_packet = SpaceWirePacket.create_packet(hdf5_file[f"/{count}/hk"][...])
                        full_msg += indent + f"hk: {hk_packet.type} {beautify_binary(hk_packet.type.value)}\n"
                        error_flags = HousekeepingData(hk_packet.data)['error_flags']
                        if error_flags:
                            msg = indent + (
                                f"Frame {count}: [red]One or more of the error flags are ON: "
                                f"{beautify_binary(error_flags, group=4, size=12)}[/red]\n"
                            )
                            full_msg += msg
                            error_msg += msg
                            has_error = True
                for count in range(4):
                    if f"/{count}/commands" in hdf5_file:
                        for idx in hdf5_file[f"/{count}/commands/"]:
                            full_msg += indent + f"command in frame {count}: {h5.get_data(hdf5_file[f'/{count}/commands/{idx}'])}\n"

            if error_flags_only and error_msg:
                rich.print(f"{filename.name=}, size={filename.stat().st_size}")
                rich.print(error_msg)
            if not error_flags_only:
                if errors_only and has_error:
                    rich.print(full_msg)
                if not errors_only:
                    rich.print(full_msg)

        except OSError as exc:
            rich.print(f"{filename=!s}, {exc}")
    else:
        rich.print(f"no such file {filename!s}")


def find_hdf5_for_obsid(files: list, requested_obsid: Union[int, str]):
    new_files = []

    for filename in sorted(files):
        try:
            with h5.get_file(filename, mode='r') as hdf5_file:
                if "/obsid" in hdf5_file:
                    obsid = h5.get_data(hdf5_file["/obsid"]).item().decode()

                    if str(requested_obsid) in obsid:
                        new_files.append(filename)
        except OSError as exc:
            MODULE_LOGGER.error(f"Couldn't open {filename} ({exc=})")
    return new_files


@click.command()
@click.argument('root')
@click.argument('filename_t')
@click.option("--obsid", help="The full OBSID, e.g. SRON_00058_02380 or only the TEST-ID, e.g. 2380")
@click.option("--error-flags-only", is_flag=True, help="Print only the filename and error information")
@click.option("--errors-only", is_flag=True, help="Print only the filename and error information")
def cli(obsid, error_flags_only, errors_only, root, filename_t):
    """Script to inspect the HDF5 files generated by the DPU Processor.

        * ROOT - the root folder that contains the HDF5 files to be checked

        * FILENAME_T - a file name template accepted by glob()
    """
    root = Path(root)

    files = glob.glob(str(root / filename_t))
    if obsid is not None:
        files = find_hdf5_for_obsid(files, obsid)
    n_files = len(files)

    rich.print(f"Number of files: {n_files}")

    print(" ".join([Path(file).name for file in files]))

    answer = input("So, you want to continue [Y/n]")
    print(answer)
    if answer.lower() in ['n', 'no']:
        return

    for filename in track(sorted(files), description=f"Checking {n_files} files"):
    # for filename in sorted(files):
        try:
            check_hdf5_file(filename, obsid, error_flags_only, errors_only)
        except Exception as exc:
            rich.print(f"[red]ERROR[/]: {Path(filename).name}: {exc!s}")
            MODULE_LOGGER.debug(f"{exc!s}", exc_info=True)


if __name__ == "__main__":
    cli()
