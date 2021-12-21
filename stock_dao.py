# Package Imports
import time
import os
import logging
import pandas as pd
import numpy as np
import pandas_datareader as pddr # Returns historical stock information: pip install pandas-datareader
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from sklearn import preprocessing # used for normalizing data
from sqlalchemy import create_engine, MetaData,table, column, insert

# refactor to hide user and password
ENGINE = create_engine(
    "mysql://admin:$johnnymysql99@johnnymysql.c4hdzvm7jbvn.us-east-2.rds.amazonaws.com/finalproject", 
    encoding='latin1'
)

logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
# Utility functions to download and retrieve stock data and then quickly retrieve it from the created database

def return_differences(graph, axis=0):
    # returns a list of the differences between each point in the graph
    l = []
    g = sorted(graph)
    for i in range(len(g)-1):
        l.append(g[i+1][axis] - g[i][axis])

    return l
        

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

def get_existing_tickers(conn):
    cursor = conn.cursor()
    cursor.execute(f'SELECT stock_id FROM stock_metadata;')
    desc = cursor.description
    column_names = [col[0] for col in desc]
    data = [r[0] for r in cursor.fetchall()]
    cursor.close()
            
    return data
                 
def add_stock_to_db(ticker, start, end, engine=ENGINE):
    data = {}
    stock = pddr.DataReader(ticker, start=start, end = end, data_source='yahoo')

    stock = add_normalized_close(stock)
    data[ticker] = stock
    engine.execute(table('stock_metadata', column('stock_id'), column('last_updated')).insert().values({'stock_id': ticker, 'last_updated': str(datetime.now())}))
    stock.to_sql(ticker, engine, if_exists='fail', index=True, chunksize=None) #index_label=None, 
    
    conn = engine.raw_connection()
    cursor = conn.cursor()
    cursor.execute(f'ALTER TABLE {ticker} ADD PRIMARY KEY (`Date`);')
    cursor.close()
    conn.close()
    return stock

def get_or_write_stocks(lst, engine=ENGINE, start='2019-1-1', end='2021-12-1'):
    conn = engine.raw_connection()
    data = {}
    existing_tickers = get_existing_tickers(conn)
    
    for ticker in lst:
        ticker = ticker.upper()
        try:
            if ticker  in existing_tickers:
                data[ticker] = pd.read_sql(f'SELECT * FROM {ticker};', conn)
            else:
                data[ticker] = add_stock_to_db(ticker, start, end, engine)

        except Exception as e:
            print("Error: ", ticker, e)
    conn.close()
        
    return data


def execute_stored_procedure(procedure, args_list, engine=ENGINE):
    conn = engine.raw_connection()
    cursor = conn.cursor()
    cursor.callproc(procedure, args_list)
    try:
        desc = cursor.description
        column_names = [col[0] for col in desc]
        data = [r[0] for r in cursor.fetchall()]
    except:
        data = None
    cursor.close()
    conn.commit()
    conn.close()
    
    return data
    
    

