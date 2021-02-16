# This file pulls minute-by-minute closes and calculates
# an hourly moving average, returning a df combining
# the two.

import pandas as pd
from alpha_vantage.techindicators import TechIndicators
from alpha_vantage.timeseries import TimeSeries
import config

class IntradayPull:
    def __init__(self, ticker):
        self.ticker = ticker
        self.data = pd.DataFrame

    def Pull(self):
        api_key = config.AlphaVantageAPIKey
        period = 60
        ti = TechIndicators(key=api_key, output_format='pandas')
        ti_data, ti_meta_data = ti.get_sma(symbol=self.ticker, interval='1min',
                                time_period=period, series_type='close')
        ts = TimeSeries(key=api_key, output_format='pandas')
        ts_data, ts_meta_data = ts.get_intraday(symbol=self.ticker, interval='1min',
                                outputsize='full');
        # equalising df sizes:
        df1 = ti_data
        df2 = ts_data['4. close'].iloc[period-1::]
        # equalising df indexes:
        df1.index = df2.index
        self.data = pd.concat([df1, df2], axis=1)

# intraday_data = pd.read_json('data/intraday_data.json')

tsla = IntradayPull('TSLA')
tsla.Pull()

intraday_data = tsla.data

# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     print(intraday_data)
