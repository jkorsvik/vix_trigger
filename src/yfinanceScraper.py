import datetime

import pandas as pd
import yfinance as yf



class Scraper:
    """Scraper class"""
    def __init__(self, ticker="^VIX", n_days=30):
        self.name = ticker
        self.ticker = yf.Ticker(f"{ticker}")
        self._historic_data = None
        self._ndays = n_days

    @property
    def historic_data(self):
        if self._historic_data is None:
            return self.get_historic_data(ticker=self.ticker, n_days=self._ndays)
        else:
            return self._historic_data

    def get_json(self, ticker_str=None, n_days=30):
        """Return json from desired dataframe"""
        if ticker_str:  # If a ticker is provided, select the provided.
            ticker = yf.Ticker(f"{ticker_str}")
        else:  # Else use the one from the instance.
            ticker = self.ticker

        # Return data as a json
        data = self.get_historic_data(ticker=ticker, n_days=n_days)
        return data.to_json(index=True, orient='split')

    @staticmethod
    def get_historic_data(ticker, n_days=30):
        """Get historic data from the past n_days, with the current ticker object."""
        # Time Info
        current_datetime = datetime.datetime.now()
        start = current_datetime - datetime.timedelta(days=n_days + 1)
        end = current_datetime - datetime.timedelta(days=1)

        # Get Data
        data = ticker.history(period='1d',
            start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d")
        )
        data.drop(labels=["Dividends", "Stock Splits"], axis=1, inplace=True)
        if data.shape[0] < 10:
            raise RuntimeError("Not enough data, we need at least Two weeks (10 days) worth!")
        data = data.reset_index().pipe(lambda d: d.rename(columns={c: c.lower() if c != "Date" else "datetime" for c in d.columns}))
        return pd.DataFrame(data)

    def get_extreme_value(self, col, method):
        """Expected col is either Open, High, Low or Close"""
        return eval(f"self.historic_data['{col}'].{method}()")

    def get_current_data(self):
        """Get the current price"""
        return self.ticker.info.get("regularMarketPrice")

    def get_current_val(self, col):
        """Get today's value from desired column."""
        return self.historic_data[col].iloc[-1]

    def recommendation(self, api=False):
        """Calculate a recommendation"""
        current_price = self.get_current_data()
        open_today = self.get_current_val("open")
        low = self.get_extreme_value("low", "min")
        high = self.get_extreme_value("high", "max")

        # Get info about stock market situation
        new_low = current_price < low
        new_high = current_price > high
        up_today = current_price > open_today

        # Do a quick analysis of the data
        if up_today and new_low:
            sell = True
        else:
            sell = False

        if not up_today and new_high:
            buy = True
        else:
            buy = False

        # Return the results
        if api:
            return {
                "recommendation": {f"Recommendations: {buy=} {sell=}"},
                "new_low": f"{new_low}",
                "new_high": f"{new_high}",
                "up_today": f"{up_today}",
            }
        return f"Recommendations: \n{buy=}\n{sell=}"


if __name__ == '__main__':
    # Get the data
    scraper = Scraper()
    print(scraper.historic_data)
    # Get the recommendation
    print(scraper.recommendation())