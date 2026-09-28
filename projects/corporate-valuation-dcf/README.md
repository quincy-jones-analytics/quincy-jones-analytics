# Corporate Valuation: DCF & Sensitivity

## Executive brief

**Decision:** What valuation range is implied by a transparent set of operating, reinvestment, and discount-rate assumptions?

This discounted-cash-flow case values a hypothetical transportation-services company. It forecasts unlevered free cash flow under downside, base, and upside assumptions; discounts those cash flows; estimates terminal value; and bridges enterprise value to equity value.

> **Synthetic demonstration:** The company, forecasts, capitalization, share count, and valuation are entirely hypothetical. This is not an appraisal, investment recommendation, or result for an actual company.

## Model framework

- **Revenue** = prior-year revenue × (1 + scenario growth).
- **EBITDA** = revenue × scenario EBITDA margin.
- **Unlevered FCF** = EBIT × (1 − tax rate) + D&A − capital expenditures − change in working capital.
- **Terminal value** = final forecast-year FCF × (1 + perpetual growth) ÷ (WACC − perpetual growth).
- **Enterprise value** = present value of explicit FCF + present value of terminal value.
- **Equity value** = enterprise value − debt + cash.

The model checks that terminal growth remains below WACC and includes a WACC/terminal-growth sensitivity grid.

## Illustrative valuation snapshot

| Scenario | Enterprise value | Equity value | Value per share |
|---|---:|---:|---:|
| Downside | $28.0M | $19.0M | $3.79 |
| Base | $56.3M | $47.3M | $9.47 |
| Upside | $79.1M | $70.1M | $14.02 |

In the base case, terminal value contributes **71.5%** of enterprise value. That makes the assumptions beyond the explicit forecast a key leadership review point. These values are hypothetical outputs, not a quote or investment conclusion.

## Files and reproduction

- `build_case.py` generates synthetic scenario assumptions, five-year cash flows, valuation outputs, sensitivity analysis, and an executive summary.
- `data/synthetic_scenario_assumptions.csv` contains the scenario operating and valuation assumptions.
- `outputs/forecast_cash_flows.csv` contains annual forecast drivers, unlevered FCF, discount factors, and present values.
- `outputs/scenario_valuation.csv` bridges enterprise and equity value by scenario.
- `outputs/wacc_growth_sensitivity.csv` shows enterprise and equity value across discount-rate and terminal-growth cases.
- `outputs/executive_summary.txt` contains the generated decision snapshot.
- `sql/analysis.sql` provides SQLite review queries.

```bash
python3 build_case.py
```

Requires Python 3.10+ and the standard library. Load `forecast_cash_flows.csv` into SQLite as `forecast_cash_flows` before running the SQL.

## Leadership discussion and limits

Focus review on the assumptions that drive the valuation range: sustainable growth and margins, reinvestment needs, WACC, and terminal growth. The terminal value should be challenged because it can account for a large share of enterprise value. This simplified demonstration excludes comparable-company calibration, debt schedules, tax-loss carryforwards, dilution, management incentives, and marketability/liquidity adjustments. Small changes in assumptions can materially move the result; do not present the synthetic value as a real company estimate.
