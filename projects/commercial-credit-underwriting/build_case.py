#!/usr/bin/env python3
"""Create a synthetic borrower spreading and credit-screening case."""
import csv
from pathlib import Path
ROOT=Path(__file__).resolve().parent; DATA=ROOT/"data"; OUT=ROOT/"outputs"
BORROWERS=[
 {"borrower":"Northstar Components","revenue":18_500_000,"growth":.07,"ebitda_margin":.145,"cash_interest":620_000,"debt":5_800_000,"annual_principal":700_000,"cash":450_000,"capex":520_000},
 {"borrower":"Harbor Freight Services","revenue":24_000_000,"growth":-.035,"ebitda_margin":.105,"cash_interest":1_050_000,"debt":10_500_000,"annual_principal":1_450_000,"cash":380_000,"capex":810_000},
 {"borrower":"Pine Ridge Packaging","revenue":12_200_000,"growth":.025,"ebitda_margin":.18,"cash_interest":410_000,"debt":3_900_000,"annual_principal":460_000,"cash":700_000,"capex":380_000},]
def write(path,rows):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open("w",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def build():
 write(DATA/"synthetic_borrower_inputs.csv",BORROWERS); rows=[]
 for b in BORROWERS:
  ebitda=b["revenue"]*b["ebitda_margin"]; interest_cover=ebitda/b["cash_interest"]
  ds= b["cash_interest"]+b["annual_principal"]; dscr=(ebitda-b["capex"])/ds
  leverage=b["debt"]/ebitda; max_debt=ebitda*3.0; headroom=max_debt-b["debt"]
  decision="Advance to diligence" if dscr>=1.35 and leverage<=3.5 and interest_cover>=2.0 else "Watch / structure" if dscr>=1.0 and leverage<=5 else "Decline / redesign"
  rows.append({"borrower":b["borrower"],"revenue_usd":b["revenue"],"growth_pct":round(b["growth"]*100,2),"ebitda_usd":round(ebitda,2),"ebitda_margin_pct":round(b["ebitda_margin"]*100,2),"debt_usd":b["debt"],"gross_leverage_x":round(leverage,3),"interest_coverage_x":round(interest_cover,3),"debt_service_usd":b["cash_interest"]+b["annual_principal"],"dscr_x":round(dscr,3),"cash_usd":b["cash"],"cash_net_debt_usd":b["debt"]-b["cash"],"illustrative_3x_debt_capacity_usd":round(max_debt,2),"debt_headroom_usd":round(headroom,2),"screen_outcome":decision})
 write(OUT/"borrower_credit_screen.csv",rows)
 stress=[]
 for b in BORROWERS:
  for shock in (0,-.10,-.20):
   e=b["revenue"]*(1+shock)*b["ebitda_margin"]; ds=b["cash_interest"]+b["annual_principal"]
   stress.append({"borrower":b["borrower"],"revenue_shock_pct":round(shock*100,1),"stressed_ebitda_usd":round(e,2),"stressed_dscr_x":round((e-b["capex"])/ds,3),"dscr_below_1x_flag":int((e-b["capex"])/ds<1)})
 write(OUT/"downside_sensitivity.csv",stress)
 best=max(rows,key=lambda r:r["dscr_x"])
 summary=f"SYNTHETIC COMMERCIAL CREDIT SCREEN\nStrongest modeled DSCR: {best['borrower']} at {best['dscr_x']:.2f}x\nScreen outcomes are preliminary triage, not approvals. Inputs are simulated.\n\nCredit review should verify borrower financial statements, add-backs, debt schedule, collateral, guarantors, covenant definitions, concentration, and repayment source. EBITDA less capex is a simplified cash-flow proxy; no taxes or working-capital forecast are modeled.\n"
 (OUT/"credit_memo.txt").write_text(summary,encoding="utf-8");return rows,stress
if __name__=="__main__": build()
