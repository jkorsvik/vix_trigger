#!/usr/bin/env python
import datetime
import yfinance as yf
import streamlit as st
import requests
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from stockstats import StockDataFrame
import yfinanceScraper 
import ticker_manager
import model

st.image('images/header.png')
st.markdown(""" # Welcome to the VIX buy or sell trigger

The purpose of this program is to provide you, the stock trader, with a 'report' on the VIX index for 
possible buy & sell triggers based on the Larry Connors 'CVR' reversal indicators.

This particular implementation examines the recent 15-period VIX daily high & low values 
and applies the following rules:

- When the VIX index makes a NEW 15 day low AND closes ABOVE its open, it signals a sell
- When the VIX index makes a NEW 15 high low AND closes BELOW its open, it signals a buy

The program will Further

It makes use of the yahoo stock quotes python library to scrape the necessary data from Yahoo Finance. 
The program will also provide you with a chart of the VIX index from the time period as an interactive candleplot.
Volume is included in the chart, but as a random number just to show more info on the chart.
"""
)

COMMASPACE = ", "

# The VIX ticker
SYMBOL = "VIX"

# Number of days of historical data to fetch (not counting today)
days_back = st.sidebar.slider('Number of days in graph', 15, 365, 15)

not_enough_data = False

# Current datetime
current_datetime = datetime.datetime.now()
data_dict = {}
st.sidebar.write("What Tickers do you want to use?")

for ticker in ticker_manager.Ticker:
    if ticker == ticker_manager.Ticker.VIX:
        store = st.sidebar.checkbox(f"{ticker.name}", value=True)
    else:
        store = st.sidebar.checkbox(f"{ticker.name}")
    if store:
        data_dict[ticker.name] = yfinanceScraper.Scraper(ticker=ticker.value, n_days=days_back)


options = st.sidebar.multiselect(
     "Which tickers would you like to display?",
     data_dict.keys())

#st.sidebar.write('You selected:', options)


def create_candleplot(scraper):
    df = scraper.historic_data
    st.write(f"**{scraper.name} Candlestick Chart**")
    fig = make_subplots(rows=2, cols=1, row_heights=[1, 0.2], vertical_spacing=0)

    fig.add_trace(go.Candlestick(x=df['datetime'],
                                         open=df['open'],
                                         high=df['high'],
                                         low=df['low'],
                                         close=df['close'],
                                increasing_line_color='#0384fc', decreasing_line_color='#e8482c', name=scraper.name), row=1, col=1)

    fig.add_trace(go.Scatter(x=df['datetime'], y=np.random.randint(20, 40, len(df)), marker_color='#fae823', name='VO', hovertemplate=[]), row=2, col=1)

    fig.update_layout({'plot_bgcolor': "#21201f", 'paper_bgcolor': "#21201f", 'legend_orientation': "h"},
                    legend=dict(y=1, x=0),
                    font=dict(color='#dedddc'), dragmode='pan', hovermode='x unified',
                    margin=dict(b=21, t=1, l=1, r=40))

    fig.update_yaxes(showgrid=False, zeroline=False, showticklabels=True,
                    showspikes=True, spikemode='across', spikesnap='cursor', showline=False, spikedash='solid')

    fig.update_xaxes(showgrid=False, zeroline=False, rangeslider_visible=False, showticklabels=True,
                    showspikes=True, spikemode='across', spikesnap='cursor', showline=False, spikedash='solid')

    fig.update_layout(hoverdistance=1)

    fig.update_traces(xaxis='x')  
                                  
    st.plotly_chart(fig)

# create a streamlit box for candleplot
def async_streamlit_candleplot(ticker, data):
    """
    Creates a streamlit box for the candleplot
    Parameters:
    data (list): All price data for the VIX index 15 days back
    """
    st.subheader(f"{ticker} Candlestick Chart")
    create_candleplot(data)

def isNewHigh(high, data):
    """
    Returns True if the 'high' is higher than any of the highs in the data
    array passed in. Otherwise returns False
    Parameters:
    high (float): Today's highest price for the VIX index
    data (list): All price data for the VIX index 15 days back
    """
    highs = data.get("High")
    for i in highs:
        try:
            if (float(i)) >= float(high):
                return False
        except ValueError:
            return False
    return True


def isNewLow(low, data):
    """
    Returns True if the 'low' is lower than any of the lows in the data
    array passed in. Otherwise returns False
    Parameters:
    low (float): Today's lowest price for the VIX index
    data (list): All price data for the VIX index 15 days back
    """
    lows = data.get("Low")
    for i in lows:
        try:
            if float(i) <= float(low):
                return False
        except ValueError:
            return False
    return True


def isCurrentHigherThanOpen(current, today_open):
    """
    Simple check to see if the current price is greater than the open price
    Parameters:
    current (float): The current price for the VIX index
    open (float): Today's opening price
    """
    return float(current) > float(today_open)


def isCurrentLowerThanOpen(current, today_open):
    """
    Simple check to see if the current price is lower than the open price
    Parameters:
    current (float): The current price for the VIX index
    open (float): Today's opening price
    """
    return float(current) < float(today_open)


# Yesterday's date
end = current_datetime - datetime.timedelta(days=1)
# 30 days ago from today
start = current_datetime - datetime.timedelta(days=days_back)

# Retrieve historical data from the VIX index via Yahoo's API
vix = yf.Ticker(f"^{SYMBOL}")
data = vix.history(start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"))
drop_cols = ["Dividends", "Stock Splits"]
for col in drop_cols:
    try:
        data.drop(col, axis=1, inplace=True)
    except:
        pass
index = data.columns
data = data.reset_index()
data = data.to_dict("list")

# Collect all data once more for one month
all_data = vix.history(period="1mo", interval="1d")
#print(all_data)


current = vix.info
current = current.get("regularMarketPrice")

opens = all_data["Open"]
open_list = opens.to_list()
newest_open = open_list[-1]

high = all_data["High"]
high_list = high.to_list()
newest_high = high_list[-1]

low = all_data["Low"]
low_list = low.to_list()
newest_low = low[-1]


def vix_trigger():
    """
    Checks to see if the data follows one of the two rules.
    Returns an informative string and picture of the VIX index
    """
    if not_enough_data:
        exit("Not enough historical data to compute an answer.\n"
             "Try again tomorrow")
    # Initialize the buy & sell indicators
    buy, sell = False, False

    # If the current price is higher than the open and today is a new 15-day low, then this is a SELL indicator
    if isCurrentHigherThanOpen(current, newest_open) & isNewLow(newest_low, data):
        sell = True

    # If the current price is lower than the open and today is a new 15-day high, then this is a BUY indicator
    if isCurrentLowerThanOpen(current, newest_open) & isNewHigh(newest_high, data):
        buy = True

    # If one of the two indicators is True, print out the given text
    if buy | sell:
        if buy:
            st.markdown("<b style='text-align: center; color: black;'>Buy indicator triggered!<br/></b>",
                        unsafe_allow_html=True)
            st.write(f"The VIX has a new 15-day high ({newest_high:.2f})\n",
                     f"& the current price ({current:.2f}) is lower\n",
                     f"than the open ({newest_open:.2f})\n",
                     "This is a BUY indicator")
            st.markdown("<b style='text-align: center; color: black;'>=======> THIS IS A BUY INDICATOR</b>",
                        unsafe_allow_html=True)
        if sell:
            st.markdown("<b style='text-align: center; color: black;'>Sell indicator triggered!<br/></b>",
                        unsafe_allow_html=True)
            st.write(f"The VIX has a new 15-day low ({newest_low:.2f})\n"
                     f"& the current price ({current:.2f}) is higher\n"
                     f"than the open ({newest_open:.2f})\n")
            st.markdown("<b style='text-align: center; color: black;'>=======> THIS IS A SELL INDICATOR</b>",
                        unsafe_allow_html=True)
    # If neither of the indicators are True, print out the given text
    else:
        st.write("No trigger was activated.\n",
                 f"The current VIX index price is ({current}).\n"
                 "Check back tomorrow")

    # Collect the image of the VIX index from stockcharts.com
    for ticker in options:
        print(ticker)
        create_candleplot(data_dict[ticker])



col1, col2 = st.columns([1,1])

# Button to run the VIX trigger
result_1 = col1.button("Click here to see if you should buy or sell today")
if result_1:
    vix_trigger()


def print_data_summary():
    """
    Prints out a summary of the data used in the vix trigger function
    Returns streamlit text of the data
    """
    st.write(f"Data retrieved from {start.date()} to {end.date()}")
    st.write(f"Current time is: {current_datetime}")
    st.write(f"Current hour is: {current_datetime.hour}")
    st.write(f"Current minute is: {current_datetime.minute}")
    st.write(f"Current second is: {current_datetime.second}")
    st.write(f"Number of days of actual market data retrieved is: {(len(data['Open']) - 1)}")
    st.write(f"Current price: {current:.2f}")
    st.write(f"Open price: {newest_open:.2f}")
    st.write(f"High price: {newest_high:.2f}")
    st.write(f"Low price: {newest_low:.2f}")

# Button to run the data summary function
result_2 = col2.button("Click here to see the data used in the VIX trigger")
if result_2:
    print_data_summary()

