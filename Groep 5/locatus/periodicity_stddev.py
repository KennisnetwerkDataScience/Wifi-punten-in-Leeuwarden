import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from locatus.util import load_data
from locatus.util import *

def device_df(addr):
    return df.loc[df.code_address == addr]

def std_week_weekday(d_df):
    d_df['T'] = pd.to_datetime(d_df['DateTimeLocal'])
    d_df['week'] = d_df['T'].apply(lambda x: x.week)
    d_df['weekday'] = d_df['T'].apply(lambda x: x.weekday())
    df_size = d_df.groupby(['week','weekday']).size()
    f = df_size.unstack(1).fillna(0)
    rf = f.div(f.sum(axis=1).sum(), axis=0)
    d = pd.DataFrame(0, index=np.arange(1, 54), columns=np.arange(7))
    d.update(rf)
    return d.std(axis=0).sum()

def freq_week_hour(d_df):
    d_df['T'] = pd.to_datetime(d_df['DateTimeLocal'])
    d_df['week'] = d_df['T'].apply(lambda x: x.week)
    d_df['hour'] = d_df['T'].apply(lambda x: x.weekday() * 24 + x.hour)
    df_size = d_df.groupby(['week','hour']).size()
    return df_size.unstack(1).fillna(0)

def freq_week_hour_full(d_df):
    d_df['T'] = pd.to_datetime(d_df['DateTimeLocal'])
    d_df['week'] = d_df['T'].apply(lambda x: x.week)
    d_df['hour'] = d_df['T'].apply(lambda x: x.weekday() * 24 + x.hour)
    df_size = d_df.groupby(['week','hour']).size()
    f = df_size.unstack(1).fillna(0)
    d = pd.DataFrame(0., index=np.arange(1, 54), columns=np.arange(7 * 24))
    d.update(f)
    return d

def std_week_hour(d_df):
    d_df['T'] = pd.to_datetime(d_df['DateTimeLocal'])
    d_df['week'] = d_df['T'].apply(lambda x: x.week)
    d_df['hour'] = d_df['T'].apply(lambda x: x.weekday() * 24 + x.hour)
    df_size = d_df.groupby(['week','hour']).size()
    f = df_size.unstack(1).fillna(0)
    rf = f.div(f.sum(axis=1).sum(), axis=0)
    d = pd.DataFrame(0, index=np.arange(1, 54), columns=np.arange(7 * 24))
    d.update(rf)
    return d.std(axis=0).sum()

def plot_device_heatmap(sel):
    plt.pcolor(sel)
    plt.yticks(np.arange(0, 54, 1))
    plt.xticks(np.arange(0, 7 * 24 + 1, 1))

def save_device_heatmap(addr):
    plot_device_heatmap(freq_week_hour_full(device_df(addr)))
    plt.savefig('results/freq_week_hour_%s.png' % addr)
    plt.close()

if __name__ == '__main__':
    df = load_data()
    df = df.loc[(df.DateTimeLocal > '2017-01-01') & (df.DateTimeLocal < '2018-01-01')]
    addresses = df.code_address.unique()[1000:]
    df_res = pd.DataFrame(columns=['count', 'std_weekday', 'std_hour'])
    for addr in addresses:
        d_df = device_df(addr)
        std_weekday = std_week_weekday(d_df)
        std_hour = std_week_hour(d_df)
        size = d_df.shape[0]
        df_res.loc[addr] = [size, std_weekday, std_hour]
        save_device_heatmap(addr)
        print('%10d %10d %6.4f %6.4f' % (addr, size, std_weekday, std_hour))

    df_res.plot(x='count', y='std_weekday', style='.')
    plt.savefig('results/count_stddev_week_weekday.png')

    df_res.plot(x='count', y='std_hour', style='.')
    plt.savefig('results/count_stddev_week_hour.png')

    df_res.plot(x='count', y='std_weekday', style='.', logx=True, logy=True)
    plt.savefig('results/count_stddev_week_weekday_log.png')

    df_res.plot(x='count', y='std_hour', style='.', logx=True, logy=True)
    plt.savefig('results/count_stddev_week_hour_log.png')
