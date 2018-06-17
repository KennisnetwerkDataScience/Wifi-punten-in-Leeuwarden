import pandas as pd
import datetime as dt

from locatus.util import *

def consecutive_days(df):
    df['date'] = df['DateTimeLocal'].apply(lambda x: dt.datetime.strptime(x, '%Y-%m-%d %H:%M:%S').date())
    df = df[['code_address', 'date']].drop_duplicates().sort_values(['code_address', 'date'])
    df['shift'] = df.groupby('code_address')['date'].shift() + dt.timedelta(days=1)
    df['cc'] = df.groupby(['code_address', (df['date'] != df['shift']).cumsum()]).cumcount()
    return df

if __name__ == '__main__':
    df = load_data()
    cd = consecutive_days(df)
    assert cd[cd.code_address == 1368474]['cc'].max() == 101
    assert cd[cd.code_address == 857937]['cc'].max() == 276
    assert cd[cd.code_address == 1133519]['cc'].max() == 249
    max_cd = cd.groupby('code_address')['cc'].max().sort_values()
    print(max_cd)
