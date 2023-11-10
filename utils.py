import math
import math
from scipy.interpolate import CubicHermiteSpline


# return all returns of a given stock close prices within a slide window of *window_length* param length
def getSlideWindowReturns(window_length, datas, data_interval):
    windowedReturns = []

    # Get number of interval within a year
    if (data_interval == "1mo"):
        intervalNb = 12
    elif (data_interval == "1wk"):
        intervalNb = 52
    else:
        raise Exception("Wrong interval")

    # Get the ajusted (with data_interval) window length
    window_ajusted_length = intervalNb * window_length

    for i in range(window_length, math.floor(len(datas["Adj Close"])/intervalNb)):
        start_close = datas["Adj Open"][i*intervalNb - window_ajusted_length]
        end_close = datas["Adj Close"][i*intervalNb-1]

        windowedReturns.append((end_close / start_close)
                               ** (1/window_length) - 1)

    return windowedReturns


# return an array of the percentage of times the returns was over the *percentage* parameters on the *period* parameter.
def getReturnsArray(datas, data_interval, periods=[1, 3, 5, 10, 15, 20, 25, 30], percentages=[0, 0.02, 0.04, 0.06, 0.08, 0.1, 0.12, 0.14, 0.16, 0.18, 0.2, 0.22, 0.24, 0.26, 0.28, 0.3]):
    returnsArray = []

    # construct rows of the array
    for period in periods:

        slideWindowReturns = getSlideWindowReturns(
            period, datas, data_interval)
        totalReturnsLength = len(slideWindowReturns)

        if (slideWindowReturns == []):
            return None

        if (totalReturnsLength > 0):

            percentage_array = []

            # construct column of the array
            for percentage in percentages:

                positives = 0

                # for each return of the last years, if the value is more than the expected minimum returns, we add 1 else 0
                for price_return in slideWindowReturns:
                    if (price_return > percentage):
                        positives += 1
                percentage_array.append(
                    round((positives / totalReturnsLength) * 100))

            returnsArray.append(percentage_array)

    return returnsArray

# add adjusted close price to the datas that take into account dividends
def addAdjustedClosePrice(datas):

    adj_close_price = []
    dividend_impact = 1
    data_length = len(datas["Close"])

    for i in range(1, data_length + 1):
        index = data_length - i  # start from the end
        if (datas["Dividends"][index] != 0):
            dividend_impact *= 1 - \
                (datas["Dividends"][index] / datas["Close"][index])

        adj_close_price.append(dividend_impact * datas["Close"][index])

    datas["Adj Close"] = adj_close_price[::-1]


# add adjusted open price to the datas that take into account dividends
def addAdjustedOpenPrice(datas):

    adj_close_price = []
    dividend_impact = 1
    data_length = len(datas["Open"])

    for i in range(1, data_length + 1):
        index = data_length - i  # start from the end
        if (datas["Dividends"][index] != 0):
            dividend_impact *= 1 - \
                (datas["Dividends"][index] / datas["Open"][index])

        adj_close_price.append(dividend_impact * datas["Open"][index])

    datas["Adj Open"] = adj_close_price[::-1]


# return the % of growing dividends over decreasing one
def getDividendGrowth(datas):

    dividendsPayoutNb = 0
    dividendsGreaterThanLastNb = 0
    lastDividendPayout = 0

    for dividend in datas["Dividends"]:
        if (dividend != 0):
            dividendsPayoutNb += 1

            if (dividend >= lastDividendPayout):
                dividendsGreaterThanLastNb += 1
            lastDividendPayout = dividend

    if (dividendsPayoutNb == 0):
        return 0.9  # Return 0.9 safe value

    return dividendsGreaterThanLastNb / dividendsPayoutNb


# fetch the market cap of a ticker
def getMarketCap(tickerInfos):
    try:
        if tickerInfos:
            if "marketCap" in tickerInfos:
                return round((tickerInfos['marketCap']/1000000000), 2)
    except Exception as e:
        print(e)
        return "not found"


def calculate_mean_with_tail(arr, tail_count):
    if (len(arr) == 0): return None # not enough data to backtest
    if tail_count <= 0:
        raise ValueError("Tail count must be greater than zero")

    if tail_count >= len(arr):
        return sum(arr) / len(arr)

    tail_elements = arr[-tail_count:]
    return sum(tail_elements) / len(tail_elements)


# get dividend yield average of the last *tail_count* years window
def getDividendsYield(datas, tail_count):
    last_record_year = 0

    annualized_yield = []
    total_dividends = 0

    for i in range(len(datas["Date"])):
        # if it's a new year, we start a new year yield record
        if datas["Date"][i][0:4] != last_record_year:
            if (last_record_year != 0):
                annualized_yield.append(
                    (total_dividends / datas["Close"][i]) * 100)
            last_record_year = datas["Date"][i][0:4]
            total_dividends = 0

        # if it's the first of january, we start a new year yield record
        elif datas["Date"][i][5:10] == "01-01":
            if (last_record_year != 0):
                annualized_yield.append(
                    (total_dividends / datas["Close"][i]) * 100)
            last_record_year = datas["Date"][i][0:4]
            total_dividends = 0

        total_dividends += datas["Dividends"][i]

    mean = calculate_mean_with_tail(annualized_yield, tail_count)
    if (mean == None): return None # not enough data to backtest
    return mean


# get "absolute" payout ratio : if payout ratio >= 0, return payout ratio, else, return 100% + abs(payout_ratio)
def getAbsPayoutRatio(tickerInfos):
    if ("trailingAnnualDividendRate" not in tickerInfos or "trailingEps" not in tickerInfos):
        return 1  # If we cannot access values, return a safety 1 value to be fair with other stocks

    absPayoutRatio = tickerInfos["trailingAnnualDividendRate"] / \
        tickerInfos['trailingEps']
    if absPayoutRatio < 0:
        absPayoutRatio = 1 + abs(absPayoutRatio)

    return absPayoutRatio


# get the dividend payout delay
def getDividendYearlyPayoutNb(datas):
    i = len(datas["Date"]) - 1
    current_year = int(datas["Date"][i][0:4])
    payout = 0

    while (i >= 0):

        if int(datas["Date"][i][0:4]) == current_year - 1:
            if (datas["Dividends"][i] != 0):
                payout += 1

        elif int(datas["Date"][i][0:4]) == current_year - 2:
            break

        i -= 1

    return payout


# return a new defined interpolation function used to the scoring of datas
def define_interpolator(x1, x2, x3, dx1, dx2, dx3, decreasing=False):
    if (decreasing == False): decreasing = 1
    else: decreasing = -1

    # Define the x and y values for interpolation
    x_values = [x1, x2, x3]
    y_values = [-1, 0, 1]
    dxdy = [dx1, dx2, dx3]

    # Create a cubic Hermite spline
    spline = CubicHermiteSpline(x_values, y_values, dxdy)

    def _interpolator(x):
        if (x >= x3): 
            return 1 * decreasing
        elif (x <= x1):
            return -1 * decreasing
        else: 
            return spline(x) * decreasing

    return _interpolator


# used to print colored message in stdout
class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    def blue(ch):
        return colors.OKBLUE + str(ch) + colors.ENDC
    
    def cyan(ch):
        return colors.OKCYAN + str(ch) + colors.ENDC
    

# define an investment profile used to set up the metrics to measure the score of stocks
class profileAversion:

    def __init__(self, TERM_LENGTH, returnsAversion, consistancyAversion, dividendGrowthAversion, marketCapAversion, dividendYieldAversion, absPayoutRatioAversion):
        self.TERM_LENGTH = TERM_LENGTH

        self.returnsAversion = returnsAversion
        self.consistancyAversion = consistancyAversion
        self.dividendGrowthAversion = dividendGrowthAversion
        self.marketCapAversion = marketCapAversion
        self.dividendYieldAversion = dividendYieldAversion
        self.absPayoutRatioAversion = absPayoutRatioAversion

    def getStockTotalScore(self, returnsScore, consistancyScore, dividendGrowthScore, marketCapScore, dividendYieldScore, absPayoutRatioScore):
        return returnsScore * self.returnsAversion + consistancyScore * self.consistancyAversion + dividendGrowthScore * self.dividendGrowthAversion + marketCapScore * self.marketCapAversion + dividendYieldScore * self.dividendYieldAversion + absPayoutRatioScore * self.absPayoutRatioAversion
