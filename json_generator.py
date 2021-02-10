import moving_average_calculation
import pandas as pd

moving_average_calculation.concatenated_df.to_json(path_or_buf='AAPL_data.json')

dataframe = pd.read_json('AAPL_data.json')

close_prices = dataframe['4. close']

final_day_price = close_prices[-16:]

penultimate_day_price = close_prices[-32:-16]

print(dataframe)
