# This file pulls minute-by-minute closes and calculates
# an hourly exponential moving average, returning a df combining
# the two.

import pandas as pd
from alpha_vantage.techindicators import TechIndicators
from alpha_vantage.timeseries import TimeSeries
import config
import sys

class IntradayPull:
    def __init__(self, ticker):
        self.ticker = ticker
        self.data = pd.DataFrame
        self.ema = pd.DataFrame

    def Pull(self):
        api_key = config.AlphaVantageAPIKey
        period = 60
        ti = TechIndicators(key=api_key, output_format='pandas')
        ti_data, ti_meta_data = ti.get_ema(symbol=self.ticker, interval='1min',
                                time_period=period, series_type='close')
        ts = TimeSeries(key=api_key, output_format='pandas')
        ts_data, ts_meta_data = ts.get_intraday(symbol=self.ticker, interval='1min',
                                outputsize='full');
        # equalising df sizes:
        df1 = ti_data[::-1]
        df2 = ts_data['4. close'].iloc[period-1::]
        # equalising df indexes:
        df1.index = df2.index
        self.data = pd.concat([df1, df2], axis=1)
        self.ema = df1

# intraday_data = pd.read_json('data/intraday_data.json')

ticker = input("Please enter a stock ticker for intraday strategy: ")

stock = IntradayPull(ticker)

stock.Pull()

intraday_data = stock.data

ema = stock.ema

# print(ema)

print(intraday_data)
# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     print(intraday_data)
