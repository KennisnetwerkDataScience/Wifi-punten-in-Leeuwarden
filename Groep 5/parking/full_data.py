import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt

from parking.util import load_garage_transactions
from parking.util import load_garages
from parking.util import timeseries_garages as timeseries
from parking.util import fix_start_assume_first
from parking.util import fix_end_by_timedelta
from parking.util import mark_periods

def dayhours():
    ret = []
    for d in range(7):
        for h in range(24):
            ret.append('%s-%s' % (d, h))
    return ret

def yearweeks(start, end):
    ret = []
    t = start
    while t < end:
        ret.append(t.strftime('%Y-%W'))
        t += dt.timedelta(weeks=1)
    return ret

def yearweek_dayhour_full(ts):
    ts['yearweek'] = ts['dt'].apply(lambda x: x.strftime('%Y-%V'))
    ts['dayhour'] = ts['dt'].apply(lambda x: x.strftime('%w-%H'))
    df = ts.groupby(['yearweek','dayhour'])['full'].any()
    f = df.unstack(1).fillna(False)
    f = f.astype(int)
    start = ts['dt'].min()
    end = ts['dt'].max()
    d = pd.DataFrame(0, index=yearweeks(start,end), columns=dayhours())
    d.update(f)
    d = d.astype(int)
    return d

def plot_heatmap(sel):
    plt.pcolor(sel)
    #plt.yticks(np.arange(sel.shape[0]))
    plt.xticks(np.arange(sel.shape[1], step=24))

def save_heatmap(ts, garage_id):
    plot_heatmap(yearweek_dayhour_full(select_garage(ts, garage_id)))
    plt.savefig('results/parking_garage_%s_heatmap_yearweek_dayhour.png' % garage_id)

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

    ts = timeseries(df)

    mark_full(ts, garages)
    mark_changed(ts)
    #mark_periods(ts)
    for i,v in garages.iterrows():
        print(i)
        print(v)
        print(changes_status(ts, i))
        save_heatmap(ts, i)
