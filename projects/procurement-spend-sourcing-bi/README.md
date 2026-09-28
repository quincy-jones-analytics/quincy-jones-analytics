# Procurement Spend and Freight Sourcing BI

## Executive brief

**Decision:** Where should procurement investigate supplier concentration, contract coverage, and freight-rate opportunities?

The reproducible synthetic dataset supports monthly spend, supplier scorecards, category opportunity screens, and procurement review in BI tools.

## Files

- `data/synthetic_procurement_transactions.csv`: 96 fictional purchase orders across suppliers and spend categories.
- `outputs/supplier_scorecard.csv`: spend, PO count, supplier share, and contract mix.
- `outputs/category_opportunity.csv`: category spend and modeled benchmark gap.
- `outputs/monthly_spend.csv`; `outputs/executive_summary.txt`.
- `sql/analysis.sql`: reusable spend and sourcing queries.

> **System boundary:** This resembles a procurement extract but is not an actual Coupa, ERP, or TMS integration. Benchmark gaps are simulated screens, not realized or validated savings.

Run `python3 build_case.py` with Python 3.10+ and the standard library. Load the source CSV into Power BI or Tableau to build spend trend, supplier concentration, category gap, and contract-coverage views. The project documents a BI-ready workflow; it does not claim a deployed enterprise dashboard.
