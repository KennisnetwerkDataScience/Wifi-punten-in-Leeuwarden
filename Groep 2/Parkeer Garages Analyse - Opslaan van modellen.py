# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 16:46:15 2018

@author: verho534
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import folium #note: will not run in explorer

from sklearn import metrics 
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_curve

#load data
path='C:/Users/verho534/Documents/Jupyter/Parkeren Data/'
parking_locations=pd.read_csv(path+'../Parkeren Data/parkeerdata/leeuwarden_garage_parking_garage_gps.csv',sep=";",decimal=",")


for garage_id in parking_locations.garage_id.unique():
    name = "../data/out-visitors_per_hour-garage" + str(garage_id) + ".csv"
    # Load data
    visitors_per_hour = pd.read_csv(path+name,sep=";")
    
    # Save progress to a file
    file = open(path + "../data/progress_file_garage_" + str(garage_id) + ".txt","w")
    
    matched_row=parking_locations.loc[parking_locations.garage_id == garage_id]
    capacity=int(matched_row.capacity_value)
    visitors_per_hour['perc'] = 100 * visitors_per_hour['cum_sum'] / capacity
    # Make a histogram and save it
    #fig1.clf()
    fig1, fig2 = plt.subplots()
    fig1 = plt.hist(visitors_per_hour['perc'], bins = 10)
    plt.title("Histogram van drukte voor garage " + str(garage_id))
    plt.xlabel("Percentage vol")
    plt.ylabel("Aantal uren")
    plt.savefig(path + "../data/Busy_hours_garage_" + str(garage_id) + ".png")
    #fig1.clf()
    plt.show()
    
    target_column = visitors_per_hour['perc']
    #m = target_column.mean()
    #for three bins, the sd can be used
    #s = target_column.std()
    # Bins can be changed to arbitrary values
    # bins = [-1, m - s * 0.5, m + s * 0.5, 1000]
    bins = [-1, 30, 50, 1000]
    file.write("The bins are " + str(bins) + "\n")
    bin_names = ['empty', 'resty', 'crowdy']
    #the names are fine, but our scikit classifier uses numbers
    bin_labels = [0,1,2]
    visitors_per_hour['occupation'] = pd.cut(target_column, bins, labels=bin_labels)
    #fig2.clf()
    fig2 = plt.hist(visitors_per_hour['occupation'], bins = 3)
    plt.title("Histogram van drukte verdeeld over 3 categorieen voor garage " + str(garage_id))
    plt.xlabel("Categorieen")
    plt.ylabel("Aantal uren")
    plt.xticks([1/3, 1, 5/3], bin_names)
    plt.savefig(path + "../data/Busy_categories_garage_" + str(garage_id) + ".png")
    # Vraag tussendoor: Is de goodness of fit afhankelijk van de binsizes?
    
    X = visitors_per_hour.copy()
    #drop the target_variable
    X= X.drop(['occupation','cum_sum'],axis=1)
    #drop id from feature table (overfitting)
    X= X.drop(['index'],axis=1)
    #drop visitors (explainable variable with respect to the binned-target variable)
    X= X.drop('perc',axis=1)
    #drop datetime (overfitting)
    X= X.drop(['date'], axis=1)
    #drop direct influencers
    X= X.drop(['count_in','count_out','delta','month'], axis=1)
    
    #Split dataset into two datasets, one to fit, and one to test
    y = visitors_per_hour['occupation']  
    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.6, test_size=0.4, shuffle = True, random_state=42)
    clf = RandomForestClassifier()
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    results = {'datasize':str(X.shape),
             'mae': metrics.mean_absolute_error(y_test, y_pred),
             'rmse': metrics.mean_squared_error(y_test, y_pred),
             'accuracy_score': metrics.accuracy_score(y_test, y_pred)} 
    file.write(str(results) + "\n")
    file.close()
    
    # Save the classifier
    import pickle
    filename = path + "../data/classifier_garage_" + str(garage_id) + ".sav"
    #with open(filename, 'wb') as f:
    #    cPickle.dump(clf, f)
    pickle.dump(clf, open(filename, 'wb'))
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    