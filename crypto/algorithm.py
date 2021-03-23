import pandas as pd
from alpha_vantage.cryptocurrencies import CryptoCurrencies
import config


api_key = config.AlphaVantageAPIKey

crypto = CryptoCurrencies(key=api_key, output_format='pandas')
crypto_data, crypto_meta_data = crypto.get_digital_currency_daily(symbol='BTC', market='USD')
print(crypto_data)
