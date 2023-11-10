from fetch_data import *
from utils import *
from display import *
from fetch_data import *

VERBOSE = False

returnScoring = define_interpolator(50, 70, 100, 0, 0, 0.05)
dividendGrowthScoring = define_interpolator(0.9, 0.95, 1, 0, 0, 0.05)
marketCapScoring = define_interpolator(3, 10, 15, 0, 0, 0)
dividendYieldScoring = define_interpolator(0, 3, 10, 0.1, 0, -0.1)
absPayoutScoring = define_interpolator(0, 0.7, 1.5, 0, 0, 0, decreasing=True)

baseProfile = profileAversion(TERM_LENGTH=5, returnsAversion=1.5, consistancyAversion=2,
                              dividendGrowthAversion=1, marketCapAversion=0.5, dividendYieldAversion=2.5, absPayoutRatioAversion=0.5)

def createPortfolio(sorted_stocks, datas, tickersInfos, stock_number=6, distribution=[0.2, 0.18, 0.17, 0.16, 0.15, 0.14]):
    portfolioStocks = list(sorted_stocks.keys())[:stock_number]

    evaluatePortfolio(datas, tickersInfos, portfolioStocks, distribution)

def evaluatePortfolio(datas, tickersInfos, portfolioStocks, distribution):
    returnsTerm, returns1y, dividendGrowth, marketCap, dividendYield = 0, 0, 0, 0, 0

    print("="*25)
    print(colors.cyan("PORTFOLIO DISTRIBUTION :"))

    for i, stock in enumerate(portfolioStocks):
        print("Ticker :", stock, "\t",
              str(round(distribution[i] * 100))+"%")
        
        # get portfolio statistics
        returnsTerm += getReturnsArray(datas[stock], datas["interval"], [
            baseProfile.TERM_LENGTH], [max(0.05, baseProfile.TERM_LENGTH / 85)])[0][0] * distribution[i]
        returns1y += getReturnsArray(
            datas[stock], datas["interval"], [1], [0])[0][0] * distribution[i]
        dividendGrowth += getDividendGrowth(datas[stock]) * distribution[i]
        marketCap += getMarketCap(tickersInfos[stock]) * distribution[i]
        dividendYield += getDividendsYield(datas[stock], 5) * distribution[i]

    print("="*25)
    print(colors.cyan("PORTFOLIO STATISTICS :"))

    print("Avg >", str(round(max(0.05, baseProfile.TERM_LENGTH / 90) * 100,2)) + "%", "returns {}y :".format(baseProfile.TERM_LENGTH), str(round(returnsTerm,2))+"%")
    print("Avg pos. returns 1y : \t", str(returns1y)+"%")
    print("Average market cap : \t", str(round(marketCap))+" Md")
    print("Avg dividend yield : \t", str(round(dividendYield, 2))+"%")
    print("Avg dividendGrowth : \t", str(round(dividendGrowth * 100, 2))+"%")


# sort ticker by their score (descending order)
def sortTickers(datas, tickersInfos, tickers):
    sortedTickers = {}

    for ticker in tickers:

        sortedTickers[ticker] = getStockScore(datas, tickersInfos, ticker)

    sortedTickers = dict(sorted(sortedTickers.items(),
                         key=lambda item: item[1], reverse=True))

    return sortedTickers


# get a global score (can be positive or negative) for a ticker
def getStockScore(datas, tickersInfos, ticker):
    TERM_LENGTH = baseProfile.TERM_LENGTH

    returnsTerm = getReturnsArray(datas[ticker], datas["interval"], [
                                  TERM_LENGTH], [max(0.05, TERM_LENGTH / 90)])
    returns1y = getReturnsArray(
        datas[ticker], datas["interval"], [1], [0])
    dividendGrowth = getDividendGrowth(datas[ticker])
    marketCap = getMarketCap(tickersInfos[ticker]) 
    dividendYield = getDividendsYield(datas[ticker], 5)
    absPayoutRatio = getAbsPayoutRatio(tickersInfos[ticker]) 

    if (returnsTerm == None or returns1y == None or dividendYield == None):
        print(colors.blue(ticker), ": Not enough data to backtest")
        return -100

    returnsScore = returnScoring(returnsTerm[0][0])
    consistancyScore = returnScoring(returns1y[0][0])
    dividendGrowthScore = dividendGrowthScoring(dividendGrowth)
    marketCapScore = marketCapScoring(marketCap)
    dividendYieldScore = dividendYieldScoring(dividendYield)
    absPayoutRatioScore = absPayoutScoring(absPayoutRatio)

    if (VERBOSE):
        print("Symbol :", colors.cyan(ticker))
        print("Return score :",  colors.blue(round(returnsScore, 3)), "Consistancy score :", colors.blue(round(consistancyScore, 3)), "Dividend growth score :", colors.blue(round(dividendGrowthScore, 3)),
            "Market cap score :", colors.blue(round(marketCapScore, 3)), "Dividend yield score :", colors.blue(round(dividendYieldScore, 3)), "Payout ratio score :", colors.blue(round(absPayoutRatioScore, 3)))
        print("-"*25)

    return round(baseProfile.getStockTotalScore(returnsScore, consistancyScore, dividendGrowthScore, marketCapScore, dividendYieldScore, absPayoutRatioScore), 2)
