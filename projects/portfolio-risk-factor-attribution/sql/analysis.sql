-- Load source as synthetic_daily_returns.
SELECT AVG(RailCo_return) AS rail_mean_daily,
       AVG(TransitTech_return) AS transit_mean_daily,
       AVG(FreightSystems_return) AS freight_mean_daily,
       AVG(market_return) AS market_mean_daily
FROM synthetic_daily_returns;

SELECT day, market_return, sector_return,
       0.40 * RailCo_return + 0.35 * TransitTech_return + 0.25 * FreightSystems_return AS portfolio_return
FROM synthetic_daily_returns ORDER BY day;
