#!/usr/bin/env python
# coding: utf-8

# # *get_stock_data*
# 
# Utility functions to download and retrieve stock data and then quickly retrieve it from the created database
# 
# 

# In[81]:


# Packages

# Package Imports
import time
import os
import pandas as pd
import numpy as np
import pandas_datareader as pddr # Returns historical stock information: pip install pandas-datareader
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mpl_finance import candlestick_ohlc # Extends matplot for financial plotting: pip install mpl-finance 
from datetime import datetime
from sklearn import preprocessing # used for normalizing data




ROOT = '/Users/j/Desktop/research/'


# In[86]:


def return_differences(graph, axis=0):
    # returns a list of the differences between each point in the graph
    l = []
    g = sorted(graph)
    for i in range(len(g)-1):
        l.append(g[i+1][axis] - g[i][axis])
    
    return l
        


# In[87]:


def log_changes(y_values, start_price=-1):
    """"Returns the log changes for a list of y values.

    Args:
        y_values (List): The list of ordered y values from the fractal graph.
        start_price (int): Useful if stock starts at certain price.

    Returns:
        DataDrame: Returns a dataframe with the log returns.
    """
    if start_price == -1:
        start_price = abs(min(y_values)) + 1
    
    fixed = [x+start_price for x in y_values]
    df = pd.DataFrame(fixed, columns=['price'])
    df['pct_change'] = df.price.pct_change()
    df['log_ret'] = np.log(df.price) - np.log(df.price.shift(1))
    return df['log_ret']


# In[88]:


def plot_data_list(data, column='Normalized Close', save=False):
    fig, ax = plt.subplots() # Needs to go before everything else
    tickers = []
    #values = []
    for key in data.keys():
        tickers.append(key)
        #values.append(data[key][column])
        stock = data[key]
        ax.plot(stock['Date'], list(stock[column]))
    
    
    plt.legend(tickers,loc='best')
    plt.xlabel('Date')
    plt.ylabel(column)
    plt.title(tickers[0] + ', ' + ', '.join(tickers[1:])+ ' ' + column)
    
    # round to nearest years.
    #datemin = np.datetime64(data['date'][0], 'Y')
    #datemax = np.datetime64(data['date'][-1], 'Y') + np.timedelta64(1, 'Y')
    #ax.set_xlim(datemin, datemax)

    # format the coords message box
    #ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')

    
    plt.grid(color='k', linestyle='-', linewidth=0.1)
    plt.tick_params(axis='x', which='major', labelsize=10)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    plt.xticks(rotation=45)
    plt.gcf().set_size_inches(30,4)
    #matplotlib.rcParams['figure.dpi'] = 200
    
    
    


# In[89]:


def add_normalized_close(df):
    # Create x, where x the 'scores' column's values as floats
    x = df[['Adj Close']].values.astype(float)

    # Create a minimum and maximum processor object
    min_max_scaler = preprocessing.MinMaxScaler(feature_range=(0, 1))

    # Create an object to transform the data to fit minmax processor
    x_scaled = min_max_scaler.fit_transform(x)

    # Run the normalizer on the dataframe
    df['Normalized Close'] = x_scaled
    
    return df

def get_existing_tickers():
    lst = []
    basepath = ROOT + 'Daily'
    for entry in os.listdir(basepath):
        if os.path.isfile(os.path.join(basepath, entry)):
            lst.append(entry)
            
    return lst
    
                 
            
def resource_data_list(lst, start='2010-1-1', end='2020-1-1',overwrite=False):
    data = {}
    
    existing_tickers = get_existing_tickers()
    
    for ticker in lst:
        try:
            if ticker + '.csv' in existing_tickers and not(overwrite):
                data[ticker] = pd.read_csv(ROOT + 'Daily/' + ticker + '.csv')

            else:
                stock = pddr.DataReader(ticker, 
                               start=start, 
                               end = end,
                               data_source='yahoo')

                stock = add_normalized_close(stock)
                data[ticker] = stock

                stock.to_csv(ROOT + 'Daily/' + ticker + '.csv' )
        except Exception as e:
            print("Error: ", ticker, e)
            
            
        
    return data
    

