import pandas as pd
import numpy as np


def load_data():
    return pd.read_csv('../data/locatus/locatusdata_bewerkt_clean.csv', sep=';')

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
