-- Load source as procurement_transactions.
SELECT category, SUM(spend_usd) AS spend_usd,
       SUM(MAX(spend_usd - benchmark_rate_usd, 0)) AS benchmark_gap_usd
FROM procurement_transactions GROUP BY category ORDER BY spend_usd DESC;

SELECT supplier, SUM(spend_usd) AS spend_usd,
       100.0 * SUM(spend_usd) / (SELECT SUM(spend_usd) FROM procurement_transactions) AS spend_share_pct
FROM procurement_transactions GROUP BY supplier ORDER BY spend_usd DESC;

SELECT month, SUM(spend_usd) AS monthly_spend_usd
FROM procurement_transactions GROUP BY month ORDER BY month;
