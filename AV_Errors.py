import requests
import json
# import userInfo


def request_err(url, data, proxy):

    try:
        if proxy == "default":
            response = requests.get(url, data, timeout=8)
            return response.json()

        else:
            response = requests.get(url, data, proxies={"http": proxy, "https": proxy}, timeout=8)
            return response.json()

    except requests.exceptions.ConnectionError as err:
        print("Connection Error: AlphaVant.py \n " +
              "Error Code: ", err)

    except requests.exceptions.HTTPError as err:
        print("HTTP Error: AlphaVant.py \n " +
              "Error: ", err)
    except requests.exceptions.Timeout as err:
        print("Timeout Error: AlphaVant.py \n " +
              "Error: ", err)


def request_err_production(url, data, proxy):

    try:
        if proxy == "default":
            response = requests.get(url, data, timeout=8)
            return response.json()

        else:
            response = requests.get(url, data, proxies={"http": proxy, "https": proxy}, timeout=8)
            return response.json()

    except requests.exceptions.ConnectionError as err:
        print("Connection Error: AlphaVant.py")

    except requests.exceptions.HTTPError as err:
        print("HTTP Error: AlphaVant.py")

    except requests.exceptions.Timeout as err:
        print("Timeout Error: AlphaVant.py")


def request_proxy_err(url):

    try:
        response = requests.get(url, timeout=8)
        return response

    except requests.exceptions.ConnectionError as err:
        print("Connection Error: proxy_list \n " +
              "Error Code: ", err)

    except requests.exceptions.HTTPError as err:
        print("HTTP Error: proxy_list \n " +
              "Error: ", err)
    except requests.exceptions.Timeout as err:
        print("Timeout Error: proxy_list \n " +
              "Error: ", err)
    except:
        print("Unkown Error")


def df_key_err(data, symbol):
    try:
        if type(data) == None:
            raise Exception("Nothing returned... check proxy")

        elif 'Error Message' in data.keys():
            raise Exception("Invalid API Call: symbol '" + symbol + "' not found")

        elif 'Note' in data.keys():
            raise Exception("API Limit Exceeded: symbol '" + symbol + "'")
    except:
        raise Exception("Unkown Error")


def df_key_err_production(data, symbol):

    try:
        if type(data) == None:
            print("Nothing returned... check proxy")

        elif 'Error Message' in data.keys():
            print("Invalid API Call: symbol '" + symbol + "' not found")

        elif 'Note' in data.keys():
            print("API Limit Exceeded: symbol '" + symbol + "'")
    except:
        print("Unknown Error: df_key_err")
