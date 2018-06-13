import pandas as pd
import numpy as np
import msgpack
from pathlib import Path
import time

def load_data():
    start = time.process_time()
    csv_file_name = '../data/parkeerdata/leeuwarden_garage_parking_transactions.csv'
    mp_file_name = '../data/parkeerdata/leeuwarden_garage_parking_transactions.msgpack'
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

def num_garages(df):
    return df.garage_id.nunique()
