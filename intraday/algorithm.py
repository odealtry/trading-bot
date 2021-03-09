import pandas as pd

intraday_data = pd.read_json('intraday/data/data.json')

intraday_data['buy'] = False
intraday_data['sell'] = False

# print(intraday_data)

# next degree of complexity: timing buy signals to come as the stock is
# regaining momentum, and sell signals as it is losing momentum.
# revisit dynamic lookback
# revisit moglen's red white blue strategy.
# experiment with sma rather than ema (This may require
# a separate directory/file structure)


class Algorithm:
    def __init__(self, dataset):
        self.dataset = dataset
        self.pos = 0
        self.num = 0
        self.percent_change = []
        self.sell_price = 0

    def evaluate(self):
        for i in self.dataset.index:
            self.close = self.dataset['4. close'][i]
            self.ema = self.dataset['EMA'][i]
            if self.pos == 0:
                self.buy_evaluation(i)
            elif self.pos == 1:
                self.sell_evaluation(i)
            if((self.num == self.dataset['4. close'].count() - 1 and self.pos == 1) or ()):
                self.sell_price = self.close
                self.pos = 0
                print("Selling now at " + str(self.sell_price))
                pc = (self.sell_price / self.buy_price - 1) * 100
                self.percent_change.append(pc)
                self.performance_calculation()

            self.num += 1

    def buy_evaluation(self, i):
        if(self.close < (self.ema * 0.965)):
            print("UNDERVALUED: Close: " + str(self.close) + "  EMA: " + str(self.ema))
            self.buy_price = self.close
            self.pos = 1
            self.dataset['buy'][i] = True
            print("Buying now at " + str(self.buy_price))

    def sell_evaluation(self, i):
        if(self.close > (self.ema * 1.035)):
            print("OVERVALUED: Close: " + str(self.close) + "  EMA: " + str(self.ema))
            self.sell(i)
        elif(self.stop_loss(i) == True):
            print("STOP LOSS: Close: " + str(self.close) + "  EMA: " + str(self.ema))
            self.sell(i)

    def stop_loss(self, i):
        self.pc = (self.close / self.buy_price - 1) * 100
        if self.pc < -3:
            return(True)

    def sell(self, i):
        self.sell_price = self.close
        self.pos = 0
        self.dataset['sell'][i] = True
        self.pc = (self.sell_price / self.buy_price - 1) * 100
        self.percent_change.append(self.pc)
        print("Selling now at " + str(self.sell_price) + " , percent change of " + str(self.pc))


    def performance_calculation(self):
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

        self.total_return = round((self.total_return - 1) * 100, 2)

        if(self.gains_count > 0):
            self.average_gain = self.gains / self.gains_count
            self.max_return = str(max(self.percent_change))
        else:
            self.average_gain = 0
            self.max_return = "none"

        if(self.losses_count > 0):
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

algo = Algorithm(intraday_data)

algo.evaluate()

algo.performance_calculation()

evaluated_data = algo.dataset

# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     print(evaluated_data)

evaluated_data.to_json(path_or_buf='intraday/data/data_with_buys.json')

print("Records of stock purchases and sales passed back to json")


