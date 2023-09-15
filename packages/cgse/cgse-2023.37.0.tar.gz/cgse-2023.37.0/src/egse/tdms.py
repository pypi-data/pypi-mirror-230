"""
This module provides functions to load and parse Labview TDMS files.

The text representation of a TDMS file is sent over a TCP/IP socket from the TCS EGSE to the Common-EGSE control
server. The format of the text string is as follows:

There are four groups of data: (1) the start time, (2) the time interval of the sampling, i.e. delta time,
(3) the parameter names, and (4) the actual sampled data. There is a blank line between each group. Each line
contains a lot of trailing whitespace in the form of a TAB character, '\\t'.

    start time:
    12/04/2019 17:38:27.584141

    dt:
    0.1

    channel names:
    Ch1_name    Ch2_name    Ch3_name

    data:
    0.1 0.2 0.3
    0.2 0.3 0.1
    0.3 0.1 0.2

A full description of the TDMS text file format is given in the TCS EGSE ICD [PTO-AST-PL-TCGSE-ICD-0012].
"""
import datetime
import io
import logging
from typing import Union

import numpy as np

from collections import namedtuple
from pathlib import Path

from egse.config import find_file
from egse.system import Timer

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)


def load_tdms_from_string(data_string: str):
    """
    Loads and parses a string representation of a Labview TDMS file. This function calls `load_tdms_from_stream()`.
    See the latter function for documentation on the return value.

    Args:
        data_string: a string containing the TDMS data

    Returns:
        a namedtuple with fields ['start_time', 'time_interval', 'names', 'values', 'time'].

    Raises:
        ValueError: when an input error is detected, e.g. incorrect file format or filename is None

    """
    with io.StringIO(data_string) as tdms:
        data = load_tdms_from_stream(tdms)

    return data


def load_tdms_from_file(filename: Union[str, Path]):
    """
    Loads and parses a text file representation of a Labview TDMS file. This function calls `load_tdms_from_stream()`.
    See the latter function for documentation on the return value.

    Args:
        filename: the full path name of the file

    Returns:
        a namedtuple with fields ['start_time', 'time_interval', 'names', 'values', 'time'].

    Raises:
        ValueError: when an input error is detected, e.g. incorrect file format or filename is None
        FileNotFoundError: when a given filename doesn't exist

    """
    if filename is None:
        raise ValueError("No filename was given or filename is None.")

    with Path(filename).open(mode='r') as tdms:
        data = load_tdms_from_stream(tdms)

    return data


def load_tdms_from_stream(stream):
    """
    Loads and parses a text representation of a Labview TDMS file. The format of the file is fixed and is
    described at the module level docstring.

    The stream is parsed and returned as a namedtuple which contains the following fields:

    * **start_time**: a `datetime` object that contains the start time of the sampling period [datetime]
    * **time_interval**: the sampling time interval [s]
    * **names**: a list of parameter names, one for each column in values [str]
    * **values**: a two-dimensional numpy array containing the samples. The shape is (number of names,
    number of samples) [float]
    * **time**: a numpy array with the sampling times for the values [datetime]

    Args:
        stream: a stream that supports the io protocol for readline() and readlines().

    Returns:
        a namedtuple with fields ['start_time', 'time_interval', 'names', 'values', 'time'].

    Raises:
        ValueError: when an input error is detected, e.g. incorrect file format or filename is None

    """

    MAX_LINE_LENGTH = 80

    # The first line in the file shall be the starting time of the sample

    line = stream.readline()
    if line.startswith('start time:'):
        line = stream.readline().rstrip()
        start_time = line.split('\t')[0]
        start_time = datetime.datetime.strptime(start_time, '%m/%d/%Y %H:%M:%S.%f')
    else:
        raise ValueError(
            f"TDMS Error: expected start time as the first line, got {line[:MAX_LINE_LENGTH]}.")

    # The next line shall be the time interval 'dt' as a float

    stream.readline()  # skip the empty line
    line = stream.readline()
    if line.startswith('dt:'):
        line = stream.readline().rstrip()
        time_interval = float(line.split('\t')[0])
    else:
        raise ValueError(f"TDMS Error: expected 'dt:', got {line[:MAX_LINE_LENGTH]}.")

    # The next line contains the channel names

    stream.readline()  # skip the empty line
    line = stream.readline()
    if line.startswith('channel names:'):
        line = stream.readline().rstrip()
        names = line.split('\t')
        keys = [name for name in names]
        data = [[] for _ in names]
    else:
        raise ValueError(f"TDMS Error: expected 'channel names:', got {line[:MAX_LINE_LENGTH]}.")

    # The next lines contain the data

    stream.readline()  # skip the empty line
    line = stream.readline()
    if line.startswith('data:'):
        lines = stream.readlines()  # this should read the rest of the file
        for line in lines:
            values = line.rstrip().split('\t')
            for idx, value in enumerate(values):
                data[idx].append(float(value))
    else:
        raise ValueError(f"TDMS Error: expected 'data:', got {line[:MAX_LINE_LENGTH]}.")

    time_serie = np.array(
        [start_time + datetime.timedelta(seconds=x*time_interval) for x in range(len(lines))]
    )

    # Make a data structure out of this, i.e. a named tuple

    tdms = namedtuple('TDMS', ['start_time', 'time_interval', 'names', 'values', 'time'])

    return tdms(start_time=start_time, time_interval=time_interval, names=keys, values=np.array(data), time=time_serie)
