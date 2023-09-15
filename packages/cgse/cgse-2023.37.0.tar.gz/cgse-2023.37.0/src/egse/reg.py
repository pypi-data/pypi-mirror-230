"""
This module defines classes and methods for working with the register
as defined in the N-FEE and the F-FEE. The register is basically a memory
map that is 32-bit aligned and contains configuration values for the
front-end electronics (FEE) of the PLATO cameras.

The class RegisterMap has all definitions of the registers as they are
defined for the two cameras in PLATO.

The class Register is basically a set of RegisterValue objects and defines
all the parameters for this registry in the registry map. A Registry is
a 32-bit field in the registry map.

The class RegisterValue is the definition of one value or parameter in
the register map and contains all the information needed to encode and
decode the register value.

The RegisterMap is initialized from a YAML configuration file that
is loaded for the N-FEE or F-FEE. The name of the configuration file is
read from the general Settings configuration file, i.e. the REGISTER_MAP
for the N-FEE and the F-FEE settings.

Examples:
```
reg_map: RegisterMap = RegisterMap('N-FEE')

# get window size for CCD#1

x_size = reg_map.get_value('reg_8_config', 'ccd1_win_size_x')
y_size = reg_map.get_value('reg_8_config', 'ccd1_win_size_y')
```
You can also use the shortcut and only specify the variable name as a key. This works as long
as the variable name is unique for the whole register map.
```
x_size = reg_map["ccd1_win_size_x"]
y_size = reg_map["ccd1_win_size_y"]
```
"""
import logging
from typing import List
from typing import Union

import numpy as np
from rich.table import Table

from egse.bits import beautify_binary
from egse.bits import clear_bit
from egse.bits import set_bit
from egse.bits import set_bits
from egse.settings import Settings
from egse.setup import SetupError
from egse.state import GlobalState

n_fee_settings = Settings.load("N-FEE")

LOGGER = logging.getLogger(__name__)


def decode_ccd_order(ccd_order: int) -> str:
    """
    The readout order of the CCDs for the N-FEE. The `ccd_order` is the value that is returned when
    reading the variable from the RegisterMap.

    Example:
        >>> decode_ccd_order(0x4E)  # new convention
        'ccd_order=0b01001110 ( 78) CCD1 -> CCD2 -> CCD3 -> CCD4'

    Args:
        ccd_order: 8-bit field decoded CCD order

    Returns:
        A string representing the readout order of the CCDs.
    """
    msg = f"ccd_order=0b{ccd_order:08b} ({ccd_order:3d}) "

    try:
        ccd_id = GlobalState.setup.camera.fee.ccd_numbering.CCD_ID
    except AttributeError:
        raise SetupError("No entry in the setup for camera.fee.ccd_numbering.CCD_ID")

    order = [f"{ccd_id[(ccd_order >> idx * 2) & 0b11]}" for idx in range(4)]
    msg += " -> ".join(order)
    return msg


def encode_ccd_order(ccd_order: List = None) -> int:
    """
    Given a list of strings that represent the CCD ID, return the encoded ccd_order that can be
    stored in the RegisterMap.

    CCD IDs are "CCD1", "CCD2", "CCD3", "CCD4".

    Example:
        >>> encode_ccd_order(["CCD1", "CCD2", "CCD3", "CCD4"])
        '0b1001110'

    Args:
        ccd_order: a list with strings that represent the CCD order

    Returns:
        The decoded value (int) of the CCD order.
    """

    try:
        ccd_id = GlobalState.setup.camera.fee.ccd_numbering.CCD_ID
    except AttributeError:
        raise SetupError("No entry in the setup for camera.fee.ccd_numbering.CCD_ID")

    order = 0
    keys_list = list(ccd_id.keys())
    values_list = list(ccd_id.values())
    for idx, name in enumerate(ccd_order):
        ccd_id = keys_list[values_list.index(name)]
        order |= ccd_id << idx * 2

    return order


class Register:
    """
    Represents a memory register as defined in the front-end electronics (FEE).

    A Register is a 32-bit field in the FEE memory map and consists of a number
    of sub-registers or RegisterValues.
    """

    def __init__(self, name: str, address: int):
        """
        Args:
            name (str): the name of this register
            address (int): the memory address of the register in the FEE memory map
                (shall be 32-bit aligned)
        Raises:
            ValueError when address is not 32-bit aligned.
        """
        if address & 0x03:
            raise ValueError(f"The given memory address is not 4-byte (32-bit) aligned. "
                             f"[address=0x{address:02x}]")
        self._name = name
        self._address = address
        self._values = {}

    @property
    def name(self):
        """The name of the 32-bit register."""
        return self._name

    @property
    def address(self):
        """The memory address of the register in the N-FEE memory map."""
        return self._address

    def values(self):
        """Returns a view on the values in the register. This view is iterable."""
        return self._values.values()

    def keys(self):
        """Returns the top-level keys, i.e. register names."""
        return self._values.keys()

    def items(self):
        """Returns the keys-value pairs of the registers from this RegisterMap."""
        return self._values.items()

    def __setitem__(self, key, value):
        self._values[key] = value

    def __getitem__(self, key):
        return self._values[key]


class RegisterValue:
    """
    Represents one value from a memory register as used by the front-end electronics (FEE).

    A register value can be a bit-field or an n-bit integer. A bit-field needs to be decoded
    separately and is treated here as an integer.
    """

    def __init__(self, register: Register, name: str, offset: int, width: int, default: int):
        """
        Args:
            register (Register): the register to which this value belongs (back reference)
            name (str): the name of this register value
            offset (int): the offset for the value in the 32-bit register [number of bits]
            width (int): the width of the register value [number of bits]
            default (int): the default register value
        """
        self._register = register
        self._name = name
        self._offset = offset
        self._width = width
        self._default = default

    def __repr__(self):
        return (
            f"Register('{self.register.name}', '{self.name}', "
            f"0x{self.register.address:0X}, {self.offset}, {self.width}, {self.default})"
        )

    @property
    def register(self):
        return self._register

    @property
    def name(self):
        return self._name

    @property
    def offset(self):
        return self._offset

    @property
    def width(self):
        return self._width

    @property
    def default(self):
        return self._default

    def get_value(self, data: bytes) -> int:
        """Read the value of this register variable from the given data.

        The data argument shall be at least 4 bytes long. The register value is assumed to fall
        within the first 32-bits of the data argument.

        This method is usually used when a register has been read from the memory map and a
        register value needs to be extracted. Alternatively, you can use the
        `get_value(reg_name, var_name)` method of the RegisterMap class.

        Args:
            data (bytes): a register data field

        Returns:
            value: the value of the given register variable.
        """
        data = int.from_bytes(data[:4], "big")
        value = (data >> self.offset) & set_bits(0x0, (0, self.width))
        return value


class RegisterMap:
    """
    The RegisterMap keeps track of the complete register map of the front-end electronics.

    When the given name argument is 'N-FEE' or 'F-FEE' the register map will be loaded from
    the corresponding configuration file and the memory map will be initialized with the
    default values. All other names will create an empty register map.

    When no name is given, or another name than 'N-FEE' or 'F-FEE', an empty register is created
    with the given name and the memory map will be initialised to zero.

    The RegisterMap only contains the critical, general and housekeeping areas. The windowing
    area is treated differently. That means the register map is 0x0800 (2048) bytes. The windowing
    area is 0x0080_0000 bytes (8MB) in size.

    """

    def __init__(self,
                 name: str = None, *,
                 size: int = 0,
                 memory_map: Union[bytearray, np.ndarray] = None):
        """
        Note: size and memory_map are keyword-only arguments, i.e. these arguments
              must be specified using the keyword.

        Args:
            name (str): the name for the register map.
            size (int): the size of the memory buffer in bytes (32-bit aligned!)
            memory_map: the memory map to be used for initialising the RegisterMap.
                The type of the memory_map can be a bytearray or a Numpy ndarray.
        """
        size = size or 0x0000_0800
        self._memory_map = bytearray(size)
        if name in ("N-FEE", "F-FEE"):
            self._name = name.upper()
            self._register_map = self._load_register_map()
            if isinstance(memory_map, np.ndarray):
                memory_map = bytearray(memory_map.tobytes())
            self._init_memory_map(memory_map)
        else:
            self._name = name
            self._register_map = {}

    def __iter__(self):
        return self._register_map.__iter__()

    def __str__(self):
        msg = f"Register Map for {self._name}\n"
        for reg_name in self:
            reg = self.get_register(reg_name)
            msg += f"{reg_name}:\n"
            for var_name in reg.keys():
                msg += f"    {var_name}={self.get_value(reg.name, var_name)}\n"
        return msg

    def __rich__(self):

        # Create a table with — for each HK parameter — the HEX value, the binary, the decimal, and the
        # calibrated value.
        #
        # To calibrate a value:
        # * get the list of parameter names for temperatures from
        # We don't want this!!!
        # supply_voltage_calibration = GlobalState.setup.camera.fee.calibration.supply_voltages
        # temperature_calibration = GlobalState.setup.camera.fee.calibration.temperatures

        table = Table("Register", "Parameter", "Value (int)", "Value (hex)")

        for reg_name in self:
            reg = self.get_register(reg_name)
            for var_name in reg.keys():
                value = self.get_value(reg.name, var_name)
                table.add_row(reg_name, var_name, str(value), hex(value))

        return table

    def get_memory_map_as_ndarray(self) -> np.ndarray:
        """
        Returns the memory map of the RegisterMap object. This memory map represents the memory
        area that is used in the N-FEE to store the configuration variables.

        Returns:
            A Numpy array of `dtype=uint8`.
        """
        return np.frombuffer(self._memory_map.copy(), dtype=np.uint8)

    def _init_memory_map(self, memory_map: bytearray = None):
        if memory_map is None:
            for reg in self._register_map.values():
                for var in reg.values():
                    self.set_value(reg.name, var.name, var.default)
        else:
            self._memory_map = memory_map


    def _load_register_map(self) -> dict:

        # This is not a good idea, the RegisterMap is not really instantiated in a critical context,
        # but this might happen. Instantiation of this class should be fast.

        fee_reg = GlobalState.setup.camera.fee.register_map

        register_map = {}

        for reg_name in fee_reg:
            # each register has the 'reg_address' as a mandatory field
            reg = Register(reg_name, fee_reg[reg_name]["reg_address"])
            for var_name in fee_reg[reg_name]:
                if var_name == "reg_address":
                    continue
                offset, width, default = fee_reg[reg_name][var_name]
                reg[var_name] = RegisterValue(reg, var_name, offset, width, default)
            register_map[reg_name] = reg

        return register_map

    def get_value(self, reg_name: str, var_name: str) -> int:
        """
        Return the current value for the given register variable name.

        This is equivalent to:

        ```value = reg_map[(reg_name, var_name)]```

        Args:
            reg_name (str): the name of the register
            var_name (str): the name of the sub-register, i.e. the name of the value

        Returns:
            value: the value of the variable from the register map.

        Raises:
            KeyError: when the var_name doesn't match a RegisterValue in the Register for reg_name.
        """
        reg: Register = self._register_map[reg_name]
        var: RegisterValue = reg[var_name]

        data = self._memory_map[reg.address : reg.address + 4]
        value = int.from_bytes(data, "big")
        value = (value >> var.offset) & set_bits(0x0, (0, var.width))

        return value

    def set_value(self, reg_name: str, var_name: str, value: int) -> None:
        """
        Set the value for the given register variable name.

        This is equivalent to:

        ```reg_map[(reg_name, var_name)] = value```

        Args:
            reg_name (str): the name of the register
            var_name (str): the name of the sub-register, i.e. the name of the value
            value (int): the new register value

        Raises:
            KeyError: when the var_name doesn't match a RegisterValue in the Register for reg_name.
        """
        reg: Register = self._register_map[reg_name]
        var: RegisterValue = reg[var_name]

        orig_value = temp = int.from_bytes(self._memory_map[reg.address : reg.address + 4], "big")
        start = var.offset
        for bit in range(var.width):
            temp = (
                set_bit(temp, start + bit) if value & (1 << bit) else clear_bit(temp, start + bit)
            )
        self._memory_map[reg.address : reg.address + 4] = temp.to_bytes(4, "big")
        if temp != orig_value:
            LOGGER.debug(
                f"set new value for register {reg_name}:{var_name}: "
                f"0b{beautify_binary(temp, size=32)} (was 0b{beautify_binary(orig_value, size=32)})"
            )

    def add_register(self, reg: Register):
        """
        Add a new Register to the register map and set the default values for all its variables.
        """
        self._register_map[reg.name] = reg
        for var in reg.values():
            self.set_value(reg.name, var.name, var.default)

    def get_register(self, reg_name: str) -> Register:
        """Returns the Register for the given name.

        Args:
            reg_name (str): the name of a Register in the RegisterMap

        Returns:
            register: the Register for the given name.

        Raises:
            KeyError: when no Register with the given name exists in the RegisterMap
        """

        # FIXME:
        #   This exposes a Register that is part of the RegisterMap and allows to make changes
        #   that can potentially invalidate the RegisterMap!
        #   Should we return a copy of the Register?
        return self._register_map[reg_name]

    def get_register_data(self, reg_name: str) -> bytes:
        """Returns the value of the register variable. A 32-bit bytes array."""
        reg: Register = self._register_map[reg_name]
        return self._memory_map[reg.address : reg.address + 4]

    def set_register_data(self, reg_name: str, data: bytes) -> None:
        """Writes the register data into the memory map."""
        reg: Register = self._register_map[reg_name]
        self._memory_map[reg.address : reg.address + 4] = data

    def get_data(self, address: int, length: int) -> bytes:
        """
        Read a range of bytes from the FEE memory map.

        Args:
            address: start address from where to start reading
            length: the number of bytes to read

        Returns:
            bytes from the requested address range.

        Raises:
            IndexError: when the address range falls out of the allowed range.
        """
        size = len(self._memory_map)
        if 0x0000_0000 <= address <= size - length:
            return self._memory_map[address : address + length]
        else:
            raise IndexError(
                f"The given address + length ({address} + {length} = {address+length}) fall out "
                f"of the addressable range of the memory map."
            )

    def set_data(self, address: int, data: bytes, length: int = 4) -> None:
        """
        Writes the register data into the memory map.

        This method can be used to replace single register values or even the complete register.
        By default, one single register will be set, i.e. 4 bytes.

        Args:
            address (int): start address from where to start writing (32-bit aligned)
            data (bytes): the data to write to the memory map
            length (int): the length of the data [default=4 bytes]

        Raises:
            ValueError when address is not 32-bit aligned.
        """
        if address & 0x03:
            raise ValueError(
                f"The given memory address is not 4-byte (32-bit) aligned. "
                f"[address=0x{address:02x}]"
            )
        self._memory_map[address : address + length] = data[:length]

    def __getitem__(self, item):
        """Return the current value for the given register variable.
        This equivalent to ``value = reg_map[reg_name, var_name]``.
        """
        if isinstance(item, str):
            return self._get_unambiguous_value(item)
        if not isinstance(item, (tuple, list)):
            raise KeyError(f"Expected a tuple or list with register name and variable name.")
        return self.get_value(item[0], item[1])

    def __setitem__(self, key, value):
        """Set the value for the given register variable.
        This equivalent to ``reg_map[reg_name, var_name] = value``.
        """
        if not isinstance(key, (tuple, list)):
            raise KeyError(
                f"Expected the 'key' argument to be a tuple or list with the register name "
                f"and the variable name as elements.")
        self.set_value(key[0], key[1], value)

    def _get_unambiguous_value(self, item):
        value = [self.get_value(reg_name, key)
                 for reg_name in self
                 for key in self.get_register(reg_name).keys()
                 if key == item]

        if len(value) == 0:
            raise KeyError(f"'{item}' is not a valid variable name in this Register map.")
        if len(value) > 1:
            raise KeyError(f"'{item}' is ambiguous and used in {len(value)} registers. Use the 'get_value()' method.")

        return value[0]

    def as_dict(self, flatten: bool = False):
        """
        Returns the RegisterMap as a dictionary. The register map is a nested data structure where
        each register contains a number of variables. When represented as a dictionary, the first
        level keys are the register names, the seconds level are the variable names and their
        values. When the registered map is returned as a flattened dict, the keys are constructed
        from the register name and the variable name, separated by a colon.

        Args:
            flatten (bool): return the RegisterMap as a flattened dictionary
        Returns:
            The RegisterMap as an (optionally flattened) dictionary.
        """
        _dict = {}
        if flatten:
            for reg in self._register_map.values():
                for var in reg.values():
                    value = self.get_value(reg.name, var.name)
                    _dict[f"{reg.name}:{var.name}"] = value
        else:
            for reg in self._register_map.values():
                vars_dict = {}
                for var in reg.values():
                    value = self.get_value(reg.name, var.name)
                    vars_dict[var.name] = value
                _dict[reg.name] = vars_dict

        return _dict


def compare_register_maps(reg_map_1: RegisterMap, reg_map_2: RegisterMap):
    """
    Compare two Register maps by content and variable names. The Register map is iterated over all
    registers and variables in registers and their names and values are compared element wise.

    When you only need to check the content, it might be better to use the
    `get_memory_map_as_ndarray()` method and compare the numpy arrays element wise, e.g.

    Args:
        reg_map_1 (RegisterMap): a register map
        reg_map_2 (RegisterMap): anothe register map

    Returns:
        A list with a description of the changes for each difference.
    """
    d1 = reg_map_1.as_dict(flatten=True)
    d2 = reg_map_2.as_dict(flatten=True)

    diff = [
        f"{k}: 0x{d1[k]:02x} -> 0x{d2[k]:02x}"
        for k, _ in set(d2.items()) - set(d1.items())
    ]

    return sorted(diff)
