# Quincy Jones — project forensic review

Review date: October 3, 2026 (UTC). Release: finance decision cases, with corrections to existing public work samples.

## Release decision

Release the three new finance decision cases as **synthetic, independently reconciled portfolio work**. Publish the reviewed J.B. Hunt workbook/memo and freight-calibration presentation correction. Preserve the distinction between 960-shipment and 1,200-shipment cases. Keep unresolved pairs-trading research out of featured finance recruiting materials.

This is a technical and presentation review, not an independent audit opinion, verification of employer outcomes, or certification of professional credentials. A passing computation does not establish that assumptions are commercially achievable. Historical uploads and personal media outside the named project scope are not certified by this report.

## What was actually checked

| Scope | Evidence and result |
|---|---|
| Three new models / 22 worksheets / nine selected cases | 128 independent Python checks reproduce operating economics, fleet present values, cash timing, exported caches and reconciliation controls. All pass. |
| Live edits in imported new workbooks | 22 tests pass: selector changes, edited inputs, preserved H1 history, missing selected vs inactive drivers, capital limit, all nine native sensitivity cells, zero opening cash, and invoice-key uniqueness. |
| Eleven existing reproducible Python projects | Existing validation suite rerun: 9,616 checks pass. Many checks are finite-value / data-shape checks; the count is not 9,616 independent economic conclusions. |
| Existing project SQL | All 26 SELECT queries across the 11 projects execute successfully in their test fixtures. Query execution alone does not prove the intended business definition. |
| Current source reconciliation | 62 live GitHub Python, SQL and CSV files compared with the local audit snapshot: zero substantive changes after newline / trailing-whitespace normalization. Live blob SHAs retained in `live_source_manifest.json`. |
| Existing site downloads and case records | 2,072 published-asset checks pass, including 960 unique shipment IDs, row-level cost/profit checks, CSV-to-SQLite tie-out, SAP sample amounts, NTD ratios, SaaS economics, freight pricing, JBHT valuation bridge, current 1,200-shipment results and SQL. |
| Interactive arithmetic | Ten checks pass for Pricing Lab baseline/margin sensitivities and Control Tower normalized scores / zero weights / totals. UI assertions are separate from this arithmetic test. |
| Existing five Excel workbooks | Imported and recalculated; no matched formula-error values before or after the review. Targeted independent arithmetic checks listed below. |
| Visual / release checks | All 22 new worksheet renders and all nine new memo pages inspected. Reviewed JBHT assumptions/DCF/summary and one-page replacement memo inspected. Source validation checks links, anchors and JavaScript syntax before deployment. |

Evidence files accompany the download: independent audit, scenario captures, recalculation tests, published-asset audit, interactive checks, existing workbook review, source manifest, and validation logs. New-model checksums identify the exact reviewed release.

## Project-by-project disposition

| Project | Finding / verification | Release disposition |
|---|---|---|
| Transportation operating plan — NEW | H1 source preserved; H2 driver economics reconstructed; July variance bridge and July–December cash roll forward tie. Base full-year revenue $11,308,100, EBITDA $124,447 (1.1%); December cash $282,038. Downside ending cash is negative $145,022. | Feature, with cash/forecast limitations visible. |
| Fleet investment committee — NEW | Independent five-year cash flows reproduce each alternative in all three cases. All nine native sensitivity outputs equal individually selected model builds. Capital limit changes eligibility. Base replacement NPV gain vs keeping fleet is $373,698, but its PV cost advantage over leasing is only $15,208. Fuel-shock case favors leasing. | Feature; condition decision on quotes, taxes, service and liquidity. |
| 13-week working capital — NEW | Every one of 26 invoices is collected or carried beyond horizon; payments and cash tie. Delayed receipts need $175,000 to restore the $100,000 floor. Mitigation still needs $105,000 and carries $194,000 invoices plus $90,000 future capex. | Feature; negative unfunded cash is an exposure, not a feasible funded plan. |
| Transportation profitability / service reliability — CURRENT | Live `build_case.py`, CSV and SQL retrieved and rerun. Reproduced 1,200 synthetic shipments, $958,707 rounded revenue, 25.9% weighted contribution margin and 91.6% on-time rate. Detroit–Cleveland remains first margin-review priority. Four SQL queries execute and tie to independent aggregation. | Feature, with synthetic label and contribution definition. |
| Transportation profitability download — LEGACY | Separate 960-shipment package: $711,317.99 revenue; 20.9% gross margin and 92.3% on time. Row-level costs/profits, unique keys and SQLite revenue reconcile. | Retain as a distinct legacy demonstration; never attach 1,200-case metrics to it. |
| Pricing Lab | $940 baseline cost and $1,146 rounded price reproduced; gross margin calculated on selling price. Tested 5%, 18% and 35% targets. | Retain simplified scenario label and omitted lane-cost warning. |
| Freight benchmark calibration | $2.26/mile cost and 16.8% broker-margin screen produce $1,358.17 for 500 miles. Removed a redundant Calibration C6:O9 block with mismatched headers; retained C13:J15 operative build. Carrier cost and broker margin are different measures. | Publish corrected binary; do not present as a carrier quote or verified profit target. |
| Michigan NTD cost benchmark | Independently recomputed cost/trip, trips/hour, cost/mile and fare recovery for 15 peers; imported workbook error scan passes. | Retain dated nominal-cost and mode/service-type boundaries. Source extraction is not freshly certified by this review. |
| SaaS unit economics / pricing | Independently reproduced growth, gross profit/margin, simple FCF/margin and pricing break-even retention. 7% price lift breaks even at 93.46% retention; 95% yields 1.0165 revenue index. | Retain dated supplied public figures; differing fiscal periods and mixes prevent a like-for-like causal conclusion. |
| J.B. Hunt integrated valuation | Corrected terminal-value / share-proxy labels and added separate EV line. EV $15,687.20mm → equity $14,237.69mm → $149.96 per proxy share; valuation unchanged. Replaced memo’s diluted-share and credential wording. About 80% of EV is discounted terminal value. | Publish reviewed workbook and memo, with market snapshot September 29, 2026 and proxy limitations. |
| Legacy transportation FP&A dashboard | Imported/recalculated without matched formula-error values; separate older model. | Retain distinct download/version; new operating-plan outputs do not describe this binary. |
| Procurement spend / sourcing BI | Existing Python suite and SQL rerun pass; current source matches audit snapshot. Synthetic PO data and benchmark gaps remain review screens. | Retain as browser prototype; no ERP or Power BI deployment claim. |
| FP&A forecast / scenario planning | Existing Python suite and SQL pass; raw H1 data reused with traceable source in new operating model. | Retain; new model is a distinct, expanded release. |
| Fleet renewal capital budgeting | Existing suite and SQL pass; expanded decision case above adds constrained alternatives and sensitivity. | Retain distinct old/new versions. |
| Freight pricing / margin strategy | Existing suite and SQL pass. | Retain synthetic/data-scope boundaries. |
| Transportation network capacity | Existing suite and SQL pass. | Retain scenario decision interpretation; no implemented network saving. |
| ERP close controls BI | Existing suite and SQL pass. | Retain simulation; no real ERP configuration claim. |
| Monthly three-statement planning | Existing suite and SQL pass. | Retain synthetic planning scope and model conventions. |
| Commercial credit underwriting | Existing suite and SQL pass. | Retain illustrative underwriting; no lending approval or actual borrower outcome. |
| Corporate valuation DCF | Existing suite and SQL pass. | Retain distinct synthetic model; do not mix with JBHT filing-based case. |
| Monte Carlo option pricing | Existing suite and SQL pass. | Retain numerical demonstration; passing simulation checks is not a trading-profit claim. |
| Portfolio risk / factor attribution | Existing suite and SQL pass. | Retain synthetic analysis; no client portfolio management claim. |
| SAP MRP / P2P / FI–CO simulations | Six unique IDs per CSV. Four P2P review invoices sum to $8,406 gross queue value. Close expense $151,750 vs $151,500 budget; aged review balances $7,100. | Retain process simulations, proposed roles and evidence gates. Queue dollars are not overpayments, losses or savings. |
| Profit Leak Control Tower | Four-factor normalized scoring and all scenario weights tested. Removed claim that recovery cost enters ranking; it does not. Clarified recoverable value is gross synthetic expectation before recovery cost. Zero weights now prompt selecting a weight. Bundled HTML refreshed. | Publish corrected explanation and preserve synthetic status. |
| Legacy pairs-trading notebook | Earlier code review found fixed initial hedge fit described as walk-forward and log-residual changes compounded as returns. No fresh economic reconstruction of this notebook in this release. | HOLD from featured finance/quant recruiting until corrected two-leg P&L, capital basis, costs, terminal liquidation and backtest description are validated. |

## Critical decisions and boundaries

1. **Operating plan:** The base cash floor has only approximately $32,038 December headroom. Cash timing uses 30-day months, fixed 35-day receivables / 20-day variable-cost payables, and tax on positive monthly EBIT only. No financing, interest, dividend schedule, loss carryforward or complete balance sheet is modeled. Cash begins in July; H1 cash is unavailable.
2. **Fleet:** The appraisal is pre-tax. Downtime is an assumed cash exposure, not observed lost revenue. Fuel-shock case changes several inputs together; it is not causal fuel attribution. Leases are cash-cost alternatives, not lease-accounting schedules. Maintenance coverage and identical service output must be validated.
3. **Cash:** Capex deferral changes timing, not total cost. Invoice acceleration assumes consent and collection feasibility. No bank facility is assumed. Funding gaps describe capital requirements relative to the floor, not approved borrowing. Beyond-horizon invoices/capex stay visible.
4. **Monitoring:** All follow-up observations are separately labeled synthetic exercises. They are not employer actuals or demonstrated realized project benefits. Action statuses start Proposed; evidence is blank until supplied.
5. **Comparisons:** Excel contains one active case selector. PDF/web comparisons are three sequential recalculation captures dated October 3, 2026 UTC, not separate competing Excel builds. The web selector displays captures; it does not recalculate arbitrary inputs.

## Defects corrected before release

- JBHT enterprise-value / terminal-value distinction, share-count proxy label, explanatory note layout, stale memo credential and diluted-share wording.
- Freight calibration’s duplicate mismatched table block.
- Control Tower’s recovery-cost claim and zero-weight action prompt; downloadable HTML matches the page.
- New workbook summary contrast, sensitivity number formatting, complete 13-week table preview and full monthly schedule rendering.
- New-model mitigation preserves the collection delay, exposes remaining funding need, and carries deferred invoices/capex forward.

## What remains unverified

Desktop Excel was unavailable: artifact-tool recalculation and exported caches were tested, including the native sensitivity table, but application-level Excel behavior is not asserted. Open the final files in desktop Excel and recalculate before editing or external decision use.

This review does not establish current issuer data, current market prices, actual customer response, vendor quotes, financing availability, tax treatment, company feasibility, actual SAP transactions, Power BI deployment, credential awards, or employer performance. Existing public-data inputs retain their supplied dates and sources; this is not a fresh re-extraction of every underlying filing/NTD dataset.

Older uploaded images, videos, alternate project copies and unresolved quant research are not silently treated as validated. The prior career inventory remains the record of that broader upload review. Only the named release candidates are promoted here.

## Reproduction

Unzip the finance package and run `python3 reproduce_financial_results.py` using Python 3.10+. It reads the three exported XLSX files and recreates the independent numerical evidence with the standard library. Select Excel cases through Assumptions!D5 (1–3). Blue inputs are editable; green cross-sheet links and dark calculations form the model build. Refresh comparison documents after edits.

The source authoring scripts are included for transparency. Their optional Excel authoring path requires the OpenAI artifact-tool runtime; the standard-library verification path does not. Existing-source regression tests and published-asset checks require their separately named project fixtures; their captured logs do not imply that those fixtures are inside every individual case download.
