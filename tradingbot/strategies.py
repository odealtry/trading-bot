"""Strategies: pure functions from prices to target positions.

A strategy takes a canonical OHLCV frame and returns a Series of 0 or 1
aligned to the same index, meaning "I want to be flat here" or "I want to be
long here". It does not know what a trade is, what money is, or whether it is
being backtested or plotted. That keeps it testable and keeps the interesting
decisions about fills and costs in one place: the engine.

Nothing here reads a file, prints, or holds state between calls.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def _hysteresis(enter, exit_):
    """Build a target position from separate entry and exit conditions.

    Mean reversion needs two thresholds rather than one: buy when price falls
    a long way below the average, sell when it rises a long way above, and sit
    still in between. That middle zone means the target depends on which
    threshold was crossed most recently, which a single comparison cannot
    express. Marking the crossings and forward-filling resolves it in one pass
    and with no loop.
    """
    state = pd.Series(np.nan, index=enter.index, dtype="float64")
    state[enter.to_numpy()] = 1.0
    state[exit_.to_numpy()] = 0.0
    return state.ffill().fillna(0.0).astype(int)


def ema_reversion(df, period=60, band=0.02):
    """Long when price falls `band` below its exponential moving average.

    The original intraday strategy. Buys weakness against a one-hour EMA on
    minute bars and sells the corresponding strength.
    """
    ema = df["close"].ewm(span=period, adjust=False).mean()
    return _hysteresis(df["close"] < ema * (1 - band), df["close"] > ema * (1 + band))


def sma_reversion(df, window=3, band=0.02):
    """Long when price falls `band` below its simple moving average.

    The original crypto strategy. Same idea as ema_reversion with a shorter,
    unweighted average, kept separate so the two can be compared directly.
    """
    sma = df["close"].rolling(window=window).mean()
    return _hysteresis(df["close"] < sma * (1 - band), df["close"] > sma * (1 + band))


def breakout(df, lookback=None, drawdown=0.10):
    """Long while price holds within `drawdown` of its running high.

    The original buy-and-hold strategy. Its exit rule was described as a stop
    loss, but a stop measured against the high rather than the entry is a
    trailing stop, and a trailing stop stated as a target position is simply
    "long while we have not given back more than 10 percent of the peak". That
    re-arms by itself on the next recovery, so it needs no separate exit path.

    lookback of None uses the all-time high; an integer uses a rolling window,
    which suits volatile assets where an all-time high may be years stale.
    """
    close = df["close"]
    high_water = close.cummax() if lookback is None else close.rolling(lookback, min_periods=1).max()
    return (close >= high_water * (1 - drawdown)).astype(int)


STRATEGIES = {
    "ema": ema_reversion,
    "sma": sma_reversion,
    "breakout": breakout,
}
