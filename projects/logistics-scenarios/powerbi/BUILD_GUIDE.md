# Power BI build guide

This is a CSV/DAX report build package. No native `.pbix`, deployed report, or Power BI Desktop validation is claimed. Python and SQL are tested; DAX still needs verification in Desktop.

## Import and types

Use Get Data > Text/CSV. Import the following with the exact table names:

| File | Table | Grain | Numeric fields |
|---|---|---|---|
| `data/transportation_shipments.csv` | Shipments | Shipment ID, 1200 rows | Distance, weight, stops, all USD fields; on_time/service_exception whole number |
| `data/diesel_benchmarks.csv` | Diesel | Region/date, 11 rows | usd_per_gallon decimal |
| `outputs/ocean_scenarios.csv` | Ocean | Case, 3 rows | All fields except case decimal |
| `outputs/air_scenarios.csv` | Air | Scenario ID/aircraft, 18 rows | All except ID, aircraft, feasibility decimal |
| `outputs/vendor_risk.csv` | VendorRisk | Vendor ID, 4 rows | risk_score and bounds decimal; preserve blank as null |

Use ISO date parsing for Shipments[ship_date] and Diesel[observation_date]. Keep IDs and labels as text. Disable automatically inferred relationships: these are separate facts, not related transactions. Do not join ocean or air examples to the shipment table. If time analysis is added, a calendar relates only to Shipments[ship_date]. Synthetic shipments include a full-year example, including future dates; they are not year-to-date actuals.

Create disconnected FuelShock and TargetMargin calculated tables from the expressions at the top of `measures.dax`, then create its measures separately. Format ratios as percentages, erosion as a number of **percentage points**, and costs as USD. Set slicers to single select; clear selection/multiple selection should show blank scenario measures rather than aggregate alternative cases.

## Four report pages

1. **Fuel and pricing:** single-select Diesel[region], FuelShock[shock], TargetMargin[Value] with Midwest, 0, and 0.18 defaults. Add lane/date/mode filters from Shipments. Cards: contribution margin, contribution/load, break-even rate and target rate. Matrix rows lane; measures revenue, scenario fuel, contribution and on-time rate. The same fuel price applies to the filtered population as a counterfactual; it is not a mapping of actual purchase location. Display the normalization definition beside the visuals.
2. **Ocean disruption:** single-select Ocean[case], default Disruption. Cards: incremental carry, contribution, margin and erosion PP. A comparison matrix with case rows can display all three cases. Do not total the alternatives. Inputs are edited in assumptions.json, rebuilt with Python, then refreshed in Desktop; the browser dashboard has additional interactive inputs.
3. **Air cargo:** single-select Air[scenario_id], default D80-S20 (80 metric tonnes, 20% assumed reduction). Matrix aircraft rows: trip cost, payload use, fuel intensity and cost/tonne-mile. Include feasibility and source-date notes. Default route 6000 km and assumed costs are synthetic. Generated scenarios vary demand 60/80/100 t and assumed reduction 0/20/40%; the reference has no reduction. No sum across aircraft alternatives is meaningful. Disable matrix grand totals.
4. **Vendor risk:** table vendor name, risk score, lower/upper bounds, missing factor and review status. Cards: priority reviews and vendors missing evidence. Blank scores must say Incomplete rather than zero. Scores/weights are edited in source inputs and rebuilt. Fictional entities are not ratings of real employers, countries or vendors.

## Desktop acceptance checks

- Midwest/0% all lanes must reconcile with `fuel_scenarios.csv` summed at the same region/shock. Ratio must equal sum contribution / sum revenue, not average lane margins.
- Change shock to +10%; contribution falls by 10% of the filtered original fuel amount. Nonfuel cost and service rate do not change.
- Verify a lane filter updates dollars, shipment count and weighted ratios together. TargetMargin changes target rate but not contribution at unchanged revenue.
- Ocean Disruption adds $1000 freight and $657.534247 carrying cost; erosion is $1657.534247 and 9.208524 percentage points.
- Air D80-S20 shows $70500 reference trip cost and $67400 A350F modeled cost. Cost/tonne-mile is 0.2363724 and 0.22597872. No operational performance claim follows from these assumed costs.
- Vendor V04 risk remains null. Missing cybersecurity bounds are 48.5–73.5; evidence review stays visible.
- Clear a scenario slicer and verify the guarded measures do not sum alternatives. Check total rows, tooltip units, refresh types and blank preservation.

These are required handoff checks. They were not run in Power BI Desktop in this release.
