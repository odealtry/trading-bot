import pandas as pd
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
import sys
import config
# import AAPL_data.json

# ticker = str(sys.argv[1])

# api_key = config.AlphaVantageAPIKey

# ts = TimeSeries(key=api_key, output_format='pandas')

# data, meta_data = ts.get_intraday(symbol=ticker, interval='60min', outputsize='full');

# # calculating simple moving average from a period of 20 days
# period = 480

# ti = TechIndicators(key=api_key, output_format='pandas')

# ti_data, ti_meta_data = ti.get_sma(symbol=ticker, interval='60min',
#                         time_period=period, series_type='close')

# df1 = ti_data
# # equalising dataframe sizes as ti_data needs the first period for calculation
# df2 = data['4. close'].iloc[period-1::]

# df2.index = df1.index

# concatenated_df = pd.concat([df1, df2], axis=1)

# concatenated_df.to_json(path_or_buf='AAPL_data.json')

# The above was used to access data from the alphavantage API and store that data in a JSON file.
# We can now use this JSON to develop the volatility analysis component of the bot independent of the API.

dataframe = pd.read_json('AAPL_data.json')

close_prices = dataframe['4. close']

# data for monday the 8th Feb 2021:
final_day_price = close_prices[-16:]

# data for friday the 5th Feb 2021:
penultimate_day_price = close_prices[-32:-16]

print(final_day_price, penultimate_day_price)
