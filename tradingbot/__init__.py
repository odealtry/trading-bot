"""A small, honest backtesting engine.

Four layers, each usable on its own:

    data       fetch, cache and normalise prices into one canonical shape
    strategies pure functions from prices to target positions
    engine     execution, costs, risk rules, equity curve
    metrics    performance statistics from an equity curve
"""

__version__ = "2.0.0"

from tradingbot.engine import Costs, Risk, Result, Trade, run
from tradingbot.strategies import STRATEGIES

__all__ = ["Costs", "Risk", "Result", "Trade", "run", "STRATEGIES", "__version__"]
