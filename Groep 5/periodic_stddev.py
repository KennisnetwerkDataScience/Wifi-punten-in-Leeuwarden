import pandas as pd
import numpy as np

from util import load_data
from util import print_n


def periodic_stddev(df, col):
    s_size = df.groupby(['code_address', col]).size()
    df_size = pd.DataFrame(s_size)
    f = df_size.unstack(1).fillna(0)
    rf = f.div(f.sum(axis=1), axis=0)
    return rf.std(axis=1)


if __name__ == "__main__":
    expected_num_entries = 32394696
    expected_num_devices = 1733808
    expected_num_sensors = 10

    df = load_data()

    assert df.shape[0] == expected_num_entries
    assert num_devices(df) == expected_num_devices
    assert num_sensors(df) == expected_num_sensors

    df['T'] = pd.to_datetime(df['DateTimeLocal'])
    df['weekday'] = df['T'].apply(lambda x: x.weekday())
    df['month'] = df['T'].apply(lambda x: x.month)
    df['day'] = df['T'].apply(lambda x: x.day)
    df['hour'] = df['T'].apply(lambda x: x.hour)

    std_m = periodic_stddev(df, 'month')
    std_d = periodic_stddev(df, 'day')
    std_w = periodic_stddev(df, 'weekday')
    std_h = periodic_stddev(df, 'hour')
    sum = df.groupby(['code_address']).size()

    df_stds = pd.concat([std_m, std_d, std_w, std_h, sum], axis=1)
    print_n(df_stds.sort_values(4), 1000)
