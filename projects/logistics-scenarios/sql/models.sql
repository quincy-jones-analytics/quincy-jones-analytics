-- SQLite views independently reproduce Python arithmetic.
-- Midwest is the explicit normalization reference, NOT a historical consumption record.
DROP VIEW IF EXISTS fuel_model;
CREATE VIEW fuel_model AS
WITH lane AS (
 SELECT lane,COUNT(*) shipments,SUM(revenue_usd) revenue_usd,SUM(fuel_cost_usd) base_fuel_usd,
 SUM(driver_cost_usd+maintenance_cost_usd+tolls_usd+accessorial_cost_usd) other_cost,
 SUM(distance_miles) miles FROM shipments GROUP BY lane
), scenario AS (
 SELECT lane.*,diesel.region,fuel_shocks.shock,
 diesel.usd_per_gallon*(1+fuel_shocks.shock) price,
 base_fuel_usd*diesel.usd_per_gallon*(1+fuel_shocks.shock)/(SELECT usd_per_gallon FROM diesel WHERE region=(SELECT reference_region FROM fuel_inputs)) scenario_fuel
 FROM lane CROSS JOIN diesel CROSS JOIN fuel_shocks
)
SELECT region,shock,lane,shipments,revenue_usd,scenario_fuel+other_cost direct_cost_usd,
 revenue_usd-scenario_fuel-other_cost contribution_usd,
 (revenue_usd-scenario_fuel-other_cost)/revenue_usd contribution_margin,
 (scenario_fuel+other_cost)/miles break_even_rate_usd_per_loaded_mile FROM scenario;

DROP VIEW IF EXISTS ocean_model;
CREATE VIEW ocean_model AS
WITH x AS (
 SELECT c."case" case_name,i.*,c.rate_change,c.extra_days,
 freight_usd*(1+rate_change) new_freight,
 inventory_value_usd*annual_carry_rate*baseline_transit_days/365.0 base_carry,
 inventory_value_usd*annual_carry_rate*extra_days/365.0 extra_carry
 FROM ocean_cases c CROSS JOIN ocean_inputs i
)
SELECT case_name,new_freight+nonfreight_cost_usd+base_carry+extra_carry total_cost_usd,
 revenue_usd-new_freight-nonfreight_cost_usd-base_carry-extra_carry contribution_usd,
 (new_freight-freight_usd+extra_carry)/revenue_usd*100 margin_erosion_pp FROM x;

DROP VIEW IF EXISTS air_model;
CREATE VIEW air_model AS
WITH x AS (
 SELECT c.scenario_id,c.demand_tonnes,c.saving,a.aircraft,a.reported_payload_tonnes,a.range_km,
 i.distance_km,MIN(c.demand_tonnes,a.reported_payload_tonnes) carried,
 i.reference_fuel_kg*(1-CASE WHEN a.aircraft='A350F' THEN c.saving ELSE 0 END) fuel,
 i.nonfuel_trip_cost_usd+CASE WHEN a.aircraft='A350F' THEN i.a350f_nonfuel_premium_usd ELSE 0 END other_cost,
 i.fuel_usd_per_kg FROM air_cases c CROSS JOIN aircraft a CROSS JOIN air_inputs i
)
SELECT scenario_id,aircraft,fuel modeled_fuel_kg,fuel*fuel_usd_per_kg+other_cost trip_cost_usd,
 CASE WHEN distance_km<=range_km AND demand_tonnes<=reported_payload_tonnes
 THEN (fuel*fuel_usd_per_kg+other_cost)/(carried*distance_km/1.609344) ELSE NULL END cost_usd_per_tonne_mile FROM x;

DROP VIEW IF EXISTS vendor_model;
CREATE VIEW vendor_model AS
SELECT v.vendor_id,
 CASE WHEN v.ownership IS NULL OR v.data_access IS NULL OR v.cybersecurity IS NULL
 OR v.route_concentration IS NULL OR v.operational_dependency IS NULL THEN NULL
 ELSE v.ownership*w.ownership+v.data_access*w.data_access+v.cybersecurity*w.cybersecurity+
 v.route_concentration*w.route_concentration+v.operational_dependency*w.operational_dependency END risk_score
 FROM vendors v CROSS JOIN risk_weights w;
