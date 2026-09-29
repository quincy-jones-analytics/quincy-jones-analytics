# Michigan Transit Cost and Productivity Benchmark

**Decision question:** Which Michigan directly operated motor-bus systems show the highest operating cost per passenger trip, and what operating factors should leaders investigate first?

## Executive finding

The 2024 Michigan peer median was **$8.53 per passenger trip**. AAATA reported **$8.28 per trip** and **16.8 passenger trips per revenue hour**, placing its unit cost near the median with productivity above the median. The widest unit-cost gaps appear in systems with low passenger trips per revenue hour and weaker recovery from 2019 ridership.

## Deliverables

- `Quincy_Jones_NTD_Transit_Cost_Benchmark.xlsx` — formula-driven peer analysis, source extract, methodology and decision dashboard
- `Quincy_Jones_NTD_Transit_Decision_Memo.pdf` — one-page recommendation
- `ntd_michigan_bus_analysis.json` — reproducible prepared data used by the model

## Scope and method

- Source: Federal Transit Administration National Transit Database
- Dataset: 2024 TS2.1 Service Data and Operating Expenses Time Series by Mode
- Peer set: 15 active Michigan Full Reporters
- Mode: Motor Bus (`MB`)
- Type of service: Directly Operated (`DO`)
- Core measures: operating cost per unlinked passenger trip, passenger trips per vehicle revenue hour, cost per vehicle revenue mile, fare recovery, general-administration share and 2019–2024 ridership recovery

## Decision use

Use unit cost as a screening measure, then distinguish demand from cost. Low passenger trips per revenue hour point toward route design, frequency, span and demand concentration. Higher cost per mile with stronger productivity points toward labor, maintenance, deadhead and service mix.

## Limitation

NTD system-level data cannot identify a specific route that loses money. Route-level passenger counts, schedules, fares and cost allocation are required before changing service. No employer-confidential information is used.

## Source

[FTA NTD TS2.1 Service Data and Operating Expenses Time Series by Mode](https://www.transit.dot.gov/ntd/data-product/ts21-service-data-and-operating-expenses-time-series-mode-2)
