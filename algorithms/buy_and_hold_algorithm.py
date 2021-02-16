import pandas as pd

buy_and_hold_data = pd.read_json('data/buy_and_hold_data.json')

# todo: implement logic that finds and saves the maximum value
# from the 'high' column and triggers a buy signal once it is exceeded.
# then

print(buy_and_hold_data)

max_entry = buy_and_hold_data.loc[buy_and_hold_data['4. close'].idxmax()]

max_close = max_entry['4. close']

# compare today's to all-time.
# if today's is highest, check if the stock is already in holdings.
# if it is not, trigger the buy method of a new purchase file,
# passing the stock ticker as an arg.
# the logic for logging this purchase in holdings
# can go in a separate file.

print(max_entry)

print(max_close)

class StockEvaluation(stock):
