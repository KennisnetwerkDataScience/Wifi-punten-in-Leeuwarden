import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from util import load_data

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

if __name__ == '__main__':
    df = load_data()
    df = df.loc[(df.DateTimeLocal > '2017-01-01') & (df.DateTimeLocal < '2018-01-01')]
    addresses = df.code_address.unique()[0:1000]
    df_res = pd.DataFrame(columns=['count', 'std_weekday', 'std_hour'])
    for addr in addresses:
        d_df = device_df(addr)
        std_weekday = std_week_weekday(d_df)
        std_hour = std_week_hour(d_df)
        size = d_df.shape[0]
        df_res.loc[addr] = [size, std_weekday, std_hour]
        print('%10d %10d %6.4f %6.4f' % (addr, size, std_weekday, std_hour))

    df_res.plot(x='count', y='std_weekday', style='.', logx=True, logy=True)
    plt.savefig('results/count_stddev_week_weekday.png')

    df_res.plot(x='count', y='std_hour', style='.', logx=True, logy=True)
    plt.savefig('results/count_stddev_week_hour.png')
