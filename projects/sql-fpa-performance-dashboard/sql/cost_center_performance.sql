WITH center_month AS (
    SELECT f.period, f.cost_center,
           SUM(CASE WHEN d.pnl_group = 'Revenue' THEN f.amount_usd ELSE 0 END) AS revenue_usd,
           SUM(CASE WHEN d.pnl_group = 'Cost of Services' THEN f.amount_usd ELSE 0 END) AS cost_of_services_usd,
           SUM(CASE WHEN d.pnl_group = 'Operating Expenses' THEN f.amount_usd ELSE 0 END) AS operating_expenses_usd
    FROM fact_actuals f JOIN dim_account d USING (account_id)
    GROUP BY f.period, f.cost_center
), budget_center AS (
    SELECT f.period, f.cost_center,
           SUM(CASE WHEN d.pnl_group = 'Revenue' THEN f.amount_usd ELSE 0 END) AS revenue_usd,
           SUM(CASE WHEN d.pnl_group = 'Cost of Services' THEN f.amount_usd ELSE 0 END) AS cost_of_services_usd,
           SUM(CASE WHEN d.pnl_group = 'Operating Expenses' THEN f.amount_usd ELSE 0 END) AS operating_expenses_usd
    FROM fact_budget f JOIN dim_account d USING (account_id)
    GROUP BY f.period, f.cost_center
), result AS (
    SELECT a.period, a.cost_center,
           a.revenue_usd AS actual_revenue_usd, b.revenue_usd AS budget_revenue_usd,
           a.cost_of_services_usd AS actual_cost_of_services_usd, b.cost_of_services_usd AS budget_cost_of_services_usd,
           a.operating_expenses_usd AS actual_operating_expenses_usd, b.operating_expenses_usd AS budget_operating_expenses_usd,
           a.revenue_usd - a.cost_of_services_usd - a.operating_expenses_usd AS actual_ebitda_usd,
           b.revenue_usd - b.cost_of_services_usd - b.operating_expenses_usd AS budget_ebitda_usd,
           (a.revenue_usd - a.cost_of_services_usd - a.operating_expenses_usd) -
           (b.revenue_usd - b.cost_of_services_usd - b.operating_expenses_usd) AS ebitda_variance_favorable_usd
    FROM center_month a JOIN budget_center b USING (period, cost_center)
)
SELECT *, DENSE_RANK() OVER (PARTITION BY period ORDER BY ebitda_variance_favorable_usd DESC) AS monthly_variance_rank
FROM result ORDER BY period, monthly_variance_rank, cost_center;
