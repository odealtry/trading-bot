import pandas as pd
import matplotlib.pyplot as plt

crypto_data = pd.read_json('crypto/data/data_with_buys.json')

# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     print(intraday_data)

# print(intraday_data)

buys = []
sells =[]

for i in crypto_data.index:
    if crypto_data['buy'][i] == True:
        buys.append(i)
    elif crypto_data['sell'][i] == True:
        sells.append(i)

crypto_data.plot()
plt.title('SMA vs Close, annotated with Buys and Sells made by trading-bot')

for date in buys:
    label = 'Buy'
    plt.annotate(label, xy=(date, crypto_data['close'][date]),
       xycoords='data', xytext=(-3, -45), textcoords='offset points',
       arrowprops=dict(facecolor='green', shrink=0.05, width=0.5, headwidth=4),
       horizontalalignment='right', verticalalignment='bottom')

for date in sells:
    label = 'Sell'
    plt.annotate(label, xy=(date, crypto_data['close'][date]),
       xycoords='data', xytext=(3, 30), textcoords='offset points',
       arrowprops=dict(facecolor='red', shrink=0.05, width=0.5, headwidth=4),
       horizontalalignment='right', verticalalignment='bottom')

plt.show()
