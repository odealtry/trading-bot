# trading-bot

*A rudimentary trading bot that accesses data from the AlphaVantage API, saves pandas dataframes to JSON format, and simulates daily stock analysis by performing iterative calculations on the resulting data structures. Two strategies are used: Intraday and Buy and Hold.*


## pull
The pull folder contains code that accesses and reorganises stock information, using [Romel Torres'](https://github.com/RomelTorres) [AlphaVantage Python wrapper](https://github.com/RomelTorres/alpha_vantage). In the case of the Buy and Hold strategy, this involved restrospectively adjusting close prices prior to stock split/merge events. I did this using AlphaVantage's split coefficient after learning that their adjusted close information isn't 100% reliable.

## data
While testing my code I often found that I exceeded the maximum number of API calls for a certain period. This is why I created json_generator.py, which uses the information pulled from the API to write two JSON files that can then be used for my algorithms, eliminating the need to rely on repeated API calls during development. 

## algorithms
**Buy and Hold**
This strategy detects and purchases when a stock is breaking out of its historic high in order to take advantage of price momentum. A 'stop loss' sell signal is triggered when the close is 10% below the historic high. This strategy is very imprecise, and is susceptible to buying high and selling low. Further work is needed to adjust the lookback length according to volatility.

**Intraday**
This strategy compares the stock price to an hourly exponential moving average on a minute by minute basis, buying if the close goes under the EMA and selling when the close exceeds the EMA. This high frequency-style strategy benefits from greater precision, both in obtaining up-to-date stock information, and accessing the EMA, a more sophisticated metric of a stock's current value. This strategy has yielded some interesting initial results.

##
Please get in touch if you have any suggestions for ways to improve my strategies - I'd love to collaborate!

This project draws on information from numerous different sources, but special thanks are due to [Richard Moglen](https://www.youtube.com/channel/UCYqMAKiU3tFijWnyqAxG4Cg), [Derrick Sherrill](https://www.youtube.com/channel/UCJHs6RO1CSM85e8jIMmCySw), and [Trade Options With Me](https://www.youtube.com/channel/UCb0_-wF6yzHvjwkngWwBVTw), whose channels have been invaluable in putting me on the right path.

**Disclaimer - this is not a viable trading bot. Do not use this code to make real life trading decisions.**
