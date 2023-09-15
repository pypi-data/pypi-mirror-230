"""
This module handles the representation, parsing and processing of N-FEE housekeeping packets.

"""
import logging
import struct
from pathlib import Path
from typing import Tuple

import numpy as np
import rich
from rich.table import Table

from egse.bits import clear_bit
from egse.bits import set_bit
from egse.bits import toggle_bit
from egse.state import GlobalState

THIS_FILE_LOCATION = Path(__file__).parent
LOGGER = logging.getLogger(__name__)


def load_hk_definition() -> Tuple[dict, int]:
    """
    Reads the 'n_fee_hk.yaml' file with the definition of the N-FEE Housekeeping packets.

    The returned value for the HK parameters is a list of three integers, [offset, shift, width].

    * offset: the offset in the HK packet data [bytes]
    * shift: the offset in the 32-bit register field [bits]
    * width: the width of the parameter in the 32-bit register field

    Returns:
        A dictionary with the HK parameter names as keys and position in the N-FEE memory map as
        values.
    """

    reg_map = GlobalState.setup.camera.fee.hk_map
    hk_map = {}

    start_address = reg_map["start_address"]
    hk_data_length = reg_map["hk_data_length"]
    reg_map = dict(filter(lambda x: x[0].startswith("reg_"), reg_map.items()))

    for reg_name, reg_hk in reg_map.items():
        offset = reg_hk["address"] - start_address
        del reg_hk["address"]

        if "twos_complement" in reg_hk:
            twos_complement = bool(reg_hk["twos_complement"])
            del reg_hk["twos_complement"]
        else:
            twos_complement = False

        # LOGGER.info(f"{reg_name=}, {twos_complement=}")

        for hk_name in reg_hk:
            var = reg_hk[hk_name]
            if len(var) == 2:
                hk_map[hk_name] = [offset, var[0], var[1], int, twos_complement]
            else:
                hk_map[hk_name] = [offset, var[0], var[1], float, twos_complement]

    return hk_map, hk_data_length


class HousekeepingData:

    """This class holds and parses the data part of an N-FEE Housekeeping packet."""
    def __init__(self, data: bytes = None):

        self.hk_definition, self.hk_data_length = load_hk_definition()

        # TODO: add a sanity check for the len(data)

        self._data = bytearray(data if data is not None else bytes(self.hk_data_length))

    def __getitem__(self, item):
        hk_def = self.hk_definition[item]
        offset, shift, width, type_, twos_complement = hk_def

        # LOGGER.info(f"{item=}, {offset=}, {shift=}, {width=}, {type_=}, {twos_complement=}")

        reg_data = self._data[offset: offset + 4]
        if type_ is int:
            value1 = int.from_bytes(reg_data, "big")
            # from egse.bits import set_bits
            # value = (value1 >> shift) & set_bits(0x0, (0, width))
            value = (value1 >> shift) & int('1'*width, 2)  # this is a factor 10 times faster

            if twos_complement:
                # Alternative ways to calculate the 2s-complement of an integer
                # value = struct.unpack(">h", value.to_bytes(length=2, byteorder="big"))[0]
                # from egse.bits import s16
                # value = s16(value)

                # I was told by MSSL that we only need to flip the msb (most significant bit)
                value = toggle_bit(value, width - 1)

        else:
            [value] = struct.unpack('f', reg_data)

        return value

    def __setitem__(self, key, value):
        hk_def = self.hk_definition[key]
        offset, shift, width, type_, twos_complement = hk_def

        if type_ is int:
            reg_data = self._data[offset: offset + 4]
            x = reg_value = int.from_bytes(reg_data, "big")
            for idx, bit in enumerate(range(shift, shift+width)):
                x = set_bit(x, bit) if value & (1 << idx) else clear_bit(x, bit)

            # print(f"{key=}: {offset} {shift} {width} - "
            #       f"reg_value=0x{reg_value:08X} x=0x{x:08X}")

            self._data[offset: offset + 4] = x.to_bytes(4, byteorder='big')

    def data_as_bytes(self) -> bytes:
        return bytes(self._data)

    @property
    def data_as_ndarray(self):
        return np.frombuffer(self._data, dtype=np.uint8)

    def data_length(self):
        return len(self._data)

    @property
    def timecode(self):
        return self['spw_timecode']

    @property
    def frame_number(self):
        return self["frame_number"]

    @property
    def error_flags(self):
        return self["error_flags"]

    def increment_frame_number(self):
        frame_number = self["frame_number"]
        frame_number = 0 if frame_number == 3 else frame_number + 1
        self["frame_number"] = frame_number
        return frame_number

    @property
    def frame_counter(self):
        return self["frame_counter"]

    def increment_frame_counter(self):
        frame_counter = self["frame_counter"]
        frame_counter = 0 if frame_counter == 0xFFFF else frame_counter + 1
        self["frame_counter"] = frame_counter
        return frame_counter

    def increment_timecode(self):
        timecode = self['spw_timecode']
        timecode = 0 if timecode == 0x3F else timecode + 1
        self["spw_timecode"] = timecode
        return timecode

    def __rich__(self):
        d = {hk_name: self[hk_name] for hk_name in self.hk_definition}
        table = Table("Parameter", "Value [int]", "Value [hex]", "Value [bin]", title="Housekeeping Data")
        for name in self.hk_definition:
            value = self[name]
            table.add_row(name, str(value), f"0x{value:0x}", f"0b{value:b}")
        return table

    def __iter__(self):
        return iter(self.hk_definition)


if __name__ == "__main__":

    import os
    from egse.fee.feesim import initialise_hk_data

    os.environ["PLATO_CONF_DATA_LOCATION"] = "/Users/rik/git/plato-cgse-conf/data/CSL1/conf"

    hk_data = HousekeepingData()
    initialise_hk_data(hk_data)
    initialise_hk_data(hk_data)

    rich.print(hk_data)
