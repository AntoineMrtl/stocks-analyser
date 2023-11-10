from fetch_data import *
from utils import *
from display import *
from fetch_data import *
from helper import *


# MAIN
tickers = ["MO", "BF-B", "MSFT", "AOS", "ADC", "MAIN", "STAG", "EPR", "SIS.TO", "STAG", "DOV", "ABT", "KO", "ABBV", "ADM", "LEG", "VFC", "AFL", "BEN", "FRT", "APD", "TROW", "TGT", "ED", "CLX", "BDX", "AAPL", "IBM",
           "WBA", "O", "CB", "CAH", "CHD", "MMM", "AMCR", "PNR", "SWK", "CHRW", "CTAS", "ALB", "CAT", "SHW", "NDSN", "ADP", "BRO", "ESS", "MDT", "CVX", "NEE", "XOM", "PEP", "SYY", "JNJ", "HRL", "CINF", "ATO", "ECL", 
           "EMR", "EXPD", "GD", "GPC", "ITW", "SJM", "KMB", "LIN", "LOW", "MKC", "MCD", "NUE", "PPG", "PG", "ROP", "SPGI", "GWW", "WMT", "WST"]
datas = getDatas(tickers, "1wk")

for ticker in tickers:
    addAdjustedClosePrice(datas[ticker])
    addAdjustedOpenPrice(datas[ticker])

tickersInfos = getTickerInfos(tickers)

sortedTickers = sortTickers(datas, tickersInfos, tickers)
print(sortedTickers)

createPortfolio(sortedTickers, datas, tickersInfos)