"""Data layer tests, covering the invariants everything downstream assumes."""

from __future__ import annotations

import pandas as pd
import pytest

from tradingbot import data


class TestFixtures:
    @pytest.mark.parametrize("name", ["SYNTH_daily", "SYNTH_1min"])
    def test_fixture_meets_the_canonical_contract(self, name):
        frame = data.load_fixture(name)

        assert list(frame.columns) == data.COLUMNS
        assert isinstance(frame.index, pd.DatetimeIndex)
        assert frame.index.is_monotonic_increasing
        assert not frame.index.has_duplicates
        assert frame.notna().all().all()
        assert (frame[["open", "high", "low", "close"]] > 0).all().all()

    def test_bars_are_internally_consistent(self):
        frame = data.load_fixture("SYNTH_daily")
        assert (frame["high"] >= frame[["open", "close"]].max(axis=1)).all()
        assert (frame["low"] <= frame[["open", "close"]].min(axis=1)).all()

    def test_unknown_fixture_lists_what_is_available(self):
        with pytest.raises(FileNotFoundError, match="SYNTH_daily"):
            data.load_fixture("does_not_exist")


class TestNormalisation:
    def test_provider_column_names_are_stripped(self):
        raw = pd.DataFrame(
            {
                "1. open": [1.0], "2. high": [2.0], "3. low": [0.5],
                "4. close": [1.5], "5. volume": [100.0],
            },
            index=pd.DatetimeIndex(["2024-01-01"]),
        )
        assert list(data._normalise(raw).columns) == data.COLUMNS

    def test_crypto_column_names_are_stripped(self):
        raw = pd.DataFrame(
            {
                "1a. open (USD)": [1.0], "2a. high (USD)": [2.0], "3a. low (USD)": [0.5],
                "4a. close (USD)": [1.5], "5. volume": [100.0],
            },
            index=pd.DatetimeIndex(["2024-01-01"]),
        )
        assert list(data._normalise(raw).columns) == data.COLUMNS

    def test_newest_first_data_is_reversed(self):
        """AlphaVantage returns newest first. Backtesting that as-is runs time
        backwards, which the previous version did for some datasets only."""
        index = pd.DatetimeIndex(["2024-01-03", "2024-01-02", "2024-01-01"])
        raw = pd.DataFrame(
            {
                "1. open": [3.0, 2.0, 1.0], "2. high": [3.0, 2.0, 1.0],
                "3. low": [3.0, 2.0, 1.0], "4. close": [3.0, 2.0, 1.0],
                "5. volume": [1.0, 1.0, 1.0],
            },
            index=index,
        )
        frame = data._normalise(raw)

        assert frame.index.is_monotonic_increasing
        assert frame["close"].tolist() == [1.0, 2.0, 3.0]

    def test_missing_columns_are_reported(self):
        raw = pd.DataFrame({"4. close": [1.0]}, index=pd.DatetimeIndex(["2024-01-01"]))
        with pytest.raises(ValueError, match="missing"):
            data._normalise(raw)

    def test_split_adjustment_scales_the_whole_bar(self):
        """A 2-for-1 split halves the pre-split bar, not just its close."""
        raw = pd.DataFrame(
            {
                "1. open": [100.0], "2. high": [110.0], "3. low": [90.0],
                "4. close": [100.0], "5. adjusted close": [50.0], "6. volume": [1.0],
            },
            index=pd.DatetimeIndex(["2024-01-01"]),
        )
        adjusted = data._adjust_for_splits(raw)

        assert adjusted["1. open"].iloc[0] == pytest.approx(50.0)
        assert adjusted["2. high"].iloc[0] == pytest.approx(55.0)
        assert adjusted["3. low"].iloc[0] == pytest.approx(45.0)


class TestLiveFetch:
    def test_missing_api_key_is_a_clear_error(self, monkeypatch):
        monkeypatch.delenv(data.API_KEY_VAR, raising=False)
        with pytest.raises(data.MissingAPIKey, match="--fixture"):
            data.load("AAPL", use_cache=False)
