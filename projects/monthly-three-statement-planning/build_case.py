#!/usr/bin/env python3
"""Build a synthetic integrated monthly FP&A model and close bridge."""
import csv
from pathlib import Path

ROOT=Path(__file__).resolve().parent
DATA=ROOT/"data"; OUT=ROOT/"outputs"
START_CASH=1_800_000.0; START_AR=2_300_000.0; START_INVENTORY=1_050_000.0
START_PPNE=4_400_000.0; START_AP=1_520_000.0; START_DEBT=2_000_000.0
EQUITY=4_200_000.0; TAX=0.25; DSO=43; DIO=52; DPO=38

def write(path,rows):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open("w",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def build():
 months=[]
 for m in range(1,13):
  season=[.92,.94,1.00,.98,1.02,1.00,1.03,1.05,1.01,1.07,1.12,1.16][m-1]
  rev=1_000_000*season*(1+.003*m); cogs=rev*(.61+.0005*m); opex=295_000*(1+.002*m)
  capex=62_000 if m not in (6,12) else 120_000; da=42_000
  interest=16_000; ebit=rev-cogs-opex-da; pretax=ebit-interest; tax=max(0,pretax*TAX); ni=pretax-tax
  months.append(dict(month=f"2026-{m:02d}",revenue=rev,cogs=cogs,opex=opex,capex=capex,da=da,interest=interest,tax=tax,ni=ni))
 actual=[]; forecast=[]; bs=[]; cash=START_CASH; ar=START_AR; inv=START_INVENTORY; ppne=START_PPNE; ap=START_AP; retained=START_CASH+START_AR+START_INVENTORY+START_PPNE-START_AP-START_DEBT-EQUITY
 for i,x in enumerate(months):
  budget_rev=1_000_000*[.92,.94,1, .98,1.02,1,1.03,1.05,1.01,1.07,1.12,1.16][i]*(1+.002*i)
  actual_row={"month":x["month"],"actual_revenue_usd":round(x["revenue"],2),"budget_revenue_usd":round(budget_rev,2),"revenue_variance_usd":round(x["revenue"]-budget_rev,2),"actual_ebitda_usd":round(x["revenue"]-x["cogs"]-x["opex"],2),"budget_ebitda_usd":round(budget_rev*.39-295000*(1+.0015*i),2)}
  actual.append(actual_row)
  delta_ar=x["revenue"]*DSO/30-ar; delta_inv=x["cogs"]*DIO/30-inv; new_ap=x["cogs"]*DPO/30; delta_ap=new_ap-ap
  cfo=x["ni"]+x["da"]-delta_ar-delta_inv+delta_ap
  cash+=cfo-x["capex"]; ar+=delta_ar; inv+=delta_inv; ppne+=x["capex"]-x["da"]; ap=new_ap; retained+=x["ni"]
  assets=cash+ar+inv+ppne; liabilities=ap+START_DEBT; equity=EQUITY+retained
  bs.append({"month":x["month"],"cash_usd":round(cash,2),"accounts_receivable_usd":round(ar,2),"inventory_usd":round(inv,2),"net_ppe_usd":round(ppne,2),"accounts_payable_usd":round(ap,2),"debt_usd":START_DEBT,"share_capital_usd":EQUITY,"retained_earnings_usd":round(retained,2),"total_assets_usd":round(assets,2),"total_liabilities_equity_usd":round(liabilities+equity,2),"balance_check_usd":round(assets-liabilities-equity,2)})
  forecast.append({"month":x["month"],"revenue_usd":round(x["revenue"],2),"cogs_usd":round(x["cogs"],2),"opex_usd":round(x["opex"],2),"ebitda_usd":round(x["revenue"]-x["cogs"]-x["opex"],2),"depreciation_usd":x["da"],"interest_usd":x["interest"],"tax_usd":round(x["tax"],2),"net_income_usd":round(x["ni"],2),"capex_usd":x["capex"],"cash_from_operations_usd":round(cfo,2),"ending_cash_usd":round(cash,2)})
 write(DATA/"synthetic_opening_balances.csv",[{"opening_cash_usd":START_CASH,"opening_ar_usd":START_AR,"opening_inventory_usd":START_INVENTORY,"opening_net_ppe_usd":START_PPNE,"opening_ap_usd":START_AP,"opening_debt_usd":START_DEBT,"share_capital_usd":EQUITY}])
 write(OUT/"monthly_income_cashflow.csv",forecast);write(OUT/"budget_variance.csv",actual);write(OUT/"balance_sheet_rollforward.csv",bs)
 summary=f"SYNTHETIC INTEGRATED FP&A MODEL\nFY2026 revenue: ${sum(x['revenue'] for x in months):,.0f}\nFY2026 EBITDA: ${sum(x['revenue']-x['cogs']-x['opex'] for x in months):,.0f}\nEnding cash: ${cash:,.0f}\nLargest monthly revenue variance: ${max(actual,key=lambda r:abs(r['revenue_variance_usd']))['revenue_variance_usd']:,.0f}\n\nAll records are synthetic. Balance sheet rolls forward cash, working capital, fixed assets, debt, and retained earnings. Simplifications: constant debt, DSO/DIO/DPO heuristics, no dividends, and tax-loss carryforward excluded.\n"
 (OUT/"executive_summary.txt").write_text(summary,encoding="utf-8")
 return actual,forecast,bs
if __name__=="__main__": build()
