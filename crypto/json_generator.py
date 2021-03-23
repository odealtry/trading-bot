import pull
import pandas as pd

crypto_data = pull.crypto_data

crypto_data.to_json(path_or_buf='crypto/data/data.json')

# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
