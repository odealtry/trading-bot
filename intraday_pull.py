import pandas as pd
from alpha_vantage.techindicators import TechIndicators
from alpha_vantage.timeseries import TimeSeries
import config
import sys

ticker = str(sys.argv[1])

api_key = config.AlphaVantageAPIKey

period = 60

ti = TechIndicators(key=api_key, output_format='pandas')

ti_data, ti_meta_data = ti.get_sma(symbol=ticker, interval='5min',
                        time_period=period, series_type='close')

ts = TimeSeries(key=api_key, output_format='pandas')

ts_data, ts_meta_data = ts.get_intraday(symbol=ticker, interval='5min',
                        outputsize='full');

df1 = ti_data
df2 = ts_data['4. close'].iloc[period-1::]

df1.index = df2.index

concatenated_df = pd.concat([df1, df2], axis=1)

with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    print(concatenated_df)
