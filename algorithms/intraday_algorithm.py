import pandas as pd
import numpy as np

intraday_data = pd.read_json('data/intraday_data.json')

intraday_data = intraday_data[::-1]

# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     print(intraday_data)

print(intraday_data)

for i in intraday_data.index:
    close = intraday_data['4. close'][i]
    ema = intraday_data['EMA'][i]
    # if(close > ema):

print(close)
print(ema)
