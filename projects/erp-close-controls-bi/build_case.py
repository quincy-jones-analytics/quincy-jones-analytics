#!/usr/bin/env python3
"""Simulate ERP-style ledger extracts, close controls, and BI-ready outputs."""
import csv
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent; DATA=ROOT/"data"; OUT=ROOT/"outputs"
JOURNALS=[
 ("J1001","2026-08-31","Cash","Operating Cash",125000,0,"Cash receipt"),
 ("J1001","2026-08-31","AR","Trade Receivables",0,125000,"Cash receipt"),
 ("J1002","2026-08-31","COGS","Cost of Sales",78000,0,"Freight and handling"),
 ("J1002","2026-08-31","AP","Trade Payables",0,78000,"Freight and handling"),
 ("J1003","2026-08-31","OPEX","Operating Expense",42000,0,"Operations payroll"),
 ("J1003","2026-08-31","Cash","Operating Cash",0,42000,"Operations payroll"),
 ("J1004","2026-08-31","AR","Trade Receivables",56000,0,"Customer invoice"),
 ("J1004","2026-08-31","Revenue","Service Revenue",0,56000,"Customer invoice"),
 ("J1005","2026-08-31","SUSP","Unmapped Account",9000,0,"Manual adjustment"),
 ("J1005","2026-08-31","Cash","Operating Cash",0,9000,"Manual adjustment"),
 ("J1006","2026-08-31","AP","Trade Payables",14500,0,"Vendor credit"),
 ("J1006","2026-08-31","COGS","Cost of Sales",0,14500,"Vendor credit"),
 ("J1007","2026-08-31","Cash","Operating Cash",30000,0,"Duplicate import check"),
 ("J1007","2026-08-31","Revenue","Service Revenue",0,29900,"Duplicate import check"),]
MAP={"Cash":"Cash","AR":"Accounts Receivable","AP":"Accounts Payable","COGS":"Cost of Goods Sold","OPEX":"Operating Expense","Revenue":"Service Revenue"}
def write(path,rows):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open("w",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def build():
 src=[dict(journal_id=j,date=d,account_code=a,account_name=n,debit_usd=de,credit_usd=cr,memo=m) for j,d,a,n,de,cr,m in JOURNALS]
 write(DATA/"synthetic_erp_gl_extract.csv",src)
 normalized=[]; journal=defaultdict(lambda:[0,0]); unknown=[]
 for x in src:
  mapped=MAP.get(x["account_code"],"UNMAPPED")
  normalized.append({**x,"account_group":mapped,"net_debit_usd":x["debit_usd"]-x["credit_usd"]})
  journal[x["journal_id"]][0]+=x["debit_usd"];journal[x["journal_id"]][1]+=x["credit_usd"]
  if mapped=="UNMAPPED": unknown.append(x)
 checks=[{"journal_id":j,"debits_usd":round(v[0],2),"credits_usd":round(v[1],2),"difference_usd":round(v[0]-v[1],2),"balanced_flag":int(round(v[0]-v[1],2)==0)} for j,v in journal.items()]
 controls=[]
 for j in checks:
  if not j["balanced_flag"]: controls.append({"control":"Journal balance","key":j["journal_id"],"severity":"High","exception_usd":j["difference_usd"],"action":"Investigate and correct before close"})
 for x in unknown: controls.append({"control":"Account mapping","key":x["account_code"],"severity":"Medium","exception_usd":x["debit_usd"]-x["credit_usd"],"action":"Assign approved chart-of-accounts mapping"})
 write(OUT/"normalized_gl.csv",normalized);write(OUT/"journal_balance_checks.csv",checks);write(OUT/"close_exceptions.csv",controls)
 total_debits=sum(x["debit_usd"] for x in src); total_credits=sum(x["credit_usd"] for x in src)
 summary=f"SYNTHETIC ERP-STYLE CLOSE CONTROL\nTransactions: {len(src)} | journals: {len(checks)}\nDebit-credit difference: ${total_debits-total_credits:,.2f}\nUnbalanced journals: {sum(1 for x in checks if not x['balanced_flag'])}\nUnmapped account lines: {len(unknown)}\n\nExports mimic common general-ledger fields; no NetSuite connection or live ERP access was used. Review exceptions before close and confirm source controls, approvals, subledger ties, and mapping governance.\n"
 (OUT/"close_summary.txt").write_text(summary,encoding="utf-8");return src,normalized,checks,controls
if __name__=="__main__": build()
