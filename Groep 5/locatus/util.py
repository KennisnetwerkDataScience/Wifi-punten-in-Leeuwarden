import pandas as pd
import numpy as np
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
