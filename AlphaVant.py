# Pull stock data using Alpha Vantage

import requests
import json
from datetime import datetime
import pandas as pd
import userInfo
import AV_Errors

API_URL = "https://www.alphavantage.co/query"


def time_series(function, adj):
    time_series_string = ""

    if adj and function == "DAILY":
        time_series_string = "Time Series (Daily)"

    elif adj:
        series = " Adjusted Time Series"
        time_series_string = function[0] + function[1:].lower() + series

    elif function.upper() == "DAILY":
        time_series_string = "Time Series (Daily)"

    else:
        time_series_string = function[0] + function[1:].lower() + " Time Series"

    return time_series_string


def format_df(function, df, symbol, adj):
    if function == "DAILY" and adj:
        col_extra1 = ["adjusted close"]
        col_extra2 = ["dividend amount", "split coefficient"]
    elif adj:
        col_extra1 = ["adjusted close"]
        col_extra2 = ["dividend amount"]
    else:
        col_extra1 = []
        col_extra2 = []

    df.columns = ["open", "high", "low", "close"] + col_extra1 + ["volume"] + col_extra2
    df["meta"] = ""
    df.insert(0, "date", df.index)

    df = df.reindex(index=df.index[::-1])
    date = str(datetime.now())
    df["meta"][0] = [['src', 'Alpha Vantage'],
                     ['date', date],
                     ['symb', symbol],
                     ['function', function.lower() + ("adj" if adj else "")],
                     ['resolution', 'n/a'],
                     ['start', str(df.tail(1)["date"]).split()[0]],
                     ['end', str(df.head(1)["date"]).split()[0]],
                     ['length', str(len(df))]]

    return df


def get_historical(function, symbol, ip="default"):
    if function not in ["MONTHLY", "DAILY", "WEEKLY"]:
        raise Exception("Invalid value: '" + function + "' \n"
                        " Acceptable values are: 'MONTHLY', 'WEEKLY', " +
                        "'DAILY'")

    data = {"function": "TIME_SERIES_" + function.upper(),
            "symbol": symbol,
            "datatype": "json",
            "outputsize": "full",
            "apikey": userInfo.key_gen()}

    data = AV_Errors.request_err_production(API_URL, data, ip)

    AV_Errors.df_key_err_production(data, symbol)

    df = pd.DataFrame.from_dict(data[time_series(function,
                                                 False)]).transpose()

    return format_df(function, df, symbol, False)


def get_historical_adjusted(function, symbol, ip="default"):
    if function not in ["MONTHLY", "DAILY", "WEEKLY"]:
        raise Exception("Invalid value: '" + function + "' \n"
                        " Acceptable values are: 'MONTHLY', 'WEEKLY', 'DAILY'")

    data = {"function": "TIME_SERIES_" + function.upper() + "_ADJUSTED",
            "symbol": symbol,
            "datatype": "json",
            "outputsize": "full",
            "apikey": userInfo.key_gen()}

    data = AV_Errors.request_err_production(API_URL, data, ip)

    AV_Errors.df_key_err_production(data, symbol)

    df = pd.DataFrame.from_dict(data[time_series(function,
                                                 True)]).transpose()

    return format_df(function, df, symbol, True)


def get_sector_perf():
    data = {"function": "SECTOR",
            "apikey": userInfo.key_gen()}

    data = AV_Errors.request_err_production(API_URL, data)

    key_lst = []
    val_lst = []

    for key in list(keys)[1:]:
        val_lst.append(data[key])
        key_lst.append(key.split(":")[1][1:])
    df = pd.DataFrame()
    df["sector period"] = key_lst

    real_est = []
    energy = []
    utilities = []
    financials = []
    staples = []
    health_care = []
    industrials = []
    materials = []
    IT = []
    consumer_discr = []
    x = []
    communic_serv = []

    for key in list(data.keys())[1:]:
        real_est.append(data[key]["Real Estate"] if "Real Estate" in data[key]
                        else "")
        energy.append(data[key]["Energy"])
        utilities.append(data[key]["Utilities"])
        financials.append(data[key]["Financials"])
        staples.append(data[key]["Consumer Staples"])
        health_care.append(data[key]["Health Care"])
        industrials.append(data[key]["Industrials"])
        materials.append(data[key]["Materials"])
        IT.append(data[key]["Information Technology"])
        consumer_discr.append(data[key]["Consumer Discretionary"])
        communic_serv.append(data[key]["Communication Services"])

    df["Real Estate"] = real_est
    df["Energy"] = energy
    df["Utilities"] = utilities
    df["Financials"] = financials
    df["Consumer Staples"] = staples
    df["Health Care"] = health_care
    df["Industrials"] = industrials
    df["Materials"] = materials
    df["Information Technology"] = IT
    df["Communication Services"] = consumer_discr
    df["Materials"] = communic_serv

    df = df.reindex(index=df.index[::-1])
    return df


'''
data = {"function": "TIME_SERIES_MONTHLY",
        "symbol": "MSFT",
        "datatype": "json",
        "outputsize": "full",
        "apikey": userInfo.key_gen()}

print("###################################################################")
response = requests.get(API_URL, data, proxies={
                        "http": "212.30.52.37:42939", "https": "212.30.52.37:42939"}, timeout=1)

print(response)
'''
