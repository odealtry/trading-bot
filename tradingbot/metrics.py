"""Performance statistics.

Everything here is a pure function of an equity curve or a trade list, which
is why the strategy, the benchmark and any future variant can all be measured
by the same code. The old version could only report the average of a list of
percentage changes, which ignores time spent in cash and cannot express
drawdown at all.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

SECONDS_PER_YEAR = 365.25 * 24 * 60 * 60
MIN_YEARS_FOR_CAGR = 1.0 / 365.25


def summarise(result):
    """Return a flat dict of statistics for a Result."""
    stats = curve_stats(result.equity)
    stats.update(trade_stats(result.trades))
    stats["exposure"] = float(result.position.mean())

    benchmark = curve_stats(result.benchmark)
    stats["benchmark_total_return"] = benchmark["total_return"]
    stats["benchmark_cagr"] = benchmark["cagr"]
    stats["benchmark_max_drawdown"] = benchmark["max_drawdown"]
    stats["excess_return"] = stats["total_return"] - benchmark["total_return"]
    return stats


def curve_stats(equity):
    """Statistics derived from an equity curve indexed by time."""
    equity = equity.dropna()
    if equity.empty:
        return {
            "total_return": float("nan"),
            "cagr": float("nan"),
            "max_drawdown": float("nan"),
            "sharpe": float("nan"),
        }

    final = float(equity.iloc[-1])
    years = _years(equity.index)

    # Annualising a span shorter than a day says nothing useful and overflows
    # long before it says anything misleading, so refuse rather than report it.
    if years >= MIN_YEARS_FOR_CAGR and final > 0:
        cagr = final ** (1.0 / years) - 1.0
    else:
        cagr = float("nan")

    returns = equity.pct_change().dropna()
    std = float(returns.std())
    if len(returns) > 1 and std > 0:
        sharpe = float(returns.mean()) / std * math.sqrt(_periods_per_year(equity.index))
    else:
        sharpe = float("nan")

    return {
        "total_return": final - 1.0,
        "cagr": cagr,
        "max_drawdown": float((equity / equity.cummax() - 1.0).min()),
        "sharpe": sharpe,
    }


def trade_stats(trades):
    """Statistics derived from a list of closed trades."""
    if not trades:
        return {
            "num_trades": 0,
            "win_rate": float("nan"),
            "avg_win": float("nan"),
            "avg_loss": float("nan"),
            "payoff_ratio": float("nan"),
            "exit_reasons": {},
        }

    returns = np.array([t.return_pct for t in trades], dtype="float64")
    wins, losses = returns[returns > 0], returns[returns <= 0]

    avg_win = float(wins.mean()) if wins.size else float("nan")
    avg_loss = float(losses.mean()) if losses.size else float("nan")
    payoff = abs(avg_win / avg_loss) if losses.size and avg_loss != 0 else float("nan")

    reasons = {}
    for trade in trades:
        reasons[trade.exit_reason] = reasons.get(trade.exit_reason, 0) + 1

    return {
        "num_trades": len(trades),
        "win_rate": float(wins.size / returns.size),
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "payoff_ratio": payoff,
        "exit_reasons": reasons,
    }


def _years(index):
    span = (index[-1] - index[0]).total_seconds()
    return span / SECONDS_PER_YEAR if span > 0 else 0.0


def _periods_per_year(index):
    """Infer bars per year from the median gap between bars.

    This is what lets one Sharpe calculation serve both minute bars and daily
    bars without being told which it is looking at.
    """
    if len(index) < 3:
        return 252.0
    stamps = np.asarray(index, dtype="datetime64[ns]").astype("int64")
    median = float(np.median(np.diff(stamps))) / 1e9
    if median <= 0:
        return 252.0
    return SECONDS_PER_YEAR / median
