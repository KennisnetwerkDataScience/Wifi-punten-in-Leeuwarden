# create_network_from_routes.py
#
# Description: creates an animation using the file created in network_lwd_store_routes.py
# Author: pca
# Date: 2018-06-26
# Version: 1.0
#
# Prerequisite: ffmpeg.exe is available on machine


import networkx as nx
import pandas as pd
from leeuwarden_kennis.config_data import base_file_location
from leeuwarden_kennis.config_data import ffmpeg_location
import collections
import matplotlib.pyplot as plt
import matplotlib.animation


# this is the file created in network_lwd_store_routes
df_visits = pd.read_csv(base_file_location(r'data\network_walks.csv'), sep=';')

# add date only column
df_visits['visit_date'] = pd.to_datetime(pd.to_datetime(df_visits['time_from'], format='%Y-%m-%d').dt.date)

all_dates = sorted(df_visits['visit_date'].unique())


# get the sensor locations.
# this file can be found here: https://github.com/KennisnetwerkDataScience/Wifi-punten-in-Leeuwarden/tree/master/data
df_sensor_locations = pd.read_csv(base_file_location(r'data\opstelpunten.csv'), sep=';', decimal=',')


def calc_width(max_width, total_routes, weight):
    return max_width * (weight / total_routes)


def create_graph(df_routes, df_sensor_locations):
    network_G = nx.Graph()

    network_sensors = collections.defaultdict(int)



    for sensor in df_sensor_locations.iterrows():
        network_G.add_node(sensor[1]['ID'])

    #total_routes = len(df_routes)
    total_routes = 0

    # add weights
    for edge in df_routes.iterrows():
        from_sensor = int(edge[1]['sensor_from'])
        to_sensor = int(edge[1]['sensor_to'])
        value = edge[1]['visit_date_count']
        total_routes += value

        network_sensors[(from_sensor, to_sensor)] += value

    for key, value in network_sensors.items():
        network_G.add_edge(key[0], key[1], weight=value)

    # add coordinates to the nodes
    for sensor in network_G.nodes():
        current_sensor = df_sensor_locations[df_sensor_locations['ID'] == sensor]
        x, y = current_sensor['lon'].iloc[0], current_sensor['lat'].iloc[0]
        network_G.node[sensor]['coordinates'] = (x, y)
        network_G.node[sensor]['location'] = current_sensor['Locatie'].to_string()

    # add width to the edges.
    for route in network_G.edges():
        sensor_from = route[0]
        sensor_to = route[1]
        network_G[route[0]][route[1]]['width'] = \
            calc_width(100.0, total_routes, network_sensors[(sensor_from, sensor_to)])

    return network_G, total_routes


def draw_network(network_G, current_date, total_routes):
    plt.clf()

    current_date_p = pd.to_datetime(current_date)

    plt.title("Leeuwarden visits on date: {0} total number of trips: {1}".format(current_date_p.strftime("%Y-%m-%d"),
                                                                                 total_routes))

    nx.draw_networkx_nodes(network_G, nx.get_node_attributes(network_G, 'coordinates'), node_shape='.', node_size=160,
                           with_labels=False)

    nx.draw_networkx_labels(network_G, pos=nx.get_node_attributes(network_G, 'coordinates'),
                            labels=nx.get_node_attributes(network_G, 'location'), font_size=9, font_color='indianred')

    nx.draw_networkx_edges(network_G, nx.get_node_attributes(network_G, 'coordinates'),
                           width=[width for width in nx.get_edge_attributes(network_G, 'width').values()], alpha=0.8,
                           edge_color='skyblue'
                           )

    frame = plt.gca()
    frame.axes.get_xaxis().set_visible(False)
    frame.axes.get_yaxis().set_visible(False)


def update_drawing(num):

    # skip first n days
    num += 400

    current_routes = df_visits[df_visits['visit_date'] == all_dates[num]].groupby(['sensor_from', 'sensor_to']).count()
    current_routes = current_routes.add_suffix('_count').reset_index()

    network_graph, total_routes = create_graph(current_routes, df_sensor_locations)

    draw_network(network_graph, all_dates[num], total_routes)


def main():
    # Create the animation for several days.

    fig, ax = plt.subplots(figsize=(20, 15))

    # We need to have ffmpeg installed
    plt.rcParams['animation.ffmpeg_path'] = ffmpeg_location()

    AnimationWriter = matplotlib.animation.writers['ffmpeg']
    writer = AnimationWriter(fps=15, metadata=dict(artist='pca 2018'), bitrate=1800)

    network_ani = matplotlib.animation.FuncAnimation(fig, update_drawing, frames=120, interval=500, repeat=False)

    print("saving")

    network_ani.save(base_file_location(r'data\im.mp4'), writer=writer)


# use to save one image
def save_one_fig(days):

    plt.clf()
    plt.figure(figsize=(20, 15))
    update_drawing(days)
    plt.savefig(base_file_location(r"data\visit_lwd.png"))

if __name__ == '__main__':
    main()