import matplotlib.pyplot as plt

from locatus.util import *


def count_of_counts(df):
    df_user_seen_count = df.groupby('code_address')['DateTimeLocal'].agg(['count']).sort_values(['count'], ascending=False)
    s_count_of_counts = df_user_seen_count['count'].value_counts()
    return s_count_of_counts

if __name__ == "__main__":
    expected_num_entries = 32394696
    expected_num_devices = 1733808
    expected_num_sensors = 10

    df = load_data()

    assert df.shape[0] == expected_num_entries
    assert num_devices(df) == expected_num_devices
    assert num_sensors(df) == expected_num_sensors

    coc = count_of_counts(df)
    fig = coc.plot(style='.', logx=True, logy=True, figsize=(10,10))
    fig.set_xlabel('count')
    fig.set_ylabel('times device seen')
    plt.savefig('results/count_of_counts.png')
