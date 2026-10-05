#!/usr/bin/env python3
"""Build four independent logistics scenario models using the standard library."""
import csv
import hashlib
import json
import math
import sqlite3
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COSTS = ['fuel_cost_usd', 'driver_cost_usd', 'maintenance_cost_usd', 'tolls_usd', 'accessorial_cost_usd']

def number(v, name, low=0, high=None):
    v = float(v)
    if not math.isfinite(v) or v < low or (high is not None and v > high):
        raise ValueError(f'Invalid {name}: {v}')
    return v

def margin(v):
    return number(v, 'target margin', 0, 0.999999)

def load_csv(path):
    with path.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def write_csv(path, rows):
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows([{k: round(v, 6) if isinstance(v, float) else v for k,v in r.items()} for r in rows])

def fuel_metrics(rows, selected_price, baseline_price, target):
    p = number(selected_price, 'diesel price', 0)
    b = number(baseline_price, 'reference diesel price', 1e-9)
    t = margin(target)
    if not rows:
        raise ValueError('No shipments')
    rev = sum(number(r['revenue_usd'], 'revenue', 1e-9) for r in rows)
    original_fuel = sum(number(r['fuel_cost_usd'], 'fuel') for r in rows)
    other = sum(sum(number(r[k], k) for k in COSTS[1:]) for r in rows)
    miles = sum(number(r['distance_miles'], 'miles', 1e-9) for r in rows)
    new_fuel = original_fuel * p / b
    cost = new_fuel + other
    return dict(shipments=len(rows), revenue_usd=rev, base_fuel_usd=original_fuel,
                inferred_gallons=original_fuel/b, scenario_fuel_usd=new_fuel,
                nonfuel_cost_usd=other, direct_cost_usd=cost, contribution_usd=rev-cost,
                contribution_margin=(rev-cost)/rev, margin_per_load_usd=(rev-cost)/len(rows),
                break_even_rate_usd_per_loaded_mile=cost/miles,
                target_rate_usd_per_loaded_mile=cost/(1-t)/miles,
                required_revenue_uplift=max(0, cost/(1-t)/rev-1),
                on_time_rate=sum(int(r['on_time']) for r in rows)/len(rows))

def ocean_metrics(a, rate_change, extra_days):
    r = number(a['revenue_usd'], 'ocean revenue', 1e-9)
    other = number(a['nonfreight_cost_usd'], 'ocean nonfreight cost')
    freight = number(a['freight_usd'], 'ocean freight')
    value = number(a['inventory_value_usd'], 'inventory value')
    carry = number(a['annual_carry_rate'], 'carry rate', 0, 1)
    baseline = number(a['baseline_transit_days'], 'baseline days')
    extra = number(extra_days, 'extra days')
    shock = number(rate_change, 'freight shock', -1)
    base_carry = value * carry * baseline / 365
    extra_carry = value * carry * extra / 365
    new_freight = freight * (1+shock)
    cost = other + new_freight + base_carry + extra_carry
    base_cost = other + freight + base_carry
    return dict(revenue_usd=r, baseline_freight_usd=freight, scenario_freight_usd=new_freight,
                baseline_carry_usd=base_carry, extra_carry_usd=extra_carry,
                total_cost_usd=cost, contribution_usd=r-cost, margin=(r-cost)/r,
                margin_erosion_usd=cost-base_cost, margin_erosion_pp=(cost-base_cost)/r*100,
                total_transit_days=baseline+extra)

def air_metrics(a, aircraft, saving):
    distance = number(a['distance_km'], 'air distance', 1e-9)
    demand = number(a['demand_tonnes'], 'air demand', 1e-9)
    payload = number(aircraft['reported_payload_tonnes'], 'payload', 1e-9)
    rng = number(aircraft['range_km'], 'range', 1e-9)
    saving = number(saving, 'fuel saving', 0, 0.999999)
    fuel = number(a['reference_fuel_kg'], 'reference fuel', 1e-9)*(1-saving)
    unit_fuel = number(a['fuel_usd_per_kg'], 'jet fuel price')
    other = number(a['nonfuel_trip_cost_usd'], 'air nonfuel')
    if aircraft['aircraft'] == 'A350F':
        other += number(a['a350f_nonfuel_premium_usd'], 'nonfuel premium')
    carried = min(demand, payload)
    feasible = distance <= rng and demand <= payload
    cost = fuel*unit_fuel+other
    miles = distance/1.609344
    return dict(distance_km=distance, demand_tonnes=demand, modeled_carried_tonnes=carried,
                unserved_tonnes=max(0, demand-payload), payload_utilization=carried/payload,
                fuel_saving_assumption=saving, modeled_fuel_kg=fuel, trip_cost_usd=cost,
                tonne_miles=carried*miles,
                cost_usd_per_tonne_mile=cost/(carried*miles) if feasible else None,
                fuel_kg_per_tonne_km=fuel/(carried*distance) if feasible else None,
                feasibility='Within published ceilings' if feasible else 'Requires mission review',
                range_utilization=distance/rng)

def vendor_metrics(v, weights, thresholds):
    if set(weights) != {'ownership','data_access','cybersecurity','route_concentration','operational_dependency'}:
        raise ValueError('Five vendor risk factors required')
    ws = {k:number(x,k+' weight',0,1) for k,x in weights.items()}
    if not math.isclose(sum(ws.values()),1,abs_tol=1e-9):
        raise ValueError('Vendor weights must total 1')
    review = number(thresholds['review'], 'review threshold', 0, 100)
    priority = number(thresholds['priority'], 'priority threshold', review, 100)
    missing = [k for k in ws if v.get(k) in ('',None)]
    scores = {k:number(v[k],k+' risk',0,100) for k in ws if k not in missing}
    lower = sum(ws[k]*scores[k] for k in scores)
    upper = lower + sum(ws[k]*100 for k in missing)
    score = lower if not missing else None
    status = 'Evidence needed' if missing else ('Priority review' if score >= priority else ('Review' if score >= review else 'Monitor'))
    return dict(risk_score=score, risk_lower_bound=lower, risk_upper_bound=upper,
                missing_factors=','.join(missing), review_status=status)

def main():
    data = ROOT/'data'; out = ROOT/'outputs'; out.mkdir(exist_ok=True)
    a = json.loads((data/'assumptions.json').read_text())
    shipments=load_csv(data/'transportation_shipments.csv')
    if len({r['shipment_id'] for r in shipments}) != len(shipments):
        raise ValueError('Duplicate shipment IDs')
    diesel=load_csv(data/'diesel_benchmarks.csv')
    prices={r['region']:float(r['usd_per_gallon']) for r in diesel}
    reference=prices[a['diesel_reference_region']]
    groups=defaultdict(list)
    for r in shipments: groups[r['lane']].append(r)
    fuel=[]
    for region,p in prices.items():
        for shock in a['fuel_shocks']:
            shock=number(shock,'diesel shock',-1)
            for lane,rs in groups.items():
                fuel.append(dict(region=region,shock=shock,lane=lane,diesel_usd_per_gallon=p*(1+shock),
                                 **fuel_metrics(rs,p*(1+shock),reference,a['target_margin'])))
    ocean=[dict(case=c['case'],rate_change=c['rate_change'],extra_days=c['extra_days'],
                **ocean_metrics(a['ocean'],c['rate_change'],c['extra_days'])) for c in a['ocean_cases']]
    aircrafts=load_csv(data/'aircraft_benchmarks.csv')
    air=[]
    for demand in [60,80,100]:
        for saving in [0,0.2,0.4]:
            for aircraft in aircrafts:
                aa={**a['air'],'demand_tonnes':demand}
                air.append(dict(scenario_id=f'D{demand}-S{round(saving*100)}',aircraft=aircraft['aircraft'],
                                **air_metrics(aa,aircraft,saving if aircraft['aircraft']=='A350F' else 0)))
    vendors=load_csv(data/'synthetic_vendors.csv')
    risk=[dict(vendor_id=v['vendor_id'],vendor_name=v['vendor_name'],
               **vendor_metrics(v,a['vendor_weights'],a['vendor_thresholds'])) for v in vendors]
    for name,rows in [('fuel_scenarios',fuel),('ocean_scenarios',ocean),('air_scenarios',air),('vendor_risk',risk)]:
        write_csv(out/(name+'.csv'),rows)
    payload=dict(assumptions=a,diesel=diesel,aircraft=aircrafts,vendors=vendors,
                 base_lanes=[dict(lane=lane,**fuel_metrics(rs,reference,reference,a['target_margin']),
                                 loaded_miles=sum(float(r['distance_miles']) for r in rs)) for lane,rs in groups.items()],
                 ocean=ocean,air=air,risk=risk,sources=json.loads((data/'sources.json').read_text()))
    (out/'dashboard_data.json').write_text(json.dumps(payload,indent=2,allow_nan=False))
    db=sqlite3.connect(out/'scenarios.sqlite')
    for table,rows in [('shipments',shipments),('diesel',diesel),('fuel_shocks',[{'shock':x} for x in a['fuel_shocks']]),
                       ('fuel_inputs',[{'reference_region':a['diesel_reference_region'],'target_margin':a['target_margin']}]),
                       ('ocean_cases',a['ocean_cases']),('ocean_inputs',[a['ocean']]),
                       ('air_inputs',[a['air']]),('aircraft',aircrafts),
                       ('air_cases',[{'scenario_id':f'D{d}-S{round(s*100)}','demand_tonnes':d,'saving':s} for d in [60,80,100] for s in [0,0.2,0.4]]),
                       ('vendors',vendors),('risk_weights',[a['vendor_weights']])]:
        db.execute(f'DROP TABLE IF EXISTS {table}')
        keys=list(rows[0])
        def numeric_key(k):
            values=[r[k] for r in rows if r.get(k) not in ('',None)]
            try:
                for v in values: float(v)
                return bool(values)
            except (ValueError,TypeError): return False
        numeric={k for k in keys if numeric_key(k)}
        columns=', '.join('"'+k+'" '+('REAL' if k in numeric else 'TEXT') for k in keys)
        db.execute(f'CREATE TABLE {table} ({columns})')
        db.executemany(f'INSERT INTO {table} VALUES ({",".join("?" for _ in keys)})',
                       [[None if r.get(k) in ('',None) else float(r[k]) if k in numeric else r[k] for k in keys] for r in rows])
    db.executescript((ROOT/'sql'/'models.sql').read_text()); db.commit(); db.close()
    template=(ROOT/'dashboard_template.html').read_text()
    (ROOT/'dashboard.html').write_text(template.replace('__DATA__',json.dumps(payload,allow_nan=False).replace('</','<\\/')))
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(data.glob('*'))}
    (out/'input_hashes.json').write_text(json.dumps(hashes,indent=2))
    print(json.dumps({'fuel_rows':len(fuel),'ocean_rows':len(ocean),'air_rows':len(air),'vendor_rows':len(risk)}))

if __name__=='__main__': main()
