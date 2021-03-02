import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime

intraday_data = pd.read_json('data/intraday/intraday_data.json')
intraday_buys = pd.read_json('data/intraday/intraday_buys.json')
intraday_sells = pd.read_json('data/intraday/intraday_sells.json')

# print(intraday_data)

# intraday_data.plot()
# plt.title('Intraday Times Series for TSLA (1 min)')
# plt.show()

# print(intraday_data)
# print(intraday_buys)
# print(intraday_sells)


for i in intraday_buys.index:
    print(i)
    i.replace('0', 'fiftee ', inplace = True)
    print(i)


# "(Timestamp('2021-02-26 15:10:00'),)"

# for i in intraday_sells.index:
#     i = datetime.datetime.strptime(i, '%Y-%m-%d %H:%M:%S')


# print(intraday_buys)
# print(intraday_sells)
