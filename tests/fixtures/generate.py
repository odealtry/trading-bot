"""Regenerate the committed sample data.

    python tests/fixtures/generate.py

The fixtures are synthetic and clearly labelled as such. They exist so that
anyone can clone the repository and get a complete backtest, with a chart,
without an API key and without waiting on a rate limit. They are generated
from a fixed seed, so the numbers in the README stay reproducible.

To backtest real prices, set ALPHAVANTAGE_API_KEY and drop the --fixture flag.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent


def make_ohlcv(n, start, freq, seed, drift, vol, level=100.0):
    """Build a plausible OHLCV series from a seeded geometric random walk."""
    rng = np.random.default_rng(seed)

    steps = rng.normal(drift, vol, size=n)
    close = level * np.exp(np.cumsum(steps))

    # Open gaps slightly from the previous close; the high and low bracket
    # both, so every bar is internally consistent.
    prev_close = np.concatenate([[level], close[:-1]])
    open_ = prev_close * np.exp(rng.normal(0.0, vol * 0.3, size=n))

    span = np.abs(rng.normal(0.0, vol * 0.8, size=n))
    high = np.maximum(open_, close) * np.exp(span)
    low = np.minimum(open_, close) * np.exp(-span)
    volume = rng.integers(1_000_000, 20_000_000, size=n).astype("float64")

    index = pd.date_range(start=start, periods=n, freq=freq, name="timestamp")
    return pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": volume},
        index=index,
    ).round(4)


def main():
    daily = make_ohlcv(
        n=1200, start="2020-01-02", freq="B", seed=20200102, drift=0.0004, vol=0.016
    )
    daily.to_csv(HERE / "SYNTH_daily.csv")

    minute = make_ohlcv(
        n=3000, start="2024-06-03 09:30", freq="min", seed=20240603,
        drift=0.000002, vol=0.0009, level=250.0,
    )
    minute.to_csv(HERE / "SYNTH_1min.csv")

    for name, frame in (("SYNTH_daily", daily), ("SYNTH_1min", minute)):
        print(
            f"{name}: {len(frame):,} bars, "
            f"{frame.index[0]:%Y-%m-%d %H:%M} to {frame.index[-1]:%Y-%m-%d %H:%M}, "
            f"close {frame['close'].iloc[0]:.2f} -> {frame['close'].iloc[-1]:.2f}"
        )


if __name__ == "__main__":
    main()
