-- Import data/synthetic_weekly_demand_capacity.csv as capacity_plan.
SELECT node, COUNT(*) AS weeks, SUM(forecast_units) AS forecast_units,
       SUM(base_capacity_units) AS base_capacity_units,
       ROUND(1.0*SUM(forecast_units)/SUM(base_capacity_units),4) AS annual_utilization,
       SUM(CASE WHEN base_utilization >= 0.90 THEN 1 ELSE 0 END) AS weeks_over_90pct,
       SUM(base_shortfall_units) AS base_shortfall_units,
       SUM(flex_capacity_used_units) AS flex_capacity_used_units,
       SUM(unserved_after_flex_units) AS unserved_after_flex_units,
       ROUND(SUM(flex_cost_usd),2) AS flex_cost_usd,
       ROUND(SUM(illustrative_risk_cost_avoided_usd),2) AS risk_cost_avoided_usd,
       ROUND(SUM(net_modeled_benefit_usd),2) AS net_modeled_benefit_usd
FROM capacity_plan GROUP BY node ORDER BY annual_utilization DESC;

-- Identify weekly decisions requiring leadership attention.
SELECT week,node,forecast_units,base_capacity_units,base_utilization,
       flex_capacity_used_units,unserved_after_flex_units,net_modeled_benefit_usd,action
FROM capacity_plan WHERE base_utilization >= 0.90 ORDER BY base_utilization DESC;
