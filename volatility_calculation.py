from alpha_vantage.timeseries import TimeSeries
import sys
import config

api_key = config.AlphaVantageAPIKey

ts = TimeSeries(key=api_key, output_format='pandas')

ticker = str(sys.argv[1])

data, meta_data = ts.get_daily(symbol=ticker,
                                    outputsize='compact');

print(data)
