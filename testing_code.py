import yfinance as yf


hist = yf.Ticker("NG=F").history(period="max")

print(hist)