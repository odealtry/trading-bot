from alpha_vantage.timeseries import TimeSeries
import sys
import config
import numpy as np
import moving_average_calculation

api_key = config.AlphaVantageAPIKey

closes_with_sma = moving_average_calculation.closes_with_sma

daily_close = closes_with_sma['5. adjusted close']

month_of_closes = daily_close[0:31]

# now we calculate the 30 day volatility for the current day
# and the previous day:

today_vol = np.std(month_of_closes[31:1:-1])
yesterday_vol = np.std(month_of_closes[30::-1])
deltavol = (today_vol - yesterday_vol) / today_vol
lookback = round(50 *(1 + deltavol))

print(today_vol)

print(yesterday_vol)

print(deltavol)

print(lookback)

