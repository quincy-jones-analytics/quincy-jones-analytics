# Power BI model guide

## Import

Import the six CSVs in `../data/`: `dim_period`, `dim_account`, `dim_cost_center`, `fact_actuals`, `fact_budget`, and `fact_working_capital`. Set all amount columns to fixed decimal/currency, `period` to text, `period_start` to date, and `month_num`/`fiscal_year` to whole number.

## Relationships

Create one-to-many, single-direction relationships from each dimension to its facts:

| One side | Many side | Key |
|---|---|---|
| DimPeriod | FactActuals | period |
| DimPeriod | FactBudget | period |
| DimPeriod | FactWorkingCapital | period |
| DimAccount | FactActuals | account_id |
| DimAccount | FactBudget | account_id |
| DimCostCenter | FactActuals | cost_center |
| DimCostCenter | FactBudget | cost_center |

Hide technical keys from report view. Sort month labels by `month_num`; use `period_start` for chronological axes. Do not join the two transaction facts directly.

## Report page

1. KPI cards: actual revenue, actual EBITDA, EBITDA margin, and favorable EBITDA variance.
2. Combo chart: monthly actual and budget EBITDA with revenue as an optional secondary series.
3. Waterfall: revenue, cost of services, and operating expense contributions to EBITDA variance.
4. Matrix: cost center by actual EBITDA, budget EBITDA, variance, and rank.
5. Working-capital line chart: net working capital actual versus budget; cards for DSO, DIO, DPO, and CCC proxies.
6. Slicers: fiscal year, quarter, month, and cost center.

## Build boundary

This repository provides source tables, SQL results, a static SVG preview, and DAX starter measures. It does not include a `.pbix` file or claim a published Power BI service report. Save your own Power BI report after rebuilding these steps, then add a screenshot or exported PDF after checking it against the source CSV outputs.
