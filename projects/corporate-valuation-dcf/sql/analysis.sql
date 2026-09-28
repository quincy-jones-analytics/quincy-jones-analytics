-- Import outputs/forecast_cash_flows.csv as forecast_cash_flows and
-- data/synthetic_scenario_assumptions.csv as scenario_assumptions.
SELECT scenario, ROUND(SUM(pv_fcf_usd),2) AS pv_explicit_fcf_usd
FROM forecast_cash_flows GROUP BY scenario ORDER BY scenario;

-- Review the explicit forecast and the discount factors for the base case.
SELECT year, revenue_usd, ebitda_usd, cash_taxes_usd, capex_usd,
       change_nwc_usd, unlevered_fcf_usd, discount_factor, pv_fcf_usd
FROM forecast_cash_flows WHERE scenario='Base' ORDER BY year;

-- Rebuild enterprise value from the explicit cash flows and Gordon-growth terminal value.
WITH explicit_pv AS (
  SELECT scenario, SUM(pv_fcf_usd) AS pv_fcf_usd
  FROM forecast_cash_flows GROUP BY scenario
), final_year AS (
  SELECT scenario, unlevered_fcf_usd, discount_factor
  FROM forecast_cash_flows WHERE year=5
)
SELECT a.scenario,
       ROUND(p.pv_fcf_usd + f.unlevered_fcf_usd * (1+a.terminal_growth)
         / (a.wacc-a.terminal_growth) * f.discount_factor, 2) AS enterprise_value_usd
FROM scenario_assumptions a
JOIN explicit_pv p ON p.scenario=a.scenario
JOIN final_year f ON f.scenario=a.scenario
ORDER BY a.scenario;
