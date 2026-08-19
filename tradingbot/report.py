"""Rendering: a text summary and a two-panel chart.

Kept separate from the engine so that a backtest can be run, tested and
composed without ever touching matplotlib or stdout.
"""

from __future__ import annotations

from tradingbot import metrics


def format_summary(result, title=""):
    """Return the performance summary as a string."""
    stats = metrics.summarise(result)
    equity = result.equity

    lines = []
    if title:
        lines += [title, "=" * len(title)]

    lines += [
        f"Period          {equity.index[0]:%Y-%m-%d %H:%M} to {equity.index[-1]:%Y-%m-%d %H:%M}"
        f"  ({len(equity):,} bars)",
        f"Costs           {result.costs.commission_bps:.1f}bps commission"
        f" + {result.costs.slippage_bps:.1f}bps slippage per side",
        f"Risk rules      {_risk_description(result.risk)}",
        "",
        f"{'Total return':<20}{_pct(stats['total_return']):>12}"
        f"{_pct(stats['benchmark_total_return']):>14}   (buy & hold)",
        f"{'CAGR':<20}{_pct(stats['cagr']):>12}{_pct(stats['benchmark_cagr']):>14}",
        f"{'Max drawdown':<20}{_pct(stats['max_drawdown']):>12}"
        f"{_pct(stats['benchmark_max_drawdown']):>14}",
        f"{'Sharpe':<20}{_num(stats['sharpe']):>12}",
        "",
        f"{'Excess vs benchmark':<20}{_pct(stats['excess_return']):>12}",
        f"{'Time in market':<20}{_pct(stats['exposure']):>12}",
        "",
        f"{'Trades':<20}{stats['num_trades']:>12,}",
        f"{'Win rate':<20}{_pct(stats['win_rate']):>12}",
        f"{'Average win':<20}{_pct(stats['avg_win']):>12}",
        f"{'Average loss':<20}{_pct(stats['avg_loss']):>12}",
        f"{'Payoff ratio':<20}{_num(stats['payoff_ratio']):>12}",
    ]

    if stats["exit_reasons"]:
        breakdown = ", ".join(
            f"{reason} {count}" for reason, count in sorted(stats["exit_reasons"].items())
        )
        lines += ["", f"Exits           {breakdown}"]

    return "\n".join(lines)


def print_summary(result, title=""):
    print(format_summary(result, title))


def plot(result, path=None, title="Backtest"):
    """Draw price with entries and exits above, equity against benchmark below."""
    import matplotlib

    if path is not None:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, (top, bottom) = plt.subplots(
        2, 1, figsize=(13, 9), sharex=True, gridspec_kw={"height_ratios": [2, 1]}
    )

    close = result.prices["close"]
    top.plot(close.index, close.to_numpy(), linewidth=0.9, color="#333333", label="Close")

    entries = [t.entry_time for t in result.trades]
    exits = [t.exit_time for t in result.trades]
    if entries:
        top.scatter(
            entries, close.reindex(entries).to_numpy(),
            marker="^", s=40, color="#2e7d32", zorder=3, label=f"Entry ({len(entries)})",
        )
    if exits:
        top.scatter(
            exits, close.reindex(exits).to_numpy(),
            marker="v", s=40, color="#c62828", zorder=3, label=f"Exit ({len(exits)})",
        )

    top.set_title(title)
    top.set_ylabel("Price")
    top.legend(loc="upper left", fontsize=9)
    top.grid(alpha=0.25)

    bottom.plot(
        result.equity.index, result.equity.to_numpy(),
        linewidth=1.2, color="#1565c0", label="Strategy",
    )
    bottom.plot(
        result.benchmark.index, result.benchmark.to_numpy(),
        linewidth=1.2, color="#9e9e9e", linestyle="--", label="Buy & hold",
    )
    bottom.axhline(1.0, color="#000000", linewidth=0.6, alpha=0.4)
    bottom.set_ylabel("Equity (start = 1.0)")
    bottom.set_xlabel("")
    bottom.legend(loc="upper left", fontsize=9)
    bottom.grid(alpha=0.25)

    fig.tight_layout()
    if path is not None:
        fig.savefig(path, dpi=130)
        plt.close(fig)
        return path

    plt.show()
    return None


def _risk_description(risk):
    parts = []
    if risk.stop_loss_pct is not None:
        parts.append(f"stop loss {risk.stop_loss_pct:.1%}")
    if risk.take_profit_pct is not None:
        parts.append(f"take profit {risk.take_profit_pct:.1%}")
    if risk.trailing_stop_pct is not None:
        parts.append(f"trailing stop {risk.trailing_stop_pct:.1%}")
    return ", ".join(parts) if parts else "none"


def _pct(value):
    return "n/a" if value != value else f"{value:.2%}"


def _num(value):
    return "n/a" if value != value else f"{value:.2f}"
