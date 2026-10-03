# Reviewed finance upgrade

October 3, 2026. Three expanded synthetic finance models, current decision memos, corrected synthetic pairs notebook, audit evidence and source code. Read Finance_Upgrade_Review.md for scope. External Tableau transaction-level claims remain on HOLD. No actual employer outcomes, approved financing or live investment performance are claimed.

## Reproduce

Run `python source/audit_upgrade.py` for the standard-library independent finance checks. Run `python source/repair_pairs.py` with numpy/pandas/matplotlib for trading ledgers and tests. The executed notebook writes its own `pairs_trading_outputs` folder.

Workbook construction and input tests require the runtime-provided `@oai/artifact-tool` package. With it resolvable by Node, run `node source/build_models.mjs` and `node source/test_upgrade.mjs` from this directory, or set `QUINCY_FINANCE_DIR` to it. This proprietary runtime dependency is not claimed to be a public npm package.

Web/PDF comparisons are dated sequential recalculation captures. Desktop Microsoft Excel was unavailable; authoring-engine checks and 2,134 LibreOffice numeric base-case cache matches establish only the stated engine scope.

The fixed horizon is 26 weeks. Expanded editable inputs have validated outputs; missing or invalid drivers expose unavailable values. Original invoice and transaction records are still required for a transaction-level Tableau audit. `SHA256SUMS.txt` identifies the package contents.
