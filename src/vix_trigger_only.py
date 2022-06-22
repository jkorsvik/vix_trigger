import datetime
import yfinance as yf
from glob import glob
import streamlit as st
import numpy as np


def main_vix(days_back):

    ### SOME GLOBALS
    COMMASPACE = ", "

    # The VIX ticker
    SYMBOL = "VIX"
    not_enough_data = False

    # Current datetime
    current_datetime = datetime.datetime.now()

    # Yesterday's date
    end = current_datetime - datetime.timedelta(days=1)
    # 30 days ago from today
    start = current_datetime - datetime.timedelta(days=days_back)

    # Retrieve historical data from the VIX index via Yahoo's API
    vix = yf.Ticker(f"^{SYMBOL}")

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
    def isNewHigh(high, all_data):
        """
        Returns True if the 'high' is higher than any of the highs in the data
        array passed in. Otherwise returns False
        Parameters:
        high (float): Today's highest price for the VIX index
        data (list): All price data for the VIX index 15 days back
        """
        highs = all_data.get("High")
        for i in highs:
            try:
                if (float(i)) >= float(high):
                    return False
            except ValueError:
                return False
        return True


    def isNewLow(low, all_data):
        """
        Returns True if the 'low' is lower than any of the lows in the data
        array passed in. Otherwise returns False
        Parameters:
        low (float): Today's lowest price for the VIX index
        data (list): All price data for the VIX index 15 days back
        """
        lows = all_data.get("Low")
        for i in lows:
            try:
                if float(i) <= float(low):
                    return False
            except ValueError:
                return False
        return True

    def clear_widget(widget):
        widget.clear()

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
        if isCurrentHigherThanOpen(current, newest_open) & isNewLow(newest_low, all_data):
            sell = True

        # If the current price is lower than the open and today is a new 15-day high, then this is a BUY indicator
        if isCurrentLowerThanOpen(current, newest_open) & isNewHigh(newest_high, all_data):
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




    buy_or_not_VIX, see_data = st.columns([1,1])

    # Button to run the VIX trigger
    result_1 = buy_or_not_VIX.button("Click here to see if you should buy or sell today")
    if result_1:
        #data, newest_high, newest_low, current, newest_open, _ = gather_base_vix_data()
        vix_trigger()


    def print_data_summary():
        """
        Prints out a summary of the data used in the vix trigger function
        Returns streamlit text of the data
        """

        with st.container() as cont:
            st.write(f"Data retrieved from {start.date()} to {end.date()}")
            st.write(f"Current time is: {current_datetime}")
            st.write(f"Current hour is: {current_datetime.hour}")
            st.write(f"Current minute is: {current_datetime.minute}")
            st.write(f"Current second is: {current_datetime.second}")
            st.write(f"Number of days of actual market data retrieved is: {(len(all_data['Open']) - 1)}")
            st.write(f"Current price: {current:.2f}")
            st.write(f"Open price: {newest_open:.2f}")
            st.write(f"High price: {newest_high:.2f}")
            st.write(f"Low price: {newest_low:.2f}")
        
    # Button to run the data summary function
    result_2 = see_data.button("Click here to see the data used in the VIX trigger")
    if result_2:
        #data, newest_high, newest_low, current, newest_open, _ = gather_base_vix_data()
        #print(data, newest_high, newest_low, current, newest_open)
        print_data_summary()
