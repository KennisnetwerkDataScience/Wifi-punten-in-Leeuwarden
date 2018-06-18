import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from util import load_data
from util import *
from locatus.periodicity_fft import plot_device_fft

def device_df(df, addr):
    return df.loc[df.code_address == addr]

def freq_week_hour_full(d_df):
    d_df['T'] = pd.to_datetime(d_df['DateTimeLocal'])
    d_df['week'] = d_df['T'].apply(lambda x: x.week)
    d_df['hour'] = d_df['T'].apply(lambda x: x.weekday() * 24 + x.hour)
    df_size = d_df.groupby(['week','hour']).size()
    f = df_size.unstack(1).fillna(0)
    d = pd.DataFrame(0., index=np.arange(1, 54), columns=np.arange(7 * 24))
    d.update(f)
    return d

def plot_device_heatmap(sel):
    print(sel)
    plt.pcolor(sel)
    plt.yticks(np.arange(0, 54, 1))
    plt.xticks(np.arange(0, 7 * 24 + 1, 1))

def save_device_heatmap(df, addr):
    plot_device_heatmap(freq_week_hour_full(device_df(df, addr)))
    plt.savefig('results/timeseries_%s_heatmap_week_hour.png' % addr)

if __name__ == '__main__':
    df = load_data()
    df = df.loc[(df.DateTimeLocal > '2017-01-01') & (df.DateTimeLocal < '2018-01-01')]
    addresses = df.code_address.unique()
    for addr in addresses:
        save_device_heatmap(df, addr)
        plot_device_fft(df, addr)
