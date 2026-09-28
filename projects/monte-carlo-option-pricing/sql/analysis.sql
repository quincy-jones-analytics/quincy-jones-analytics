-- Load output CSVs as option_pricing_results and convergence.
SELECT strike_usd, analytic_call_usd, mc_call_usd, call_standard_error_usd,
       ABS(mc_call_usd - analytic_call_usd) AS absolute_pricing_error
FROM option_pricing_results ORDER BY strike_usd;

SELECT strike_usd, pairs, mc_call_usd, analytic_call_usd,
       standard_error_usd, absolute_error_usd
FROM convergence ORDER BY strike_usd, pairs;
