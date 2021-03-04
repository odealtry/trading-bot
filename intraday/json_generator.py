import intraday_pull
import pandas as pd

intraday_pull.intraday_data.to_json(path_or_buf='intraday/intraday_data.json')
