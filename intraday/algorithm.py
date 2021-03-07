import pandas as pd

intraday_data = pd.read_json('intraday/data/data.json')

# intraday_data = intraday_data[::-1]

intraday_data['buy'] = False
intraday_data['sell'] = False

print(intraday_data)

pos = 0
num = 0
percent_change = []


# I need to establish definitively that the algorithm isn't obtaining
# an unfair advantage that is boosting its performance.
# I am suspicious of the ema: specifically, that it is
# accessing information from the future in calculating
# its average - see buys at market close that are triggered
# when the ema reflects the following morning's prices.

for i in intraday_data.index:
    close = intraday_data['4. close'][i]
    ema = intraday_data['EMA'][i]

    if(close < (ema * 0.99)):
        if(pos == 0):
            print("UNDERVALUED: Close: " + str(close) + "  EMA: " + str(ema))
            buy_price = close
            pos = 1
            intraday_data['buy'][i] = True
            print("Buying now at " + str(buy_price))

    elif(close > (ema * 1.01)):
        if(pos == 1):
            print("OVERVALUED: Close: " + str(close) + "  EMA: " + str(ema))
            sell_price = close
            pos = 0
            intraday_data['sell'][i] = True
            pc = (sell_price / buy_price - 1) * 100
            percent_change.append(pc)
            print("Selling now at " + str(sell_price) + " , percent change of " + str(pc))

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

intraday_data.to_json(path_or_buf='intraday/data/data_with_buys.json')

print("Records of stock purchases and sales passed back to json")

# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     print(intraday_data)
