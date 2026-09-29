# Freight Pricing Benchmark Calibration

## Question
How does the 500-mile pricing recommendation change when assumed costs and margin are replaced with public benchmarks?

## Data
ATRI 2025 Operational Costs of Trucking update for 2024 carrier costs and C.H. Robinson FY2025 adjusted gross profit margin.

## Method
Price = total carrier cost / (1 - target margin). The calibrated case uses $2.260 carrier cost per mile and a 16.8% target margin on price.

## Result
The quote moves from $1,146.34 ($2.29/mile) to $1,358.17 ($2.72/mile), an 18.5% increase.

## Recommendation
Use $2.72 per mile as the starting benchmark, then add lane-specific deadhead, tolls, detention, seasonality, equipment, and imbalance adjustments.

## Caveats
ATRI is a carrier-cost benchmark while C.H. Robinson is a broker. This is a sanity check, not a production quote engine.

[Open the public case and download the Excel model and decision brief](https://quincy-jones-analytics.gzsxwzqv7q.chatgpt.site/freight-pricing-calibration.html)
