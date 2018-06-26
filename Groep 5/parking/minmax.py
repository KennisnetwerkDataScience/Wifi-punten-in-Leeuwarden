import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
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


def yearweek_weekday_max(ts):
    tag(ts, 'dt', 'yearweek', year_week)
    tag(ts, 'dt', 'weekday', weekday)
    df = ts.groupby(['yearweek','weekday'])['sum'].max()
    f = df.unstack(1).fillna(False)
    start = ts['dt'].min()
    end = ts['dt'].max()
    d = pd.DataFrame(0, index=yearweeks(start,end), columns=weekdays())
    d.update(f)
    d = d.astype(int)
    return d

def yearweek_weekday_min(ts):
    tag(ts, 'dt', 'day', day)
    df = ts.groupby(['day'])['sum'].min()
    return d

def select_garage(ts, garage_id):
    return ts[(ts['garage_id'] == garage_id)]

def smooth(box_pts):
    def smooth_(y):
        box = np.ones(box_pts) / box_pts
        y_smooth = np.convolve(y, box, mode='same')
        return y_smooth
    return smooth_

if __name__ == '__main__':
    garages = load_garages()

    df = load_garage_transactions()
    print('Assume start nan at previous entry')
    fix_start_assume_first(df)
    print('Assume end nan after 0 hours')
    fix_end_by_timedelta(df, dt.timedelta(hours=0))

    ts = timeseries_garages(df)
    tag(ts, 'dt', 'yearweek', year_week)
    min = ts.groupby(['garage_id', 'yearweek'])['sum'].min()
    max = ts.groupby(['garage_id', 'yearweek'])['sum'].max()

    colors = ['r','b','g','c','m']

    xlabels = ts['yearweek'].unique()

    legend = []
    legend.extend(['minimum %s' % i for i in np.arange(36, 41)])
    legend.extend(['smooth(10) %s' % i for i in np.arange(36, 41)])

    fig, ax = plt.subplots(figsize=(20, 10))
    ax.xaxis.set_major_formatter(FuncFormatter(yearweek_formatter_labels(xlabels, 13)))
    ax.xaxis.set_major_locator(MultipleLocator(13))
    ax.set_color_cycle(colors)
    ax.plot(min.groupby('garage_id').apply(pd.Series).unstack(0), linestyle='--')
    ax.plot(min.groupby('garage_id').apply(smooth(10)).apply(pd.Series).transpose())
    ax.legend(legend, loc='upper right')
    plt.savefig('results/parking_garages_min.png')
    #plt.show()
    plt.close()

    legend = []
    legend.extend(['maximum %s' % i for i in np.arange(36, 41)])
    legend.extend(['smooth(10) %s' % i for i in np.arange(36, 41)])

    fig, ax = plt.subplots(figsize=(20, 10))
    i = 0
    for garage_id,v in garages.sort_index().iterrows():
        capacity = garages.loc[[garage_id]]['capacity_value'].iloc[0]
        ax.axhline(y=capacity, color=colors[i])
        i = i + 1

    ax.xaxis.set_major_formatter(FuncFormatter(yearweek_formatter_labels(xlabels, 13)))
    ax.xaxis.set_major_locator(MultipleLocator(13))
    ax.set_color_cycle(colors)
    ax.plot(max.groupby('garage_id').apply(pd.Series).unstack(0), linestyle='--')
    ax.plot(max.groupby('garage_id').apply(smooth(10)).apply(pd.Series).transpose())
    ax.legend(legend, loc='upper right')

    plt.savefig('results/parking_garages_max.png')
    #plt.show()
    plt.close()
