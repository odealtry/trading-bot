# This file will calculate the 50-day moving average and compare it to recent close prices.
# This information will allow the bot to identify:
# - buy opportunities, when the close is lower than the sma;
# - sell opportunities, when the close is higher than the sma.

import pandas as pd
from alpha_vantage.timeseries import TimeSeries
import sys
import config

ticker = str(sys.argv[1])

api_key = config.AlphaVantageAPIKey

ts = TimeSeries(key=api_key, output_format='pandas')

ts_data, ts_meta_data = ts.get_daily_adjusted(symbol=ticker, outputsize='full');

# selecting the desired columns

df1 = ts_data['2. high']
df2 = ts_data['4. close']
df3 = ts_data['8. split coefficient']

df1.index = df2.index = df3.index

concatenated_df = pd.concat([df1, df2, df3], axis=1)

# concatenated_df = pd.read_json('buy_and_hold_data.json')


# analysing data for stock split/merge events:
split_day = (concatenated_df.loc[concatenated_df['8. split coefficient'] != 1])
split_date = (split_day.index[0])
split_coefficient = int(split_day['8. split coefficient'])

# then adjust data prior to that entry according to its value.
# a copy of concatenated_df will need to be made,
# and .loc used for accessing and changing data.

new_df = concatenated_df.copy()

post_split_data = new_df[:split_date]

pre_split_data = new_df[split_date:]
# removing the split day so as not to change its value:
pre_split_data = pre_split_data[1:]

pre_split_data.loc[:, '2. high'] = pre_split_data.loc[:, '2. high'] / split_coefficient
pre_split_data.loc[:, '4. close'] = pre_split_data.loc[:, '4. close'] / split_coefficient

frames = [post_split_data, pre_split_data]
result = pd.concat(frames)

# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     print(result)

# reducing dataframe to annual size:
buy_and_hold_data = result[:251]

print(buy_and_hold_data)

# todo: implement logic that finds and saves the maximum value
# from the 'high' column and triggers a buy signal once it is exceeded.
# then

