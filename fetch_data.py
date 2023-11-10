import requests
import os
import yfinance as yf
import numpy as np
import pandas as pd
import json
from bs4 import BeautifulSoup
import requests

alphaVantageApiKey = "6XWJ1YRTZPXP7EAQ"


# get historical data for a ticker
def getTickerData(ticker, interval):
    filename = f"datas/{ticker}_{interval}.csv"

    # check if data is already saved locally
    if os.path.exists(filename):
        data = pd.read_csv(filename)
        return data

    # else, download it
    data = yf.download(ticker, period="max", interval=interval, threads=False)[
        ["Open", "High", "Low", "Close"]]
    # add dividends
    stock = yf.Ticker(ticker)
    dividends = np.array(stock.history(
        period="max", interval=interval)["Dividends"])
    data = data.copy()

    data.loc[:, ("Dividends")] = dividends

    data = data[data['Open'] != 0]  # remove 0 values of Open column

    # then save it for the next load
    data.to_csv(filename)
    data = pd.read_csv(filename)

    return data


def getDatas(tickers, interval):
    datas = dict()

    print("Importing datas...")

    for i in range(len(tickers)):
        datas.update({tickers[i]: getTickerData(tickers[i], interval)})

    datas.update({"interval": interval})

    return datas

# return the mean annualized returns for a given stock close prices


def getMeanAnnualizedReturns(close_prices, data_interval):
    # Get number of interval within a year
    if (data_interval == "1mo"):
        intervalNb = 12
    elif (data_interval == "1wk"):
        intervalNb = 52
    else:
        raise Exception("Wrong interval")

    # Use the formula : POW(last_close_price / first_close_price, 1 / interval_number_in_a_year)
    dataLength = len(close_prices)
    return (close_prices[dataLength - 1] / close_prices[0]) ** (1/(dataLength/intervalNb))


apiBase = 'https://query2.finance.yahoo.com'
headers = {
    "User-Agent":
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64)"
}


def getCredentials(cookieUrl='https://fc.yahoo.com', crumbUrl=apiBase+'/v1/test/getcrumb'):
    cookie = requests.get(cookieUrl).cookies
    crumb = requests.get(url=crumbUrl, cookies=cookie, headers=headers).text
    return {'cookie': cookie, 'crumb': crumb}


credentials = getCredentials()


def getTickerInfos(tickers):
    infos = {}
    url = apiBase + '/v7/finance/quote'
    params = {'symbols': ','.join(tickers), 'crumb': credentials['crumb']}

    response = requests.get(
        url, params=params, cookies=credentials['cookie'], headers=headers)
    quotes = response.json()['quoteResponse']['result']

    for i in range(len(tickers)):
        infos[tickers[i]] = quotes[i]

    return infos


# make a call to alpha vantage api
def fetchAlphaVantageAPI(ticker, function):
    baseurl = 'https://www.alphavantage.co/query?function='
    response = requests.get(baseurl + function + '&symbol=' + ticker + '&apikey=' + alphaVantageApiKey)
    soup = BeautifulSoup(response.content, 'html.parser')
    return json.loads(str(soup))


# return the average yearly net income growth
def getNetIncomeYGrowth(ticker):    
    data = fetchAlphaVantageAPI(ticker, 'INCOME_STATEMENT')

    if ("annualReports" not in data): return -0.05 # return safety -5% growth if we can't access datas

    netIncomes = [int(n["netIncome"]) for n in data["annualReports"]]

    avg = [(netIncomes[i-1] - netIncomes[i]) / netIncomes[i] for i in range(1, len(netIncomes))]

    if (len(avg) == 0): return -0.05 # return safety -5% growth if we can't access datas

    return round((sum(avg) / len(avg)), 4)