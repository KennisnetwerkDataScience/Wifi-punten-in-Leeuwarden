import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator, MultipleLocator

from parking.util import load_garage_transactions
from parking.util import load_garages
from parking.util import timeseries_garages
from parking.util import fix_start_assume_first
from parking.util import fix_end_by_timedelta
from parking.util import mark_periods
from parking.util import dayhours
from parking.util import yearweeks
from parking.util import *


def yearweek_dayhour_full(ts):
    tag(ts, 'dt', 'yearweek', year_week)
    tag(ts, 'dt', 'dayhour', weekday_hour)
    df = ts.groupby(['yearweek','dayhour'])['full'].any()
    f = df.unstack(1).fillna(False)
    f = f.astype(int)
    start = ts['dt'].min()
    end = ts['dt'].max()
    d = pd.DataFrame(0, index=yearweeks(start,end), columns=dayhours())
    d.update(f)
    d = d.astype(int)
    return d

def yearweek_dayhour_max(ts):
    tag(ts, 'dt', 'yearweek', year_week)
    tag(ts, 'dt', 'dayhour', weekday_hour)
    df = ts.groupby(['yearweek','dayhour'])['sum'].max()
    f = df.unstack(1).fillna(False)
    start = ts['dt'].min()
    end = ts['dt'].max()
    d = pd.DataFrame(0, index=yearweeks(start,end), columns=dayhours())
    print(f)
    d.update(f)
    d = d.astype(int)
    print(d)
    return d

def plot_heatmap(sel):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    xs = range(sel.shape[1])
    ys = range(sel.shape[0])

    ax.xaxis.set_major_formatter(ticker.NullFormatter())
    ax.xaxis.set_major_locator(MultipleLocator(24))

    ax.yaxis.set_minor_formatter(FuncFormatter(weekday_hour_formatter))
    ax.yaxis.set_minor_locator(ticker.IndexLocator(base=24, offset=12))

    for tick in ax.yaxis.get_minor_ticks():
        tick.tick1line.set_markersize(0)
        tick.tick2line.set_markersize(0)
        tick.label1.set_horizontalalignment('center')

    ax.yaxis.set_major_formatter(FuncFormatter(yearweek_formatter(sel, 13)))
    ax.yaxis.set_major_locator(MultipleLocator(13))

    plt.pcolor(sel)
    #plt.yticks(np.arange(sel.shape[0]))
    #plt.xticks(np.arange(sel.shape[1], step=24))

def save_heatmap(ts, garage_id):
    plot_heatmap(yearweek_dayhour_full(select_garage(ts, garage_id)))
    plt.savefig('results/parking_garage_%s_heatmap_yearweek_dayhour_full.png' % garage_id)
    plt.close()

    plot_heatmap(yearweek_dayhour_max(select_garage(ts, garage_id)))
    plt.savefig('results/parking_garage_%s_heatmap_yearweek_dayhour_max.png' % garage_id)
    plt.close()

def select_garage(ts, garage_id):
    return ts[(ts['garage_id'] == garage_id)]

def mark_full(ts, garages):
    ts['capacity'] = ts['garage_id'].map(garages['capacity_value'])
    ts['full'] = ts['sum'] >= ts['capacity']

def mark_changed(ts):
    g = ts.groupby('garage_id')['full']
    ts['shifted'] = g.shift()
    ts['changed'] = ts['full'] ^ ts['shifted']
    ts.changed.fillna(True, inplace=True)

def changes_status(ts, garage_id):
    return ts.loc[(ts['garage_id'] == garage_id) & ts['changed']]

if __name__ == '__main__':
    garages = load_garages()

    df = load_garage_transactions()
    print('Assume start nan at previous entry')
    fix_start_assume_first(df)
    print('Assume end nan after 0 hours')
    fix_end_by_timedelta(df, dt.timedelta(hours=0))

    #df['duration'] = df['end'] - df['start']

    ts = timeseries_garages(df)

    mark_full(ts, garages)
    mark_changed(ts)
    #mark_periods(ts)
    for i,v in garages.iterrows():
        print(i)
        print(v)
        #print(changes_status(ts, i))
        save_heatmap(ts, i)
