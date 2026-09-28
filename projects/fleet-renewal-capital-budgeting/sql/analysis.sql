-- Import outputs/scenario_cash_flows.csv as scenario_cash_flows.
SELECT scenario, ROUND(SUM(discounted_cash_flow_usd),2) AS npv_usd
FROM scenario_cash_flows GROUP BY scenario ORDER BY scenario;

-- Review the base-case cash-flow build and the discounted stream.
SELECT year, initial_investment_usd, operating_savings_usd,
       depreciation_tax_shield_usd, after_tax_salvage_usd,
       cash_flow_usd, discount_factor, discounted_cash_flow_usd
FROM scenario_cash_flows WHERE scenario='Base' ORDER BY year;
