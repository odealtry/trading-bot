import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

intraday_data = pd.read_json('data/intraday_data.json')

# print(intraday_data)

intraday_data.plot()
plt.title('Intraday Times Series for TSLA (1 min)')
plt.show()
