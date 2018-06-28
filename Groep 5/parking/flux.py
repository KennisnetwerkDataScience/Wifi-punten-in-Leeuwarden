import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates

from parking.util import *

outdir = 'results/parking/garage/flux'

def flux_sum(ts, sample, window, garage_id, start, end):
    print(garage_id)
    print(start)
    print(end)
    tsd = ts.loc[start:end]
    tsd = tsd[tsd.garage_id == garage_id]
    print(tsd)
    tsd['out'] = np.where(tsd['count']==-1, 1, 0)
    tsd['in'] = np.where(tsd['count']==1, 1, 0)
    if tsd.shape[0] == 0:
        return tsd
    res = tsd.resample(sample)['in', 'out', 'count'].sum().fillna(0).rolling(window=window, min_periods=1).mean()
    res['sum'] = tsd[~tsd.index.duplicated(keep='first')].resample(sample).ffill()['sum']
    return res


def hour_formatter(val, pos):
    if val.minute == 0:
        return '%2s:%2s' % (val.hour, val.minute)
    return ''

def save_plot(ts, garages, sample, window, garage_id, start, end):
    capacity = garages.loc[[garage_id]]['capacity_value'].iloc[0]

    res = flux_sum(ts, sample, window, garage_id, start, end)
    if res.shape[0] == 0:
        return
    fig, ax = plt.subplots(figsize=(20, 10))
    plt.title(start.strftime('%Y-%m-%d'))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H-%M"))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H-%M"))
    #ax.xaxis.set_major_formatter(ticker.FuncFormatter(hour_formatter))
    #ax.xaxis.set_major_locator(ticker.MultipleLocator(24))
    ax.set_xlabel('time')
    ax.set_ylabel('flux', color='b')
    plt.ylim(-10, 30)
    ax.plot(res['count'], color='b', label='flux')
    ax.plot(res['in'], color='g', label='in')
    ax.plot(res['out'], color='y', label='out')
    ax.axhline(y=0, color='b')
    ax.legend(loc='upper left')
    ax2 = ax.twinx()
    ax2.set_ylabel('cars', color='r')
    plt.ylim(0, capacity + 100)
    ax2.plot(res['sum'], color='r', label='cumsum')
    ax2.axhline(y=capacity, color='r')
    ax2.axhline(y=0, color='r')
    ax2.legend(loc='upper right')
    ensure_dir('%s/%s' % (outdir, garage_id))
    plt.savefig('%s/%s/%s_%s.png' % (outdir, garage_id, start.strftime(dt_format), start.strftime(end)))
    plt.close()

if __name__ == '__main__':
    sample='1T'
    window=10

    ensure_dir(outdir)

    garages = load_garages()

    df = load_garage_transactions()
    fix_start_assume_first(df)
    fix_end_by_timedelta(df, dt.timedelta(hours=0))

    ts = timeseries_garages(df)
    ts = ts.set_index('dt')
    start = ts.index[0]
    start = start.replace(hour=0, minute=0, second=0)
    e = ts.index[-1]
    while(start < e):
        end = start + dt.timedelta(days=1)
        save_plot(ts, garages, '1T', 10, 36, start, end)
        save_plot(ts, garages, '1T', 10, 37, start, end)
        save_plot(ts, garages, '1T', 10, 38, start, end)
        save_plot(ts, garages, '1T', 10, 39, start, end)
        save_plot(ts, garages, '1T', 10, 40, start, end)
        start = end
