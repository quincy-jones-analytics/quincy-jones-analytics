# FP&A Forecasting & Scenario Planning

## Executive brief

**Decision:** What operating assumptions should leaders use for the FY2026 outlook, and what triggers should prompt a reforecast?

This driver-based planning case combines six months of synthetic actuals with a three-scenario second-half forecast. It translates unit volume, realized price, unit cost, fixed cost, and operating expense assumptions into revenue, EBITDA, and margin outcomes.

> **Synthetic demonstration:** Every record, assumption, and financial result is simulated. It is not company data, an employer result, or a claim of realized savings.

## Decision snapshot

Run `python3 build_case.py` to regenerate the annual scenario bridge, monthly forecast, and summary from the fixed model assumptions.

| FY2026 scenario | Revenue | EBITDA | EBITDA margin |
|---|---:|---:|---:|
| Downside | $10.43M | -$616K | -5.9% |
| Base | $11.31M | $124K | 1.1% |
| Upside | $11.83M | $534K | 4.5% |

**Executive read:** The modeled EBITDA range spans about $1.15M. The base case is only slightly above break-even, so leadership should review volume, price realization, and cost inflation assumptions together and define reforecast triggers. The scenarios are sensitivities, not probability-weighted guidance.

- Base case sets a planning reference point; downside and upside cases bound the modeled range.
- H1 actuals stay constant across all scenarios, so H2 operating assumptions explain the scenario spread.
- Recommended leadership routine: review volume, price, and cost drivers monthly; set named owners and trigger levels before changing the forecast.

## Model design

- Three segments: Core, Enterprise, Services.
- Actual period: January–June 2026; forecast period: July–December 2026.
- Scenario drivers: unit growth, price growth, variable-cost inflation, and operating-expense growth.
- **Revenue** = units × price per unit.
- **EBITDA** = revenue − variable cost − fixed cost − operating expense.
- Forecast is a transparent deterministic planning example; it does not infer probabilities.

## Files

- `build_case.py` generates the synthetic input, scenario model, annual summary, and executive summary.
- `data/synthetic_actuals_h1.csv` contains segment-level H1 inputs.
- `outputs/h2_scenario_model.csv` contains monthly H2 results by scenario and segment.
- `outputs/annual_scenario_summary.csv` bridges common actuals and forecast for each scenario.
- `sql/analysis.sql` reproduces the annual and segment rollups in SQLite.

## Reproduce

Requires Python 3.10+ and the standard library only.

```bash
python3 build_case.py
```

Load the generated CSV files into SQLite tables named `actuals` and `forecast_h2`, then run `sql/analysis.sql`.

## Executive discussion and limits

The appropriate action is to align owners and thresholds to the three forecast drivers, then refresh assumptions when actual demand, realized price, or cost inflation moves outside the agreed band. This model excludes working capital, tax, financing, product cannibalization, and actual company history. A real forecast needs validated general-ledger actuals, a calendar, headcount and hiring plans, product/customer mix, cash flow, and documented assumption owners. Scenario values are not guidance and should not be presented as an outlook for a real organization.
