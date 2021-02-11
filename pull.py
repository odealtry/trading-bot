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

# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     print(data)

# calculating simple moving average from a period of 50 days.
# this period will be made dynamic by the information calculated
# in volatility_calculation.py

period = 50

ti = TechIndicators(key=api_key, output_format='pandas')

ti_data, ti_meta_data = ti.get_sma(symbol=ticker, interval='daily',
                        time_period=period, series_type='close')

# reversing df1 row order and equalising df sizes:
df1 = ti_data.iloc[::-1]
df2 = data['5. adjusted close'].iloc[:-(period-1)]
df3 = data['2. high'].iloc[:-(period-1)]

df1.index = df2.index = df3.index

concatenated_df = pd.concat([df1, df2, df3], axis=1)


# reducing dataframe to manageable size:
closes_with_sma = concatenated_df[:100]

# closes_with_sma = pd.read_json('AAPL_data.json')

with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    print(closes_with_sma)
