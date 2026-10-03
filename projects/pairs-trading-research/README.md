# Synthetic pairs research — corrected ledger

Independent research with AI-assisted construction and review. Synthetic prices and simulated returns; no actual investment performance is claimed.

The corrected model uses two actual share positions, historical rolling fits that exclude the current observation, prior-held-position mark-to-market, traded-dollar costs, short borrow, positive financing exposure, marked-equity returns and terminal liquidation. Thirty-four checks passed, including future-data isolation and ledger reconciliation.

Base ending equity is $112,223.66 from $100,000 (12.22% simulated return). Stress drawdown is −9.89%, versus −8.25% with the monitor: a 1.65 percentage-point simulated reduction. The prior 28.48% to 12.49% claim is retired.

Limits: synthetic prices, close-price fills, no latency, additional slippage, real borrow availability or real-market validation. This is not a deployable strategy recommendation.

Open the executed notebook and inspect the three CSV ledgers. The notebook is self-contained and writes a pairs_trading_outputs folder; the standalone source requires numpy, pandas and matplotlib and writes its output folder. [Current review](../finance-release/Finance_Upgrade_Review.md) · [Live research case](https://quincy-jones-analytics.gzsxwzqv7q.chatgpt.site/pairs-trading-research)
