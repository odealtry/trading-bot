import pandas as pd
from alpha_vantage.cryptocurrencies import CryptoCurrencies
import config


api_key = config.AlphaVantageAPIKey

crypto_symbol = input("Please enter a cryptocurrency symbol: ")

crypto = CryptoCurrencies(key=api_key, output_format='pandas')
crypto_data, crypto_meta_data = crypto.get_digital_currency_daily(symbol=crypto_symbol, market='USD')
print(crypto_meta_data)

# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
print(crypto_data)

crypto_data = crypto_data['4a. close (USD)']

print(crypto_data)
