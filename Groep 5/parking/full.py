import pandas as pd
import numpy as np
import datetime as dt

from parking.util import load_garage_transactions
from parking.util import load_garages
from parking.util import timeseries_garages as timeseries
from parking.util import fix_start_assume_first
from parking.util import fix_end_by_timedelta
from parking.util import mark_periods

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

    df['duration'] = df['end'] - df['start']

    ts = timeseries(df)

    mark_full(ts, garages)
    mark_changed(ts)
    mark_periods(ts)
    for i,v in garages.iterrows():
        print(i)
        print(v)
        print(changes_status(ts, i))
