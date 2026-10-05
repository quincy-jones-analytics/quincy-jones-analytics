# Validation results — October 5, 2026

## Completed

- **32 Python regression tests passed.** Coverage includes original 1200-row population and IDs, cost/revenue preservation, fuel shocks, weighted margins, per-load and rate reconciliations, unchanged nonfuel costs and service flags, input bounds, zero-price cases, baseline versus incremental ocean carry, air ranking reversals, range/payload ceilings, kilometre/mile conversion, vendor missing evidence, known zero scores, weight validation and threshold edges.
- **Independent SQLite views reconcile.** The test suite compares 198 region/shock/lane rows across five fuel metrics, three ocean cases across three metrics, 18 aircraft scenarios across three metrics, and four vendor ratings, including SQL NULL preservation. Comparisons use a 0.000001 tolerance for numeric outputs rounded to six decimal places.
- **23 dashboard JavaScript logic checks passed.** The shipped JavaScript was executed with a minimal DOM fixture in Node. Initialization, fuel shock/lane scenarios, invalid margin, ocean delay isolation, invalid delay, air defaults/ranking reversal/ceiling suppression, vendor missing/zero/invalid-weight cases, populated exports and restored error states were checked.
- Source URLs and dates for EIA and aircraft specifications were read on October 5, 2026. Public benchmarks are kept apart from synthetic operating inputs. The dated Boeing payload definition is retained and explained.

## Execution limits

Native browser rendering, mobile layout, click event delivery and browser file downloads were **not verified**. A native Chromium executable was unavailable and its download failed. `tests/browser_validation.cjs` contains browser acceptance checks and screenshot steps for a machine with Playwright and Chromium. The dashboard arithmetic checks are not a substitute for visual/browser testing.

Power BI Desktop is unavailable. DAX, slicers, native visual behavior and refresh have not been executed there. `powerbi/BUILD_GUIDE.md` includes concrete acceptance values and blank/total checks. No `.pbix`, published Power BI Service report, Tableau dashboard, live data refresh or employer deployment is claimed.

## Reproduce checks

```bash
python3 build_models.py
python3 -m unittest discover -s tests -v
node tests/dashboard_logic.cjs
# Optional, requires Playwright and a supported Chromium installation:
node tests/browser_validation.cjs
```

The tests use defined sample-case acceptance values. When changing the example's default assumptions, update the affected golden expectations deliberately; do not suppress a failed reconciliation.

The package retains source CSVs and a hash register. Future publication of a native report should include browser or Desktop validation, actual-input provenance where applicable, and an updated source snapshot.
