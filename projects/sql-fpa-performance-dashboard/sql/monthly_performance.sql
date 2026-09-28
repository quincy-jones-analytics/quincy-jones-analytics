WITH actual_month AS (
    SELECT f.period,
           SUM(CASE WHEN d.pnl_group = 'Revenue' THEN f.amount_usd ELSE 0 END) AS revenue_usd,
           SUM(CASE WHEN d.pnl_group = 'Cost of Services' THEN f.amount_usd ELSE 0 END) AS cost_of_services_usd,
           SUM(CASE WHEN d.pnl_group = 'Operating Expenses' THEN f.amount_usd ELSE 0 END) AS operating_expenses_usd
    FROM fact_actuals f JOIN dim_account d USING (account_id)
    GROUP BY f.period
), budget_month AS (
    SELECT f.period,
           SUM(CASE WHEN d.pnl_group = 'Revenue' THEN f.amount_usd ELSE 0 END) AS revenue_usd,
           SUM(CASE WHEN d.pnl_group = 'Cost of Services' THEN f.amount_usd ELSE 0 END) AS cost_of_services_usd,
           SUM(CASE WHEN d.pnl_group = 'Operating Expenses' THEN f.amount_usd ELSE 0 END) AS operating_expenses_usd
    FROM fact_budget f JOIN dim_account d USING (account_id)
    GROUP BY f.period
), combined AS (
    SELECT a.period,
           a.revenue_usd AS actual_revenue_usd, b.revenue_usd AS budget_revenue_usd,
           a.cost_of_services_usd AS actual_cost_of_services_usd, b.cost_of_services_usd AS budget_cost_of_services_usd,
           a.operating_expenses_usd AS actual_operating_expenses_usd, b.operating_expenses_usd AS budget_operating_expenses_usd,
           a.revenue_usd - a.cost_of_services_usd AS actual_gross_profit_usd,
           b.revenue_usd - b.cost_of_services_usd AS budget_gross_profit_usd,
           a.revenue_usd - a.cost_of_services_usd - a.operating_expenses_usd AS actual_ebitda_usd,
           b.revenue_usd - b.cost_of_services_usd - b.operating_expenses_usd AS budget_ebitda_usd
    FROM actual_month a JOIN budget_month b USING (period)
), variance AS (
    SELECT *, actual_revenue_usd - budget_revenue_usd AS revenue_variance_favorable_usd,
              budget_cost_of_services_usd - actual_cost_of_services_usd AS cost_variance_favorable_usd,
              budget_operating_expenses_usd - actual_operating_expenses_usd AS opex_variance_favorable_usd,
              actual_ebitda_usd - budget_ebitda_usd AS ebitda_variance_favorable_usd
    FROM combined
)
SELECT period, actual_revenue_usd, budget_revenue_usd, revenue_variance_favorable_usd,
       actual_cost_of_services_usd, budget_cost_of_services_usd, cost_variance_favorable_usd,
       actual_operating_expenses_usd, budget_operating_expenses_usd, opex_variance_favorable_usd,
       actual_gross_profit_usd, budget_gross_profit_usd, actual_ebitda_usd, budget_ebitda_usd,
       ebitda_variance_favorable_usd,
       CASE WHEN actual_revenue_usd = 0 THEN NULL ELSE actual_ebitda_usd / actual_revenue_usd END AS actual_ebitda_margin_pct,
       SUM(actual_ebitda_usd) OVER (ORDER BY period ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS ytd_actual_ebitda_usd,
       LAG(actual_ebitda_usd) OVER (ORDER BY period) AS prior_month_actual_ebitda_usd,
       AVG(actual_ebitda_usd) OVER (ORDER BY period ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS rolling_3m_actual_ebitda_usd
FROM variance ORDER BY period;
