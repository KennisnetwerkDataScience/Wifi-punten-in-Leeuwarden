import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import msgpack
from pathlib import Path
import time

def load_data():
    start = time.process_time()
    csv_file_name = '../data/locatus/locatusdata_bewerkt_clean.csv'
    mp_file_name = '../data/locatus/locatusdata_bewerkt_clean.msgpack'
    mp_file = Path(mp_file_name)
    data = None
    if mp_file.is_file():
        data = pd.read_msgpack(mp_file_name)
        stop = time.process_time()
    else:
        data = pd.read_csv(csv_file_name, sep=';')
        stop = time.process_time()
        data.to_msgpack(mp_file_name)
    print('Loading took %.3f s' % (stop - start))
    return data

def num_devices(df):
    return df.code_address.nunique()

def num_sensors(df):
    return df.VirtualSensorCode.nunique()

def print_n(df, n):
    with pd.option_context('display.max_rows', n):
        print (df)

def print_device_entries(df, addr, n):
    df_user = df.loc[df.code_address == addr].sort_values('DateTimeLocal')
    print_n(df_user, n)

def device_time(df, addr):
    return df.loc[df.code_address == addr].sort_values('DateTimeLocal')

def year_week(x):
    return '%04d-%02d' % (x.isocalendar()[0], x.isocalendar()[1])

def weekday_hour(x):
    return '%1d-%02d' % (x.isocalendar()[2], x.hour)

def tag(df, f, t, fun):
    df[t] = df[f].apply(lambda x: fun(x))

def weekdayhours():
    ret = []
    for d in range(1,8):
        for h in range(24):
            ret.append('%1d-%02d' % (d, h))
    return ret

def yearweeks(s):
    ret = []
    start = s.min()
    end = s.max()
    t = start
    while t < end:
        ret.append(year_week(t))
        t += dt.timedelta(weeks=1)
    return ret

weekday_labels = ['ma','di','wo','do','vr','za','zo']

def weekdayhour_formatter(val, pos):
    return weekday_labels[int(val / 24) % 7]

def weekday_formatter(val, pos):
    return weekday_labels[int(val) % 7]

def yearweek_formatter(s, d):
    def f(val, pos):
        if val % d == 0 and val >= 0 and val < len(s):
            return s[int(val)]
        return ''
    return f

def set_axis_yearweek_weekdayhour(ax, s):
    #plt.xlim(0, len(s))
    ax.xaxis.set_major_formatter(ticker.NullFormatter())
    ax.xaxis.set_major_locator(ticker.IndexLocator(base=24, offset=0))

    ax.xaxis.set_minor_formatter(ticker.FuncFormatter(weekdayhour_formatter))
    ax.xaxis.set_minor_locator(ticker.IndexLocator(base=24, offset=12))

    for tick in ax.xaxis.get_minor_ticks():
        tick.tick1line.set_markersize(0)
        tick.tick2line.set_markersize(0)
        tick.label1.set_verticalalignment('center')

    ax.yaxis.set_major_formatter(ticker.FuncFormatter(yearweek_formatter(s, 13)))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(13))
