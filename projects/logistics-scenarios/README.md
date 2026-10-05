# Logistics scenarios: fuel, ocean, air cargo and vendor risk

**Quincy Jones · Independent portfolio extension · October 5, 2026**

Open `dashboard.html` in a browser to explore all four models and export the current scenarios. It works offline, with embedded sample data and no external scripts. The GitHub file view shows source code; download the file or package to use the dashboard.

## Decisions supported

| Model | Decision question | Inputs and boundary |
|---|---|---|
| Fuel and pricing | How much contribution is exposed to regional diesel prices and ±10% shocks? | 1200 synthetic shipment values from the authoritative transportation case, plus EIA diesel snapshot. Cost-only sensitivity. |
| Ocean disruption | Is the cost of delay large enough to warrant a rerouting review? | Separate fictional ocean shipment with freight shock and incremental inventory carrying cost. |
| Air cargo | How do equal-demand mission economics change with fuel and nonfuel assumptions? | Published aircraft screening ceilings; assumed fuel, price, demand and other costs. |
| Vendor risk | Which dependencies need evidence or priority review? | Five-factor weighted rubric and fictional vendors; missing evidence cannot become a zero-risk score. |

Public benchmarks are sourced; operating records and outputs are synthetic or modeled. These are not employer data, observed air performance, actual quotes, realized savings or real-vendor risk ratings.

## Run and inspect

Requires Python 3.10+ with only standard-library modules:

```bash
python3 build_models.py
python3 -m unittest discover -s tests -v
```

The build reads editable `data/assumptions.json`, CSV inputs and the dashboard template. It writes four result CSVs, an embedded browser dashboard, dashboard JSON, input hashes, and a SQLite database. Open `outputs/scenarios.sqlite` to query `fuel_model`, `ocean_model`, `air_model`, and `vendor_model`. Views independently reproduce core arithmetic. The optional browser validation uses Playwright; it is not needed for model regeneration.

## Definitions that matter

**Fuel:** Implied gallons = original synthetic fuel dollars / Midwest diesel $6.526 per gallon. Scenario fuel = implied gallons × selected region price × (1 + shock). This is an explicit normalization assumption, not a historical fuel calibration: the original shipment generator had no gallons or weekly purchase price. Midwest/0% preserves original cost values. Revenue, volume, nonfuel costs and service flags stay fixed. Weighted margin = sum contribution / sum revenue. Contribution/load = contribution / count. Break-even rate = direct cost / loaded miles; target rate = direct cost / (1 − target margin) / loaded miles. Empty miles, overhead and corporate allocations are absent. All lanes, including Toronto, share the chosen counterfactual US retail benchmark; no Canadian price mapping is implied.

**Ocean:** Baseline carry = inventory value × annual carry rate × baseline days / 365. Extra carry uses extra days only. Total cost = other shipment costs + shocked freight + baseline carry + extra carry. Margin erosion compares each case to the identical inputs at no shock/no extra days. Inventory value is the carrying-cost base, not an additional expense added to shipment cost. The example does not reconcile inventory value to this fictional service revenue; it is a logistics cost exposure model, not a product gross-margin statement.

**Air:** Cost = assumed kg fuel × assumed USD/kg + assumed nonfuel trip cost. The A350F fuel-saving percentage and nonfuel premium are user assumptions. Both examples serve the same modeled demand, when within ceilings. Metric tonnes, statute miles and kilometres are kept distinct (1 mile = 1.609344 km). Published maximum payload/range are necessary screening limits, not a joint payload-range performance curve. Above either ceiling, unit economics are withheld and mission review is required. Air fuel calculations are a single-route scenario; distance changes the transport-work denominator, not the assumed trip fuel. Re-enter mission fuel whenever distance changes. No fleet investment recommendation is supported without flight, utilization, maintenance, leasing, financing, ULD, runway and certification data.

The Boeing reference uses its July 2, 2024 release: 102 t maximum payload and 9200 km range. Current Boeing pages use a 107 t gross structural definition; the benchmark intentionally retains its dated definition. Airbus's September 29, 2026 release supplies 111 t and 8700 km and identifies flight testing. The manufacturer's up-to-40% claim is not imported as measured performance or as a 777F-specific comparison. The default 20% is explicitly hypothetical; test 0% as well.

**Vendor:** Factors: ownership/governance, data access, cybersecurity, route concentration and operational dependency. Default weights 15/20/25/20/20%. Each score 0–100, greater = more risk. Ownership is governance/change-of-control clarity, not nationality. Weights must total 100%. 70+ = priority review; 40–69.99 = review; below 40 = monitor. Missing factors produce no final score; lower/upper bounds substitute 0/100 for missing factors. The rubric prioritizes evidence, not failure probabilities. No current news event assigns a risk rating to a real company.

## Example findings, not realized outcomes

- A 10% diesel rise lowers modeled contribution by exactly 10% of baseline fuel cost at Midwest prices. Use the lowest-margin lane to discuss a pricing review alongside reliability.
- Ocean +25% freight/+10 days adds $1657.53: $1000 freight and $657.53 carry. It erodes margin by 9.21 percentage points on the fictional $18000 revenue.
- Equal 80 t demand over 6000 km yields modeled trip costs $70500 reference and $67400 A350F at a hypothetical 20% fuel reduction and $5000 nonfuel premium. At 0% reduction, the A350F example costs $75500 and reverses the ranking.
- Sample Platform D has no complete score until cybersecurity evidence arrives. Its possible score spans 48.5–73.5, so missing evidence could conceal a priority review.

## Portfolio integration

This extension complements [Freight Pricing Benchmark Calibration](https://github.com/quincy-jones-analytics/quincy-jones-analytics/tree/main/projects/freight-pricing-calibration) and [Transportation Profitability & Service Reliability](https://github.com/quincy-jones-analytics/transportation-profitability-analysis). It preserves their existing models and definitions. Source shipment **values** are copied from the pinned authoritative case; line endings may differ. The ocean example is not relabeled as part of the existing trucking population. Vendor risk is a standalone control-tower extension with fictional IDs, ready for a future verified supplier-ID join.

## Power BI and interview handoff

`powerbi/BUILD_GUIDE.md` gives exact table imports, grains, filters, page layouts and expected results. `powerbi/measures.dax` provides guarded measures and disconnected scenario controls. No native PBIX or deployed Power BI report is included; DAX requires Desktop validation.

`INTERVIEW_NOTES.md` connects the work to dispatch, service reliability and finance without attributing portfolio outcomes to employers. `VALIDATION.md` reports automated checks and remaining execution limits. `data/sources.json` is the source register, including dates and scope. Source snapshots require manual refresh and validation; they are not live feeds.
