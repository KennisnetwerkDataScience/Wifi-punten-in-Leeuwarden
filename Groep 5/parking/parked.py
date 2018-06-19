import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt

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
    d = pd.DataFrame(0., index=np.arange(7), columns=np.arange(24))
    d.update(f)
    return d

def yearweek_dayhour_max(ts):
    tag(ts, 'dt', 'yearweek', year_week)
    tag(ts, 'dt', 'dayhour', weekday_hour)
    df = ts.groupby(['yearweek','dayhour'])['sum'].mean()
    f = df.unstack(1).fillna(0)
    d = pd.DataFrame(0., index=np.arange(7), columns=np.arange(24))
    d.update(f)
    return d

def plot_heatmap(sel):
    plt.pcolor(sel)
    plt.yticks(np.arange(7))
    plt.xticks(np.arange(24))

def save_heatmap(ts, one):
    plot_heatmap(weekday_hour_max(select_zone(ts, zone)))
    plt.savefig('results/parking_zone_%s_heatmap_week_hour.png' % zone)

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
    for zone in zones:
        print(zone)
        print(ts[(ts['zone'] == zone)])

    for zone in zones:
        print('%4d %6d' %(zone,ts[(ts['zone'] == zone)]['sum'].max()))
        save_heatmap(ts, zone)
