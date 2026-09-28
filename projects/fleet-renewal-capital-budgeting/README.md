# Fleet Renewal: Capital Budgeting & Investment Screen

## Executive brief

**Decision:** Should leaders advance a fleet-renewal proposal for diligence, redesign it, or defer pending evidence on operating savings?

This capital-budgeting case compares a hypothetical fleet replacement against a simplified keep-the-current-fleet baseline. It translates assumed fuel, maintenance, and downtime savings into after-tax cash flows, then screens NPV, IRR, payback, and break-even savings across downside, base, and upside cases.

> **Synthetic demonstration:** Purchase cost, trade-in value, savings, useful life, and hurdle rates are illustrative assumptions. They are not a quote, procurement recommendation, employer result, or claim of realized savings.

## Decision framework

- **Net initial investment** = gross capital expenditure − trade-in proceeds.
- **Annual after-tax project cash flow** = operating savings × (1 − tax rate) + depreciation tax shield.
- **Terminal after-tax salvage** = assumed terminal salvage × (1 − tax rate), paid in the final modeled year.
- **NPV** discounts all project cash flows at the scenario hurdle rate, including the year-zero outlay.
- **IRR** is calculated by bisection on the project cash-flow stream.
- The sensitivity grid varies assumed savings and gross capital cost around the base case.

The model uses straight-line depreciation over the seven-year life, a 25% tax assumption, constant annual operating savings, and no financing effects.

## Illustrative decision snapshot

| Scenario | NPV | IRR | Simple payback | Screen |
|---|---:|---:|---:|---|
| Downside | -$470K | 8.2% | 5.30 years | Defer / redesign |
| Base | $1.89M | 21.2% | 3.57 years | Advance to diligence |
| Upside | $3.76M | 31.4% | 2.76 years | Advance to diligence |

The base case clears its 10% hurdle, while downside does not. The decision is therefore to validate savings and asset costs, not to treat the screen as a purchase approval.

## Files and reproduction

- `build_case.py` generates synthetic assumptions, annual cash flows, investment screens, and sensitivity outputs.
- `data/synthetic_capital_budget_assumptions.csv` documents each scenario's cost, savings, and hurdle assumptions.
- `outputs/scenario_cash_flows.csv` contains year-zero and annual after-tax cash flows with discount factors.
- `outputs/investment_screen.csv` summarizes NPV, IRR, payback, break-even savings, and the screen result.
- `outputs/capex_savings_sensitivity.csv` shows NPV across capital-cost and savings multipliers.
- `outputs/executive_summary.txt` provides a generated decision snapshot.
- `sql/analysis.sql` contains SQLite NPV and cash-flow review queries.

```bash
python3 build_case.py
```

Requires Python 3.10+ and the standard library. Import `scenario_cash_flows.csv` into SQLite as `scenario_cash_flows` before running the SQL.

## Leadership discussion and limits

“Advance to diligence” means validate the operational case; it is not authorization to purchase. Confirm asset specifications, tax treatment, vendor quotes, energy prices, maintenance history, uptime impact, disposal proceeds, and implementation risk. The downtime savings are assumptions rather than guaranteed cash receipts. The model excludes financing structure, inflation, ramp timing, working capital, tax basis of retired assets, and alternative use of capital. Replace assumptions with approved evidence before making a real investment decision.
