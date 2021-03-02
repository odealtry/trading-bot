import pandas as pd
import numpy as np
import datetime as dt

intraday_data = pd.read_json('data/intraday/intraday_data.json')

intraday_data = intraday_data[::-1]

print(intraday_data)

pos = 0
num = 0
percent_change = []

# to plot buy/sell signals against stock info, I need to persist
# information at the moment the signal is generated.
# For the moment, try appending df rows to a list.
# create two dfs of buy and sell signals, and save them to
# new data jsons.

buys = []
buy_times = []
sells = []
sell_times = []

for i in intraday_data.index:
    close = intraday_data['4. close'][i]
    ema = intraday_data['EMA'][i]

    if(close < (ema * 0.99)):
        print("Undervalued")
        if(pos == 0):
            buy_price = close
            pos = 1
            print("Buying now at " + str(buy_price))
            buys.append(close)
            buy_times.append(i)

    elif(close > (ema * 1.01)):
        print("Uptick")
        if(pos == 1):
            sell_price = close
            pos = 0
            print("Selling now at " + str(sell_price))
            pc = (sell_price / buy_price - 1) * 100
            percent_change.append(pc)
            sells.append(close)
            sell_times.append(i)

    if(num == intraday_data['4. close'].count() - 1 and pos == 1):
        sell_price = close
        pos = 0
        print("Selling now at " + str(sell_price))
        pc = (sell_price / buy_price - 1) * 100
        percent_change.append(pc)

    num += 1

print(percent_change)

gains = 0
gains_count = 0
losses = 0
losses_count = 0
total_return = 1

for i in percent_change:
    if (i > 0):
        gains += i
        gains_count += 1
    else:
        losses += i
        losses_count += 1
    total_return = total_return * ((i / 100) + 1)

total_return = round((total_return - 1) * 100, 2)

if(gains_count > 0):
    average_gain = gains / gains_count
    max_return = str(max(percent_change))
else:
    average_gain = 0
    max_return = "none"

if(losses_count > 0):
    average_loss = losses / losses_count
    max_loss = str(min(percent_change))
    ratio = str(-average_gain / average_loss)
else:
    average_loss = 0
    max_loss = "none"
    ratio = "infinite"


print()
print("Test period starting at " + str(intraday_data.index[0]) + " for a total of " + str(gains_count + losses_count) + " trades.")
print("Gain/Loss Ratio: " + str(ratio))
print("Average Gain: " + str(average_gain))
print("Average Loss: " + str(average_loss))
print("Max Return: " + str(max_return))
print("Max Loss: " + str(max_loss))
print("TOTAL RETURN OVER " + str(gains_count + losses_count) + " TRADES: " + str(total_return) + "%")
print()
print()

buy_index = pd.Index(buy_times)
sell_index = pd.Index(sell_times)

buys = pd.DataFrame(buys, index=[buy_index], columns=['close'])
sells = pd.DataFrame(sells, index=[sell_index], columns=['close'])

print(buys)
print(sells)

buys.to_json(path_or_buf='data/intraday/intraday_buys.json')
sells.to_json(path_or_buf='data/intraday/intraday_sells.json')






























