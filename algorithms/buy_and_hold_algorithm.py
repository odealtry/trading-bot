import pandas as pd

buy_and_hold_data = pd.read_json('data/buy_and_hold_data.json')

# todo: implement logic that finds and saves the maximum value
# from the 'high' column and triggers a buy signal once it is exceeded.
# then

# print(buy_and_hold_data)

buy_and_hold_data = buy_and_hold_data[::-1]

# print(buy_and_hold_data)

# max_entry = buy_and_hold_data.loc[buy_and_hold_data['4. close'].idxmax()]

# max_close = max_entry['4. close']

# compare today's to all-time.
# if today's is highest, check if the stock is already in holdings.
# if it is not, trigger the buy method of a new purchase file,
# passing the stock ticker as an arg.
# the logic for logging this purchase in holdings
# can go in a separate file.

historic_high = 0
pos = 0
num = 0
percent_change = []

for i in buy_and_hold_data.index:
    close = buy_and_hold_data['4. close'][i]
    if (close > historic_high):
        historic_high = close
        print("Breakout")
        if (pos == 0):
            bp = close
            pos = 1
            print("Buying now at " + str(bp))

    elif (close < historic_high):
        print("Selloff")
        if(pos == 1):
            sp = close
            pos = 0
            print("Selling now at " + str(sp))
            pc = (sp / bp - 1) * 100
            percent_change.append(pc)
    if(num == buy_and_hold_data['4. close'].count() - 1 and pos == 1):
        sp = close
        pos = 0
        print("Selling now at " + str(sp))
        pc = (sp / bp - 1) * 100
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

if(gains_count > 0 or losses_count > 0):
    batting_average = gains_count / (gains_count + losses_count)
else:
    batting_average = 0


print()
print("Test period starting" + str(buy_and_hold_data.index[0]) + ", having executed " + str(gains_count + losses_count) + " trades.")
print("Batting Average: " + str(batting_average))
print("Gain/Loss Ratio: " + str(ratio))
print("Average Gain: " + str(average_gain))
print("Average Loss: " + str(average_loss))
print("Max Return: " + str(max_return))
print("Max Loss: " + str(max_loss))
print("TOTAL RETURN OVER " + str(gains_count + losses_count) + " TRADES: " + str(total_return) + "%")
print()
