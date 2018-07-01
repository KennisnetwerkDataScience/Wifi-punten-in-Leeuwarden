# pca: used random forest models from "parkeer garages analyse - opslaan van modellen.py
# to predict 7 july 2018 and visualize the parking garages.

import pandas as pd
import datetime

from sklearn.ensemble import RandomForestClassifier
import pickle
import networkx as nx
from leeuwarden_kennis.config_data import base_file_location
from leeuwarden_kennis.config_data import ffmpeg_location
import collections
import matplotlib.pyplot as plt
import matplotlib.animation

parking_ids = [36, 37, 38, 39, 40]

classifiers = {garage_id: pickle.load(open(base_file_location(r"data\classifier_garage_{0}.sav").format(garage_id),
                                           "rb")) for garage_id in parking_ids}


# prepare dataset
# fields:
# index;date;hour;count_in;count_out;delta;cum_sum;week;month;day;dayofyear;weekday;year;YYYYMMDD;HH;R
def create_dataset(prediction_date: datetime.datetime, rain: float):
    pd_prediction_date = pd.to_datetime(prediction_date)

    ds_dict = dict()

    for idx in range(0, 24):
        date = pd_prediction_date.strftime('%Y-%m-%d')
        hr = idx
        # not used in prd
        count_in = 0
        count_out = 0
        delta = 0
        cum_sum = 0

        week = pd_prediction_date.week
        month = pd_prediction_date.month
        day = pd_prediction_date.day
        dayofyear = pd_prediction_date.dayofyear
        weekday = pd_prediction_date.weekday()
        year = pd_prediction_date.year
        YYYYMMDD = pd_prediction_date.strftime('%Y%m%d')
        HH = idx
        R = rain

        ds_dict[idx] = (idx, date, hr, count_in, count_out, delta, cum_sum, week, month, day, dayofyear, weekday, year, YYYYMMDD, HH, R)

    return pd.DataFrame.from_dict(ds_dict, columns=['index', 'date', 'hour', 'count_in', 'count_out', 'delta', 'cum_sum', 'week', 'month', 'day', 'dayofyear',
                                                    'weekday', 'year', 'YYYYMMDD', 'HH', 'R'], orient='index')



def prepare_dataset_mem(visitors_per_hour):


    X = visitors_per_hour.copy()
    # drop the target_variable
    X = X.drop(['cum_sum'], axis=1)
    # drop id from feature table (overfitting)
    X = X.drop(['index'], axis=1)
    # drop visitors (explainable variable with respect to the binned-target variable)
    # drop datetime (overfitting)
    X = X.drop(['date'], axis=1)
    # drop direct influencers
    X = X.drop(['count_in', 'count_out', 'delta', 'month'], axis=1)
    # drop weather data dates
    X = X.drop(['YYYYMMDD', 'HH'], axis=1)
    return X


def prepare_dataset(garage_id):
    #path = r'E:\Files\leeuwarden\leeuwarden_data'
    parking_locations = pd.read_csv(base_file_location(r'parkeerdata\leeuwarden_garage_parking_garage_gps.csv'),
                                    sep=";", decimal=",")

    name = r"data\out-visitors_per_hour-garage" + str(garage_id) + "_predict.csv"

    # Load data
    visitors_per_hour = pd.read_csv(base_file_location(name), sep=";")

    matched_row = parking_locations.loc[parking_locations.garage_id == garage_id]
    capacity = int(matched_row.capacity_value)
    visitors_per_hour['perc'] = 100 * visitors_per_hour['cum_sum'] / capacity

    X = visitors_per_hour.copy()
    # drop the target_variable
    #X = X.drop(['occupation', 'cum_sum'], axis=1)
    X = X.drop(['cum_sum'], axis=1)
    # drop id from feature table (overfitting)
    X = X.drop(['index'], axis=1)
    # drop visitors (explainable variable with respect to the binned-target variable)
    X = X.drop('perc', axis=1)
    # drop datetime (overfitting)
    X = X.drop(['date'], axis=1)
    # drop direct influencers
    X = X.drop(['count_in', 'count_out', 'delta', 'month'], axis=1)
    # drop weather data dates
    X = X.drop(['YYYYMMDD', 'HH'], axis=1)
    return X



def create_graph(df_predictions, df_garage_locations, hour):
    network_G = nx.Graph()

    color_map = dict()
    color_map[0] = 'green'
    color_map[1] = 'orange'
    color_map[2] = 'red'

    for garage in df_garage_locations.iterrows():
        garage_id = garage[1]['garage_id']
        network_G.add_node(garage_id)

        x, y = garage[1]['longitude'], garage[1]['latitude']
        print((x,y))
        network_G.node[garage_id]['coordinates'] = (x, y)
        network_G.node[garage_id]['location'] = garage[1]['garage_nm']
        network_G.node[garage_id]['width'] = garage[1]['capacity_value'] * 2


        network_G.node[garage_id]['color'] = color_map[df_predictions.loc[garage_id][hour]]

    return network_G


def draw_network(network_G, prediction_date, prediction_hour):
    plt.clf()

    print("drawing")

    #img = plt.imread(base_file_location(r'data\datascience2.png'))
    #plt.imshow(img, extent=[5.783061373, 5.808963910, 53.196978176, 53.207452884])


    plt.title("Leeuwarden occupancy on date: {0} hour: {1}".format(prediction_date.strftime("%Y-%m-%d"),
                                                                                 prediction_hour))

    nx.draw_networkx_nodes(network_G, nx.get_node_attributes(network_G, 'coordinates'), node_shape='.',
                           node_size=list(nx.get_node_attributes(network_G, 'width').values()),
                           with_labels=False, node_color=list(nx.get_node_attributes(network_G, 'color').values()))

    nx.draw_networkx_labels(network_G, pos=nx.get_node_attributes(network_G, 'coordinates'),
                            labels=nx.get_node_attributes(network_G, 'location'), font_size=9, font_color='black')

    frame = plt.gca()
    frame.axes.get_xaxis().set_visible(False)
    frame.axes.get_yaxis().set_visible(False)


# for testing
#save_one_fig(df_predictions, df_garage_locations, prediction_date, 10)

def update_drawing(n_frame, max_frames, df_predictions, df_garage_locations, prediction_date):

    prediction_hour = int((24 * n_frame) / max_frames)

    parking_graph = create_graph(df_predictions, df_garage_locations, prediction_hour)

    draw_network(parking_graph, prediction_date, prediction_hour)



# use to save one image
def save_one_fig(df_predictions, df_garage_locations, prediction_date, prediction_hour):

    plt.clf()
    plt.figure(figsize=(15, 15))

    update_drawing(prediction_hour, 24, df_predictions, df_garage_locations, prediction_date)
    plt.savefig(base_file_location(r"data\parking_lwd.png"))


# try to predict
def generate_for_date(prediction_date, raining):
    ds_garage_visits = create_dataset(prediction_date, raining)

    X = prepare_dataset_mem(ds_garage_visits)

    predictions = dict()

    for garage_id in parking_ids:
        predictions[garage_id] = classifiers[garage_id].predict(X).tolist()

    df_predictions = pd.DataFrame.from_dict(predictions, orient='index')

    return df_predictions


is_raining = 0.0
prediction_date = datetime.date(2018, 7, 7)

df_garage_locations = pd.read_csv(base_file_location(r'parkeerdata\leeuwarden_garage_parking_garage_gps.csv'), sep=';', decimal=',')

df_predictions = generate_for_date(prediction_date, is_raining)

fig, ax = plt.subplots(figsize=(15, 10))

# We need to have ffmpeg installed
plt.rcParams['animation.ffmpeg_path'] = ffmpeg_location()

AnimationWriter = matplotlib.animation.writers['ffmpeg']
writer = AnimationWriter(fps=15, metadata=dict(artist='pca 2018'), bitrate=1800)

# show 1 day with 400 frames
max_frames = 400

network_ani = matplotlib.animation.FuncAnimation(fig, update_drawing, frames=max_frames, interval=150, repeat=False,
                                                 fargs=(max_frames, df_predictions, df_garage_locations, prediction_date))

print("saving")

network_ani.save(base_file_location(r'data\im_all_visit_garage.mp4'), writer=writer)

print("ready")
