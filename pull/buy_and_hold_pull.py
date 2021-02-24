# This file pulls daily closes and highs and
# retroactively adjusts values in the event of a
# stock split or merge.

import pandas as pd
from alpha_vantage.timeseries import TimeSeries
import config

class BuyAndHoldPull:
    def __init__(self, ticker):
        self.ticker = ticker
        self.data = pd.DataFrame

    def Pull(self):
        api_key = config.AlphaVantageAPIKey
        ts = TimeSeries(key=api_key, output_format='pandas')
        ts_data, ts_meta_data = ts.get_daily_adjusted(symbol=self.ticker, outputsize='full');
        # selecting the desired columns
        df1 = ts_data['2. high']
        df2 = ts_data['4. close']
        df3 = ts_data['8. split coefficient']
        df1.index = df2.index = df3.index
        concatenated_df = pd.concat([df1, df2, df3], axis=1)
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
        self.data = result


# buy_and_hold_data = pd.read_json('data/buy_and_hold_data.json')

tsla = BuyAndHoldPull('TSLA')
tsla.Pull()

buy_and_hold_data = tsla.data

print(buy_and_hold_data)
# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     print(buy_and_hold_data)
