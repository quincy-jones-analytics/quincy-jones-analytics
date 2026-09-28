# ERP-Style Close Controls and BI Dataset

## Executive brief

**Decision:** Which ledger exceptions need resolution before close, and can leaders trust the reporting layer?

This case simulates a small general-ledger export, maps source account codes to reporting groups, tests journal balance, and produces an exception queue plus normalized, BI-ready data.

## Files

- `data/synthetic_erp_gl_extract.csv`: fictional journal-line export.
- `outputs/normalized_gl.csv`: normalized rows and debit/credit sign convention.
- `outputs/journal_balance_checks.csv`: debit-credit control by journal.
- `outputs/close_exceptions.csv`: prioritized unmapped-account and out-of-balance items.
- `outputs/close_summary.txt`; `sql/analysis.sql` for close review.

> **System boundary:** The export resembles common ERP fields for demonstration. No NetSuite, Coupa, or other live ERP integration was used. Treat it as a simulation of an analytics workflow, not production-system experience.

Run `python3 build_case.py` with Python 3.10+ and the standard library. A real deployment would require role-based access, source lineage, approved account mappings, close-calendar controls, and reconciliation to subledgers.
