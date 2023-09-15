from argparse import ArgumentParser

import pandas as pd

# Use these names to read the agilent channels from the setup
from egse.state import GlobalState

# This script generates the tm_dictionary entries for the agilent channels defined in the setup.
# It uses Heino's harnes excel sheet to fill in what each channel is connected to in the description.

long_names = ['agilent34970_0', 'agilent34970_1', 'agilent34972_0', 'agilent34972_1']
short_names = ['AG34970_0', 'AG34970_1', 'AG34972_0', 'AG34972_1']
storage_mnemonic = ['AG34970-0', 'AG34970-1', 'AG34972-0', 'AG34972-1']
sensor_types = ['two_wire', 'four_wire', 'thermocouples', 'pt100']

parser = ArgumentParser()
parser.add_argument('--filename', '-f', type=str, required=True, help="path to Heino's connection spreadsheet")
args = parser.parse_args()

with open(args.filename, 'rb') as f:
    harness = pd.read_excel(f)

setup = GlobalState.setup

for long_name, short_name, mnemonic in zip(long_names, short_names, storage_mnemonic):
    for sensor_type in sensor_types:
        for channel in setup.gse[long_name][sensor_type]:

            # find matching column in excel sheet
            description = ""
            for index, row in harness.iterrows():
                if row[1].lower() == long_name and row[2] == channel:
                    description = row[3]
                    break

            print(f'{long_name} temperature read-out;{mnemonic};GSRON_{short_name}_R{channel};GSRON_{short_name}_R{channel};timestamp;;;;;{description};;Ohm;;;;;;;;')
            print(f'{long_name} temperature read-out;{mnemonic};GSRON_{short_name}_T{channel};GSRON_{short_name}_T{channel};timestamp;;;;;{description};;DegCelsius;;;;;;;;')
            
