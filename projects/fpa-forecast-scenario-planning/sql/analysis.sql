-- Import data/synthetic_actuals_h1.csv as actuals and
-- outputs/h2_scenario_model.csv as forecast_h2 before running.
-- H1 is common across scenarios; H2 forecast differs by scenario.
WITH h1 AS (
  SELECT SUM(units * price_per_unit_usd) AS revenue,
         SUM(units * (price_per_unit_usd - variable_cost_per_unit_usd)
             - fixed_cost_usd - operating_expense_usd) AS ebitda
  FROM actuals
), h2 AS (
  SELECT scenario, SUM(revenue_usd) AS revenue, SUM(ebitda_usd) AS ebitda
  FROM forecast_h2 GROUP BY scenario
)
SELECT scenario, ROUND(h1.revenue + h2.revenue, 2) AS fy_revenue_usd,
       ROUND(h1.ebitda + h2.ebitda, 2) AS fy_ebitda_usd,
       ROUND((h1.ebitda + h2.ebitda)/(h1.revenue + h2.revenue), 4) AS fy_ebitda_margin
FROM h1 CROSS JOIN h2 ORDER BY scenario;

-- H2 revenue and EBITDA by scenario and segment
SELECT scenario, segment, SUM(revenue_usd) AS revenue_usd,
       SUM(ebitda_usd) AS ebitda_usd,
       ROUND(SUM(ebitda_usd)/SUM(revenue_usd), 4) AS ebitda_margin
FROM forecast_h2 GROUP BY scenario, segment ORDER BY scenario, segment;
