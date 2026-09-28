# Transportation Network Capacity Planning

## Executive brief

**Decision:** Which node-weeks need a flexible capacity option before service risk rises?

This case builds a 52-week demand and capacity plan across five synthetic transportation nodes. It flags high-utilization periods, sizes an illustrative flex-capacity response, and compares its assumed cost with a simple service-risk proxy to structure an executive review.

> **Synthetic demonstration:** Demand, capacity, cost, and service-risk values are simulated examples. They are not company forecasts, operational results, or realized savings.

## Decision snapshot

Run `python3 build_case.py` to reproduce the node scorecard, weekly plan, and summary.

| Modeled measure | Result |
|---|---:|
| Network utilization | 91.5% |
| Node-weeks at or above 90% utilization | 165 of 260 |
| Modeled flex capacity used | 3,629 units |
| Flex capacity cost | $77.1K |
| Illustrative risk-cost proxy avoided | $561.8K |
| Net modeled benefit | $484.6K |

The pressure is broad across all five nodes, so the immediate executive question is whether to secure flexible capacity options and review the forecast weekly. Treat the risk proxy as a sensitivity, not a measured cost or investment return; validate forecast confidence, labor and equipment availability, and vendor terms before committing.

## Planning logic

- Five synthetic nodes × 52 weeks = 260 node-week records.
- **Utilization** = forecast demand ÷ available base capacity.
- The planning scenario stages flex capacity when forecast utilization exceeds 90%, capped at 12% of base capacity.
- **Illustrative risk proxy** = demand above a 90% utilization trigger × an assumed service-risk cost per unit.
- **Net modeled benefit** = modeled risk cost avoided − flex capacity cost.
- Weekly thresholds are prompts for review; they are not calibrated service commitments.

## Files and reproduction

- `build_case.py` regenerates inputs and decision outputs with deterministic assumptions; standard library only, Python 3.10+.
- `data/synthetic_weekly_demand_capacity.csv` contains the 260 modeled node-weeks.
- `outputs/weekly_capacity_plan.csv` provides the week-level decision view.
- `outputs/node_capacity_scorecard.csv` rolls up pressure, flex use, and scenario economics by node.
- `outputs/risk_cost_sensitivity.csv` shows the net modeled result at half, base, and double the assumed risk cost.
- `outputs/executive_summary.txt` summarizes network totals.
- `sql/analysis.sql` includes SQLite rollups and a high-utilization review queue.

```bash
python3 build_case.py
```

Load the generated input into SQLite as `capacity_plan` before running the SQL.

## Executive discussion and limits

Before authorizing real capacity, validate forecast bias, backhaul opportunities, labor availability, equipment constraints, service commitments, vendor quotes, and the cost of failure. Set a weekly review owner and escalation threshold, then compare forecast and actual utilization. The case does not model shipment-level network flows, routing optimization, stochastic lead times, contractual penalties, fixed investment, or causal service outcomes.
