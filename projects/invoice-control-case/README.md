# Invoice exceptions and cash control

New synthetic portfolio case, October 3, 2026. Created with AI assistance; proposed owners are simulated roles, not positions Quincy has held. This case does not recover the missing records from the archived Tableau dashboard.

[Public case study](https://quincy-jones-analytics.gzsxwzqv7q.chatgpt.site/invoice-control-case) · [Decision memo](../completed-control-cases/Invoice_Controls_Decision_Memo.pdf) · [Full source CSV](../completed-control-cases/source/new_supplier_invoices.csv) · [Audit](../completed-control-cases/case_audit.json) · [Definitions and reproduction](../completed-control-cases/README.md)

Both new cases passed 1,197 record and reconciliation checks. The pricing model separates contribution from gross margin and includes a severe volume-loss scenario. Invoice review distinguishes duplicate candidates, confirmed repeats, cleared candidates, missing evidence and paid/unpaid actions. Realized recovery remains zero.

The source builder uses Python standard-library modules plus reportlab. Numerical/data reproduction works without font files; the full downloadable package supplies fonts for identical memo layout. Native Tableau rendering/publication and desktop Microsoft Excel testing remain outside the observed scope.
