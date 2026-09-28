# SQL practice path: FP&A performance case

Use the synthetic tables in `../projects/sql-fpa-performance-dashboard/data/`. Work from `projects/sql-fpa-performance-dashboard/` and run `python3 build_case.py` first. The case uses SQLite syntax and no additional packages.

## Setup

The builder creates an in-memory SQLite schema and runs the analysis. To practice interactively, create a local database, execute `sql/schema.sql`, and import each CSV from `data/` into the matching table. Keep `period` as `YYYY-MM` text and `amount_usd` as numeric.

## Six-step sequence

| Step | SQL skill | Practice task | Check your result against |
|---|---|---|---|
| 1 | `SELECT`, `WHERE`, `ORDER BY` | Show actual rows for 2025 Q4 operating payroll, highest amount first. | `fact_actuals`, `dim_period`, and `dim_account` |
| 2 | `GROUP BY`, `SUM`, `COUNT` | Calculate actual and budget totals by account group. | Three P&L groups; revenue is positive-valued |
| 3 | `JOIN` | Join actuals to account names and compare to budget by month and cost center. | Keys are period + cost center + account |
| 4 | `CASE`, CTEs | Normalize favorable variance so positive is favorable for both revenue and expense. | `sql/monthly_performance.sql` |
| 5 | Window functions | Add prior-month EBITDA, YTD EBITDA, and a three-month rolling average. | `prior_month_actual_ebitda_usd`, `ytd_actual_ebitda_usd`, `rolling_3m_actual_ebitda_usd` |
| 6 | Ranking and working capital | Rank cost centers each month, then calculate a cash conversion cycle proxy. | `sql/cost_center_performance.sql` and `sql/working_capital.sql` |

## Capstone questions

1. Which month has the largest unfavorable EBITDA variance, and which cost center ranks worst that month?
2. Is the EBITDA gap driven more by revenue, cost of services, or operating expenses?
3. Does the net-working-capital gap worsen during any month where EBITDA beats budget?
4. What extra source data would you need before treating the DSO/DIO/DPO proxies as close-quality results?

Use the generated outputs as answer checks, not as a substitute for writing the queries yourself. A complete solution should reconcile account-level totals to monthly performance and cost-center totals to the same consolidated figures.
