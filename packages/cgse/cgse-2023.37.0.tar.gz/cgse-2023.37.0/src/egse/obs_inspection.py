import argparse

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn, BarColumn, TaskProgressColumn
from rich.table import Table

from egse import h5
from egse.dpu.fitsgen import get_hdf5_filenames_for_obsid
from egse.fee.nfee import HousekeepingData
from egse.spw import DataPacket, HousekeepingPacket
from egse.state import GlobalState


def parse_arguments():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--obsid",
        type=str,
        help="Observation Identifier.",
    )

    parser.add_argument(
        "--location",
        type=str,
        help="Location where the data is stored.  This is the folder with the /daily and /obs sub-folders.",
    )

    return parser.parse_args()


def print_table(obsid: str, location: str):
    obs_hdf5_filenames = get_hdf5_filenames_for_obsid(obsid, location)
    num_hdf5_files = len(obs_hdf5_filenames)
    print(f"Found {num_hdf5_files} HDF5 files for obsid {obsid}")

    ccd_bin_to_id = GlobalState.setup.camera.fee.ccd_numbering.CCD_BIN_TO_ID
    n_fee_side = GlobalState.setup.camera.fee.ccd_sides.enum
    
    table = Table(title=f"Report for obsid {obsid}", expand=False)
    table.add_column("HDF5", justify="right")
    table.add_column("Group", no_wrap=True, justify="center")
    table.add_column("Timestamp", no_wrap=True)
    table.add_column("CCD", no_wrap=True)
    table.add_column("Command")

    console = Console(width=200)

    with Progress(
            SpinnerColumn(),
            BarColumn(),
            TaskProgressColumn(),
            # *Progress.get_default_columns(),
            TimeElapsedColumn(),
            console=Console(),
            transient=False,
    ) as progress:

        hdf5_file_task = progress.add_task("[red]Opening HDF5 file", total=num_hdf5_files)

        progress_index = 0

        while not progress.finished:
            progress.update(hdf5_file_task, advance=1)
            hdf5_filename = obs_hdf5_filenames[progress_index]

            try:
                hdf5_index = int(hdf5_filename.split("_")[-1].split(".")[0])
                with h5.get_file(hdf5_filename, mode="r", locking=False) as hdf5_file:

                    for group_index in range(0, 4):

                        end_section = group_index == 3 if "3" in hdf5_file else True

                        ccd = None

                        try:
                            group = hdf5_file[str(group_index)]

                            has_e_side = False
                            has_f_side = False

                            try:
                                timestamp = group["timecode"].attrs["timestamp"]

                                hk = HousekeepingData(HousekeepingPacket(group["hk"]).data)
                                has_error_flags = hk["error_flags"] != 0

                                data = group["data"]

                                for packet_index in [0, len(data) - 1]:
                                    packet_type = DataPacket(data[str(packet_index)]).type

                                    ccd_number = ccd_bin_to_id[packet_type.ccd_number]

                                    ccd_side = packet_type.ccd_side
                                    if ccd_side == n_fee_side.E:
                                        has_e_side = True
                                    else:
                                        has_f_side = True
                                if has_e_side and has_f_side:
                                    ccd = f"{ccd_number} BOTH"
                                elif has_e_side:
                                    ccd = f"{ccd_number}E"
                                elif has_f_side:
                                    ccd = f"{ccd_number}F"
                                if has_error_flags:
                                    ccd = f"{ccd} (!)"
                            except KeyError:
                                ccd = None  # No data transmitted

                            # Command

                            try:
                                commands = group["commands"]

                                for command_index in range(len(commands)):
                                    command = commands[str(command_index)][()]

                                    if command_index == 0:
                                        table.add_row(str(hdf5_index), str(group_index), timestamp, ccd,
                                                      f"{command_index}: {command}",
                                                      end_section=end_section and len(commands) == 1)
                                    elif command_index == len(commands) - 1:
                                        table.add_row(None, None, None, None, f"{command_index}: {command}",
                                                      end_section=end_section)
                                    else:
                                        table.add_row(None, None, None, None, f"{command_index}: {command}",
                                                      end_section=False)
                            except KeyError:
                                table.add_row(str(hdf5_index), str(group_index), timestamp, ccd, None,
                                              end_section=end_section)  # No commands sent
                        except KeyError:
                            pass  # Internal sync
            except OSError as exc:
                print("OS error")
            except RuntimeError as exc:
                print("Runtime error")
            # table.add_row(None, None, None, None)

            progress_index += 1

    console.print(table)


if __name__ == "__main__":
    """ Print table with status of the given observation.
    
    We loop over all HDF5 files for the given observation and extract the following information for all data groups
    in each of them:
        - Number of the HDF5 files (extracted from the filename);
        - Group number;
        - CCD number (1/2/3/4);
        - CCD side (E/F/BOTH);
        - Commands.
        
    Example: python -m egse.obs_inspection --obsid 00135_IAS --location /STER/platodata/IAS/data/IAS
    """

    args = parse_arguments()
    print_table(args.obsid, args.location)

