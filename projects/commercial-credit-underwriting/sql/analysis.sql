-- Load outputs as borrower_credit_screen and downside_sensitivity.
SELECT borrower, gross_leverage_x, interest_coverage_x, dscr_x,
       debt_headroom_usd, screen_outcome
FROM borrower_credit_screen ORDER BY dscr_x DESC;

SELECT borrower, revenue_shock_pct, stressed_dscr_x, dscr_below_1x_flag
FROM downside_sensitivity ORDER BY borrower, revenue_shock_pct;
