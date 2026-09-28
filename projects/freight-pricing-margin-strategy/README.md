# Freight Pricing & Margin Strategy

## Executive brief

**Decision:** Where should a pricing leader review rate floors, protect contribution, or test market headroom?

This case analyzes 960 synthetic freight bids across six lanes. It pairs quote context with estimated trip cost and simulated award outcomes, then compares current quoting levels with a transparent cost-plus reference at a 20% contribution margin.

> **Synthetic demonstration:** Bid records, rates, costs, and award outcomes are generated examples. They are not customer information, market quotes, employer performance, or realized pricing results.

## Decision snapshot

Run `python3 build_case.py` to create a lane scorecard and executive summary.

| Modeled measure | Result |
|---|---:|
| Bids / awards | 960 / 535 |
| Modeled win rate | 55.7% |
| Awarded revenue | $409.8K |
| Awarded contribution | $89.4K |
| Weighted contribution margin | 21.8% |

The lowest modeled awarded margin is Detroit–Cleveland at 13.0% (96 awards from 160 bids). The cost-plus reference is 8.7% above its average quote, making that lane a candidate for cost validation and a controlled rate-floor test. Review modeled win rate and customer context with the margin; this is not an automatic quote instruction.

## Method

- Creates a fixed-seed bid history with lane, customer tier, quote, market reference, estimated operating cost, and award flag.
- **Contribution** = awarded quote − estimated cost.
- **Weighted margin** = total awarded contribution ÷ total awarded revenue.
- **Target price** = estimated cost ÷ (1 − target margin).
- Simulated award probability varies with quote-to-market position and a simple tier effect; it is illustrative and is not a fitted demand model.

## Files and reproduction

- `build_case.py` regenerates all synthetic records and outputs; standard library only, Python 3.10+.
- `data/synthetic_bid_history.csv` contains 960 bid records.
- `outputs/lane_pricing_scorecard.csv` combines win rate, contribution, observed modeled margin, and target-price scenario.
- `outputs/executive_summary.txt` summarizes the case.
- `sql/analysis.sql` contains SQLite queries for lane economics and the target reference price.

```bash
python3 build_case.py
```

Load the generated input into SQLite as `bids` before running the SQL.

## Leadership guardrails

Validate accessorial capture, empty miles, fuel terms, shipment mix, and account-level contract provisions before using any rate comparison. Pair price realization with win rate, retention, service, and contribution. Any live test should have a defined segment, holdout or comparison design, floor/ceiling, owner, and stop condition. This model excludes elasticity, customer lifetime value, competitor response, network effects, and negotiation dynamics; it is not a production pricing engine.
