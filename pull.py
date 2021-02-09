import pandas as pd
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
import sys
import random
import config

ticker = str(sys.argv[1])

api_key = config.AlphaVantageAPIKey

ts = TimeSeries(key=api_key, output_format='pandas')

data, meta_data = ts.get_intraday(symbol=ticker, interval='60min', outputsize='full');

# print(ticker)
# print(meta_data)
# print(data)

# calculating simple moving average from a period of 20 days
period = 480

ti = TechIndicators(key=api_key, output_format='pandas')

ti_data, ti_meta_data = ti.get_sma(symbol=ticker, interval='60min',
                        time_period=period, series_type='close')

df1 = ti_data
df2 = data['4. close']

print(df1)
print(df2)
