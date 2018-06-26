import pandas as pd
import numpy as np
import datetime as dt
import msgpack
from pathlib import Path
import time

weekday_labels = ['ma','di','wo','do','vr','za','zo']

def day(x):
    return x.date()

def weekday_hour_formatter(val, pos):
    #if val % 24 == 0:
    return weekday_labels[int(val / 24) % 7]
    #return ''

def weekday_formatter(val, pos):
    return weekday_labels[int(val) % 7]

def yearweek_formatter(df, d):
    labels = df.index
    print(d)
    def f(val, pos):
        if val % d == 0 and val < len(labels):
            return labels[int(val)]
        return ''
    return f

def yearweek_formatter_labels(labels, d):
    def f(val, pos):
        print('%s %s' % (val, pos))
        if val % d == 0 and val < len(labels) and val >= 0:
            print(labels)
            print('return %s' % labels[int(val)])
            return labels[int(val)]
        return ''
    return f

def weekdays():
    return ['%1d' % d for d in range(1,8)]

def hours():
    return ['%02d' % d for d in range(24)]

def week(x):
    return '%2d' % x.isocalendar()[1]

def weekday(x):
    return '%1d' % x.isocalendar()[2]

def hour(x):
    return '%02d' % x.hour

def year_week(x):
    return '%04d-%02d' % (x.isocalendar()[0], x.isocalendar()[1])

def weekday_hour(x):
    return '%1d-%02d' % (x.isocalendar()[2], x.hour)

def tag(df, f, t, fun):
    df[t] = df[f].apply(lambda x: fun(x))

def dayhours():
    ret = []
    for d in range(1,8):
        for h in range(24):
            ret.append('%1d-%02d' % (d, h))
    return ret

def yearweeks(start, end):
    ret = []
    t = start
    while t < end:
        ret.append(year_week(t))
        t += dt.timedelta(weeks=1)
    return ret

def load_garage_transactions():
    start = time.process_time()
    csv_file_name = '../data/parkeerdata/leeuwarden_garage_parking_transactions.csv'
    mp_file_name = '../data/parkeerdata/leeuwarden_garage_parking_transactions.msgpack'
    mp_file = Path(mp_file_name)
    df = None
    if mp_file.is_file():
        df = pd.read_msgpack(mp_file_name)
        stop = time.process_time()
    else:
        df = pd.read_csv(csv_file_name, sep=';')
        stop = time.process_time()
        df['start'] = pd.to_datetime(df['start_parking_dt'], format='%d-%m-%Y %H:%M')
        df['end'] = pd.to_datetime(df['end_parking_dt'], format='%d-%m-%Y %H:%M')
        df['pay'] = pd.to_datetime(df['pay_parking_dt'], format='%d-%m-%Y %H:%M')
        df['zone'] = df['garage_id']
        df.to_msgpack(mp_file_name)
    print('Loading took %.3f s' % (stop - start))
    return df

def load_street_transactions():
    start = time.process_time()
    csv_file_name = '../data/parkeerdata/leeuwarden_street_parking_transactions.csv'
    mp_file_name = '../data/parkeerdata/leeuwarden_street_parking_transactions.msgpack'
    mp_file = Path(mp_file_name)
    df = None
    if mp_file.is_file():
        df = pd.read_msgpack(mp_file_name)
        stop = time.process_time()
    else:
        df = pd.read_csv(csv_file_name, sep=';', dtype={'meter_code': object})
        stop = time.process_time()
        df = df[df.isnull().any(axis=1) == False]
        df = df[df['total_duration_sec'] > 0]
        df['start'] = pd.to_datetime(df['start_parking_dt'], format='%d-%m-%Y %H:%M')
        df['end'] = df.apply(lambda r: r['start'] + dt.timedelta(seconds=r['total_duration_sec']), axis=1)
        df['zone'] = df['meter_code'].apply(lambda x: int(x[0:4]))
        df.to_msgpack(mp_file_name)
    print('Loading took %.3f s' % (stop - start))
    return df

def load_mobile_transactions():
    start = time.process_time()
    csv_file_name = '../data/parkeerdata/leeuwarden_mobile_parking_transactions.csv'
    mp_file_name = '../data/parkeerdata/leeuwarden_mobile_parking_transactions.msgpack'
    mp_file = Path(mp_file_name)
    df = None
    if mp_file.is_file():
        df = pd.read_msgpack(mp_file_name)
        stop = time.process_time()
    else:
        df = pd.read_csv(csv_file_name, sep=';')
        stop = time.process_time()
        df['start'] = pd.to_datetime(df['start_parking_dt'], format='%d-%m-%Y %H:%M')
        df['end'] = pd.to_datetime(df['end_parking_dt'], format='%d-%m-%Y %H:%M')
        df['zone'] = df['zone_code']
        df.to_msgpack(mp_file_name)
    print('Loading took %.3f s' % (stop - start))
    return df

def load_garages():
    csv_file_name = '../data/parkeerdata/leeuwarden_garage_parking_garage.csv'
    df = pd.read_csv(csv_file_name, sep=';')
    df.set_index('garage_id', inplace=True)
    return df

def fix_start_assume_first(df):
    df['start'].fillna(method='ffill', inplace=True)

def fix_end_by_timedelta(df, td):
    sel = df['end_parking_dt'].isnull()
    na = df[sel]
    df.loc[sel, 'end'] = na['start'] + td

def mark_periods(ts):
    ts['weekday'] = ts['dt'].apply(lambda x: x.weekday())
    ts['hour'] = ts['dt'].apply(lambda x: x.hour)

def timeseries_garages(df):
    start = pd.DataFrame(df['garage_id'], columns=('dt', 'garage_id', 'count'))
    start['dt'] = df['start']
    start['count'] = 1

    end = pd.DataFrame(df['garage_id'], columns=('dt', 'garage_id', 'count'))
    end['dt'] = df['end']
    end['count'] = -1

    ts = start.append(end, ignore_index=True).sort_values('dt')
    ts['sum'] = ts.groupby('garage_id')['count'].transform(pd.Series.cumsum)

    return ts

def timeseries(df):
    start = pd.DataFrame(df['zone'], columns=('dt', 'zone', 'count'))
    start['dt'] = df['start']
    start['count'] = 1

    end = pd.DataFrame(df['zone'], columns=('dt', 'zone', 'count'))
    end['dt'] = df['end']
    end['count'] = -1

    ts = start.append(end, ignore_index=True).sort_values('dt')
    ts['sum'] = ts.groupby('zone')['count'].transform(pd.Series.cumsum)

    return ts
