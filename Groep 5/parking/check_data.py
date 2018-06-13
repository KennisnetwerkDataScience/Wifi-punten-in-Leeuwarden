import pandas as pd
import numpy as np
import datetime as dt
from util import load_data

def transform_dt(df):
    df['start'] = pd.to_datetime(df['start_parking_dt'], format='%d-%m-%Y %H:%M')
    df['end'] = pd.to_datetime(df['end_parking_dt'], format='%d-%m-%Y %H:%M')
    df['pay'] = pd.to_datetime(df['pay_parking_dt'], format='%d-%m-%Y %H:%M')

    df['duration'] = df['end'] - df['start']

def check_entries(df):
    has_null = df[pd.isnull(df[['start_parking_dt','end_parking_dt']]).any(axis=1)]
    print('%d with a null in a start / end column' % has_null.shape[0])

    has_null = df[pd.isnull(df['start_parking_dt'])]
    print('%d with a null in the start column' % has_null.shape[0])

    has_null = df[pd.isnull(df['end_parking_dt'])]
    print('%d with a null in the end column' % has_null.shape[0])

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

def check_timeseries(ts):
    max_count = ts['sum'].max()
    print('%d max in one garage' % max_count)

    max_count = ts.groupby('garage_id')['sum'].max()
    for e,i in max_count.iteritems():
        print('%s max in garage %s' % (i,e))

if __name__ == '__main__':
    df = load_data()
    transform_dt(df)
    check_entries(df)
    ts = timeseries(df)
    check_timeseries(ts)
