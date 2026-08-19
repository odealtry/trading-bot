"""The execution engine.

Takes prices and a target position, returns a trade ledger and an equity
curve. Three rules are enforced here rather than left to the discipline of
whoever writes the next strategy:

1. Everything observed at the close of bar i executes at the open of bar
   i + 1. A strategy cannot trade on information it would not have had,
   because it never gets the chance to.
2. Every fill pays commission and slippage.
3. A buy-and-hold benchmark runs over the same bars, through the same code,
   with the same costs. A return with nothing to compare it against is not
   a result.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import numpy as np
import pandas as pd

SIGNAL = "signal"
STOP_LOSS = "stop_loss"
TAKE_PROFIT = "take_profit"
TRAILING_STOP = "trailing_stop"
END_OF_DATA = "end_of_data"


@dataclass(frozen=True)
class Costs:
    """Per-side trading costs in basis points. One basis point is 0.01%.

    Commission and slippage are charged together as an effective spread: buys
    fill above the quoted price and sells below it. The defaults are realistic
    for retail equities and are deliberately not zero, because a strategy that
    only works at zero cost does not work.
    """

    commission_bps: float = 5.0
    slippage_bps: float = 2.0

    @property
    def one_way(self):
        return (self.commission_bps + self.slippage_bps) / 10_000.0

    def buy_price(self, price):
        return price * (1.0 + self.one_way)

    def sell_price(self, price):
        return price * (1.0 - self.one_way)


@dataclass(frozen=True)
class Risk:
    """Exit rules applied to every strategy alike.

    These live in the engine rather than in strategy code because they are
    path dependent: they need the entry price and the peak since entry, which
    a stateless target position has no way to know. Keeping them here also
    means every strategy gets identical semantics, and any of them can be
    switched off to see whether it was earning its keep.
    """

    stop_loss_pct: Optional[float] = None
    take_profit_pct: Optional[float] = None
    trailing_stop_pct: Optional[float] = None

    @property
    def active(self):
        return any(
            v is not None
            for v in (self.stop_loss_pct, self.take_profit_pct, self.trailing_stop_pct)
        )


@dataclass(frozen=True)
class Trade:
    entry_time: pd.Timestamp
    entry_price: float
    exit_time: pd.Timestamp
    exit_price: float
    return_pct: float
    exit_reason: str


@dataclass(frozen=True)
class Result:
    equity: pd.Series
    benchmark: pd.Series
    position: pd.Series
    trades: List[Trade]
    prices: pd.DataFrame
    signals: pd.Series
    costs: Costs
    risk: Risk


def run(prices, signals, costs=None, risk=None):
    """Backtest `signals` over `prices` and return a Result."""
    costs = costs if costs is not None else Costs()
    risk = risk if risk is not None else Risk()

    if not isinstance(prices, pd.DataFrame) or prices.empty:
        raise ValueError("prices must be a non-empty DataFrame")
    for column in ("open", "close"):
        if column not in prices.columns:
            raise ValueError(f"prices is missing the {column!r} column")

    signals = (
        pd.Series(signals, index=prices.index)
        .reindex(prices.index)
        .fillna(0)
        .clip(0, 1)
        .astype(int)
    )

    equity, position, trades = _simulate(prices, signals, costs, risk)

    # The benchmark goes through the identical code path with an always-long
    # target and no risk rules, so it inherits the same one-bar execution lag
    # and the same costs. Anything else would be quietly flattering.
    always_long = pd.Series(1, index=prices.index, dtype=int)
    benchmark, _, _ = _simulate(prices, always_long, costs, Risk())

    return Result(
        equity=equity,
        benchmark=benchmark,
        position=position,
        trades=trades,
        prices=prices,
        signals=signals,
        costs=costs,
        risk=risk,
    )


def _simulate(prices, signals, costs, risk):
    index = prices.index
    opens = prices["open"].to_numpy(dtype="float64")
    closes = prices["close"].to_numpy(dtype="float64")
    wants = signals.to_numpy(dtype="int64")
    n = len(index)

    equity = np.empty(n, dtype="float64")
    position = np.zeros(n, dtype="int64")
    trades: List[Trade] = []

    cash, units = 1.0, 0.0
    entry_price, entry_time, peak = 0.0, None, 0.0

    # Decided at the previous bar's close, executed at this bar's open.
    pending = None
    # Set after a risk exit. Blocks re-entry until the signal goes flat first,
    # otherwise a stop loss fires and the still-true signal buys straight back
    # in on the next bar, forever.
    blocked = False

    for i in range(n):
        # A. Execute whatever the previous bar decided, at this bar's open.
        if pending is not None:
            action, reason = pending
            pending = None
            if action == "enter" and units == 0.0:
                entry_price = costs.buy_price(opens[i])
                units, cash = cash / entry_price, 0.0
                entry_time, peak = index[i], closes[i]
            elif action == "exit" and units > 0.0:
                exit_price = costs.sell_price(opens[i])
                cash, units = units * exit_price, 0.0
                trades.append(
                    Trade(
                        entry_time=entry_time,
                        entry_price=entry_price,
                        exit_time=index[i],
                        exit_price=exit_price,
                        return_pct=exit_price / entry_price - 1.0,
                        exit_reason=reason,
                    )
                )
                if reason != SIGNAL:
                    blocked = True

        # B. Mark to market on this bar's close.
        equity[i] = cash + units * closes[i]
        position[i] = 1 if units > 0.0 else 0

        # C. Look at this bar's close and decide what happens at the next open.
        if units > 0.0:
            peak = max(peak, closes[i])
            reason = _risk_exit(closes[i], entry_price, peak, risk)
            if reason is not None:
                pending = ("exit", reason)
            elif wants[i] == 0:
                pending = ("exit", SIGNAL)
        else:
            if blocked and wants[i] == 0:
                blocked = False
            if wants[i] == 1 and not blocked:
                pending = ("enter", None)

    # Nothing can fill after the last bar, so close any open position against
    # the final close and label it honestly rather than leaving it unrealised.
    if units > 0.0:
        exit_price = costs.sell_price(closes[-1])
        cash, units = units * exit_price, 0.0
        trades.append(
            Trade(
                entry_time=entry_time,
                entry_price=entry_price,
                exit_time=index[-1],
                exit_price=exit_price,
                return_pct=exit_price / entry_price - 1.0,
                exit_reason=END_OF_DATA,
            )
        )
        equity[-1] = cash

    return (
        pd.Series(equity, index=index, name="equity"),
        pd.Series(position, index=index, name="position"),
        trades,
    )


def _risk_exit(close, entry_price, peak, risk):
    """Return an exit reason if a risk rule has been breached, else None.

    Checks run against the close rather than the intrabar low. Triggering on
    the low would imply we know the path the price took inside the bar and
    could have filled at exactly the stop level, which minute and daily data
    do not support. Checking the close is the conservative reading: the exit
    happens later and at a worse price than a real resting order would get.
    """
    if not risk.active:
        return None
    if risk.stop_loss_pct is not None and close <= entry_price * (1 - risk.stop_loss_pct):
        return STOP_LOSS
    if risk.take_profit_pct is not None and close >= entry_price * (1 + risk.take_profit_pct):
        return TAKE_PROFIT
    if risk.trailing_stop_pct is not None and close <= peak * (1 - risk.trailing_stop_pct):
        return TRAILING_STOP
    return None
