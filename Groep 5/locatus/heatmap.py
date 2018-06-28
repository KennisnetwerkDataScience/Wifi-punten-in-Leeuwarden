import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import os, sys

from locatus.util import *
#from locatus.periodicity_fft import plot_device_fft

outdir = 'results/locatus/device_heatmap_yearweek_weekdayhour/'

def device_df(df, addr):
    return df.loc[df.code_address == addr]

def freq_yearweek_weekdayhour_full(df):
    df_size = df.groupby(['code_address','yearweek','weekdayhour']).size()
    f = df_size.unstack(2).fillna(0)
    #d = pd.DataFrame(0, index=yearweeks(df['dt']), columns=weekdayhours())
    #d.update(f)
    return f

def plot_device_heatmap(df, idx):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    d = pd.DataFrame(0, index=idx, columns=weekdayhours())
    d.update(df)
    #print(df)
    #print(d)
    plt.pcolor(d)
    set_axis_yearweek_weekdayhour(ax, idx)

def save(idx):
    def save_(grp):
        addr = grp.index.get_level_values(0)[0]
        print(addr)
        #print(grp)
        #idx = grp.index.get_level_values(1)
        grp.index = grp.index.droplevel(0)
        plot_device_heatmap(grp, idx)
        plt.savefig('%s%s.png' % (outdir, addr))
        plt.close()
    return save_

if __name__ == '__main__':
    #from locatus.heatmap import *
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    df = load_data()
    print('dt')
    df['dt'] = pd.to_datetime(df['DateTimeLocal'])
    df = df[['dt', 'code_address']]
    print('tag yearweek')
    tag(df, 'dt', 'yearweek', year_week)
    print('tag weekdayhour')
    tag(df, 'dt', 'weekdayhour', weekday_hour)
    yidx = yearweeks(df.dt)
    #df = df.loc[(df.DateTimeLocal > '2017-01-01') & (df.DateTimeLocal < '2018-01-01')]
    step = 100000
    for i in np.arange(0, num_devices(df), step):
        print('select')
        dfs = df.loc[(df.code_address >= i*step) & (df.code_address < (i+1)*step)]
        print('frequencies')
        f = freq_yearweek_weekdayhour_full(dfs)
        #idx = f.index.get_level_values(1).unique().sort_values()
        f.groupby('code_address').apply(save(yidx))
    #df = df.loc[(df.DateTimeLocal > '2017-01-01') & (df.DateTimeLocal < '2018-01-01')]
    #addresses = df.code_address.unique()
    #for addr in addresses:
    #    save_device_heatmap(df, addr)
#    #plot_device_fft(df, addr)
