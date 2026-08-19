"""Command line entry point.

    python -m tradingbot --fixture --strategy ema
    python -m tradingbot --symbol AAPL --strategy breakout --interval 1d
"""

from __future__ import annotations

import argparse
import sys

from tradingbot import data, engine, report
from tradingbot.strategies import STRATEGIES


def build_parser():
    parser = argparse.ArgumentParser(
        prog="tradingbot",
        description="Backtest a strategy against historical prices.",
    )

    source = parser.add_argument_group("data")
    source.add_argument("--symbol", default="SYNTH", help="ticker or crypto symbol")
    source.add_argument("--interval", default="1d", help="1d, or intraday e.g. 1min")
    source.add_argument("--asset", default="equity", choices=("equity", "crypto"))
    source.add_argument(
        "--fixture",
        nargs="?",
        const="SYNTH_daily",
        default=None,
        metavar="NAME",
        help="use committed sample data instead of the API (no key required)",
    )
    source.add_argument("--no-cache", action="store_true", help="ignore the local cache")

    strategy = parser.add_argument_group("strategy")
    strategy.add_argument(
        "--strategy", default="ema", choices=sorted(STRATEGIES), help="which strategy to run"
    )
    strategy.add_argument("--period", type=int, help="ema span / sma window / breakout lookback")
    strategy.add_argument("--band", type=float, help="reversion band, e.g. 0.02 for 2 percent")

    execution = parser.add_argument_group("execution")
    execution.add_argument("--commission-bps", type=float, default=5.0)
    execution.add_argument("--slippage-bps", type=float, default=2.0)
    execution.add_argument("--stop-loss", type=float, default=None, metavar="PCT")
    execution.add_argument("--take-profit", type=float, default=None, metavar="PCT")
    execution.add_argument("--trailing-stop", type=float, default=None, metavar="PCT")

    output = parser.add_argument_group("output")
    output.add_argument("--plot", nargs="?", const="", metavar="PATH",
                        help="draw the chart; give a path to save instead of display")

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)

    try:
        if args.fixture is not None:
            prices = data.load_fixture(args.fixture)
            label = f"{args.fixture} (sample data)"
        else:
            prices = data.load(
                args.symbol,
                interval=args.interval,
                asset=args.asset,
                use_cache=not args.no_cache,
            )
            label = f"{args.symbol} {args.interval}"
    except (data.MissingAPIKey, FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    signals = STRATEGIES[args.strategy](prices, **_strategy_kwargs(args))

    result = engine.run(
        prices,
        signals,
        costs=engine.Costs(
            commission_bps=args.commission_bps, slippage_bps=args.slippage_bps
        ),
        risk=engine.Risk(
            stop_loss_pct=args.stop_loss,
            take_profit_pct=args.take_profit,
            trailing_stop_pct=args.trailing_stop,
        ),
    )

    title = f"{args.strategy} on {label}"
    report.print_summary(result, title=title)

    if args.plot is not None:
        saved = report.plot(result, path=args.plot or None, title=title)
        if saved:
            print(f"\nChart written to {saved}")

    return 0


def _strategy_kwargs(args):
    """Map the generic --period and --band flags onto each strategy's parameters."""
    names = {"ema": "period", "sma": "window", "breakout": "lookback"}
    kwargs = {}
    if args.period is not None:
        kwargs[names[args.strategy]] = args.period
    if args.band is not None:
        kwargs["drawdown" if args.strategy == "breakout" else "band"] = args.band
    return kwargs


if __name__ == "__main__":
    raise SystemExit(main())
