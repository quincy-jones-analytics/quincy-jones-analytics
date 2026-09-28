#!/usr/bin/env python3
"""Simulate return data and calculate portfolio risk and factor attribution."""
import csv, math, random
from pathlib import Path
ROOT=Path(__file__).resolve().parent; DATA=ROOT/"data"; OUT=ROOT/"outputs"
SEED=7319; N=252; WEIGHTS={"RailCo":.40,"TransitTech":.35,"FreightSystems":.25}
def write(path,rows):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open("w",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def solve(a,b):
 m=[list(map(float,row))+[float(rhs)] for row,rhs in zip(a,b)];n=len(b)
 for i in range(n):
  p=max(range(i,n),key=lambda r:abs(m[r][i]));m[i],m[p]=m[p],m[i]
  q=m[i][i]
  if abs(q)<1e-14: raise ValueError("Singular factor matrix")
  m[i]=[x/q for x in m[i]]
  for r in range(n):
   if r!=i:
    q=m[r][i];m[r]=[x-q*y for x,y in zip(m[r],m[i])]
 return [m[i][-1] for i in range(n)]
def stdev(x):
 mu=sum(x)/len(x);return math.sqrt(sum((v-mu)**2 for v in x)/(len(x)-1))
def build():
 rng=random.Random(SEED); rows=[]; market=[]; sector=[]; names=list(WEIGHTS)
 params={"RailCo":(1.10,.45,.0045),"TransitTech":(.85,.72,.0050),"FreightSystems":(1.25,.30,.0060)}
 for d in range(N):
  m=rng.gauss(.00025,.010);s=rng.gauss(.00008,.006); market.append(m);sector.append(s);r={"day":d+1,"market_return":m,"sector_return":s}
  for name,(bm,bs,eps) in params.items():r[name+"_return"]=bm*m+bs*s+rng.gauss(0,eps)
  rows.append(r)
 write(DATA/"synthetic_daily_returns.csv",rows)
 portfolio=[sum(WEIGHTS[n]*r[n+"_return"] for n in names) for r in rows]
 losses=sorted(-x for x in portfolio);var=losses[math.ceil(.95*N)-1];cvar=sum(x for x in losses if x>=var)/sum(1 for x in losses if x>=var)
 wealth=peak=1.0;maxdd=0.0
 for x in portfolio:
  wealth*=1+x;peak=max(peak,wealth);maxdd=max(maxdd,1-wealth/peak)
 mu=sum(portfolio)/N;vol=stdev(portfolio);cov=sum((x-mu)*(y-sum(market)/N) for x,y in zip(portfolio,market))/(N-1);beta=cov/(stdev(market)**2)
 # OLS intercept, market and sector loadings.
 X=[[1.0,m,s] for m,s in zip(market,sector)];xtx=[[sum(row[i]*row[j] for row in X) for j in range(3)] for i in range(3)];xty=[sum(row[i]*y for row,y in zip(X,portfolio)) for i in range(3)];coef=solve(xtx,xty)
 metrics=[{"metric":"annualized_return_arithmetic","value":mu*252},{"metric":"annualized_volatility","value":vol*math.sqrt(252)},{"metric":"historical_var_95_daily_loss","value":var},{"metric":"historical_cvar_95_daily_loss","value":cvar},{"metric":"maximum_drawdown","value":maxdd},{"metric":"market_beta","value":beta},{"metric":"sharpe_rf_2pct","value":(mu-.02/252)/vol*math.sqrt(252)},{"metric":"factor_alpha_daily","value":coef[0]},{"metric":"market_factor_loading","value":coef[1]},{"metric":"sector_factor_loading","value":coef[2]}]
 write(OUT/"portfolio_risk_metrics.csv",metrics)
 scenarios=[("Market shock",-.10,0), ("Sector shock",0,-.15),("Combined severe",-.15,-.20)]
 stress=[]
 for label,ms,ss in scenarios:
  contributions={n:params[n][0]*ms+params[n][1]*ss for n in names};pr=sum(WEIGHTS[n]*contributions[n] for n in names)
  stress.append({"scenario":label,"market_factor_shock_pct":ms*100,"sector_factor_shock_pct":ss*100,"portfolio_return_pct":pr*100,"portfolio_loss_usd_per_1m":-pr*1_000_000})
 write(OUT/"factor_stress.csv",stress)
 summary=f"SYNTHETIC PORTFOLIO RISK STUDY\nObservations: {N} simulated daily returns | seed: {SEED}\nAnnualized volatility: {vol*math.sqrt(252):.1%}\nHistorical 95% one-day VaR: {var:.2%}\nHistorical 95% one-day CVaR: {cvar:.2%}\nMaximum drawdown: {maxdd:.1%}\nMarket beta: {beta:.2f}\n\nAll assets, factors, and returns are simulated. This is a method demonstration, not investment advice or evidence of real portfolio performance. Historical VaR is sample-dependent; it can understate tail risk and does not describe losses beyond the chosen sample and confidence level.\n"
 (OUT/"executive_summary.txt").write_text(summary,encoding="utf-8");return rows,metrics,stress
if __name__=="__main__":build()
