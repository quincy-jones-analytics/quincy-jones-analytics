# Quincy Jones — finance decision portfolio

Three synthetic cases with editable Excel models, decision memos, approval conditions, proposed ownership, action trackers and simulated follow-up:

- `Operating_Plan.xlsx` / decision memo: profit and cash under volume, price and cost scenarios.
- `Fleet_Investment.xlsx` / decision memo: keep, replace or lease; capital eligibility and native two-input sensitivity.
- `Cash_Working_Capital.xlsx` / decision memo: invoice-level 13-week liquidity, delayed collections, mitigation and remaining funding needs.

Read `Quincy_Jones_Project_Forensic_Audit.md` before using a result. Historical actuals in these cases are synthetic. No employer savings, financial approval, executive position or credential award is implied.

## Review and use

1. Read the memo’s requested decision and conditions.
2. Open the model; Assumptions D5 selects cases 1–3. Blue inputs are editable. Recalculate.
3. Trace Summary → operating schedules → assumptions/source; inspect Audit differences.
4. Update Actions only with actual approval/evidence. The Review sheet is a separate synthetic monitoring exercise.
5. Run `python3 reproduce_financial_results.py` to verify the original released scenarios using only Python’s standard library. Changing workbook assumptions also requires adapting verifier scenario assumptions; the original verifier is an audit of this release, not a general Excel engine.
6. Web/PDF comparisons are dated captures. Refresh them after any edit.

## Ownership / interview preparation

Quincy authored the independent portfolio work, with AI-assisted model construction and review. Proposed Finance, Treasury, Procurement and Operations roles are simulation participants.

Be ready to explain why volume and unit margin interact; why working capital differs from profit; why cash timing is not savings; why fleet NPV ranking changes; and why a funding floor breach is not an approved credit line. Trace a result live in Excel before using it in an interview.

## Exact optional portfolio resume bullets

- Built an operating-plan case preserving 18 synthetic H1 segment records and modeling H2 volume, pricing and cost assumptions; reconciled EBITDA drivers and a July–December cash forecast across three scenarios.
- Evaluated five-year keep, replace and lease fleet alternatives with a capital limit and native two-input sensitivity; identified a base-case replacement preference and a fuel-shock case favoring leasing.
- Built a 13-week invoice-level cash forecast using 26 synthetic receivables; modeled collection delays and mitigation while retaining remaining funding needs and beyond-horizon obligations.

These describe portfolio analysis, not employer implementation. Put them under Portfolio Projects.
