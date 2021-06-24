import pandas as pd
import datetime
from vix_trigger import isNewLow, isNewHigh, isCurrentHigherThanOpen, isCurrentLowerThanOpen
import yfinance as yf

# Select from to which date you want to see what you could have made/lost
# NB! Can not be today's date, and it will require some processing power with dates
# far away from each other
start_date = '2021-01-31'
end_date = '2021-02-11'
# Do not change these two
days_back = 15
SYMBOL = 'VIX'
# Choose the stock you want to compare the vix trigger with (ticker)
stock_symbol = "TSLA"


def vix_trigger():
    """
    Checks to see if the data follows one of the two rules.
    Returns 0 if it signals a sell
    Returns 1 if it signals a buy
    Returns 2 if it does not signal anything
    """

    # Initialize the buy & sell indicators
    buy, sell = False, False

    # If the current price is higher than the open and today is a new 15-day low, then this is a SELL indicator
    if isCurrentHigherThanOpen(current, newest_open) & isNewLow(newest_low, data):
        sell = True

    # If the current price is lower than the open and today is a new 15-day high, then this is a BUY indicator
    if isCurrentLowerThanOpen(current, newest_open) & isNewHigh(newest_high, data):
        buy = True

    # If one of the two indicators is True, print out the given text
    if buy:
        # Buy
        return 1
    elif sell:
        # Sell
        return 0
    else:
        # No trigger
        return 2

# Create a list of all dates between the user specified dates
string_list = pd.date_range(start_date, end_date,
                            freq='D').strftime("%Y-%m-%d").tolist()
date_list = [datetime.datetime.strptime(date, "%Y-%m-%d") for date in string_list]

# The dictionary which the triggers and their dates will be stored
buy_sell_dict = {}

for current_datetime in date_list:
    # Yesterday's date from the current date the loop is on
    end = current_datetime - datetime.timedelta(days=1)
    # 30 days ago from from the current date the loop is on
    start = current_datetime - datetime.timedelta(days=30)

    # Retrieve historical data from the VIX index via Yahoo's API
    vix = yf.Ticker(f"^{SYMBOL}")
    data = vix.history(start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"))
    data.drop(labels=["Volume", "Dividends", "Stock Splits"], axis=1, inplace=True)
    index = data.columns
    data = data.reset_index().drop("Date", axis=1)
    data = data.to_dict("list")

    # Collect all data ones more for one month
    all_data = vix.history(start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"))

    # Validate that we have enough historical data to continue
    if len(data['Open']) < days_back:
        not_enough_data = True

    # Retrieve the data from the date the loop is currently on
    current_data = vix.history(start=current_datetime.strftime("%Y-%m-%d"),
                               end=current_datetime.strftime("%Y-%m-%d"))
    # Some dates don't have data and will give an index error
    try:
        # Get to closing price for the current date the loop is on
        current = current_data['Close'][0]
        # Get all opening prices 30 days back
        opens = all_data["Open"]
        open_list = opens.to_list()
        # The opening price on the current date the loop i on
        newest_open = current_data['Open']

        # Get all high prices 30 days back
        high = all_data["High"]
        high_list = high.to_list()
        # The high price of the current date the loop is on
        newest_high = current_data['High']

        #Get all low prices 30 days back
        low = all_data["Low"]
        low_list = low.to_list()
        # The low price of the current date the loop is on
        newest_low = current_data['Low']

        # Run the vix_trigger function
        result = vix_trigger()
        if result == 1:
            buy_sell_dict[current_data.index[0].strftime("%Y-%m-%d")] = 'Buy'
        if result == 0:
            buy_sell_dict[current_data.index[0].strftime("%Y-%m-%d")] = 'Sell'
        if result == 2:
            pass
    # In case of IndexError
    except IndexError:
        pass

# Get data from user specified stock with an interval of user specified dates
ticker = yf.Ticker(stock_symbol)
stock_data = ticker.history(start=start_date, end=end_date)
stock_data.drop(labels=["Volume", "Dividends", "Stock Splits"], axis=1, inplace=True)
stock_data = stock_data.reset_index()

# The dictionary all closing prices will be stored for the user specified stock
stock_close = {}

# Filter out everything but the closing price from dates which contain buy or sell triggers
for key in buy_sell_dict:
    stock_close[key] = stock_data.loc[stock_data.Date == key, ['Close']]
for key in stock_close:
    stock_close[key] = stock_close[key]['Close']
    stock_close[key] = float(stock_close[key])

# Specify which dates are buy trigger dates and which are sell trigger dates
buy_dates = []
sell_dates = []
for key in buy_sell_dict:
    trigger = buy_sell_dict[key]
    if trigger == 'Buy':
        buy_dates.append(key)
    else:
        sell_dates.append(key)

# The portfolio in which the buy and sell price will be stored
portfolio = {'buy': None, 'sell': None, }
# A list to store all profits after each buy and sell
profit = []

# Go over all closing prices in the dictionary
for key in stock_close:
    # If the date (key) is in the buy dates list and no buy or sell info is stored
    if key in buy_dates and portfolio['buy'] is None and portfolio['sell'] is None:
        # Add the price to the portfolio
        portfolio['buy'] = stock_close[key]
        # Used to check that you can not sell from dates before the buy
        buy_year = int(key[0:4])
        buy_month = int(key[5:7])
        buy_day = int(key[8:10])
    # If the date (key) is in the sell dates list and a buy is stored while sell is not
    if key in sell_dates and portfolio['buy'] is not None and portfolio['sell'] is None:
        # Used to check that you can not sell from dates before the buy
        sell_year = int(key[0:4])
        sell_month = int(key[5:7])
        sell_day = int(key[8:10])
        # If the sell year is larger or equal to the buy year
        if sell_year >= buy_year:
            # If the sell month is equal to buy month the day date must be larger
            if sell_month == buy_month:
                if sell_day > buy_month:
                    # Add the sell price to the portfolio
                    portfolio['sell'] = stock_close[key]
            # If the sell month is larger than tge buy month
            if sell_month > buy_month:
                # Add the sell price to the portfolio
                portfolio['sell'] = stock_close[key]
    #If the portfolio is full
    if portfolio['buy'] is not None and portfolio['sell'] is not None:
        # Compute the profit
        profit.append((portfolio['sell'] - portfolio['buy']))
        # Reset the portfolio
        portfolio['buy'] = None
        portfolio['sell'] = None

# Print out what the user could have made/lost if they followed the vix trigger
if sum(profit) > 0:
    print(f'If you followed the VIX index trigger you would have made {sum(profit):.2f}$')
elif sum(profit) == 0:
    print(f'You would have broken even if you followed the vix index trigger {sum(profit):.2f}$')
else:
    print(f'If you followed the VIX index trigger you would have lost {sum(profit):.2f}$')