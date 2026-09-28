WITH balances AS (
    SELECT period,
           MAX(CASE WHEN scenario = 'Actual' THEN accounts_receivable_usd END) AS actual_ar_usd,
           MAX(CASE WHEN scenario = 'Actual' THEN inventory_usd END) AS actual_inventory_usd,
           MAX(CASE WHEN scenario = 'Actual' THEN accounts_payable_usd END) AS actual_ap_usd,
           MAX(CASE WHEN scenario = 'Budget' THEN accounts_receivable_usd END) AS budget_ar_usd,
           MAX(CASE WHEN scenario = 'Budget' THEN inventory_usd END) AS budget_inventory_usd,
           MAX(CASE WHEN scenario = 'Budget' THEN accounts_payable_usd END) AS budget_ap_usd
    FROM fact_working_capital GROUP BY period
), pnl AS (
    SELECT p.period, p.actual_revenue_usd, p.actual_cost_of_services_usd
    FROM (
        SELECT f.period,
               SUM(CASE WHEN d.pnl_group = 'Revenue' THEN f.amount_usd ELSE 0 END) AS actual_revenue_usd,
               SUM(CASE WHEN d.pnl_group = 'Cost of Services' THEN f.amount_usd ELSE 0 END) AS actual_cost_of_services_usd
        FROM fact_actuals f JOIN dim_account d USING (account_id) GROUP BY f.period
    ) p
), metrics AS (
    SELECT b.*, p.actual_revenue_usd, p.actual_cost_of_services_usd,
           actual_ar_usd + actual_inventory_usd - actual_ap_usd AS actual_net_working_capital_usd,
           budget_ar_usd + budget_inventory_usd - budget_ap_usd AS budget_net_working_capital_usd,
           actual_ar_usd * 30.0 / NULLIF(p.actual_revenue_usd, 0) AS dso_monthly_proxy_days,
           actual_inventory_usd * 30.0 / NULLIF(p.actual_cost_of_services_usd, 0) AS dio_monthly_proxy_days,
           actual_ap_usd * 30.0 / NULLIF(p.actual_cost_of_services_usd, 0) AS dpo_monthly_proxy_days
    FROM balances b JOIN pnl p USING (period)
), changes AS (
    SELECT *, LAG(actual_net_working_capital_usd) OVER (ORDER BY period) AS prior_month_actual_nwc_usd,
              LAG(budget_net_working_capital_usd) OVER (ORDER BY period) AS prior_month_budget_nwc_usd
    FROM metrics
)
SELECT period, actual_ar_usd, actual_inventory_usd, actual_ap_usd,
       actual_net_working_capital_usd, budget_net_working_capital_usd,
       actual_net_working_capital_usd - budget_net_working_capital_usd AS nwc_variance_usd,
       prior_month_actual_nwc_usd - actual_net_working_capital_usd AS actual_cash_release_proxy_usd,
       prior_month_budget_nwc_usd - budget_net_working_capital_usd AS budget_cash_release_proxy_usd,
       dso_monthly_proxy_days, dio_monthly_proxy_days, dpo_monthly_proxy_days,
       dso_monthly_proxy_days + dio_monthly_proxy_days - dpo_monthly_proxy_days AS cash_conversion_cycle_proxy_days
FROM changes ORDER BY period;
