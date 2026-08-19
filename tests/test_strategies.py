"""Strategy tests.

Strategies are pure, so they can be checked directly against a price series
without running a backtest at all. That was impossible in the previous
version, where signal logic, position state and printing shared one method.
"""

from __future__ import annotations

import pandas as pd
import pytest

from tradingbot import data, strategies
from tradingbot.strategies import STRATEGIES


def frame(closes):
    index = pd.date_range("2024-01-01", periods=len(closes), freq="D")
    return pd.DataFrame({"close": [float(c) for c in closes]}, index=index)


class TestContract:
    @pytest.mark.parametrize("name", sorted(STRATEGIES))
    def test_output_is_aligned_binary_and_complete(self, name):
        prices = data.load_fixture("SYNTH_daily")
        signals = STRATEGIES[name](prices)

        assert isinstance(signals, pd.Series)
        assert signals.index.equals(prices.index)
        assert set(signals.unique()) <= {0, 1}
        assert signals.notna().all()

    @pytest.mark.parametrize("name", sorted(STRATEGIES))
    def test_strategies_do_not_mutate_their_input(self, name):
        prices = data.load_fixture("SYNTH_daily")
        before = prices.copy()
        STRATEGIES[name](prices)
        pd.testing.assert_frame_equal(prices, before)


class TestReversion:
    def test_flat_prices_never_trigger(self):
        prices = frame([100.0] * 50)
        assert strategies.ema_reversion(prices).sum() == 0
        assert strategies.sma_reversion(prices).sum() == 0

    def test_goes_long_below_the_band_and_holds_through_the_middle(self):
        # Settle at 100, drop hard enough to trigger, then recover only partway.
        closes = [100.0] * 10 + [90.0, 99.0, 100.0]
        signals = strategies.ema_reversion(frame(closes), period=5, band=0.02)

        assert signals.iloc[9] == 0, "no signal while price is at its average"
        assert signals.iloc[10] == 1, "long once price is 10 percent below"
        assert signals.iloc[11] == 1, "still long inside the band, not flipped out"

    def test_exits_above_the_upper_band(self):
        closes = [100.0] * 10 + [90.0, 130.0]
        signals = strategies.ema_reversion(frame(closes), period=5, band=0.02)

        assert signals.iloc[10] == 1
        assert signals.iloc[11] == 0

    def test_band_width_changes_how_often_it_trades(self):
        prices = data.load_fixture("SYNTH_daily")
        tight = strategies.ema_reversion(prices, band=0.005).diff().abs().sum()
        wide = strategies.ema_reversion(prices, band=0.10).diff().abs().sum()
        assert tight > wide


class TestBreakout:
    def test_long_while_near_the_high_flat_after_a_slump(self):
        closes = [100.0, 110.0, 120.0, 115.0, 95.0]
        signals = strategies.breakout(frame(closes), drawdown=0.10)

        assert signals.iloc[2] == 1, "at a new high"
        assert signals.iloc[3] == 1, "4 percent off the high is inside the band"
        assert signals.iloc[4] == 0, "21 percent off the high is not"

    def test_re_arms_on_recovery(self):
        closes = [100.0, 120.0, 95.0, 118.0]
        signals = strategies.breakout(frame(closes), drawdown=0.10)

        assert signals.tolist() == [1, 1, 0, 1]

    def test_rolling_lookback_forgets_an_old_high(self):
        closes = [100.0, 200.0] + [100.0] * 10
        all_time = strategies.breakout(frame(closes), lookback=None, drawdown=0.10)
        rolling = strategies.breakout(frame(closes), lookback=3, drawdown=0.10)

        assert all_time.iloc[-1] == 0, "still measured against the 200 peak"
        assert rolling.iloc[-1] == 1, "the 200 peak has rolled out of the window"
