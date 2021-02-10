from alpha_vantage.timeseries import TimeSeries
import sys
import config
import numpy as np

api_key = config.AlphaVantageAPIKey

ts = TimeSeries(key=api_key, output_format='pandas')

ticker = str(sys.argv[1])

data, meta_data = ts.get_daily(symbol=ticker,
                                    outputsize='compact');

daily_close = data['4. close']

month_of_closes = daily_close[0:31]

# now we calculate the 30 day volatility for the current day
# and the previous day:

today_vol = np.std(month_of_closes[1:31])
yesterday_vol = np.std(month_of_closes[0:30])

print(today_vol, yesterday_vol)
