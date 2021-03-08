import pandas as pd

intraday_data = pd.read_json('intraday/data/data.json')

intraday_data['buy'] = False
intraday_data['sell'] = False

print(intraday_data)

# Algorithm class should have an evaluate function that:
# iterates through the datatset;
# redirects depending on whether pos == 0;
# recreates buy and sell logic in separate functions,
# triggering signals if all conditions evaluate to true.

class Algorithm:
    def __init__(dataset):
        self.dataset = dataset
        self.pos = 0
        self.num = 0
        self.percent_change = []

    def evaluate:
        for i in self.dataset.index:
            self.close = self.dataset['4. close'][i]
            self.ema = self.dataset['EMA'][i]
            if self.pos == 0:
                buy_evaluation(self.close, self.ema)
            elif self.pos == 1:
                sell_evaluation(self.close, self.ema)
            if(self.num == self.dataset['4. close'].count() - 1 and self.pos == 1):
                sell_price = close
                self.pos = 0
                print("Selling now at " + str(sell_price))
                pc = (sell_price / buy_price - 1) * 100
                self.percent_change.append(pc)

            self.num += 1

    def buy_evaluation(close, ema):
        if(close < (ema * 0.99)):
            print("UNDERVALUED: Close: " + str(close) + "  EMA: " + str(ema))
            self.buy_price = close
            self.pos = 1
            self.dataset['buy'][i] = True
            print("Buying now at " + str(buy_price))

    def sell_evaluation(close, ema):
        if(close > (ema * 1.01)):
            print("OVERVALUED: Close: " + str(close) + "  EMA: " + str(ema))
            self.sell_price = close
            self.pos = 0
            self.dataset['sell'][i] = True
            self.pc = (sell_price / buy_price - 1) * 100
            self.percent_change.append(self.pc)
            print("Selling now at " + str(self.sell_price) + " , percent change of " + str(self.pc))

    def performance_calculation:
        self.gains = 0
        self.gains_count = 0
        self.losses = 0
        self.losses_count = 0
        self.total_return = 1
        print(self.percent_change)






for i in self.percent_change:
    if (i > 0):
        self.gains += i
        self.gains_count += 1
    else:
        self.losses += i
        self.losses_count += 1
    self.total_return = self.total_return * ((i / 100) + 1)

total_return = round((total_return - 1) * 100, 2)

if(gains_count > 0):
    self.average_gain = self.gains / self.gains_count
    self.max_return = str(max(self.percent_change))
else:
    self.average_gain = 0
    self.max_return = "none"

if(losses_count > 0):
    self.average_loss = self.losses / self.losses_count
    self.max_loss = str(min(self.percent_change))
    self.ratio = str(-(self.average_gain) / self.average_loss)
else:
    self.average_loss = 0
    self.max_loss = "none"
    self.ratio = "infinite"


print()
print("Test period starting at " + str(self.dataset.index[0]) + " for a total of " + str(self.gains_count + self.losses_count) + " trades.")
print("Gain/Loss Ratio: " + str(self.ratio))
print("Average Gain: " + str(self.average_gain))
print("Average Loss: " + str(self.average_loss))
print("Max Return: " + str(self.max_return))
print("Max Loss: " + str(self.max_loss))
print("TOTAL RETURN OVER " + str(self.gains_count + self.losses_count) + " TRADES: " + str(self.total_return) + "%")
print()
print()

intraday_data.to_json(path_or_buf='intraday/data/data_with_buys.json')

print("Records of stock purchases and sales passed back to json")

# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     print(intraday_data)
