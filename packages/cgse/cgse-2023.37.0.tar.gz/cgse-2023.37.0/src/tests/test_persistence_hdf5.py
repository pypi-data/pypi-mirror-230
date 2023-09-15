from pathlib import Path

from egse.storage.persistence import HDF5
from egse.h5 import get_file

# TODO:
#
#   * add a test for HDF5() without a prep, that will result in a AttributeError

FILENAME = "xxx.hdf5"


def test_adding_two_commands_to_the_same_frame_number():

    # Creating the same entry twice in the HDF5 file results in the following error:
    #
    #   OSError: Unable to create link (name already exists)
    #

    with HDF5(filename=FILENAME, prep={"mode": 'w'}) as h5_file:
        h5_file.create(data={"/0/command": "command_set_dump_mode()"})

    h5 = get_file(filename=FILENAME, mode='r')
    assert h5["/0/commands/0"][()] == b'command_set_dump_mode()'
    h5.close()

    with HDF5(filename=FILENAME, prep={"mode": 'w'}) as h5_file:
        h5_file.create(data={"/0/command": "command_set_dump_mode()"})
        h5_file.create(data={"/0/command": "command_set_full_image_mode()"})
        h5_file.create(data={"/0/command": "command_set_full_image_pattern_mode()"})

    h5 = get_file(filename=FILENAME, mode='r')
    assert h5["/0/commands/0"][()] == b'command_set_dump_mode()'
    assert h5["/0/commands/1"][()] == b'command_set_full_image_mode()'
    assert h5["/0/commands/2"][()] == b'command_set_full_image_pattern_mode()'
    h5.close()

    Path(FILENAME).unlink(missing_ok=True)
