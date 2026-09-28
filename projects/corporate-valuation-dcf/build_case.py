#!/usr/bin/env python3
"""Build a deterministic, synthetic discounted-cash-flow valuation case."""
from __future__ import annotations
import csv
from pathlib import Path

ROOT=Path(__file__).resolve().parent
DATA,OUT=ROOT/"data",ROOT/"outputs"
INITIAL_REVENUE=45_000_000.0
TAX_RATE=0.25
D_AND_A_PCT=0.04
CAPEX_PCT=0.052
NWC_PCT_INCREMENTAL_REVENUE=0.02
DEBT=12_000_000.0
CASH=3_000_000.0
SHARES=5_000_000.0
YEARS=5
SCENARIOS={
 "Downside":{"revenue_growth":0.025,"ebitda_margin":0.135,"wacc":0.115,"terminal_growth":0.015},
 "Base":{"revenue_growth":0.055,"ebitda_margin":0.165,"wacc":0.100,"terminal_growth":0.025},
 "Upside":{"revenue_growth":0.075,"ebitda_margin":0.18,"wacc":0.095,"terminal_growth":0.030},
}

def write_csv(path:Path,rows:list[dict])->None:
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open("w",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def model(s:dict)->tuple[list[dict],dict]:
 growth=s["revenue_growth"];margin=s["ebitda_margin"];wacc=s["wacc"];g=s["terminal_growth"]
 if not 0<g<wacc<1: raise ValueError("Terminal growth must be below WACC.")
 rows=[];prev=INITIAL_REVENUE
 for year in range(1,YEARS+1):
  revenue=prev*(1+growth);ebitda=revenue*margin;da=revenue*D_AND_A_PCT;ebit=ebitda-da
  taxes=max(0,ebit*TAX_RATE);nopat=ebit-taxes;capex=revenue*CAPEX_PCT
  nwc=max(0,(revenue-prev)*NWC_PCT_INCREMENTAL_REVENUE)
  fcf=nopat+da-capex-nwc;pv=fcf/(1+wacc)**year
  rows.append({"scenario":s["scenario"],"year":year,"revenue_usd":round(revenue,2),"ebitda_usd":round(ebitda,2),
   "ebitda_margin":round(margin,4),"da_usd":round(da,2),"ebit_usd":round(ebit,2),"cash_taxes_usd":round(taxes,2),
   "capex_usd":round(capex,2),"change_nwc_usd":round(nwc,2),"unlevered_fcf_usd":round(fcf,2),
   "discount_factor":round(1/(1+wacc)**year,12),"pv_fcf_usd":round(pv,2)})
  prev=revenue
 tv=rows[-1]["unlevered_fcf_usd"]*(1+g)/(wacc-g)
 pv_tv=tv/(1+wacc)**YEARS
 ev=sum(x["pv_fcf_usd"] for x in rows)+pv_tv
 equity=ev-DEBT+CASH
 summary={"scenario":s["scenario"],"wacc":wacc,"terminal_growth":g,"pv_explicit_fcf_usd":round(sum(x["pv_fcf_usd"] for x in rows),2),
  "terminal_value_usd":round(tv,2),"pv_terminal_value_usd":round(pv_tv,2),"enterprise_value_usd":round(ev,2),
  "net_debt_usd":DEBT-CASH,"equity_value_usd":round(equity,2),"shares":SHARES,
  "illustrative_value_per_share_usd":round(equity/SHARES,2),"ev_to_year1_ebitda":round(ev/rows[0]["ebitda_usd"],2),
  "terminal_value_share_of_ev":round(pv_tv/ev,4)}
 return rows,summary

def build()->dict:
 DATA.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
 assumption_rows=[]
 for name,p in SCENARIOS.items(): assumption_rows.append({"scenario":name,**p})
 write_csv(DATA/"synthetic_scenario_assumptions.csv",assumption_rows)
 allrows=[];summaries=[]
 for name,p in SCENARIOS.items():
  r,s=model({"scenario":name,**p});allrows.extend(r);summaries.append(s)
 write_csv(OUT/"forecast_cash_flows.csv",allrows)
 write_csv(OUT/"scenario_valuation.csv",summaries)
 base=next(x for x in summaries if x["scenario"]=="Base")
 sens=[]
 baseflows=[x["unlevered_fcf_usd"] for x in allrows if x["scenario"]=="Base"]
 for wacc in (0.08,0.09,0.10,0.11,0.12):
  for g in (0.01,0.015,0.02,0.025,0.03):
   if g>=wacc: continue
   pve=sum(f/(1+wacc)**i for i,f in enumerate(baseflows,1))
   tv=baseflows[-1]*(1+g)/(wacc-g);pv_tv=tv/(1+wacc)**YEARS;ev=pve+pv_tv
   sens.append({"wacc":wacc,"terminal_growth":g,"enterprise_value_usd":round(ev,2),
    "equity_value_usd":round(ev-DEBT+CASH,2),"illustrative_value_per_share_usd":round((ev-DEBT+CASH)/SHARES,2)})
 write_csv(OUT/"wacc_growth_sensitivity.csv",sens)
 summary=("SYNTHETIC DCF VALUATION CASE\nAll company data and forecast assumptions are hypothetical.\n\n"
  f"Base enterprise value: ${base['enterprise_value_usd']:,.0f}\nBase equity value: ${base['equity_value_usd']:,.0f}\n"
  f"Illustrative value per share: ${base['illustrative_value_per_share_usd']:,.2f}\n"
  f"Terminal value share of enterprise value: {base['terminal_value_share_of_ev']:.1%}\n"
  f"Scenario enterprise-value range: ${min(x['enterprise_value_usd'] for x in summaries):,.0f} to ${max(x['enterprise_value_usd'] for x in summaries):,.0f}\n\n"
  "Decision use: challenge growth, margin, reinvestment, and discount-rate assumptions before discussing a valuation range.\n"
  "This is an educational model, not an appraisal, security recommendation, or estimate for a real issuer.\n")
 (OUT/"executive_summary.txt").write_text(summary,encoding="utf-8")
 return {"cashflows":allrows,"scenarios":summaries,"sensitivity":sens,"summary":summary}

if __name__=="__main__": print(build()["summary"])
