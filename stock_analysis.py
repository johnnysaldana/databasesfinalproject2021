import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from stock_dao import get_or_write_stocks
from functools import reduce
from statsmodels.tsa.stattools import coint, adfuller, grangercausalitytests

def plot_data_list(data, column='Normalized Close', filename='unnamed.png'):
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
    matplotlib.rcParams['figure.dpi'] = 200
    plt.savefig(filename)
    
def remove_unshared_dates(values):
    min_length =  len(values[0])
    for lst in values[1:]:
        if len(lst) < min_length:
            min_length = len(lst)
            
    for i in range(len(values)):
        values[i] = values[i][-1 * min_length:]
        
    return values

def correlate_stocks(data, column='Close'):
    values = []
    labels = []
    for key in data.keys():
        labels.append(key)
        values.append(list(data[key][column].dropna()))
    values = remove_unshared_dates(values)
    # Only gets rows starting at the most recent common date amongst stocks
        
    corr = np.corrcoef(values)
    
    return (corr, labels)

def cointegrate_stocks(data, column):
    labels = []
    for key in data.keys():
        labels.append(key)
        
    #values = remove_unshared_dates(values)
    
    pvalue_matrix = np.zeros(shape=(len(labels),len(labels)))
    score_matrix = np.zeros(shape=(len(labels),len(labels)))
    
    for i, x in enumerate(labels):
        for j, y in enumerate(labels):
            if x == y:
                score = None
                pvalue = 0
                
            else:
                lst = [data[x][column].dropna(), data[y][column].dropna()]
                lst = remove_unshared_dates(lst)
                
                score, pvalue, _ = coint(lst[0], lst[1])
            pvalue_matrix[i,j] = pvalue
            score_matrix[i,j] = score
    
    return (pvalue_matrix, score_matrix, labels)

def mask_corr_matrix(corr, del_same_corr=False):

    if del_same_corr:
        count = 0
        #corr = np.delete(corr,1,0)
        corr = np.delete(corr,1,1)
        while count < len(corr):
            corr[count][count + 1:] = [None]*(len(corr) - (count + 1))
            count = count + 1
        
    else:
        count = 0
        while count < len(corr):
            corr[count][count + 1:] = [None]*(len(corr) - (count + 1))
            count = count + 1
    
    
    return corr

def corr_matrix_heatmap(corr, labels, path):
    sns.heatmap(mask_corr_matrix(corr, False), center=-1,cmap="YlGnBu",
            square=True, annot=True, linewidths=2,xticklabels=labels,yticklabels=labels, cbar_kws={"shrink": .7})
    size = round(len(labels) / 1.3)
    sns.set(font_scale=0.7)
    plt.gcf().set_size_inches(size,size)
    plt.savefig(path)
    
    
def coint_matrix_heatmap(pmatrix, smatrix, labels, column, path):
    fig, (ax1, ax2) = plt.subplots(1,2)
    pronounced = sns.cubehelix_palette(light=1, as_cmap=True)
    df_pmatrix = pd.DataFrame(pmatrix)
    
    # make it discrete
    df_q = pd.DataFrame()
    for col in df_pmatrix:
        df_q[col] = pd.to_numeric( pd.qcut(df_pmatrix[col], len(labels), labels=list(range(len(labels)))) )


    sns.heatmap(pmatrix, ax=ax1, cmap=plt.cm.Blues_r,
            square=True, annot=True, linewidths=3,xticklabels=labels,yticklabels=labels, 
                cbar_kws={"shrink": .3})
    
    sns.heatmap(smatrix, ax=ax2, center=-1,
            square=True, annot=True, linewidths=3,xticklabels=labels,yticklabels=labels, 
                cbar_kws={"shrink": .3})
    size = round(len(labels) * 2)
    sns.set(font_scale=0.8)
    
    fig.suptitle(labels[0] + ', ' + ', '.join(labels[1:])+ ' Cointegration Matrices ' + column)
    ax1.title.set_text('P-Value Matrix')
    ax2.title.set_text('Score Matrix')
    fig.tight_layout()
    fig.subplots_adjust(top=1.4)
    
    plt.gcf().set_size_inches(size,size)
    plt.savefig(path)
    
# Trade using a simple strategy
def z_score_series(series):
    return (series - series.mean()) / np.std(series)

def z_score_norm_list(series, lower, upper):
    z_norm = [lower + (upper - lower) * x for x in series]
    
    return z_norm

def trade(S1, S2, window1, window2, path):
    
    # If window length is 0, algorithm doesn't make sense, so exit
    if (window1 == 0) or (window2 == 0):
        return 0
    
    # Compute rolling mean and rolling standard deviation
    ratios = S1/S2
    
    ma1 = ratios.rolling(window=window1,
                               center=False).mean()
    ma2 = ratios.rolling(window=window2,
                               center=False).mean()
    std = ratios.rolling(window=window2,
                        center=False).std()
    
    zscore = (ma1 - ma2)/std
    
    # Simulate trading
    # Start with no money and no positions
    money = 1000
    countS1 = 0
    countS2 = 0
    for i in range(len(ratios)):
        # Sell short if the z-score is > 1
        if zscore[i] < -1:
            money += S1[i] - S2[i] * ratios[i]
            countS1 -= 1
            countS2 += ratios[i]
            
            #print('Selling Ratio %s %s %s %s'%(money, ratios[i], countS1,countS2))
        # Buy long if the z-score is < -1
        elif zscore[i] > 1:
            money -= S1[i] - S2[i] * ratios[i]
            countS1 += 1
            countS2 -= ratios[i]
            #print('Buying Ratio %s %s %s %s'%(money,ratios[i], countS1,countS2))
        # Clear positions if the z-score between -.5 and .5
        elif abs(zscore[i]) < 0.75:
            money += S1[i] * countS1 + S2[i] * countS2
            countS1 = 0
            countS2 = 0
            #print('Exit pos %s %s %s %s'%(money,ratios[i], countS1,countS2))
    
    
    r = S1 / S2
    z = z_score_series(r)
    #z_norm = pd.Series(z_score_norm_list(z, min(z), max(z)), z.index)
    plt.figure(figsize=(15,7))
    r.plot()
    buy = r.copy()
    sell = r.copy()
    buy[z>-.5] = 0
    sell[z<.5] = 0
    buy[60:].plot(color='g', linestyle='None', marker='^')
    sell[60:].plot(color='r', linestyle='None', marker='^')
    x1,x2,y1,y2 = plt.axis()
    plt.axis((x1,x2,r.min(),r.max()))
    plt.legend(['Ratio', 'Buy Signal', 'Sell Signal'])
    plt.savefig(path)
            
    return money, z

    