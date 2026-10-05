import csv
import json
import math
import sqlite3
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import build_models as m

class Models(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a=json.loads((ROOT/'data/assumptions.json').read_text())
        cls.s=m.load_csv(ROOT/'data/transportation_shipments.csv')
        cls.aircraft=m.load_csv(ROOT/'data/aircraft_benchmarks.csv')
        cls.v=m.load_csv(ROOT/'data/synthetic_vendors.csv')
        cls.db=sqlite3.connect(ROOT/'outputs/scenarios.sqlite')
        cls.db.row_factory=sqlite3.Row
    @classmethod
    def tearDownClass(cls): cls.db.close()
    def f(self,p=6.526,target=.18): return m.fuel_metrics(self.s,p,6.526,target)
    def test_01_population_and_ids(self):
        self.assertEqual(len(self.s),1200);self.assertEqual(len({s['shipment_id'] for s in self.s}),1200)
        self.assertEqual(len({s['lane'] for s in self.s}),6)
    def test_02_original_revenue_and_cost(self):
        self.assertAlmostEqual(self.f()['revenue_usd'],958706.75,places=2)
        self.assertAlmostEqual(self.f()['direct_cost_usd'],sum(sum(float(r[k]) for k in m.COSTS) for r in self.s),places=6)
    def test_03_plus_ten_fuel_exposure(self):
        self.assertAlmostEqual(self.f()['contribution_usd']-self.f(6.526*1.1)['contribution_usd'],self.f()['base_fuel_usd']*.1,places=6)
    def test_04_minus_ten_fuel_exposure(self):
        self.assertAlmostEqual(self.f(6.526*.9)['contribution_usd']-self.f()['contribution_usd'],self.f()['base_fuel_usd']*.1,places=6)
    def test_05_nonfuel_and_service_fixed(self):
        for k in ['nonfuel_cost_usd','on_time_rate','revenue_usd','shipments']:
            self.assertEqual(self.f()[k],self.f(8)[k])
    def test_06_target_does_not_change_profit(self):
        self.assertEqual(self.f(target=.5)['contribution_usd'],self.f()['contribution_usd'])
        self.assertGreater(self.f(target=.5)['target_rate_usd_per_loaded_mile'],self.f()['target_rate_usd_per_loaded_mile'])
    def test_07_per_load_and_weighted_margin(self):
        f=self.f(); self.assertAlmostEqual(f['margin_per_load_usd']*1200,f['contribution_usd'])
        self.assertAlmostEqual(f['contribution_margin']*f['revenue_usd'],f['contribution_usd'])
    def test_08_break_even_and_target_rate(self):
        f=self.f(); miles=sum(float(r['distance_miles']) for r in self.s)
        self.assertAlmostEqual(f['break_even_rate_usd_per_loaded_mile']*miles,f['direct_cost_usd'])
        self.assertAlmostEqual(f['target_rate_usd_per_loaded_mile']*miles*(1-.18),f['direct_cost_usd'])
    def test_09_zero_fuel_price(self):
        f=self.f(0); self.assertEqual(f['scenario_fuel_usd'],0)
        self.assertEqual(f['direct_cost_usd'],f['nonfuel_cost_usd'])
    def test_10_invalid_fuel_inputs(self):
        for p,t in [(-1,.18),(math.nan,.18),(math.inf,.18),(6.526,1)]:
            with self.assertRaises(ValueError):self.f(p,t)
        with self.assertRaises(ValueError):m.fuel_metrics([],1,1,.18)
        with self.assertRaises(ValueError):m.fuel_metrics(self.s,1,0,.18)
    def test_11_regional_prices(self):
        prices={r['region']:float(r['usd_per_gallon']) for r in m.load_csv(ROOT/'data/diesel_benchmarks.csv')}
        self.assertEqual(prices['Midwest'],6.526);self.assertEqual(prices['U.S.'],6.382)
        self.assertGreater(self.f(prices['California'])['direct_cost_usd'],self.f(prices['Gulf Coast'])['direct_cost_usd'])
    def test_12_ocean_base_carry_included_once(self):
        r=m.ocean_metrics(self.a['ocean'],0,0)
        self.assertAlmostEqual(r['total_cost_usd'],14000+120000*.2*25/365)
        self.assertEqual(r['margin_erosion_usd'],0)
    def test_13_ocean_incremental_costs(self):
        r=m.ocean_metrics(self.a['ocean'],.25,10)
        self.assertAlmostEqual(r['extra_carry_usd'],120000*.2*10/365)
        self.assertAlmostEqual(r['margin_erosion_usd'],1000+120000*.2*10/365)
        self.assertAlmostEqual(r['margin_erosion_pp'],r['margin_erosion_usd']/18000*100)
    def test_14_zero_inventory_and_carry(self):
        for field in ['inventory_value_usd','annual_carry_rate']:
            r=m.ocean_metrics({**self.a['ocean'],field:0},.25,10)
            self.assertEqual(r['extra_carry_usd'],0);self.assertEqual(r['margin_erosion_usd'],1000)
    def test_15_negative_delay_rejected(self):
        with self.assertRaises(ValueError):m.ocean_metrics(self.a['ocean'],0,-1)
    def test_16_air_equal_demand_economics(self):
        x=m.air_metrics(self.a['air'],self.aircraft[0],0)
        y=m.air_metrics(self.a['air'],self.aircraft[1],.2)
        self.assertEqual(x['modeled_carried_tonnes'],y['modeled_carried_tonnes'])
        self.assertEqual(x['trip_cost_usd'],70500);self.assertEqual(y['trip_cost_usd'],67400)
        self.assertAlmostEqual(x['cost_usd_per_tonne_mile'],.2363724)
    def test_17_zero_saving_reverses_ranking(self):
        ref=m.air_metrics(self.a['air'],self.aircraft[0],0)
        zero=m.air_metrics(self.a['air'],self.aircraft[1],0)
        self.assertGreater(zero['trip_cost_usd'],ref['trip_cost_usd'])
    def test_18_air_payload_ceiling(self):
        r=m.air_metrics({**self.a['air'],'demand_tonnes':120},self.aircraft[1],.2)
        self.assertEqual(r['unserved_tonnes'],9);self.assertIsNone(r['cost_usd_per_tonne_mile'])
    def test_19_air_range_ceiling(self):
        r=m.air_metrics({**self.a['air'],'distance_km':8800},self.aircraft[1],.2)
        self.assertIsNone(r['cost_usd_per_tonne_mile']);self.assertIsNone(r['fuel_kg_per_tonne_km'])
    def test_20_air_distance_unit_conversion(self):
        a={**self.a['air'],'distance_km':1.609344}
        r=m.air_metrics(a,self.aircraft[0],0)
        self.assertAlmostEqual(r['tonne_miles'],80)
    def test_21_zero_demand_and_invalid_savings(self):
        for a,s in [({**self.a['air'],'demand_tonnes':0},.2),(self.a['air'],1),(self.a['air'],-.1)]:
            with self.assertRaises(ValueError):m.air_metrics(a,self.aircraft[1],s)
    def test_22_vendor_manual_scores(self):
        r=m.vendor_metrics(self.v[0],self.a['vendor_weights'],self.a['vendor_thresholds'])
        self.assertEqual(r['risk_score'],50.75);self.assertEqual(r['review_status'],'Review')
    def test_23_missing_vendor_evidence_bounds(self):
        r=m.vendor_metrics(self.v[3],self.a['vendor_weights'],self.a['vendor_thresholds'])
        self.assertIsNone(r['risk_score']);self.assertEqual(r['review_status'],'Evidence needed')
        self.assertEqual(r['risk_lower_bound'],48.5);self.assertEqual(r['risk_upper_bound'],73.5)
    def test_24_zero_score_is_known_not_missing(self):
        v={**self.v[3],'cybersecurity':0}
        r=m.vendor_metrics(v,self.a['vendor_weights'],self.a['vendor_thresholds'])
        self.assertEqual(r['risk_score'],48.5);self.assertEqual(r['missing_factors'],'')
    def test_25_risk_threshold_edges(self):
        for value,label in [(39.9,'Monitor'),(40,'Review'),(70,'Priority review')]:
            v={**self.v[0],**{k:value for k in self.a['vendor_weights']}}
            r=m.vendor_metrics(v,self.a['vendor_weights'],self.a['vendor_thresholds'])
            self.assertEqual(r['review_status'],label)
    def test_26_invalid_weights_and_scores(self):
        with self.assertRaises(ValueError):m.vendor_metrics(self.v[0],{**self.a['vendor_weights'],'ownership':.5},self.a['vendor_thresholds'])
        with self.assertRaises(ValueError):m.vendor_metrics({**self.v[0],'cybersecurity':101},self.a['vendor_weights'],self.a['vendor_thresholds'])
    def test_27_sql_fuel_independent_reconciliation(self):
        rows=m.load_csv(ROOT/'outputs/fuel_scenarios.csv'); self.assertEqual(len(rows),198)
        sql={(r['region'],r['shock'],r['lane']):r for r in self.db.execute('SELECT * FROM fuel_model')}
        for r in rows:
            s=sql[(r['region'],float(r['shock']),r['lane'])]
            for k in ['revenue_usd','direct_cost_usd','contribution_usd','contribution_margin','break_even_rate_usd_per_loaded_mile']:
                self.assertAlmostEqual(float(r[k]),s[k],delta=1e-6)
    def test_28_sql_ocean_reconciliation(self):
        sql={r['case_name']:r for r in self.db.execute('SELECT * FROM ocean_model')}
        for r in m.load_csv(ROOT/'outputs/ocean_scenarios.csv'):
            for k in ['total_cost_usd','contribution_usd','margin_erosion_pp']:self.assertAlmostEqual(float(r[k]),sql[r['case']][k],delta=1e-6)
    def test_29_sql_air_reconciliation(self):
        sql={(r['scenario_id'],r['aircraft']):r for r in self.db.execute('SELECT * FROM air_model')}
        for r in m.load_csv(ROOT/'outputs/air_scenarios.csv'):
            for k in ['modeled_fuel_kg','trip_cost_usd','cost_usd_per_tonne_mile']:self.assertAlmostEqual(float(r[k]),sql[(r['scenario_id'],r['aircraft'])][k],delta=1e-6)
    def test_30_sql_risk_reconciliation(self):
        sql={r['vendor_id']:r['risk_score'] for r in self.db.execute('SELECT * FROM vendor_model')}
        for r in m.load_csv(ROOT/'outputs/vendor_risk.csv'):
            if r['risk_score']=='':self.assertIsNone(sql[r['vendor_id']])
            else:self.assertAlmostEqual(float(r['risk_score']),sql[r['vendor_id']])
    def test_31_shipments_nonnegative_costs_and_binary_flags(self):
        for r in self.s:
            for k in m.COSTS+['revenue_usd','distance_miles']:self.assertGreaterEqual(float(r[k]),0)
            for k in ['on_time','service_exception']:self.assertIn(r[k],['0','1'])
    def test_32_dashboard_json_and_input_integrity(self):
        d=json.loads((ROOT/'outputs/dashboard_data.json').read_text())
        self.assertEqual(sum(r['shipments'] for r in d['base_lanes']),1200)
        self.assertIn('Prototype',d['aircraft'][1]['status'])
        self.assertNotIn('__DATA__',(ROOT/'dashboard.html').read_text())

if __name__=='__main__':unittest.main()
