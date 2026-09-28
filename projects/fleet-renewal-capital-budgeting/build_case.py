#!/usr/bin/env python3
"""Build a deterministic, synthetic fleet-renewal capital-budgeting case."""
from __future__ import annotations
import csv
from pathlib import Path

ROOT=Path(__file__).resolve().parent
DATA,OUT=ROOT/"data",ROOT/"outputs"
TAX_RATE=0.25
LIFE=7
SCENARIOS={
 "Downside":{"gross_capex_usd":5_500_000,"trade_in_usd":250_000,"fuel_savings_usd":480_000,
  "maintenance_savings_usd":280_000,"downtime_savings_usd":300_000,"terminal_salvage_usd":300_000,"hurdle_rate":0.11},
 "Base":{"gross_capex_usd":5_000_000,"trade_in_usd":350_000,"fuel_savings_usd":700_000,
  "maintenance_savings_usd":450_000,"downtime_savings_usd":350_000,"terminal_salvage_usd":500_000,"hurdle_rate":0.10},
 "Upside":{"gross_capex_usd":4_800_000,"trade_in_usd":400_000,"fuel_savings_usd":850_000,
  "maintenance_savings_usd":550_000,"downtime_savings_usd":500_000,"terminal_salvage_usd":650_000,"hurdle_rate":0.095},
}

def write_csv(path:Path,rows:list[dict])->None:
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open("w",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def cashflows(capex:float,trade:float,fuel:float,maint:float,downtime:float,salvage:float,rate:float,tax:float=TAX_RATE,life:int=LIFE)->list[dict]:
 initial=capex-trade
 annual_savings=fuel+maint+downtime
 depreciation=capex/life
 annual_after_tax=annual_savings*(1-tax)+depreciation*tax
 rows=[{"year":0,"initial_investment_usd":round(initial,2),"operating_savings_usd":0.0,"depreciation_tax_shield_usd":0.0,"after_tax_salvage_usd":0.0,"cash_flow_usd":round(-initial,2),"discount_factor":1.0,"discounted_cash_flow_usd":round(-initial,2)}]
 for year in range(1,life+1):
  aftertax_salvage=salvage*(1-tax) if year==life else 0.0
  cf=annual_after_tax+aftertax_salvage
  factor=1/(1+rate)**year
  rows.append({"year":year,"initial_investment_usd":0.0,"operating_savings_usd":round(annual_savings,2),
   "depreciation_tax_shield_usd":round(depreciation*tax,2),"after_tax_salvage_usd":round(aftertax_salvage,2),
   "cash_flow_usd":round(cf,2),"discount_factor":round(factor,9),"discounted_cash_flow_usd":round(cf*factor,2)})
 return rows

def npv(rate:float,flows:list[float])->float:
 return sum(cf/(1+rate)**year for year,cf in enumerate(flows))

def irr(flows:list[float])->float:
 low=-0.999999;high=1.0
 while npv(high,flows)>0 and high<1_000_000: high=high*2+0.01
 if npv(high,flows)>0: raise ValueError("IRR is not bracketed for this cash-flow stream.")
 for _ in range(120):
  mid=(low+high)/2
  if npv(mid,flows)>0: low=mid
  else: high=mid
 return (low+high)/2

def payback(flows:list[float],rate:float|None=None)->float|None:
 total=0.0
 for year,cf in enumerate(flows):
  amount=cf if rate is None else cf/(1+rate)**year
  prev=total;total+=amount
  if total>=0 and year>0 and amount>0:
   return (year-1)+(-prev/amount)
 return None

def evaluate(name:str,p:dict,capex_mult:float=1.0,savings_mult:float=1.0)->tuple[list[dict],dict]:
 capex=p["gross_capex_usd"]*capex_mult;trade=p["trade_in_usd"]
 fuel=p["fuel_savings_usd"]*savings_mult;maint=p["maintenance_savings_usd"]*savings_mult;down=p["downtime_savings_usd"]*savings_mult
 flows=cashflows(capex,trade,fuel,maint,down,p["terminal_salvage_usd"],p["hurdle_rate"])
 values=[x["cash_flow_usd"] for x in flows];n= npv(p["hurdle_rate"],values);rate=irr(values)
 annuity=sum(1/(1+p["hurdle_rate"])**i for i in range(1,LIFE+1))
 pv_shield=(capex/LIFE*TAX_RATE)*annuity
 pv_salvage=p["terminal_salvage_usd"]*(1-TAX_RATE)/(1+p["hurdle_rate"])**LIFE
 break_even=max(0,(capex-trade-pv_shield-pv_salvage)/(annuity*(1-TAX_RATE)))
 summary={"scenario":name,"gross_capex_usd":round(capex,2),"trade_in_usd":round(trade,2),"net_initial_investment_usd":round(capex-trade,2),
  "annual_operating_savings_usd":round(fuel+maint+down,2),"hurdle_rate":p["hurdle_rate"],"npv_usd":round(n,2),"irr":round(rate,6),
  "simple_payback_years":round(payback(values),2) if payback(values) is not None else "Beyond life",
  "discounted_payback_years":round(payback(values,p["hurdle_rate"]),2) if payback(values,p["hurdle_rate"]) is not None else "Beyond life",
  "break_even_annual_savings_usd":round(break_even,2),"decision_screen":"Advance to diligence" if n>0 and rate>p["hurdle_rate"] else "Defer / redesign"}
 for r in flows:r["scenario"]=name
 return flows,summary

def build()->dict:
 DATA.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
 assumptions=[{"scenario":k,**v} for k,v in SCENARIOS.items()]
 write_csv(DATA/"synthetic_capital_budget_assumptions.csv",assumptions)
 flows=[];summaries=[]
 for k,p in SCENARIOS.items():
  f,s=evaluate(k,p);flows.extend(f);summaries.append(s)
 write_csv(OUT/"scenario_cash_flows.csv",flows);write_csv(OUT/"investment_screen.csv",summaries)
 base=next(x for x in summaries if x["scenario"]=="Base")
 sens=[]
 for cm in (0.9,1.0,1.1):
  for sm in (0.6,0.8,1.0,1.2,1.4):
   f,_=evaluate("Base",SCENARIOS["Base"],cm,sm)
   sens.append({"capex_multiplier":cm,"savings_multiplier":sm,"npv_usd":round(sum(x["discounted_cash_flow_usd"] for x in f),2)})
 write_csv(OUT/"capex_savings_sensitivity.csv",sens)
 summary=("SYNTHETIC FLEET-RENEWAL CAPITAL-BUDGETING CASE\nAll costs and savings assumptions are hypothetical.\n\n"
  f"Base net initial investment: ${base['net_initial_investment_usd']:,.0f}\nBase annual operating savings: ${base['annual_operating_savings_usd']:,.0f}\n"
  f"Base NPV at {base['hurdle_rate']:.1%}: ${base['npv_usd']:,.0f}\nBase IRR: {base['irr']:.1%}\n"
  f"Base simple payback: {base['simple_payback_years']} years\nBreak-even annual savings: ${base['break_even_annual_savings_usd']:,.0f}\n"
  f"Downside NPV: ${summaries[0]['npv_usd']:,.0f}; upside NPV: ${summaries[2]['npv_usd']:,.0f}.\n\n"
  "Decision use: advance only if verified operating savings clear the hurdle in the downside case or a staged pilot narrows uncertainty.\n"
  "This is a screening model, not a procurement recommendation or forecast of realized savings.\n")
 (OUT/"executive_summary.txt").write_text(summary,encoding="utf-8")
 return {"flows":flows,"scenarios":summaries,"sensitivity":sens,"summary":summary}

if __name__=="__main__":print(build()["summary"])
