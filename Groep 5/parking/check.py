import pandas as pd
import numpy as np
import datetime as dt

from parking.util import load_garage_transactions
from parking.util import load_garages


def transform_dt(df):
    if not 'start' in df.columns:
        df['start'] = pd.to_datetime(df['start_parking_dt'], format='%d-%m-%Y %H:%M')
    if not 'end' in df.columns:
        df['end'] = pd.to_datetime(df['end_parking_dt'], format='%d-%m-%Y %H:%M')
    if not 'pay' in df.columns:
        df['pay'] = pd.to_datetime(df['pay_parking_dt'], format='%d-%m-%Y %H:%M')

    df['duration'] = df['end'] - df['start']

def check_entries(df):
    print('%d entries' % df.shape[0])

    has_null = df[pd.isnull(df[['start_parking_dt','end_parking_dt']]).any(axis=1)]
    print('%d with a null in a start / end column' % has_null.shape[0])

    has_null = df['start_parking_dt'].isnull().sum()
    print('%d with a null in the start column' % has_null)

    has_null = df['end_parking_dt'].isnull().sum()
    print('%d with a null in the end column' % has_null)

    rows = df[df['duration'] < dt.timedelta(0)]
    print('%d with a negative duration' % rows.shape[0])

    rows = df[df['duration'] == dt.timedelta(0)]
    print('%d with a 0 duration' % rows.shape[0])

    duration = df['duration']
    max_duration = duration[pd.isnull(duration) == False].sort_values().max()
    print('max duration is %s' % max_duration)

    max_duration = df[(df['duration'].isnull() == False) & (df['card_type_id'] == 220)].sort_values('duration')['duration'].max()
    print('max duration for short parking is %s' % max_duration)

    count = df[(df['duration'].isnull() == False) & (df['card_type_id'] == 220) & (df['duration'] > dt.timedelta(days=1))].sort_values('duration')['duration'].count()
    print('%d short parking entries longer than one day' % count)

def timeseries(df):
    start = pd.DataFrame(df['garage_id'], columns=('dt', 'garage_id'))
    start['dt'] = df['start']
    start['count'] = 1

    end = pd.DataFrame(df['garage_id'], columns=('dt', 'garage_id'))
    end['dt'] = df['end']
    end['count'] = -1

    ts = start.append(end, ignore_index=True).sort_values('dt')
    ts['sum'] = ts.groupby('garage_id')['count'].transform(pd.Series.cumsum)

    return ts

def check_timeseries(ts, garages):
    max_count = ts['sum'].max()
    print('%d max in one garage' % max_count)

    max_count = ts.groupby('garage_id')['sum'].max()
    for i,v in max_count.iteritems():
        capacity = garages.loc[i]['capacity_value']
        name = garages.loc[i]['garage_nm']
        print('%r %s max in garage %s with capacity %d' % (v <= capacity, v, name, capacity))

def fix_start_assume_first(df):
    df['start'].fillna(method='ffill', inplace=True)

def fix_end_by_timedelta(df, td):
    sel = df['end_parking_dt'].isnull()
    na = df[sel]
    df.loc[sel, 'end'] = na['start'] + td

def mark_full(ts):
    ts['capacity'] = ts['garage_id'].map(garages['capacity_value'])
    ts['full'] = ts['sum'] >= ts['capacity']

def mark_changed(ts):
    g = ts.groupby('garage_id')['full']
    ts['shifted'] = g.shift()
    ts['changed'] = ts['full'] ^ ts['shifted']
    ts.changed.fillna(True, inplace=True)

def mark_periods(ts):
    ts['weekday'] = ts['dt'].apply(lambda x: x.weekday())
    ts['hour'] = ts['dt'].apply(lambda x: x.hour)

def changes_status(ts, garage_id):
    return ts.loc[(ts['garage_id'] == garage_id) & ts['changed']]

if __name__ == '__main__':
    garages = load_garages()

    df = load_garage_transactions()
    transform_dt(df)
    check_entries(df)
    ts = timeseries(df)
    check_timeseries(ts, garages)

    print('Assume start nan at previous entry')
    fix_start_assume_first(df)

    print('Assume end nan after 6 hours')
    fix_end_by_timedelta(df, dt.timedelta(hours=6))
    df['duration'] = df['end'] - df['start']
    ts = timeseries(df)
    check_timeseries(ts, garages)

    print('Assume end nan after 5 hours')
    fix_end_by_timedelta(df, dt.timedelta(hours=5))
    df['duration'] = df['end'] - df['start']
    ts = timeseries(df)
    check_timeseries(ts, garages)

    print('Assume end nan after 0 hours')
    fix_end_by_timedelta(df, dt.timedelta(hours=0))
    df['duration'] = df['end'] - df['start']
    ts = timeseries(df)
    check_timeseries(ts, garages)
