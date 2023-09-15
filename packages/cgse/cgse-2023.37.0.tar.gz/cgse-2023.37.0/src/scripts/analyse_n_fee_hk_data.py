from __future__ import annotations

from pathlib import Path

import click
import pandas as pd
import rich
from rich.console import Console

TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f%z'

@click.command()
@click.argument('filename')
def analyse_n_fee_hk_data(filename: str | Path, new_format: int = True):
    """Analyses the N-FEE HK data that is saved in the CSV file."""

    filepath = Path(filename)

    if filepath.exists():
        console = Console(width=140)

        n_fee_hk = pd.read_csv(filepath, sep=",")
        df = pd.DataFrame(n_fee_hk, columns=['timestamp'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], format=TIME_FORMAT).map(pd.Timestamp.timestamp)
        df['time'] = df['timestamp']
        step = 2 if new_format else 1
        df = df.iloc[::step].set_index('time').sort_index()
        df_diff = df.diff()
        rich.print(df_diff)
        df_diff.plot(style='.-')

        # import matplotlib.pyplot as plt
        # plt.plot(df['time'], df['timestamp'], 'k.-')
        # plt.show()

    else:
        rich.print(f"no such file {filename!s}")


if __name__ == "__main__":
    # analyse_n_fee_hk_data()
    analyse_n_fee_hk_data("/Users/rik/data/CSL1/daily/20230514/20230514_CSL1_N-FEE-HK.csv", new_format=True)
    analyse_n_fee_hk_data("/Users/rik/data/CSL1/daily/20230515/20230515_CSL1_N-FEE-HK.csv", new_format=True)
    analyse_n_fee_hk_data("/Users/rik/00961_CSL1_chimay_N-FEE-HK_20230427_121117.csv", new_format=False)
