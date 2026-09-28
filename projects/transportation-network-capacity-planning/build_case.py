#!/usr/bin/env python3
"""Build a deterministic, synthetic weekly transportation capacity case."""
from __future__ import annotations
import csv, math
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parent
DATA,OUT=ROOT/"data",ROOT/"outputs"
SEED=20260928
NODES={
    "Detroit": {"capacity":520,"base_demand":465,"cost_per_unit":88,"service_risk_cost":145},
    "Chicago": {"capacity":610,"base_demand":555,"cost_per_unit":92,"service_risk_cost":160},
    "Atlanta": {"capacity":440,"base_demand":395,"cost_per_unit":105,"service_risk_cost":175},
    "Nashville": {"capacity":360,"base_demand":327,"cost_per_unit":97,"service_risk_cost":155},
    "Cleveland": {"capacity":330,"base_demand":302,"cost_per_unit":82,"service_risk_cost":138},
}
FIELDS=["week","node","forecast_units","base_capacity_units","base_utilization","base_shortfall_units",
        "flex_capacity_limit_units","flex_capacity_used_units","flex_cost_usd","unserved_after_flex_units",
        "illustrative_service_risk_cost_usd","illustrative_risk_cost_avoided_usd","net_modeled_benefit_usd","action"]

def write_csv(path:Path,rows:list[dict])->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def build()->dict:
    rows=[]
    for week in range(1,53):
        seasonal=1+0.085*math.sin((week-5)*2*math.pi/52)+ (0.09 if week>=47 else 0)
        for idx,(node,p) in enumerate(NODES.items()):
            forecast=round(p["base_demand"]*seasonal*(1+0.006*math.sin(week*idx+1)))
            cap=round(p["capacity"]*(1+0.008*math.sin(week*0.7+idx)))
            util=forecast/cap;short=max(0,forecast-cap)
            flex_limit=round(cap*0.12)
            # Executive scenario: procure incremental flex capacity only for forecast demand above 90% utilization.
            trigger=max(0,forecast-round(cap*0.90))
            flex_used=min(flex_limit,trigger)
            unserved=max(0,forecast-cap-flex_used)
            flex_cost=flex_used*p["cost_per_unit"]*0.23
            base_risk_pressure=max(0,forecast-round(cap*0.90))
            remaining_risk_pressure=max(0,forecast-round(cap*0.90)-flex_used)
            risk=base_risk_pressure*p["service_risk_cost"]
            remaining_risk=remaining_risk_pressure*p["service_risk_cost"]
            avoided=risk-remaining_risk
            net=avoided-flex_cost
            if util>=.98: action="Secure flex capacity; confirm labor and equipment"
            elif util>=.90: action="Pre-stage flex option; review forecast weekly"
            else: action="Hold base plan; monitor demand and availability"
            rows.append({"week":f"W{week:02d}","node":node,"forecast_units":forecast,"base_capacity_units":cap,
                "base_utilization":round(util,4),"base_shortfall_units":short,"flex_capacity_limit_units":flex_limit,
                "flex_capacity_used_units":flex_used,"flex_cost_usd":round(flex_cost,2),
                "unserved_after_flex_units":unserved,"illustrative_service_risk_cost_usd":round(risk,2),
                "illustrative_risk_cost_avoided_usd":round(avoided,2),"net_modeled_benefit_usd":round(net,2),"action":action})
    write_csv(DATA/"synthetic_weekly_demand_capacity.csv",rows)
    # Weekly source data and decision outputs are separate to keep inputs transparent.
    write_csv(OUT/"weekly_capacity_plan.csv",rows)
    grouped=defaultdict(list)
    for r in rows:grouped[r["node"]].append(r)
    summary=[]
    for node,g in grouped.items():
        demand=sum(r["forecast_units"] for r in g);capacity=sum(r["base_capacity_units"] for r in g)
        short=sum(r["base_shortfall_units"] for r in g);used=sum(r["flex_capacity_used_units"] for r in g)
        unserved=sum(r["unserved_after_flex_units"] for r in g)
        summary.append({"node":node,"weeks":len(g),"forecast_units":demand,"base_capacity_units":capacity,
            "annual_utilization":round(demand/capacity,4),"weeks_over_90pct_utilization":sum(r["base_utilization"]>=.90 for r in g),
            "base_shortfall_units":short,"flex_capacity_used_units":used,"unserved_after_flex_units":unserved,
            "flex_cost_usd":round(sum(r["flex_cost_usd"] for r in g),2),
            "illustrative_risk_cost_avoided_usd":round(sum(r["illustrative_risk_cost_avoided_usd"] for r in g),2),
            "net_modeled_benefit_usd":round(sum(r["net_modeled_benefit_usd"] for r in g),2)})
    summary.sort(key=lambda x:x["annual_utilization"],reverse=True)
    write_csv(OUT/"node_capacity_scorecard.csv",summary)
    total_demand=sum(r["forecast_units"] for r in rows);total_cap=sum(r["base_capacity_units"] for r in rows)
    high=sum(r["base_utilization"]>=.90 for r in rows);short=sum(r["base_shortfall_units"] for r in rows)
    use=sum(r["flex_capacity_used_units"] for r in rows);unserved=sum(r["unserved_after_flex_units"] for r in rows)
    flex_cost=sum(r["flex_cost_usd"] for r in rows);avoided=sum(r["illustrative_risk_cost_avoided_usd"] for r in rows)
    sensitivity=[]
    for multiplier in (0.5,1.0,2.0):
        sensitivity.append({"risk_cost_multiplier":multiplier,"flex_capacity_cost_usd":round(flex_cost,2),
            "illustrative_risk_cost_avoided_usd":round(avoided*multiplier,2),
            "net_modeled_benefit_usd":round(avoided*multiplier-flex_cost,2)})
    write_csv(OUT/"risk_cost_sensitivity.csv",sensitivity)
    summary_text=("SYNTHETIC NETWORK CAPACITY CASE\nAll demand, capacity, costs, and risk estimates are simulated.\n\n"
        f"Node-weeks modeled: {len(rows):,}\nAnnual forecast units: {total_demand:,}\nBase capacity units: {total_cap:,}\n"
        f"Network utilization: {total_demand/total_cap:.1%}\nNode-weeks at or above 90% utilization: {high:,}\n"
        f"Base shortfall units: {short:,}\nModeled flex capacity used: {use:,}\nUnserved units after flex scenario: {unserved:,}\n"
        f"Flex capacity cost: ${flex_cost:,.0f}\nIllustrative service risk cost avoided: ${avoided:,.0f}\n"
        f"Net modeled benefit: ${avoided-flex_cost:,.0f}\n\n"
        f"Risk-cost sensitivity (half/base/double): ${sensitivity[0]['net_modeled_benefit_usd']:,.0f} / ${sensitivity[1]['net_modeled_benefit_usd']:,.0f} / ${sensitivity[2]['net_modeled_benefit_usd']:,.0f}.\n"
        "Decision use: validate forecast confidence and capacity availability, then stage flexible options for high-utilization node-weeks.\n"
        "The avoided-risk estimate is an assumption-based scenario, not realized savings or proof that capacity causes service improvement.\n")
    (OUT/"executive_summary.txt").write_text(summary_text,encoding="utf-8")
    return {"rows":rows,"nodes":summary,"summary":summary_text,"network_utilization":total_demand/total_cap}

if __name__=="__main__":
    r=build();print(r["summary"])
