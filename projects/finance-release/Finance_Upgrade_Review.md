# Quincy Jones — finance portfolio upgrade review

**October 3, 2026 · Reviewed finance release · Tableau projects: HOLD**

The integrated operating plan, after-tax fleet investment model, 26-week liquidity model and corrected synthetic pairs research are built and internally audited. **469 checks passed**: 318 independent financial checks, 117 spreadsheet input/sensitivity checks and 34 trading checks. Base-case formula-error scans found no matches. All 28 sheets were rendered and reviewed, with affected assumptions and nine memo pages visually inspected after updates.

A separate LibreOfficeDev 26.8 opening/save reproduced **2,134 numeric base-case formula caches with zero differences**. This verifies a second spreadsheet engine, not desktop Microsoft Excel or every Excel feature. Selected scenario inputs and all newly added editable constant drivers were tested for missing/invalid values in the authoring engine. A fixed 26-week horizon and linked cash-floor display now identify their noneditable roles.

The verified finance components passed the release checks and are prepared for publication with synchronized models, memos, charts, case text and audit evidence. These are independent, AI-assisted synthetic cases, not employer results, approved financing or executive employment experience. The two Tableau projects remain excluded from featured audited finance work because their transaction-level populations cannot be verified. No claim is made that every external Tableau or Kaggle publication has been repaired.

## Decision memos

### Operating plan — address downside funding before committing spending

The base full-year 2026 operating view (synthetic H1 actuals plus H2 forecast) produces $11,308,100 revenue, $124,447 EBITDA (1.10% margin) and $508,855 ending cash. Minimum monthly cash is $279,760. Closing debt is $540,000. All six monthly balance sheets reconcile within the tested tolerance.

The downside produces a $616,492 EBITDA loss and negative ending cash of $14,908. Against the proposed $250,000 minimum cash reserve, that implies a $264,908 shortfall. Negative modeled cash denotes unmet funding, not an approved overdraft. The upside ends with $697,166 cash and $534,147 EBITDA.

The build now links credit collections, supplier payments, asset additions, depreciation, interest, principal repayment and simplified tax-loss offsets to the income statement, cash flow and balance sheet. Opening balances are explicit synthetic assumptions. Retained earnings follows the opening balance sheet; it is not a plug that forces forecast balances to reconcile.

**Proposed ownership:** finance validates opening cash, AR/AP, debt and collection history before approval; operations validates volumes and costs; management approves spending and a downside funding response. Review monthly actual-versus-plan cash and EBITDA. Escalate whenever forecast cash falls below $250,000. These are proposed roles, not positions Quincy has held.

**Limits:** no inventory, deferred tax accounting, dividends or new borrowing. Opening tax losses are zero and future losses are assumed fully usable. Collection patterns and asset lives require real-source validation. Earlier operating cash results are superseded because the working-capital and opening-balance scope changed.

### Fleet investment — lease is narrowly favored under the modeled tax assumptions

Five-year base after-tax present-value costs are $1,674,901 for keeping the fleet, $1,447,379 for replacing it, and $1,441,461 for leasing. Lease savings versus keep are $233,440; replacement savings are $227,522. Leasing leads replacement by only **$5,918**. This small difference is a reason to validate quotes and assumptions before authorizing either alternative.

Replacement requires $685,500 unlevered initial outlay, within the synthetic $700,000 budget. The new build includes old tax basis, disposal taxes, new-asset depreciation, transition costs, mileage allowance and excess-mile charges. Purchase-loan draw, principal, interest and fee are separate from unlevered valuation. A simplified lease-obligation roll-forward is included; this is not a full accounting-standard lease classification or financial-statement implementation.

**Proposed ownership:** procurement obtains comparable purchase and lease quotes; fleet operations validates mileage and downtime; finance validates tax usability, residual values and financing terms; management approves the alternative and spending envelope. Reassess after quote changes, mileage shifts, or inability to use deductions immediately.

**Limits:** immediate full use of modeled tax deductions is assumed. The hypothetical loan is not approved financing. Retire the earlier pre-tax replacement recommendation when presenting this expanded after-tax case. Nine sensitivity combinations were checked against the active build in the spreadsheet engine; desktop Excel behavior remains unverified.

### Liquidity — distinguish collection action from added revenue assumptions

The horizon now covers 26 weeks, October 5, 2026 through March 29, 2027. Deferred week-14 capex is paid inside the forecast. Opening invoices and newly issued credit invoices are separate, with distinct IDs and collection dates.

The base case needs no revolver draw and has minimum funded cash of $178,981. A two-week receipt delay requires peak debt of **$105,247** to maintain the $100,000 cash floor, within a hypothetical $200,000 commitment. The mitigation case has the same peak debt and lower modeled funding costs ($862 versus $1,022). It does not eliminate the earliest funding need. The facility is an assumption, not a bank commitment.

Week-26 cash is $1,160,500 in base, $975,978 in delay and $976,138 in mitigation. Future outstanding AR is $184,000 in base and $368,000 in the delayed cases. These larger ending balances depend heavily on the **new $92,000 weekly credit-billings assumption**, separate from opening AR and direct cash sales. Do not attribute the change from the old 13-week model solely to collection improvements or capex deferral.

**Proposed ownership:** treasury validates bank balances and facility availability; AR staff validates due dates and customer promises; operations validates supplier, payroll and capex timing; management approves borrowing and spending changes. Review weekly; escalate residual funding shortfalls or commitment exhaustion immediately.

**Limits:** no bank underwriting, covenant package, vendor financing or real customer behavior is established. Interest uses opening weekly debt, with a simplified annual-rate/52 convention. The undrawn commitment fee is modeled explicitly. With no facility, the delay case exposes a funding shortfall rather than concealing it.

### Pairs research — corrected accounting materially changes reported results

The revised two-leg ledger uses actual shares, prior-held positions for mark-to-market, traded-dollar costs, short borrow, positive financing exposure, marked-equity returns and terminal liquidation. Rolling fits exclude the current observation. Mutation of future prices leaves earlier outputs unchanged.

On the preserved synthetic path, base ending equity is $112,223.66 from $100,000 capital (12.22% simulated return). Stress return is −2.06%; stress with the monitor is −0.27%. Stress drawdown is −9.89%, versus −8.25% with the monitor: a **1.65 percentage-point** modeled reduction. Retire the previous 28.48% to 12.49% drawdown claim.

**Limits:** synthetic prices; fills at the observed close; no execution latency, additional slippage, real borrow availability, corporate actions or real-market validation. This is research, not a live strategy or realized investment track record. Funding costs are zero in the standard cases but a higher-exposure test confirms the funding calculation activates.

## Tableau source audit

| Artifact | Evidence inspected | Finding | Release requirement |
| --- | --- | --- | --- |
| Industrial Product Pricing & Discount Economics | Downloaded TWBX, workbook XML and embedded CSV | CSV contains six product-family summaries, not 480 transaction records. The extract contains six rows matching the CSV. | Obtain transaction-level source and reconcile it to the extract and chart, or explicitly publish a six-family summary-only analysis. |
| Supplier Invoice Controls & Recovery Audit | Public chart; attempted workbook export | The 700-invoice population, exception classification and exposure totals could not be reconciled to source rows. Export did not produce a usable source file. | Obtain invoice-level data, workbook and exception methodology; reconcile population, duplicate groups, payment status and overlapping exceptions. |

Pricing summary revenue is $350,825,023.86 and contribution is $151,661,750.26. Their ratio is **43.2300%**. Product-level contribution/revenue ratios differ from the existing `Avg Gross Margin Pct` field. This is not sufficient evidence that the average is wrong: gross-versus-contribution definitions and unweighted-versus-weighted averaging may differ. The chart sums already aggregated average percentages; that is fragile if more than one summary row exists per family.

For a revenue-weighted contribution margin, use Tableau calculation `SUM([Contribution USD]) / SUM([Revenue USD])`, format it as a percentage and label it **Contribution margin (weighted)**. Do not relabel the existing average as this measure without changing the calculation. Verify actual field names in the workbook. Weighted discount needs transaction list-price and discount dollars; it cannot be recovered faithfully from six average-discount figures.

Supplier controls must distinguish *candidate duplicate*, *confirmed duplicate*, *unpaid preventable exposure*, *paid potential recovery* and *realized recovery*. A missing PO or receipt mismatch is a control exception, not automatically a recoverable loss. De-duplicate overlapping exception exposure and document confidence/false-positive handling. Do not fabricate raw records to satisfy the claimed population.

## Public-source review and dated scope

| Model | Verified evidence / dated basis | Required treatment |
| --- | --- | --- |
| JBHT valuation | FY2025 diluted weighted-average shares 97.688 million; Q2 2026 diluted weighted-average shares 94.944 million; H1 2026 diluted weighted average 95.073 million; June 30 point-in-time shares 93.914939 million. | Identify the chosen share-count basis explicitly. Q2 EPS weighted-average shares are not a current spot fully diluted count. Do not silently combine June debt/cash with a December valuation bridge. The existing model has not been rolled forward in this package. |
| Trucking cost benchmark | ATRI's official 2026 news summary reports $2.336 per mile for 2025, versus the earlier model's $2.260 for 2024. Full 2026 report/components were not retrieved. | Keep older component assumptions dated; do not invent a new component breakdown. At the retained 16.8% screening margin, 500 miles at $2.336 implies a $1,403.85 screening quote, not a validated customer price. |
| Transit peers | FTA annual-data index was checked; 2024 annual files remain visible. | Keep annual cost/service comparisons matched to their periods. Do not mix 2026 monthly ridership with 2024 annual expenses. New annual datasets have not been fully re-audited here. |
| SaaS comparables | Salesforce FY2026, ServiceNow FY2025 and Adobe FY2025 filings were rechecked against the existing annual input table. | Revenue, prior revenue, cost of revenue, CFO and capex match the cited statements. The comparison remains annual-period analysis, not a current-quarter update. |

SaaS sources: [Salesforce FY2026](https://www.sec.gov/Archives/edgar/data/1108524/000110852426000060/crm-20260131.htm), [ServiceNow FY2025](https://www.sec.gov/Archives/edgar/data/1373715/000137371526000007/now-20251231.htm), [Adobe FY2025](https://www.sec.gov/Archives/edgar/data/796343/000079634326000003/adbe-20251128.htm).

Sources checked: [JBHT FY2025 10-K](https://www.sec.gov/Archives/edgar/data/728535/000143774926005294/jbht20251231_10k.htm), [JBHT Q2 2026 10-Q](https://investor.jbhunt.com/~/media/Files/J/jb-hunt-ir/financial-reports/financial-statement/2026/Q2.pdf), [ATRI official news index](https://truckingresearch.org/about-atri/atri-news-and-media/), [FTA NTD data](https://www.transit.dot.gov/ntd/ntd-data). Data periods above are distinct from the October 3 review date.

## Exact portfolio and resume wording

Use these bullets only for the **Independent Finance Projects** section; do not put simulated results under employer achievements. They describe the delivered work, not realized business impact.

- Built an integrated six-month operating forecast linking working capital, debt, depreciation, cash flow and balance sheet across three synthetic scenarios; reconciled every forecast balance sheet.
- Compared keep, replace and lease alternatives using a five-year after-tax model with disposal taxes, mileage charges and separate purchase financing; tested nine discount-rate and maintenance combinations.
- Extended a synthetic cash forecast to 26 weeks with invoice-level collection schedules, deferred capex, revolver draws, repayment, interest and commitment fees; modeled a $105,247 peak funding requirement under delayed receipts.
- Rebuilt synthetic pairs research with two-leg share accounting, rolling historical fits, turnover costs and marked-equity returns; verified ledger reconciliation, future-data isolation and terminal liquidation.

Correct employment entry to **US Foods | Dispatch / Route Builder | 2020–2022**. Correct education dates to **University of Phoenix | March 2014–June 2016**; list the field or qualification only if confirmed. Do not infer degree completion from attendance. These are exact replacements based on the user's corrections; the live Google resume has not been edited in this upgrade.

Suggested portfolio introduction: “Independent finance projects combining transportation operations context with forecasting, investment appraisal, liquidity planning and reproducible research. Each case documents its assumptions, decision implications, proposed owners and validation limits. Synthetic business cases and simulated trading results are clearly identified.”

These projects now present a stronger decision-analysis structure. They should support analyst-level applications; the artifacts alone do not establish executive-level professional responsibility, employer savings or a school pedigree. Credibility comes from transparent scope, sound calculations and clear ownership of the research.

## Release disposition

- **Completed:** integrated schedules; tax/financing/mileage fleet additions; 26-week cash and capex timing; trading ledger repair; missing/invalid new constant-input controls; source review of the cited SaaS annual data; synchronized memo/chart/case wording; preserved dated JBHT, transit and freight model scopes.
- **Completed engine checks:** authoring-engine financial/input/sensitivity checks and a separate LibreOffice base-case cache comparison. Desktop Microsoft Excel remains untested and no Excel application certification is claimed.
- **Tableau HOLD:** pricing CSV and Hyper agree on six product-family summaries; original 480 transactions are not present. Supplier workbook download did not return a usable source file, and its View Data window could not be connected through the browser. The claimed 700 invoices, classification and overlapping exposure cannot be certified.
- **Source freshness:** the public benchmark/valuation cases remain explicitly dated. They have not silently become current-quarter models. The new ATRI headline benchmark does not supply a new component breakdown.
- **Publication scope:** expanded finance cases, corrected research download and clear external Tableau hold disclosures. Existing legacy audit evidence is preserved as historical. A successful deployment receipt, recorded separately, establishes publication; this review does not assert an unobserved deployment.

To complete the Tableau audit, provide the original transaction/invoice CSVs or a workbook containing those rows. No fabricated replacement populations will be used. The separate Red Cross application review provides exact role-specific resume replacements and an application-ready cover letter. The live Google resume is unchanged. The new /pricing-summary page publishes only the reconciled six-family summary; neither original Tableau workbook is represented as repaired or republished.
