import matplotlib.pyplot as plt

from util import load_data


def count_of_counts(df):
    df_user_seen_count = df.groupby('code_address')['DateTimeLocal'].agg(['count']).sort_values(['count'], ascending=False)
    s_count_of_counts = df_user_seen_count['count'].value_counts()
    return s_count_of_counts

def plot_count_of_counts(s_count_of_counts):
    plt.xscale('log')
    plt.yscale('log')
    s_count_of_counts.plot.line()
    plt.show()


if __name__ == "__main__":
    expected_num_entries = 32394696
    expected_num_devices = 1733808
    expected_num_sensors = 10

    df = load_data()

    assert df.shape[0] == expected_num_entries
    assert num_devices(df) == expected_num_devices
    assert num_sensors(df) == expected_num_sensors

    coc = count_of_counts(df)
    plot(coc)
