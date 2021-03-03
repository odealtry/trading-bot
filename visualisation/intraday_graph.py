import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime

intraday_data = pd.read_json('data/intraday/intraday_data.json')


# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     print(intraday_data)

# print(intraday_data)

# intraday_data.plot()
# plt.title('Intraday Times Series for TSLA (1 min)')
# plt.show()

buys = []
sells =[]

for i in intraday_data.index:
    if intraday_data['buy'][i] == True:
        buys.append(i)
    elif intraday_data['sell'][i] == True:
        sells.append(i)

print(buys)
print(sells)
