"""Fetch, cache and normalise price data.

Everything downstream of this module sees the same thing: a DataFrame with
columns open/high/low/close/volume, a timezone-naive DatetimeIndex sorted
oldest-first, and float64 values. Equities and crypto are indistinguishable
by the time they leave here, which is why nothing else in the codebase has
an asset-class branch in it.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import pandas as pd

COLUMNS = ["open", "high", "low", "close", "volume"]

_ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = _ROOT / "data" / "cache"
FIXTURE_DIR = _ROOT / "tests" / "fixtures"

API_KEY_VAR = "ALPHAVANTAGE_API_KEY"

# AlphaVantage prefixes its columns differently on every endpoint:
# "4. close" on equities, "4a. close (USD)" on crypto. Rather than maintain
# three lookup tables, strip the decoration and keep the base name.
_PREFIX = re.compile(r"^\d+[a-z]?\.\s*")
_SUFFIX = re.compile(r"\s*\([A-Z]{3}\)$")


class MissingAPIKey(RuntimeError):
    """Raised when a live fetch is attempted with no API key configured."""


def load(symbol, interval="1d", asset="equity", use_cache=True):
    """Return canonical OHLCV data for `symbol`.

    interval is "1d" for daily bars or an intraday string such as "1min".
    asset is "equity" or "crypto". Results are cached to data/cache so that
    repeated backtests during development do not burn the API rate limit,
    which on AlphaVantage's free tier is easy to do.
    """
    cache = _cache_path(symbol, interval, asset)
    if use_cache and cache.exists():
        return _read_csv(cache)

    frame = _fetch(symbol, interval, asset)
    cache.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(cache)
    return frame


def load_fixture(name="SYNTH_daily"):
    """Load a committed fixture, so the project runs with no API key."""
    path = FIXTURE_DIR / f"{name}.csv"
    if not path.exists():
        available = ", ".join(sorted(p.stem for p in FIXTURE_DIR.glob("*.csv"))) or "none"
        raise FileNotFoundError(f"No fixture named {name!r}. Available: {available}")
    return _read_csv(path)


def _cache_path(symbol, interval, asset):
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", f"{symbol}_{interval}_{asset}")
    return CACHE_DIR / f"{safe}.csv"


def _read_csv(path):
    frame = pd.read_csv(path, index_col=0, parse_dates=True)
    return _finalise(frame)


def _fetch(symbol, interval, asset):
    key = os.environ.get(API_KEY_VAR)
    if not key:
        raise MissingAPIKey(
            f"Set {API_KEY_VAR} to fetch live data, or pass --fixture to run "
            f"against the committed sample data instead."
        )

    if asset == "crypto":
        from alpha_vantage.cryptocurrencies import CryptoCurrencies

        client = CryptoCurrencies(key=key, output_format="pandas")
        raw, _ = client.get_digital_currency_daily(symbol=symbol, market="USD")
        return _normalise(raw)

    from alpha_vantage.timeseries import TimeSeries

    client = TimeSeries(key=key, output_format="pandas")
    if interval == "1d":
        raw, _ = client.get_daily_adjusted(symbol=symbol, outputsize="full")
        return _normalise(_adjust_for_splits(raw))

    raw, _ = client.get_intraday(symbol=symbol, interval=interval, outputsize="full")
    return _normalise(raw)


def _adjust_for_splits(raw):
    """Scale OHLC by the adjusted-close ratio.

    AlphaVantage gives an adjusted close but leaves open/high/low unadjusted,
    so a split shows up as a cliff in three columns out of four. The ratio
    between close and adjusted close is the cumulative adjustment factor, and
    applying it to the other price columns keeps the bar internally consistent.
    """
    columns = {_clean(c): c for c in raw.columns}
    if "adjusted close" not in columns or "close" not in columns:
        return raw

    raw = raw.copy()
    factor = raw[columns["adjusted close"]] / raw[columns["close"]]
    for name in ("open", "high", "low", "close"):
        if name in columns:
            raw[columns[name]] = raw[columns[name]] * factor
    return raw


def _clean(name):
    return _SUFFIX.sub("", _PREFIX.sub("", str(name))).strip().lower()


def _normalise(raw):
    frame = raw.rename(columns=_clean)
    frame = frame.loc[:, ~frame.columns.duplicated()]

    missing = [c for c in COLUMNS if c not in frame.columns]
    if missing:
        raise ValueError(
            f"Provider response is missing {missing}. Got: {sorted(frame.columns)}"
        )

    return _finalise(frame[COLUMNS])


def _finalise(frame):
    """Apply the invariants the rest of the codebase relies on."""
    frame = frame.loc[:, [c for c in COLUMNS if c in frame.columns]].copy()
    frame.index = pd.to_datetime(frame.index)
    if getattr(frame.index, "tz", None) is not None:
        frame.index = frame.index.tz_localize(None)
    frame.index.name = "timestamp"

    frame = frame.astype("float64")
    # Oldest first, always. The old code reversed some datasets and not others,
    # which is an excellent way to backtest a strategy against time running
    # backwards without noticing.
    frame = frame.sort_index()
    frame = frame[~frame.index.duplicated(keep="last")]
    return frame.dropna(subset=["open", "close"])
