# Monte Carlo Option Pricing and Greeks

## Executive brief

**Decision:** Does a Monte Carlo estimate converge toward an analytical benchmark, and how does sampling error change with path count?

The model prices European calls and puts under geometric Brownian motion, uses antithetic variates, compares estimates with Black–Scholes, reports standard errors and convergence, and checks ATM Greeks with finite differences.

## Files

- `data/synthetic_model_assumptions.csv`: fixed assumptions and seed.
- `outputs/option_pricing_results.csv`: analytical/Monte Carlo prices, standard error, delta, gamma, and vega.
- `outputs/convergence.csv`; `outputs/independent_greek_checks.csv`; `outputs/executive_summary.txt`.
- `sql/analysis.sql`: review queries for price error and sampling convergence.

> **Model limits:** Synthetic inputs; European exercise; no dividends, jumps, stochastic volatility, market calibration, transaction costs, or early exercise. This is a quantitative methods demonstration, not investment advice.

Run `python3 build_case.py` with Python 3.10+ and the standard library. A fixed seed ensures reproducible results.
