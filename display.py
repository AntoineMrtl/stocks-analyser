import numpy as np
import matplotlib.pyplot as plt
from utils import define_interpolator

def displayDividendYieldHistory(ticker, datas):

    last_dividend = 0
    dividend_yield_history = []
    date_history = []

    for i in range(len(datas["Date"])):

        if (datas["Dividends"][i] != 0):
            last_dividend = datas["Dividends"][i]

        dividend_yield_history.append(last_dividend / datas["Close"][i])
        date_history.append(datas["Date"][i])

    # Create a figure and axis
    fig, ax = plt.subplots()

    # Plot your data
    ax.plot(date_history, dividend_yield_history)

    plt.xticks(date_history[::60], rotation=45)


    # Optionally, adjust the subplot layout to prevent clipping of labels
    plt.tight_layout()

    plt.savefig(ticker + '-DividendYield.png')


def plot_interpolator(x1, x2, x3, dx1, dx2, dx3, decreasing=False):
    x = np.linspace(x1, x3, 100)
    y = [define_interpolator(x1, x2, x3, dx1, dx2, dx3, decreasing)(val) for val in x]

    # Plot the function
    plt.plot(x, y, label='Custom Interpolation')
    plt.xlabel('x')
    plt.ylabel('Function Value')
    plt.title('Custom Interpolation Function')
    plt.legend()
    plt.grid(True)
    plt.show()
    plt.savefig("Interpolator.png")