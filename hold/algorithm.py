import pandas as pd

buy_and_hold_data = pd.read_json('hold/hold_data.json')

buy_and_hold_data = buy_and_hold_data[::-1]

print(buy_and_hold_data)

historic_high = buy_and_hold_data['4. close'][0]
pos = 0
num = 0
percent_change = []

for i in buy_and_hold_data.index:
    close = buy_and_hold_data['4. close'][i]
    if (close > historic_high):
        historic_high = close
        print("Breakout")
        if (pos == 0):
            buy_price = close
            pos = 1
            print("Buying now at " + str(buy_price))

    elif (close < (historic_high * 0.9)):
        print("Selloff")
        if(pos == 1):
            sell_price = close
            pos = 0
            print("Selling now at " + str(sell_price))
            pc = (sell_price / buy_price - 1) * 100
            percent_change.append(pc)

    if(num == buy_and_hold_data['4. close'].count() - 1 and pos == 1):
        sell_price = close
        pos = 0
        print("Selling now at " + str(sell_price))
        pc = (sell_price / buy_price - 1) * 100
        percent_change.append(pc)

    num += 1

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
print("Test period starting at " + str(buy_and_hold_data.index[0]) + " for a total of " + str(gains_count + losses_count) + " trades.")
print("Gain/Loss Ratio: " + str(ratio))
print("Average Gain: " + str(average_gain))
print("Average Loss: " + str(average_loss))
print("Max Return: " + str(max_return))
print("Max Loss: " + str(max_loss))
print("TOTAL RETURN OVER " + str(gains_count + losses_count) + " TRADES: " + str(total_return) + "%")
print()
