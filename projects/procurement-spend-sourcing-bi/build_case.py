#!/usr/bin/env python3
"""Build a synthetic procurement and freight sourcing BI case."""
import csv
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent; DATA=ROOT/"data"; OUT=ROOT/"outputs"
SUPPLIERS=[("Apex Freight","Contracted",.90), ("BlueRail Logistics","Contracted",.82), ("Cedar Transport","Spot",.72), ("Delta Carriers","Spot",.78)]
CATS=[("Linehaul",34000,1.035),("Fuel surcharge",9800,1.12),("Accessorial",6200,1.18),("Packaging",5100,1.04)]
def write(path,rows):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open("w",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def build():
 spend=[]
 for i in range(1,97):
  supplier,contract,statusshare=SUPPLIERS[(i*7+i//5)%4];cat,base,mult=CATS[(i*3+i//7)%4]
  month=(i-1)%12+1; amount=base*(1+((i%9)-4)*.025)*(1+.002*month)
  contracted=(supplier in ("Apex Freight","BlueRail Logistics"))
  benchmark=amount/(mult if cat in ("Fuel surcharge","Accessorial") else 1.08)
  spend.append({"po_id":f"PO-{i:04d}","month":f"2026-{month:02d}","supplier":supplier,"supplier_type":"Contract" if contracted else "Spot","category":cat,"spend_usd":round(amount,2),"contract_rate_usd":round(benchmark,2) if contracted else "","benchmark_rate_usd":round(benchmark,2),"on_contract_flag":int(contracted)})
 write(DATA/"synthetic_procurement_transactions.csv",spend)
 supplier_agg=defaultdict(lambda:[0,0,0]); cat_agg=defaultdict(lambda:[0,0,0]); monthly=defaultdict(float)
 for r in spend:
  s=supplier_agg[r["supplier"]];s[0]+=r["spend_usd"];s[1]+=1;s[2]+=r["on_contract_flag"]
  c=cat_agg[r["category"]];c[0]+=r["spend_usd"];c[1]+=max(0,r["spend_usd"]-r["benchmark_rate_usd"]);c[2]+=1
  monthly[r["month"]]+=r["spend_usd"]
 total=sum(x["spend_usd"] for x in spend)
 sup=[{"supplier":k,"spend_usd":round(v[0],2),"po_count":v[1],"spend_share_pct":round(100*v[0]/total,2),"contract_po_share_pct":round(100*v[2]/v[1],2)} for k,v in supplier_agg.items()]
 cats=[{"category":k,"spend_usd":round(v[0],2),"benchmark_gap_usd":round(v[1],2),"po_count":v[2]} for k,v in cat_agg.items()]
 month=[{"month":k,"spend_usd":round(v,2)} for k,v in sorted(monthly.items())]
 write(OUT/"supplier_scorecard.csv",sup);write(OUT/"category_opportunity.csv",cats);write(OUT/"monthly_spend.csv",month)
 contracted=sum(r["spend_usd"] for r in spend if r["on_contract_flag"])
 summary=f"SYNTHETIC PROCUREMENT / SOURCING BI\nTotal modeled spend: ${total:,.0f}\nSpend on contracted supplier POs: {contracted/total:.1%}\nLargest category benchmark gap: ${max(cats,key=lambda r:r['benchmark_gap_usd'])['benchmark_gap_usd']:,.0f}\n\nOpportunities are directional screens, not validated savings. Benchmark construction is synthetic. Validate rates, accessorial rules, fuel indexes, service quality, and contract coverage before negotiation. Dataset simulates purchase-order exports; it is not a Coupa or ERP integration.\n"
 (OUT/"executive_summary.txt").write_text(summary,encoding="utf-8");return spend,sup,cats,month
if __name__=="__main__": build()
