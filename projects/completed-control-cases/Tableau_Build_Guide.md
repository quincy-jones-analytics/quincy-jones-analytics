# Native Tableau build from the new source populations

This guide specifies the new cases. Native Tableau workbooks have not been created, rendered or published by this package. The completed public case studies use browser charts and downloadable records/memos.

## Pricing

Connect to `source/new_pricing_transactions.csv`. TransactionID is a unique text key; Units and Cents fields are whole numbers; InvoiceDate is a date; DiscountBps is an integer. These are 480 newly generated January-June 2026 records.

Create these calculations:

```
Revenue USD = SUM([RevenueCents]) / 100
Contribution USD = SUM([ContributionCents]) / 100
Contribution margin (weighted) = SUM([ContributionCents]) / SUM([RevenueCents])
Discount rate (weighted) = SUM([DiscountCents]) / SUM([ListRevenueCents])
```

Build a family bar view for contribution, a family table for revenue/margin/discount, and a transaction-detail sheet with TransactionID. Format rates as percentages. COUNTD(TransactionID) must be 480, revenue $7,804,631.20, contribution $1,871,379.20 and contribution margin 23.9778043580%. Do not sum already aggregated percentages.

The memo's discount-cap scenarios are separate hypothetical results in pricing_metrics.json. They apply to the full eligible portfolio, not the smaller proposed pilot. Keep them labeled as scenarios; the continuous break-even unit-loss threshold is not measured customer elasticity.

## Invoice controls

Connect to `classified_supplier_invoices.csv`, which contains all original fields plus reviewed classifications for 700 newly generated postings. Use RecordID as the key. VendorInvoiceNumber intentionally repeats. Keep PurchaseOrderID and missing receipt evidence as meaningful blanks.

```
Gross review workload USD = SUM([GrossReviewCents]) / 100
Unpaid review workload USD = SUM([UnpaidReviewCents]) / 100
Paid confirmed potential recovery USD = SUM([PaidConfirmedPotentialRecoveryCents]) / 100
Unpaid confirmed potential avoidance USD = SUM([UnpaidConfirmedDuplicateAvoidanceCents]) / 100
Realized recovery USD = SUM([RealizedRecoveryCents]) / 100
```

Use PrimaryReviewCategory for a non-overlapping bar chart. Retain all individual flags and DuplicateReviewOutcome in a detail view. Whole-population controls: 700 unique RecordIDs; $1,061,832 total posting value; 121 flagged postings; $187,208 unique gross review workload; $128,781 unpaid review workload; $4,782 paid confirmed potential recovery; $7,006 unpaid confirmed potential avoidance; $0 realized recovery.

Twenty candidate groups contain 40 postings. Synthetic evidence confirms ten repeated postings, clears five valid installment groups, verifies ten original postings, and leaves five groups unresolved. Missing receipt evidence on two rows must stay in review. Paid/unpaid confirmed amounts are subsets of review workload; do not add them to workload or call them realized savings. Review evidence is synthetic and supplied separately.

## Before native Tableau publishing

Open the new workbook in Tableau, reconcile the controls above without filters, test family/supplier/payment-status filters, inspect tooltips and percentage formats, verify a reset restores full-population totals, and check desktop/mobile layouts. Publish under distinct new-case titles and disclose synthetic records. Preserve the old dashboards as archives. A native publication should be marked complete only after its rendered controls and live publication have been verified.
