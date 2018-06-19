import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
import matplotlib.ticker as ticker

from parking.util import load_garage_transactions
from parking.util import load_mobile_transactions
from parking.util import load_street_transactions
from parking.util import fix_start_assume_first
from parking.util import fix_end_by_timedelta
from parking.util import mark_periods
from parking.util import timeseries
from parking.util import dayhours
from parking.util import yearweeks
from parking.util import *


def weekday_hour_max(ts):
    tag(ts, 'dt', 'weekday', weekday)
    tag(ts, 'dt', 'hour', hour)
    df = ts.groupby(['weekday','hour'])['sum'].mean()
    f = df.unstack(1).fillna(0)
    d = pd.DataFrame(0., index=weekdays(), columns=hours())
    d.update(f)
    return d

def plot_heatmap(sel):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    xs = range(sel.shape[1])
    ys = range(sel.shape[0])

    ax.yaxis.set_major_formatter(ticker.NullFormatter())
    ax.yaxis.set_major_locator(MultipleLocator(1))

    ax.yaxis.set_minor_formatter(FuncFormatter(weekday_formatter))
    ax.yaxis.set_minor_locator(ticker.FixedLocator([0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5]))

    ax.xaxis.set_major_locator(MultipleLocator(6))

    for tick in ax.yaxis.get_minor_ticks():
        tick.tick1line.set_markersize(0)
        tick.tick2line.set_markersize(0)
        tick.label1.set_horizontalalignment('center')

    plt.pcolor(sel)

def save_heatmap(ts, one):
    plot_heatmap(weekday_hour_max(select_zone(ts, zone)))
    plt.savefig('results/parking_zone_%s_heatmap_week_hour.png' % zone)
    plt.close()

def select_zone(ts, zone):
    return ts[(ts['zone'] == zone)]

if __name__ == '__main__':
    df_g = load_garage_transactions()
    print('Assume start nan at previous entry')
    fix_start_assume_first(df_g)
    print('Assume end nan after 0 hours')
    fix_end_by_timedelta(df_g, dt.timedelta(hours=0))
    df_g = df_g.filter(items=['zone', 'start', 'end'])

    df_m = load_mobile_transactions()
    df_m = df_m.filter(items=['zone', 'start', 'end'])
    df_s = load_street_transactions()
    df_s = df_s.filter(items=['zone', 'start', 'end'])
    df = df_g.append(df_m, ignore_index=True).append(df_s, ignore_index=True)

    df['duration'] = df['end'] - df['start']

    ts = timeseries(df)
    mark_periods(ts)

    zones = df['zone'].unique()
    #for zone in zones:
    #    print(zone)
    #    print(ts[(ts['zone'] == zone)])

    for zone in zones:
        print('%4d %6d' %(zone,ts[(ts['zone'] == zone)]['sum'].max()))
        save_heatmap(ts, zone)
