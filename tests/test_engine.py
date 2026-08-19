"""Engine tests.

Every case here uses a hand-built price series where the correct answer can
be worked out on paper, so a failure points at the engine rather than at the
data. Between them these cover the three bugs that survived years in the
previous version: silently discarded trade flags, a hard crash on positional
indexing, and same-bar fills.
"""

from __future__ import annotations

import pandas as pd
import pytest

from tradingbot import engine, strategies
from tradingbot.engine import Costs, Risk

FREE = Costs(commission_bps=0.0, slippage_bps=0.0)


def frame(opens, closes):
    index = pd.date_range("2024-01-01", periods=len(closes), freq="D")
    return pd.DataFrame(
        {
            "open": [float(o) for o in opens],
            "high": [float(max(o, c)) for o, c in zip(opens, closes)],
            "low": [float(min(o, c)) for o, c in zip(opens, closes)],
            "close": [float(c) for c in closes],
            "volume": [1_000.0] * len(closes),
        },
        index=index,
    )


def signals(values, prices):
    return pd.Series(values, index=prices.index, dtype=int)


class TestExecutionTiming:
    def test_signal_fills_at_the_next_bar_open(self):
        """A signal seen at bar 1 fills at bar 2's open, not bar 1's close."""
        prices = frame(opens=[10, 20, 30, 40, 50], closes=[11, 21, 31, 41, 51])
        result = engine.run(prices, signals([0, 1, 0, 0, 0], prices), costs=FREE)

        assert len(result.trades) == 1
        trade = result.trades[0]
        assert trade.entry_price == pytest.approx(30.0)
        assert trade.exit_price == pytest.approx(40.0)
        assert trade.return_pct == pytest.approx(40.0 / 30.0 - 1.0)
        assert trade.exit_reason == engine.SIGNAL

    def test_signal_on_the_final_bar_cannot_trade(self):
        """There is no next bar to fill against, so nothing should happen.

        This is the lookahead guard. An engine that filled at the signal bar's
        own close would report a trade here.
        """
        prices = frame(opens=[10, 10, 10, 10, 10], closes=[10, 10, 10, 10, 99])
        result = engine.run(prices, signals([0, 0, 0, 0, 1], prices), costs=FREE)

        assert result.trades == []
        assert result.equity.iloc[-1] == pytest.approx(1.0)

    def test_open_position_is_closed_against_the_final_bar(self):
        prices = frame(opens=[10, 10, 10], closes=[10, 10, 12])
        result = engine.run(prices, signals([1, 1, 1], prices), costs=FREE)

        assert len(result.trades) == 1
        assert result.trades[0].exit_reason == engine.END_OF_DATA
        assert result.trades[0].exit_price == pytest.approx(12.0)


class TestAccounting:
    def test_equity_tracks_the_trade(self):
        prices = frame(opens=[100, 100, 100], closes=[100, 100, 150])
        result = engine.run(prices, signals([1, 1, 1], prices), costs=FREE)

        # Enter at bar 1's open of 100, exit against bar 2's close of 150.
        assert result.equity.iloc[-1] == pytest.approx(1.5)

    def test_costs_are_charged_on_both_sides(self):
        prices = frame(opens=[10, 20, 30, 40, 50], closes=[11, 21, 31, 41, 51])
        sig = signals([0, 1, 0, 0, 0], prices)

        free = engine.run(prices, sig, costs=FREE).trades[0]
        charged = engine.run(
            prices, sig, costs=Costs(commission_bps=5.0, slippage_bps=5.0)
        ).trades[0]

        assert charged.entry_price == pytest.approx(30.0 * 1.001)
        assert charged.exit_price == pytest.approx(40.0 * 0.999)
        assert charged.return_pct < free.return_pct

    def test_flat_strategy_never_leaves_the_starting_equity(self):
        prices = frame(opens=[10] * 5, closes=[10, 12, 8, 15, 9])
        result = engine.run(prices, signals([0] * 5, prices), costs=FREE)

        assert result.trades == []
        assert (result.equity == 1.0).all()
        assert result.position.sum() == 0


class TestRiskRules:
    def test_stop_loss_fires_and_reports_itself(self):
        prices = frame(opens=[100, 100, 100, 100, 95], closes=[100, 100, 100, 96, 95])
        result = engine.run(
            prices, signals([1] * 5, prices), costs=FREE, risk=Risk(stop_loss_pct=0.02)
        )

        assert len(result.trades) == 1
        trade = result.trades[0]
        assert trade.exit_reason == engine.STOP_LOSS
        assert trade.entry_price == pytest.approx(100.0)
        assert trade.exit_price == pytest.approx(95.0)

    def test_take_profit_fires(self):
        prices = frame(opens=[100, 100, 100, 100, 106], closes=[100, 100, 100, 106, 106])
        result = engine.run(
            prices, signals([1] * 5, prices), costs=FREE, risk=Risk(take_profit_pct=0.05)
        )

        assert [t.exit_reason for t in result.trades] == [engine.TAKE_PROFIT]

    def test_trailing_stop_measures_from_the_peak_not_the_entry(self):
        # Rises to 110, then falls to 98. That is only 2 percent below the entry
        # but 11 percent below the peak, so a 10 percent trailing stop must fire.
        prices = frame(
            opens=[100, 100, 100, 100, 100, 97], closes=[100, 100, 110, 105, 98, 97]
        )
        result = engine.run(
            prices, signals([1] * 6, prices), costs=FREE, risk=Risk(trailing_stop_pct=0.10)
        )

        assert [t.exit_reason for t in result.trades] == [engine.TRAILING_STOP]

    def test_risk_exit_blocks_immediate_re_entry(self):
        """Without the latch, a still-true signal buys straight back in."""
        prices = frame(opens=[100] * 6, closes=[100, 100, 90, 90, 90, 90])
        result = engine.run(
            prices, signals([1] * 6, prices), costs=FREE, risk=Risk(stop_loss_pct=0.05)
        )

        assert len(result.trades) == 1
        assert result.trades[0].exit_reason == engine.STOP_LOSS
        assert result.position.iloc[-1] == 0

    def test_re_entry_is_allowed_once_the_signal_resets(self):
        prices = frame(
            opens=[100] * 8, closes=[100, 100, 90, 90, 90, 100, 100, 100]
        )
        sig = signals([1, 1, 1, 0, 0, 1, 1, 1], prices)
        result = engine.run(prices, sig, costs=FREE, risk=Risk(stop_loss_pct=0.05))

        assert [t.exit_reason for t in result.trades] == [
            engine.STOP_LOSS,
            engine.END_OF_DATA,
        ]

    def test_no_risk_rules_means_no_risk_exits(self):
        prices = frame(opens=[100] * 4, closes=[100, 50, 40, 30])
        result = engine.run(prices, signals([1] * 4, prices), costs=FREE)

        assert [t.exit_reason for t in result.trades] == [engine.END_OF_DATA]


class TestBenchmark:
    def test_benchmark_is_buy_and_hold_over_the_same_bars(self):
        prices = frame(opens=[100, 100, 100], closes=[100, 100, 120])
        result = engine.run(prices, signals([0, 0, 0], prices), costs=FREE)

        assert (result.equity == 1.0).all()
        assert result.benchmark.iloc[-1] == pytest.approx(1.2)

    def test_benchmark_pays_the_same_costs(self):
        prices = frame(opens=[100, 100, 100], closes=[100, 100, 120])
        costed = engine.run(
            prices, signals([0, 0, 0], prices), costs=Costs(10.0, 0.0)
        )

        assert costed.benchmark.iloc[-1] < 1.2


class TestContract:
    def test_signals_are_aligned_and_coerced(self):
        prices = frame(opens=[10] * 4, closes=[10, 11, 12, 13])
        result = engine.run(prices, [0, 1, 1, 0], costs=FREE)

        assert result.signals.index.equals(prices.index)
        assert set(result.signals.unique()) <= {0, 1}

    def test_position_series_reflects_holdings(self):
        prices = frame(opens=[10, 20, 30, 40, 50], closes=[11, 21, 31, 41, 51])
        result = engine.run(prices, signals([0, 1, 0, 0, 0], prices), costs=FREE)

        assert result.position.tolist() == [0, 0, 1, 0, 0]

    def test_empty_prices_are_rejected(self):
        with pytest.raises(ValueError):
            engine.run(pd.DataFrame(), pd.Series(dtype=int))

    def test_missing_open_column_is_rejected(self):
        prices = frame(opens=[10, 10], closes=[10, 10]).drop(columns=["open"])
        with pytest.raises(ValueError, match="open"):
            engine.run(prices, pd.Series([0, 0], index=prices.index))


class TestRealisticRun:
    def test_strategy_runs_end_to_end_on_fixture_data(self):
        from tradingbot import data

        prices = data.load_fixture("SYNTH_daily")
        result = engine.run(prices, strategies.ema_reversion(prices))

        assert len(result.equity) == len(prices)
        assert result.equity.notna().all()
        assert result.benchmark.notna().all()
        # The bug that mattered most in the old version: trades were logged to
        # stdout but never recorded anywhere a chart or a metric could see.
        assert len(result.trades) > 0
        assert result.position.sum() > 0
