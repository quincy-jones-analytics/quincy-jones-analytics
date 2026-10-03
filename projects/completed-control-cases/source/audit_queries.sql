-- Values are integer cents. Candidate matching is a review signal, not proof of a duplicate.
SELECT COUNT(*), SUM(net), SUM(contribution) FROM pricing;
SELECT family, SUM(net) AS revenue_cents, SUM(contribution) AS contribution_cents,
       CAST(SUM(contribution) AS REAL)/NULLIF(SUM(net),0) AS weighted_contribution_margin
FROM pricing GROUP BY family;
SELECT COUNT(*), SUM(amount) FROM invoices;
SELECT supplier, number, amount, COUNT(*) AS candidate_count
FROM invoices GROUP BY supplier, number, amount HAVING COUNT(*)>1;
-- Keep receipt-null rows unresolved in real source data. Never treat NULL as a clean match.
SELECT * FROM invoices WHERE receipt IS NULL;
