from typing import Tuple

from utils.vix_utils import (
    isCurrentHigherThanOpen,
    isCurrentLowerThanOpen,
    isNewHigh,
    isNewLow,
)


def vix_signals(all_data, vix_data, current) -> Tuple[bool, bool]:
    DAYS_BACK = 14
    all_data.drop(labels=["Volume", "Dividends", "Stock Splits"], axis=1, inplace=True)
    all_data = all_data.reset_index().drop("Date", axis=1)
    all_data = all_data.to_dict("list")

    if len(data.get("Close")) < days_back:
        print(
            "Not enough historical data available to continue (need at least 15 days of market data)"
        )
    opens = all_data["Open"]
    open_list = opens.to_list()
    newest_open = open_list[-1]

    high = all_data["High"]
    high_list = high.to_list()
    newest_high = high_list[-1]

    low = all_data["Low"]
    low_list = low.to_list()
    newest_low = low[-1]
    buy, sell = False, False
    # if the current price is higher than the open and today is a new 15-day low,
    # then this is a SELL indicator
    if isCurrentHigherThanOpen(current, newest_open) & isNewLow(newest_low, data):
        # print 'today is a 15-day low (' + str(low) + ') & the current price (' + str(current) + ') is higher than the open (' + str(open) + ')'
        sell = True

    # if the current price is lower than the open and today is a new 15-day high,
    # then this is a BUY indicator
    if isCurrentLowerThanOpen(current, newest_open) & isNewHigh(newest_high, data):
        # print 'today is a 15-day high (' + str(high) + ') & the current price (' + str(current) + ') is lower than the open (' + str(open) + ')'
        buy = True
    return buy, sell
