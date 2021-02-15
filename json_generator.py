import buy_and_hold_pull
import intraday_pull
import pandas as pd
import sys

buy_and_hold_pull.concatenated_df.to_json(path_or_buf='buy_and_hold_data.json')

