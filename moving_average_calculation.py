# This file will calculate the 50-day moving average and compare it to recent close prices.
# This information will allow the bot to identify:
# - buy opportunities, when the close is lower than the sma;
# - sell opportunities, when the close is higher than the sma.

import pandas as pd
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
import sys
import config

ticker = str(sys.argv[1])

api_key = config.AlphaVantageAPIKey

ts = TimeSeries(key=api_key, output_format='pandas')

data, meta_data = ts.get_daily_adjusted(symbol=ticker, outputsize='full');

# calculating simple moving average from a period of 50 days.
# this period will be made dynamic by the information calculated
# in volatility_calculation.py

period = 50

ti = TechIndicators(key=api_key, output_format='pandas')

ti_data, ti_meta_data = ti.get_sma(symbol=ticker, interval='daily',
                        time_period=period, series_type='close')

df1 = ti_data
# reversing df2 row order and equalising sizes of df1 and df2:
df2 = (data['5. adjusted close'].iloc[::-1]).iloc[period-1::]

df2.index = df1.index

concatenated_df = pd.concat([df1, df2], axis=1)

# reducing dataframe size to 251, average number of annual trading days
annual_data = concatenated_df[-251:]
# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     print(annual_data)
