#!/usr/bin/env python3
"""Price European options by Black-Scholes and Monte Carlo simulation."""
import csv, math, random
from pathlib import Path
ROOT=Path(__file__).resolve().parent; DATA=ROOT/"data"; OUT=ROOT/"outputs"
SPOT=100.0; RATE=.04; VOL=.25; TENOR=1.0; SEED=1948; PAIRS=50000
def cdf(x): return .5*(1+math.erf(x/math.sqrt(2)))
def bs(spot,strike,rate,vol,t):
 d1=(math.log(spot/strike)+(rate+.5*vol*vol)*t)/(vol*math.sqrt(t));d2=d1-vol*math.sqrt(t)
 call=spot*cdf(d1)-strike*math.exp(-rate*t)*cdf(d2)
 put=strike*math.exp(-rate*t)*cdf(-d2)-spot*cdf(-d1)
 return call,put,d1,d2
def write(path,rows):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open("w",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def build():
 assumptions=[{"spot_usd":SPOT,"risk_free_rate":RATE,"volatility":VOL,"tenor_years":TENOR,"simulation_pairs":PAIRS,"seed":SEED,"method":"Geometric Brownian motion; antithetic variates"}]
 write(DATA/"synthetic_model_assumptions.csv",assumptions)
 rng=random.Random(SEED); strikes=[80.,90.,100.,110.,120.]; sims={k:[] for k in strikes}; zvals=[]
 drift=(RATE-.5*VOL*VOL)*TENOR; diffusion=VOL*math.sqrt(TENOR)
 for _ in range(PAIRS):
  z=rng.gauss(0,1);zvals.append(z)
  for k in strikes:
   st1=SPOT*math.exp(drift+diffusion*z);st2=SPOT*math.exp(drift-diffusion*z);disc=math.exp(-RATE*TENOR)
   sims[k].append((disc*(max(st1-k,0)+max(st2-k,0))/2,disc*(max(k-st1,0)+max(k-st2,0))/2))
 rows=[]
 for k in strikes:
  call,put,d1,d2=bs(SPOT,k,RATE,VOL,TENOR); pairs=sims[k];mc=sum(x[0] for x in pairs)/PAIRS;se=math.sqrt(sum((x[0]-mc)**2 for x in pairs)/(PAIRS-1)/PAIRS)
  rows.append({"strike_usd":k,"analytic_call_usd":round(call,6),"mc_call_usd":round(mc,6),"call_standard_error_usd":round(se,6),"call_error_in_se":round((mc-call)/se,3),"analytic_put_usd":round(put,6),"mc_put_usd":round(sum(x[1] for x in pairs)/PAIRS,6),"delta_call":round(cdf(d1),6),"gamma":round(math.exp(-.5*d1*d1)/math.sqrt(2*math.pi)/(SPOT*VOL*math.sqrt(TENOR)),6),"vega_per_1pct_vol":round(SPOT*math.exp(-.5*d1*d1)/math.sqrt(2*math.pi)*math.sqrt(TENOR)*.01,6)})
 write(OUT/"option_pricing_results.csv",rows)
 convergence=[]
 for k in (80.,100.,120.):
  truth=bs(SPOT,k,RATE,VOL,TENOR)[0]
  for n in (100,1000,10000,PAIRS):
   x=sims[k][:n];est=sum(q[0] for q in x)/n;se=math.sqrt(sum((q[0]-est)**2 for q in x)/(n-1)/n) if n>1 else 0
   convergence.append({"strike_usd":k,"pairs":n,"mc_call_usd":round(est,6),"analytic_call_usd":round(truth,6),"standard_error_usd":round(se,6),"absolute_error_usd":round(abs(est-truth),6)})
 write(OUT/"convergence.csv",convergence)
 # Finite-difference delta and gamma at ATM provide an independent Greek check.
 h=1.; c0=bs(SPOT,100,RATE,VOL,TENOR)[0];cm=bs(SPOT-h,100,RATE,VOL,TENOR)[0];cp=bs(SPOT+h,100,RATE,VOL,TENOR)[0]
 greeks=[{"metric":"analytic_put_call_parity_difference","value":round(rows[2]["analytic_call_usd"]-rows[2]["analytic_put_usd"]-(SPOT-100*math.exp(-RATE*TENOR)),10)},{"metric":"finite_difference_atm_delta","value":round((cp-cm)/(2*h),6)},{"metric":"finite_difference_atm_gamma","value":round((cp-2*c0+cm)/(h*h),6)}]
 write(OUT/"independent_greek_checks.csv",greeks)
 summary=f"SYNTHETIC OPTION PRICING STUDY\nUnderlying: ${SPOT:.2f} | volatility: {VOL:.0%} | rate: {RATE:.1%} | tenor: {TENOR:.1f} year\nMonte Carlo paths: {2*PAIRS:,} (antithetic pairs)\nATM analytic call: ${rows[2]['analytic_call_usd']:.4f}\nATM Monte Carlo call: ${rows[2]['mc_call_usd']:.4f}\nATM Monte Carlo standard error: ${rows[2]['call_standard_error_usd']:.4f}\n\nSynthetic model study under constant-volatility, constant-rate geometric Brownian motion. It omits dividends, stochastic volatility, jumps, transaction costs, early exercise, and calibration to market quotes. Not investment advice.\n"
 (OUT/"executive_summary.txt").write_text(summary,encoding="utf-8");return rows,convergence,greeks
if __name__=="__main__":build()
