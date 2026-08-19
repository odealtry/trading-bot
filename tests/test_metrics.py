"""Metrics tests, all against curves whose answers are known by hand."""

from __future__ import annotations

import math

import pandas as pd
import pytest

from tradingbot import metrics
from tradingbot.engine import Trade


def curve(values, freq="D", start="2024-01-01"):
    index = pd.date_range(start, periods=len(values), freq=freq)
    return pd.Series([float(v) for v in values], index=index)


def trade(return_pct, reason="signal"):
    stamp = pd.Timestamp("2024-01-01")
    return Trade(stamp, 100.0, stamp, 100.0 * (1 + return_pct), return_pct, reason)


class TestCurveStats:
    def test_total_return(self):
        assert metrics.curve_stats(curve([1.0, 1.5, 1.25]))["total_return"] == pytest.approx(0.25)

    def test_max_drawdown_is_measured_from_the_peak(self):
        # Peak 1.2, trough 0.9, so the worst drawdown is 0.9 / 1.2 - 1.
        stats = metrics.curve_stats(curve([1.0, 1.2, 0.9, 1.1]))
        assert stats["max_drawdown"] == pytest.approx(-0.25)

    def test_a_curve_that_only_rises_has_no_drawdown(self):
        assert metrics.curve_stats(curve([1.0, 1.1, 1.2]))["max_drawdown"] == pytest.approx(0.0)

    def test_cagr_over_exactly_one_year(self):
        index = pd.DatetimeIndex(["2020-01-01", "2021-01-01"])
        equity = pd.Series([1.0, 1.5], index=index)
        # 365 days against a 365.25 day year, so a shade above 50 percent.
        assert metrics.curve_stats(equity)["cagr"] == pytest.approx(0.5, abs=0.005)

    def test_cagr_compounds_over_multiple_years(self):
        index = pd.DatetimeIndex(["2020-01-01", "2024-01-01"])
        equity = pd.Series([1.0, 4.0], index=index)
        stats = metrics.curve_stats(equity)
        assert stats["cagr"] == pytest.approx(4.0 ** (1 / 4.0) - 1, abs=0.005)

    def test_flat_curve_has_no_sharpe(self):
        assert math.isnan(metrics.curve_stats(curve([1.0, 1.0, 1.0]))["sharpe"])

    def test_empty_curve_does_not_raise(self):
        stats = metrics.curve_stats(pd.Series(dtype="float64"))
        assert math.isnan(stats["total_return"])

    def test_sharpe_scales_with_bar_frequency(self):
        """The same returns annualise differently on daily and minute bars."""
        values = [1.0, 1.01, 1.005, 1.02, 1.015, 1.03]
        daily = metrics.curve_stats(curve(values, freq="D"))["sharpe"]
        minutely = metrics.curve_stats(curve(values, freq="min"))["sharpe"]
        assert minutely > daily


class TestTradeStats:
    def test_counts_wins_and_losses(self):
        stats = metrics.trade_stats([trade(0.10), trade(-0.05), trade(0.20), trade(-0.05)])

        assert stats["num_trades"] == 4
        assert stats["win_rate"] == pytest.approx(0.5)
        assert stats["avg_win"] == pytest.approx(0.15)
        assert stats["avg_loss"] == pytest.approx(-0.05)
        assert stats["payoff_ratio"] == pytest.approx(3.0)

    def test_exit_reasons_are_tallied(self):
        stats = metrics.trade_stats(
            [trade(0.1, "signal"), trade(-0.1, "stop_loss"), trade(-0.1, "stop_loss")]
        )
        assert stats["exit_reasons"] == {"signal": 1, "stop_loss": 2}

    def test_no_trades_is_not_an_error(self):
        stats = metrics.trade_stats([])
        assert stats["num_trades"] == 0
        assert math.isnan(stats["win_rate"])

    def test_all_winners_has_no_payoff_ratio(self):
        stats = metrics.trade_stats([trade(0.1), trade(0.2)])
        assert stats["win_rate"] == pytest.approx(1.0)
        assert math.isnan(stats["payoff_ratio"])


class TestSummarise:
    def test_summary_includes_the_benchmark_comparison(self):
        from tradingbot import engine
        from tests.test_engine import frame, signals

        prices = frame(opens=[100, 100, 100], closes=[100, 100, 120])
        result = engine.run(
            prices, signals([0, 0, 0], prices), costs=engine.Costs(0.0, 0.0)
        )
        stats = metrics.summarise(result)

        assert stats["total_return"] == pytest.approx(0.0)
        assert stats["benchmark_total_return"] == pytest.approx(0.2)
        assert stats["excess_return"] == pytest.approx(-0.2)
        assert stats["exposure"] == pytest.approx(0.0)
