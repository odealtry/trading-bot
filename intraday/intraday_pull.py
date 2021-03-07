# This file pulls minute-by-minute closes and calculates
# an hourly exponential moving average, returning a df combining
# the two.

import pandas as pd
from alpha_vantage.techindicators import TechIndicators
from alpha_vantage.timeseries import TimeSeries
import config

class IntradayPull:
    def __init__(self, ticker):
        self.ticker = ticker
        self.data = pd.DataFrame
        self.raw_ema = pd.DataFrame
        self.raw_ts = pd.DataFrame
        self.ts_close = pd.DataFrame

    def Pull(self):
        api_key = config.AlphaVantageAPIKey
        period = 30
        ti = TechIndicators(key=api_key, output_format='pandas')
        ti_data, ti_meta_data = ti.get_ema(symbol=self.ticker, interval='1min',
                                time_period=period, series_type='close')
        ts = TimeSeries(key=api_key, output_format='pandas')
        ts_data, ts_meta_data = ts.get_intraday(symbol=self.ticker, interval='1min',
                                outputsize='full');
        self.raw_ema = ti_data
        self.raw_ts = ts_data
        df1 = ti_data
        # adjusting ts dataframe to only include close:
        df2 = ts_data['4. close']
        self.ts_close = df2
        self.data = pd.concat([df1, df2], axis=1)

# intraday_data = pd.read_json('intraday/data/data.json')

ticker = input("Please enter a stock ticker for intraday strategy: ")

stock = IntradayPull(ticker)

stock.Pull()

# raw_ema = stock.raw_ema
# raw_ts = stock.raw_ts

# ts_close = stock.ts_close

intraday_data = stock.data

# print("Raw ema:")
# print(raw_ema)

# print("Raw ts:")
# print(raw_ts)

# print("ts close:")
# print(ts_close)

# print("Final concatenation:")
print(intraday_data)
# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     print(intraday_data)



























