WITH monthly AS (
    SELECT p.*, b.budget_revenue_usd, b.budget_cost_usd, b.budget_opex_usd FROM (
        SELECT f.period,
               SUM(CASE WHEN d.pnl_group = 'Revenue' THEN f.amount_usd ELSE 0 END) AS actual_revenue_usd,
               SUM(CASE WHEN d.pnl_group = 'Cost of Services' THEN f.amount_usd ELSE 0 END) AS actual_cost_usd,
               SUM(CASE WHEN d.pnl_group = 'Operating Expenses' THEN f.amount_usd ELSE 0 END) AS actual_opex_usd
        FROM fact_actuals f JOIN dim_account d USING (account_id) GROUP BY f.period
    ) p JOIN (
        SELECT f.period,
               SUM(CASE WHEN d.pnl_group = 'Revenue' THEN f.amount_usd ELSE 0 END) AS budget_revenue_usd,
               SUM(CASE WHEN d.pnl_group = 'Cost of Services' THEN f.amount_usd ELSE 0 END) AS budget_cost_usd,
               SUM(CASE WHEN d.pnl_group = 'Operating Expenses' THEN f.amount_usd ELSE 0 END) AS budget_opex_usd
        FROM fact_budget f JOIN dim_account d USING (account_id) GROUP BY f.period
    ) b USING (period)
)
SELECT 'Revenue' AS bridge_step, SUM(actual_revenue_usd) AS actual_usd, SUM(budget_revenue_usd) AS budget_usd,
       SUM(actual_revenue_usd - budget_revenue_usd) AS favorable_variance_usd FROM monthly
UNION ALL
SELECT 'Cost of Services', SUM(actual_cost_usd), SUM(budget_cost_usd), SUM(budget_cost_usd - actual_cost_usd) FROM monthly
UNION ALL
SELECT 'Operating Expenses', SUM(actual_opex_usd), SUM(budget_opex_usd), SUM(budget_opex_usd - actual_opex_usd) FROM monthly
UNION ALL
SELECT 'EBITDA', SUM(actual_revenue_usd - actual_cost_usd - actual_opex_usd),
       SUM(budget_revenue_usd - budget_cost_usd - budget_opex_usd),
       SUM((actual_revenue_usd - actual_cost_usd - actual_opex_usd) -
           (budget_revenue_usd - budget_cost_usd - budget_opex_usd)) FROM monthly;
