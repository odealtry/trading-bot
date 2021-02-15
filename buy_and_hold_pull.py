# This file will calculate the 50-day moving average and compare it to recent close prices.
# This information will allow the bot to identify:
# - buy opportunities, when the close is lower than the sma;
# - sell opportunities, when the close is higher than the sma.

import pandas as pd
from alpha_vantage.timeseries import TimeSeries

import sys
import config

# ticker = str(sys.argv[1])

# api_key = config.AlphaVantageAPIKey

# ts = TimeSeries(key=api_key, output_format='pandas')

# data, meta_data = ts.get_daily_adjusted(symbol=ticker, outputsize='full');

# # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
# #     print(data)

# # calculating simple moving average from a period of 50 days

# period = 50

# ti = TechIndicators(key=api_key, output_format='pandas')

# ti_data, ti_meta_data = ti.get_sma(symbol=ticker, interval='daily',
#                         time_period=period, series_type='close')

# # reversing df1 row order and equalising df sizes:
# df1 = ti_data.iloc[::-1]
# df2 = data['4. close'].iloc[:-(period-1)]
# df3 = data['2. high'].iloc[:-(period-1)]
# df4 = data['8. split coefficient'].iloc[:-(period-1)]

# df1.index = df2.index = df3.index = df4.index

# concatenated_df = pd.concat([df1, df2, df3, df4], axis=1)

concatenated_df = pd.read_json('data.json')

# analysing data for stock split/merge events:
split_day = (concatenated_df.loc[concatenated_df['8. split coefficient'] != 1])
split_coefficient = int(split_day['8. split coefficient'])

# then adjust data prior to that entry according to its value.

split_date = (split_day.index[0])

values_with_split = concatenated_df[split_date:]

pre_split_data = values_with_split.iloc[1:]

pre_split_data['2. high'] =  pre_split_data['2. high'] / split_coefficient
pre_split_data['4. close'] =  pre_split_data['4. close'] / split_coefficient

post_split = concatenated_df[:split_date]
adjusted_pre_split = pre_split_data

frames = [post_split, adjusted_pre_split]
result = pd.concat(frames)

# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     print(result)

print(result)

# reducing dataframe to annual size:
# annual_data = concatenated_df[:251]

