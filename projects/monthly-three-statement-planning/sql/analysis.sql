-- Load the output CSVs as budget_variance and balance_sheet_rollforward.
SELECT month, actual_revenue_usd, budget_revenue_usd, revenue_variance_usd,
       actual_ebitda_usd - budget_ebitda_usd AS ebitda_variance_usd
FROM budget_variance ORDER BY month;

SELECT month, ending_cash_usd, net_income_usd, cash_from_operations_usd
FROM monthly_income_cashflow ORDER BY month;

SELECT month, total_assets_usd, total_liabilities_equity_usd, balance_check_usd
FROM balance_sheet_rollforward WHERE ABS(balance_check_usd) > 0.02;
