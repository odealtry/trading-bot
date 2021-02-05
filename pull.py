import pandas
from alpha_vantage.timeseries import TimeSeries
import sys
import random

ticker = str(sys.argv[1])

api_key = open('.gitignore').read().splitlines()[0]

time = TimeSeries(key=api_key, output_format='pandas')

data = time.get_intraday(symbol=ticker, interval='1min', outputsize='full');

print(ticker)
print(data)
