#!/usr/bin/env python3
"""Build a synthetic procurement and freight sourcing BI case."""
import csv, json
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
 summary=f"SYNTHETIC PROCUREMENT / SOURCING BI\nTotal modeled spend: ${total:,.0f}\nSpend on contracted supplier POs: {contracted/total:.1%}\nLargest category benchmark gap: ${max(cats,key=lambda r:r['benchmark_gap_usd'])['benchmark_gap_usd']:,.0f}\n\nDecision brief: start with a rate and coverage validation for the largest spend categories, then review supplier concentration and service quality before selecting any sourcing event. The benchmark gap is a directional screening measure, not realized or validated savings.\n\nAll data and benchmarks are synthetic. This dataset simulates purchase-order exports; it is not a Coupa or ERP integration.\n"
 (OUT/"executive_summary.txt").write_text(summary,encoding="utf-8")
 make_dashboard(spend,sup,cats,month)
 return spend,sup,cats,month

def make_dashboard(spend,sup,cats,month):
 dash=ROOT/"dashboard";dash.mkdir(parents=True,exist_ok=True)
 (dash/"data.js").write_text("window.SPEND_ROWS="+json.dumps(spend,separators=(",",":"))+";\n",encoding="utf-8")
 svg=['''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="850" viewBox="0 0 1280 850">
<rect width="1280" height="850" fill="#f3f6fa"/><rect x="0" y="0" width="1280" height="142" fill="#10233f"/>
<text x="48" y="58" fill="#fff" font-family="Arial" font-size="30" font-weight="700">Freight Spend &amp; Sourcing Review</text>
<text x="48" y="94" fill="#b8c9df" font-family="Arial" font-size="16">Synthetic purchase-order case · 2026 · decision-support prototype</text>
<text x="48" y="124" fill="#74dbc6" font-family="Arial" font-size="13" font-weight="700">SOURCING OPPORTUNITY SCREEN</text>''']
 def txt(x,y,s,size=14,color="#19304c",weight="400"):
  svg.append(f'<text x="{x}" y="{y}" fill="{color}" font-family="Arial" font-size="{size}" font-weight="{weight}">{s}</text>')
 def card(x,label,value,sub):
  svg.append(f'<rect x="{x}" y="166" width="375" height="110" rx="12" fill="#fff" stroke="#d9e2ee"/>')
  txt(x+20,196,label,13,"#60738c","700");txt(x+20,237,value,30,"#10233f","700");txt(x+20,260,sub,12,"#74859b")
 card(40,"TOTAL MODELED SPEND",f"${sum(r['spend_usd'] for r in spend):,.0f}",f"{len(spend)} synthetic purchase orders")
 card(452,"CONTRACT PO SHARE",f"{sum(r['on_contract_flag'] for r in spend)/len(spend):.1%}","Share of orders flagged on contract")
 card(864,"BENCHMARK GAP SCREEN",f"${sum(r['benchmark_gap_usd'] for r in cats):,.0f}","Directional screen · not validated savings")
 svg.append('<rect x="40" y="300" width="750" height="302" rx="12" fill="#fff" stroke="#d9e2ee"/><rect x="810" y="300" width="430" height="302" rx="12" fill="#fff" stroke="#d9e2ee"/>')
 txt(64,335,"Monthly spend",18,"#10233f","700");txt(64,356,"USD · purchase order month",12,"#74859b")
 maxm=max(r['spend_usd'] for r in month)
 chart_x,chart_y,chart_w,chart_h=78,390,680,150
 svg.append(f'<line x1="{chart_x}" y1="{chart_y+chart_h}" x2="{chart_x+chart_w}" y2="{chart_y+chart_h}" stroke="#cbd6e3"/>')
 for i,r in enumerate(month):
  bx=chart_x+i*55+3;h=chart_h*r['spend_usd']/maxm;by=chart_y+chart_h-h
  svg.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="34" height="{h:.1f}" rx="4" fill="#168c89"/>')
  txt(bx-1,chart_y+chart_h+23,r['month'][5:],11,"#74859b")
 txt(64,574,"Source: synthetic PO records · monthly totals aggregate all suppliers and categories",11,"#74859b")
 txt(834,335,"Benchmark gap by category",18,"#10233f","700");txt(834,356,"Screening measure · USD",12,"#74859b")
 maxc=max(r['benchmark_gap_usd'] for r in cats)
 for i,r in enumerate(sorted(cats,key=lambda x:x['benchmark_gap_usd'],reverse=True)):
  y=398+i*44;txt(834,y+13,r['category'],12,"#526780")
  svg.append(f'<rect x="960" y="{y}" width="210" height="17" rx="7" fill="#e7edf4"/><rect x="960" y="{y}" width="{210*r["benchmark_gap_usd"]/maxc:.1f}" height="17" rx="7" fill="#ed9b52"/>')
  txt(1178,y+13,f"${r['benchmark_gap_usd']:,.0f}",12,"#19304c","700")
 svg.append('<rect x="40" y="626" width="1200" height="162" rx="12" fill="#fff" stroke="#d9e2ee"/>')
 txt(64,661,"Supplier concentration &amp; contract coverage",18,"#10233f","700")
 for x,label in [(64,"Supplier"),(430,"Modeled spend"),(690,"Share of spend"),(930,"Contract PO share")]:txt(x,690,label,12,"#74859b","700")
 for i,r in enumerate(sorted(sup,key=lambda x:x['spend_usd'],reverse=True)):
  y=720+i*28;txt(64,y,r['supplier'],13);txt(430,y,f"${r['spend_usd']:,.0f}",13);txt(690,y,f"{r['spend_share_pct']:.1f}%",13);txt(930,y,f"{r['contract_po_share_pct']:.0f}%",13)
 svg.append('<rect x="40" y="808" width="1200" height="1" fill="#d9e2ee"/>')
 txt(40,832,"Illustrative synthetic data only. Validate rates, index rules, contract terms, and service quality before acting on the modeled gaps.",12,"#586b82")
 svg.append('</svg>')
 (dash/"dashboard-preview.svg").write_text("\n".join(svg),encoding="utf-8")
if __name__=="__main__": build()
