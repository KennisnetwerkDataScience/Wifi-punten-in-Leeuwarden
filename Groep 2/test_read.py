# small test

import pandas as pd


# only read in first 150000 rows
df_locatus = pd.read_csv(r'locatusdata_bewerkt.csv', sep=';', nrows=250000)

# position of each wifi sensor
sensor_positions = pd.read_csv(r'gps_locaties_sensors.csv', sep=';', decimal=',')

# join the sensor positions to the wifi data, so the locations are available in the dataframe
df_joined = df_locatus.join(sensor_positions.set_index('sensor_id'), on='VirtualSensorCode')

# count number of passages for each wifi point (not complete at the moment)
print(df_joined.groupby(['VirtualSensorCode']).count().id)
