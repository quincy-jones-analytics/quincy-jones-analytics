# J.B. Hunt Three-Statement and DCF Valuation

An illustrative corporate-finance case applying three-statement forecasting, discounted cash flow valuation, sensitivity analysis and trading comps to J.B. Hunt Transport Services.

## Base case
At an 8.0% WACC and 2.5% perpetual growth rate, the DCF implies **$149.96 per share**, compared with a **$226.07** market snapshot dated September 29, 2026. The model sensitivity grid ranges from approximately $109 to $238 per share. This is a portfolio estimate, not company guidance or investment advice.

## Model contents
- Five years of SEC-reported historical financials (2021–2025)
- Linked income statement, balance sheet and cash flow forecast (2026E–2030E)
- Formula-driven DCF and WACC / terminal growth sensitivity grid
- Trading comps versus Old Dominion, C.H. Robinson and Landstar
- Editable assumptions, reconciliation checks, citations and limitations

## Deliverables


### Download directly from GitHub

- [Quincy_Jones_JBHT_Three_Statement_DCF.xlsx](./Quincy_Jones_JBHT_Three_Statement_DCF.xlsx)
- [Quincy_Jones_JBHT_Investment_Memo.pdf](./Quincy_Jones_JBHT_Investment_Memo.pdf)

- [Excel model](https://quincy-jones-analytics.gzsxwzqv7q.chatgpt.site/jbht-valuation/Quincy_Jones_JBHT_Three_Statement_DCF.xlsx)
- [One-page investment memo](https://quincy-jones-analytics.gzsxwzqv7q.chatgpt.site/jbht-valuation/Quincy_Jones_JBHT_Investment_Memo.pdf)
- [Portfolio case page](https://quincy-jones-analytics.gzsxwzqv7q.chatgpt.site/jbht-valuation.html)

## Sources
J.B. Hunt [FY2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/728535/000143774926005294/jbht20251231_10k.htm) and [SEC Companyfacts](https://data.sec.gov/api/xbrl/companyfacts/CIK0000728535.json). Peer fundamentals from SEC Companyfacts. Market inputs dated September 29, 2026.

The forecast simplifies working capital, other assets and liabilities, debt, taxes and share count. The case demonstrates forecasting, DCF mechanics, sensitivity analysis, and source reconciliation.


## Model review notes — October 3, 2026

The following issues were identified in the workbook reviewed during the portfolio audit. These notes disclose the issues; they do not represent a corrected workbook release.

- **DCF label:** Cell H7 says “Enterprise value,” while I7 calculates the undiscounted terminal value. H7 should read “Terminal value at year 5.” Enterprise value is the sum of discounted forecast cash flows and discounted terminal value.
- **Share-count label:** The assumption derived from market capitalization divided by price is an implied share-count proxy. It should not be labeled as a verified diluted share count. Reconcile it to an appropriate fully diluted share basis before interpreting per-share value.
- **Terminal-value dependence:** Approximately 80% of modeled enterprise value comes from discounted terminal value. WACC, perpetual growth, and terminal cash-flow assumptions require particular scrutiny.
- **Simplifications:** The model holds several balance-sheet items and share count constant. A more complete model would reconcile debt, buybacks, share count, and working-capital drivers.
- **Validation scope:** Independent arithmetic reproduced the cached base-case value of approximately $149.96 per share. This confirms the inspected calculation, not the economic reasonableness of the assumptions or the accuracy of every model cell.

These are historical portfolio assumptions and a dated price snapshot, not a current valuation recommendation.
