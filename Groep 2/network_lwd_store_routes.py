import networkx as nx
import pandas as pd
from leeuwarden_kennis.config_data import base_file_location
import datetime
import queue as Q


# example line: 6;"2054";"2017-08-17 13:27:00";"646.0";994771
def parse_line(line):
    splitted_line = line.rstrip().split(";")

    visitor_id = splitted_line[4]
    sensor_code = splitted_line[1].strip("\"")
    visit_timestamp = datetime.datetime.strptime(splitted_line[2].strip('""'), '%Y-%m-%d %H:%M:%S')

    return visitor_id, sensor_code, visit_timestamp


def process_file():
    visit_info = Q.PriorityQueue()

    cnt = 0
    with open(base_file_location('locatus\locatusdata_bewerkt_filtered.csv'), 'r') as infile:
        # skip header
        next(infile)
        for line in infile:

            visitor, sensor, visit_timestamp = parse_line(line)

            visit_info.put((visitor, visit_timestamp, sensor))
            cnt += 1

            if cnt % 500000 == 0:
                print("cnt: {0}".format(cnt))
    return visit_info


# When time difference is more than n_hrs than return False, else True
def in_time_hrs(time_a, time_b, n_hrs):
    if time_a == datetime.datetime.min:
        return False
    if time_b == datetime.datetime.min:
        return False

    time_delta = abs(time_b - time_a)

    return time_delta.total_seconds() <= (n_hrs * 60 * 60)


def make_network(visits_pq):
    network_walks = []

    last_person = -1
    last_location = -1
    last_visit_time = datetime.datetime.now()

    while not visits_pq.empty():
        visit_record = visits_pq.get()
        current_person = visit_record[0]
        current_location = visit_record[2]
        current_visit_time = visit_record[1]

        # change of location
        if current_location != last_location and current_person == last_person and in_time_hrs(last_visit_time, current_visit_time, 12):
            network_walks.append((current_person, last_location, current_location, last_visit_time, current_visit_time))

        last_person = current_person
        last_location = current_location
        last_visit_time = current_visit_time

    return network_walks


visits_pq = process_file()
network = make_network(visits_pq)

# make a pandas df from this
network_df = pd.DataFrame(network, columns=['visitor', 'sensor_from', 'sensor_to', 'time_from', 'time_to'])
network_df.to_csv(base_file_location(r'data\network_walks.csv'), index=None, sep=';')

