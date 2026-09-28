-- Load output CSVs as normalized_gl, journal_balance_checks, and close_exceptions.
SELECT journal_id, debits_usd, credits_usd, difference_usd
FROM journal_balance_checks WHERE balanced_flag = 0;

SELECT account_group, SUM(net_debit_usd) AS net_debit_usd
FROM normalized_gl GROUP BY account_group ORDER BY account_group;

SELECT severity, control, COUNT(*) AS exception_count,
       SUM(ABS(exception_usd)) AS gross_exception_usd
FROM close_exceptions GROUP BY severity, control ORDER BY severity;
