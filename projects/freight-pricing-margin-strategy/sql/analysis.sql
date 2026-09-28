-- Import data/synthetic_bid_history.csv as bids.
SELECT lane, COUNT(*) AS bids, SUM(awarded) AS awards,
       ROUND(1.0*SUM(awarded)/COUNT(*),4) AS win_rate,
       ROUND(SUM(CASE WHEN awarded=1 THEN current_quote_usd ELSE 0 END),2) AS awarded_revenue_usd,
       ROUND(SUM(CASE WHEN awarded=1 THEN estimated_cost_usd ELSE 0 END),2) AS awarded_cost_usd,
       ROUND((SUM(CASE WHEN awarded=1 THEN current_quote_usd ELSE 0 END)
             - SUM(CASE WHEN awarded=1 THEN estimated_cost_usd ELSE 0 END))
             / NULLIF(SUM(CASE WHEN awarded=1 THEN current_quote_usd ELSE 0 END),0),4) AS awarded_margin
FROM bids GROUP BY lane ORDER BY awarded_margin;

-- Cost-plus reference price at a 20% contribution margin; not a demand forecast.
SELECT lane, ROUND(AVG(current_quote_usd),2) AS avg_quote_usd,
       ROUND(AVG(estimated_cost_usd),2) AS avg_estimated_cost_usd,
       ROUND(AVG(estimated_cost_usd)/(1-0.20),2) AS reference_price_usd
FROM bids GROUP BY lane ORDER BY lane;
