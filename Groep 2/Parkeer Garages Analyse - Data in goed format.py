# -*- coding: utf-8 -*-
"""
Created on Mon Jun 18 17:27:48 2018

@author: verho534
"""
#import libraries
import pandas as pd
import numpy as np
import folium #note: will not run in explorer

#load data
path='C:/Users/verho534/Documents/Jupyter/Parkeren Data/'
parking_transactions=pd.read_csv(path+'../Parkeren Data/parkeerdata/leeuwarden_garage_parking_transactions.csv',sep=";")
parking_locations=pd.read_csv(path+'../Parkeren Data/parkeerdata/leeuwarden_garage_parking_garage_gps.csv',sep=";",decimal=",")
weather = pd.read_csv(path+'knmi/knmi_uurgeg_270_2011-2020_leeuwarden.csv',sep=";")

#%% Get needed data from the KNMI dataset
weatherdata = weather[['YYYYMMDD','HH','R']]
mask = (weatherdata['YYYYMMDD'] >= 20160101) #we only want the data from 2016 onwards
weatherdata = weatherdata[mask]
weatherdata['date'] = pd.to_datetime(weatherdata['YYYYMMDD'], format = '%Y%m%d').dt.date

weatherdata.to_csv(path + "../data/weatherdata",sep=";")
#%% Plot the locations of the parking locations
folium_map = folium.Map(location=[np.mean(parking_locations.latitude[:]), np.mean(parking_locations.longitude[:])],
                        zoom_start = 15, control_scale = True)
for i in range(len(parking_locations)):
    folium.Marker([parking_locations.latitude[i], parking_locations.longitude[i]],
                  popup = parking_locations.garage_nm[i], icon=folium.Icon(icon='car', prefix='fa')).add_to(folium_map)
folium_map.save(path+"../data/plot_garages.html")

#%% Drop columns that we do not use
parking_transactions=parking_transactions.drop(['pay_parking_dt','entry_station_cid','pay_station_cid','exit_station_cid'],axis=1)
# Show the number of nans in the dataset
parking_transactions.isnull().sum()
# delete the rows with nans in the column in or out
parking_transactions=parking_transactions.dropna()
# Change the date column to date
parking_transactions['visit_datetime'] = pd.to_datetime(parking_transactions['start_parking_dt'], format='%d-%m-%Y %H:%M')

# Add a column with the weekday
#parking_transactions['weekday_name'] = parking_transactions['visit_datetime'].dt.weekday_name

parking_transactions['start_parking_dt'] = pd.to_datetime(parking_transactions['start_parking_dt'], format='%d-%m-%Y %H:%M')
parking_transactions['end_parking_dt'] = pd.to_datetime(parking_transactions['end_parking_dt'], format='%d-%m-%Y %H:%M')

parking_transactions['start_date'] = parking_transactions['start_parking_dt'].dt.date
parking_transactions['end_date'] = parking_transactions['end_parking_dt'].dt.date
parking_transactions['start_hour'] = parking_transactions['start_parking_dt'].dt.hour
parking_transactions['end_hour'] = parking_transactions['end_parking_dt'].dt.hour


#%% Make different datasets per garage
for garage_id in parking_locations.garage_id.unique():
    mask = parking_transactions['garage_id']==garage_id
    data= parking_transactions.loc[mask]
    name="../data/parking_events-garage"+str(garage_id)+".csv"
    print("Written to",name,"shape",data.shape)
    data.to_csv(name,sep=";",index=False)

#%% 
for garage_id in parking_locations.garage_id.unique():
    name = "../data/parking_events-garage" + str(garage_id) + ".csv"
    # Download the dataset per garage
    garage_transactions = pd.read_csv(path+name,sep=";")
    #Create new datasets per garage
    visitors_in_per_hour = garage_transactions.groupby(['start_date','start_hour'],as_index=False)['transaction_id'].count().rename(columns={'transaction_id':'count_in','start_date':'date','start_hour':'hour'})
    visitors_out_per_hour = garage_transactions.groupby(['end_date','end_hour'],as_index=False)['transaction_id'].count().rename(columns={'transaction_id':'count_out','end_date':'date','end_hour':'hour'})
    # Merge the two datasets
    visitors_per_hour = pd.merge(visitors_in_per_hour,visitors_out_per_hour, on=['date','hour'], how='outer')
    # Fill the nans that occur with 0s
    visitors_per_hour['count_in'] = visitors_per_hour['count_in'].fillna(0)
    visitors_per_hour['count_out'] = visitors_per_hour['count_out'].fillna(0)
    # Add column that is the difference of in and out per hour
    visitors_per_hour['delta'] = visitors_per_hour['count_in'] - visitors_per_hour['count_out']
    # Sort the data on tijd
    visitors_per_hour = visitors_per_hour.sort_values(['date', 'hour']).reset_index()
    # Make a column which is the cumulative sum of delta, to see how many cars are in the garage at the moment
    visitors_per_hour['cum_sum'] = visitors_per_hour.delta.cumsum()
    
    #add columns to explain the trend
    visitors_per_hour['datetime'] = pd.to_datetime(visitors_per_hour['date'])
    visitors_per_hour['week'] = visitors_per_hour['datetime'].dt.week
    visitors_per_hour['month'] = visitors_per_hour['datetime'].dt.month
    visitors_per_hour['day'] = visitors_per_hour['datetime'].dt.day
    visitors_per_hour['dayofyear'] = visitors_per_hour['datetime'].dt.dayofyear
    visitors_per_hour['weekday'] = visitors_per_hour['datetime'].dt.weekday
    visitors_per_hour['year'] = visitors_per_hour['datetime'].dt.year
    # add the column of weather data, does not work yet...
    visitors_per_hour[["date"]] = visitors_per_hour[["date"]].astype(str) 
    visitors_per_hour.merge(weatherdata, how = 'left', left_on = ['date', 'hour'], right_on = ['date', 'HH'])
    
    visitors_per_hour = visitors_per_hour.drop('datetime',axis=1)
    name = "../data/out-visitors_per_hour-garage" + str(garage_id) + ".csv"
    #save the datasets
    visitors_per_hour.to_csv(path+name,sep=";",index=False)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    