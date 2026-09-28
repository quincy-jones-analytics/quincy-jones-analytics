#!/usr/bin/env python3
"""Build a reproducible synthetic freight pricing and margin case."""
from __future__ import annotations
import csv, random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA, OUT = ROOT / "data", ROOT / "outputs"
SEED, TARGET_MARGIN, N_BIDS = 20260928, 0.20, 960
LANES = {
    "Detroit-Chicago": (275, 2.10, 1.02), "Detroit-Cleveland": (170, 2.28, 1.08),
    "Detroit-Atlanta": (720, 1.88, 0.98), "Detroit-Toronto": (235, 2.36, 1.12),
    "Detroit-Nashville": (535, 2.00, 1.03), "Detroit-Indianapolis": (285, 2.04, 0.99),
}
FIELDS = ["bid_id", "bid_date", "lane", "customer_tier", "distance_miles", "weight_lb", "stops",
          "current_quote_usd", "market_reference_usd", "estimated_cost_usd", "awarded"]

def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

def build() -> dict:
    rng=random.Random(SEED); rows=[]; lane_names=list(LANES)
    tiers=["Strategic", "Core", "Transactional"]
    tier_discount={"Strategic":0.96,"Core":1.00,"Transactional":1.035}
    for i in range(1,N_BIDS+1):
        lane=lane_names[(i-1)%len(lane_names)]; miles, rate, complexity=LANES[lane]
        distance=max(70,int(rng.gauss(miles,miles*0.08))); weight=int(rng.uniform(2500,38000))
        stops=rng.choices([1,2,3],[.70,.24,.06])[0]; tier=tiers[(i-1)%len(tiers)]
        market=distance*rate*rng.uniform(.96,1.04)+max(0,stops-1)*35
        quote=market*tier_discount[tier]*rng.uniform(.96,1.05)
        fuel=distance*rng.uniform(.58,.69)*complexity
        driver=(72+distance*rng.uniform(.45,.55))*complexity
        maintenance=distance*rng.uniform(.12,.17)*complexity
        toll=distance*rng.uniform(.02,.06)*complexity
        accessorial=stops*18 + (rng.uniform(20,70) if rng.random()<.12 else 0)
        cost=fuel+driver+maintenance+toll+accessorial
        # Illustrative award probability declines as the quote moves above market.
        probability=max(.08,min(.86,.54 - .72*(quote/market-1) + (0.08 if tier=="Strategic" else 0)))
        awarded=int(rng.random()<probability)
        rows.append({"bid_id":f"B{i:05d}","bid_date":f"2026-{((i-1)%12)+1:02d}-{((i*5-1)%28)+1:02d}",
            "lane":lane,"customer_tier":tier,"distance_miles":distance,"weight_lb":weight,"stops":stops,
            "current_quote_usd":round(quote,2),"market_reference_usd":round(market,2),
            "estimated_cost_usd":round(cost,2),"awarded":awarded})
    write_csv(DATA/"synthetic_bid_history.csv",rows)
    groups=defaultdict(list)
    for r in rows: groups[r["lane"]].append(r)
    score=[]
    for lane,g in groups.items():
        won=[x for x in g if x["awarded"]]
        revenue=sum(x["current_quote_usd"] for x in won); cost=sum(x["estimated_cost_usd"] for x in won)
        target_price=sum(x["estimated_cost_usd"]/(1-TARGET_MARGIN) for x in g)/len(g)
        current= sum(x["current_quote_usd"] for x in g)/len(g)
        change=target_price/current-1
        if change > .05: action="Review rate floor; test selective increases"
        elif change < -.05: action="Test win-rate headroom before reducing price"
        else: action="Maintain guardrails; monitor mix and cost drift"
        score.append({"lane":lane,"bids":len(g),"awarded_bids":len(won),"win_rate":round(len(won)/len(g),4),
            "awarded_revenue_usd":round(revenue,2),"awarded_estimated_cost_usd":round(cost,2),
            "awarded_contribution_usd":round(revenue-cost,2),"awarded_contribution_margin":round((revenue-cost)/revenue,4) if revenue else 0,
            "avg_quote_usd":round(current,2),"target_price_for_20pct_margin_usd":round(target_price,2),
            "target_vs_current_change":round(change,4),"illustrative_action":action})
    score.sort(key=lambda x:x["awarded_contribution_margin"])
    write_csv(OUT/"lane_pricing_scorecard.csv",score)
    total=sum(r["awarded"] for r in rows); rev=sum(r["current_quote_usd"] for r in rows if r["awarded"])
    cost=sum(r["estimated_cost_usd"] for r in rows if r["awarded"]); margin=(rev-cost)/rev
    summary=("SYNTHETIC FREIGHT PRICING CASE\nAll bids, award outcomes, rates, and costs are simulated.\n\n"
        f"Bids modeled: {len(rows):,}\nAwarded bids: {total:,} ({total/len(rows):.1%} modeled win rate)\n"
        f"Awarded revenue: ${rev:,.0f}\nEstimated awarded cost: ${cost:,.0f}\nContribution: ${rev-cost:,.0f}\n"
        f"Weighted contribution margin: {margin:.1%}\nTarget margin scenario: {TARGET_MARGIN:.0%}\n\n"
        "Decision use: validate lane cost estimates and contract context, then pilot controlled rate changes while tracking win rate and realized contribution.\n"
        "The target-price formula is cost-plus arithmetic; it does not model customer response, contract constraints, or competitive behavior.\n")
    (OUT/"executive_summary.txt").write_text(summary,encoding="utf-8")
    return {"rows":rows,"score":score,"summary":summary,"margin":margin}

if __name__=="__main__":
    r=build();print(r["summary"])
