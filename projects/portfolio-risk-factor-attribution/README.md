# Portfolio Risk and Factor Attribution

## Executive brief

**Decision:** How much simulated portfolio risk comes from market and sector exposures, and how do tail-loss measures compare with volatility?

This Python case generates 252 synthetic daily observations, builds an equal-weight portfolio, computes annualized volatility, historical VaR/CVaR, drawdown, market beta, and a two-factor OLS attribution, then applies explicit factor shocks.

## Files

- `data/synthetic_daily_returns.csv`: seeded simulation with asset, market, and sector returns.
- `outputs/portfolio_risk_metrics.csv`, `factor_stress.csv`, and `executive_summary.txt`.
- `sql/analysis.sql`: SQL rollups for portfolio statistics and stress comparisons.

> **Synthetic demonstration:** The assets, factors, and return history are generated data—not market observations, backtest results, or investment advice. VaR/CVaR depend on the sample and do not estimate losses outside it.

Run `python3 build_case.py` with Python 3.10+ and the standard library. The seed makes outputs repeatable; the small-sample factor model is educational and omits rebalancing costs, changing exposures, and factor-model diagnostics.
