import pandas as pd
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
import sys
import config

ticker = str(sys.argv[1])

api_key = config.AlphaVantageAPIKey

ts = TimeSeries(key=api_key, output_format='pandas')

data, meta_data = ts.get_intraday(symbol=ticker, interval='60min', outputsize='full');

# calculating simple moving average from a period of 20 days
period = 10

ti = TechIndicators(key=api_key, output_format='pandas')

ti_data, ti_meta_data = ti.get_sma(symbol=ticker, interval='60min',
                        time_period=period, series_type='close')

df1 = ti_data
# equalising dataframe sizes as ti_data needs the first period for calculation
df2 = data['4. close'].iloc[period-1::]

df2.index = df1.index

concatenated_df = pd.concat([df1, df2], axis=1)

# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     print(dataframe)

# print(final_day_price, penultimate_day_price)
# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     print(concatenated_df)
