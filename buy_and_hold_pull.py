# This file will calculate the 50-day moving average and compare it to recent close prices.
# This information will allow the bot to identify:
# - buy opportunities, when the close is lower than the sma;
# - sell opportunities, when the close is higher than the sma.

import pandas as pd
from alpha_vantage.timeseries import TimeSeries
import sys
import config

# ticker = str(sys.argv[1])

# period = 50

# api_key = config.AlphaVantageAPIKey

# ts = TimeSeries(key=api_key, output_format='pandas')

# data, meta_data = ts.get_daily_adjusted(symbol=ticker, outputsize='full');

# # reversing df1 row order and equalising df sizes:

# df1 = data['4. close'].iloc[:-(period-1)]
# df2 = data['2. high'].iloc[:-(period-1)]
# df3 = data['8. split coefficient'].iloc[:-(period-1)]

# df1.index = df2.index = df3.index

# concatenated_df = pd.concat([df1, df2, df3], axis=1)

concatenated_df = pd.read_json('buy_and_hold_data.json')

# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     print(concatenated_df)

# analysing data for stock split/merge events:
split_day = (concatenated_df.loc[concatenated_df['8. split coefficient'] != 1])
split_coefficient = int(split_day['8. split coefficient'])

# then adjust data prior to that entry according to its value.
# a copy of concatenated_df will need to be made,
# and .loc and mask used for accessing and changing data.

new_df = concatenated_df.copy()

split_date = (split_day.index[0])

post_split_data = new_df[:split_date]

print(post_split_data)

pre_split_data = new_df[split_date:]

print(pre_split_data)

# pre_split_data['2. high'] =  pre_split_data['2. high'] / split_coefficient
# pre_split_data['4. close'] =  pre_split_data['4. close'] / split_coefficient

# post_split = concatenated_df[:split_date]
# adjusted_pre_split = pre_split_data

# frames = [post_split, adjusted_pre_split]
# result = pd.concat(frames)

# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     print(result)

# print(result)

# reducing dataframe to annual size:
# annual_data = concatenated_df[:251]

