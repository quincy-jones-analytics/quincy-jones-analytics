# Commercial Credit Underwriting Screen

## Executive brief

**Decision:** Which illustrative borrowers merit deeper diligence, and how resilient is repayment capacity under a revenue downside?

The case spreads synthetic borrower inputs into EBITDA, leverage, interest coverage, debt-service coverage, and a clearly labeled preliminary screen. It also tests a 10% and 20% revenue contraction.

## Files and method

- `data/synthetic_borrower_inputs.csv`: three fictional borrower profiles and key debt assumptions.
- `outputs/borrower_credit_screen.csv`: leverage, coverage, simplified debt capacity, and triage outcome.
- `outputs/downside_sensitivity.csv`: debt-service coverage after revenue shocks.
- `outputs/credit_memo.txt`: a short diligence-oriented summary.
- `sql/analysis.sql`: SQLite queries for screening and downside review.

DSCR proxy = (EBITDA − maintenance capex) ÷ (cash interest + scheduled principal). The 3.0x debt capacity is an illustrative screen, not a lending policy.

> **Synthetic demonstration:** All borrowers and financials are fictional. Results are not credit approvals. Actual underwriting requires validated statements, normalized earnings, working-capital needs, collateral, covenant definitions, guarantor review, and repayment analysis.

Run `python3 build_case.py` with Python 3.10+ and the standard library.
