import intraday_pull
import pandas as pd

intraday_data = intraday_pull.intraday_data

intraday_data.to_json(path_or_buf='intraday/data/data.json')

# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
