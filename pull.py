import pandas
from alpha_vantage.timeseries import TimeSeries
import sys
import random
import config

ticker = str(sys.argv[1])

api_key = open('.gitignore').read().splitlines()[0]

time = TimeSeries(key=config.AlphaVantageAPIKey, output_format='pandas')

data = time.get_intraday(symbol=ticker, interval='30min', outputsize='full');

print(ticker)
print(data)
