# Integrated Monthly Three-Statement Planning

## Executive brief

**Decision:** How do the operating plan, working-capital movements, and capital spending affect monthly earnings and liquidity?

This synthetic monthly model links an income statement and cash flow roll-forward to a balance-sheet view, then compares revenue and EBITDA with a simple budget baseline.

## Model and outputs

- Revenue, cost of goods sold, operating expense, depreciation, interest, taxes, and net income by month.
- Cash flow uses net income, depreciation, changes in receivables/inventory/payables, and capital spending.
- The balance sheet rolls cash, working capital, net PP&E, debt, share capital, and retained earnings; each month includes a balance check.
- Files: `outputs/monthly_income_cashflow.csv`, `budget_variance.csv`, `balance_sheet_rollforward.csv`, and `executive_summary.txt`.
- `sql/analysis.sql` provides variance and balance-control review queries.

> **Synthetic demonstration:** No employer financials or actual company results are included. DSO/DIO/DPO are planning assumptions; debt is held constant; the model omits dividends, debt amortization, and tax-loss carryforwards.

Run `python3 build_case.py` with Python 3.10+ and its standard library. The script regenerates the input and outputs deterministically.
