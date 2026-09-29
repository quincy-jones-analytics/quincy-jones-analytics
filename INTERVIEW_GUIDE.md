# Interview Guide: Four Flagship Portfolio Cases

This file is a preparation aid, not a claim of employer results. Public-data projects cite their sources; synthetic projects are labeled.

## 1) Freight Pricing Benchmark Calibration

- **Question:** How does a simple 500-mile quote change when public operating benchmarks replace assumed costs?
- **Data:** ATRI operating-cost benchmarks and a public freight broker's reported adjusted gross profit margin.
- **Method:** Translate per-mile benchmarks into trip cost, divide cost by one minus the target price margin, and compare the calibrated quote with the original worked case.
- **Finding:** The modeled quote increases from $2.29 to $2.72 per mile.
- **Recommendation:** Validate deadhead, tolls, detention, insurance, and lane conditions before using any benchmark-based quote.
- **Caveat:** Public averages are not a carrier's actual cost structure and do not replace current lane-market data.

## 2) Transportation Profitability Dashboard

- **Question:** Which lane should be reviewed first for margin and service risk?
- **Data:** 1,200 synthetic shipments across six lanes.
- **Method:** Reproducible Python and SQLite-ready SQL calculate revenue, direct cost, contribution margin, on-time rate, and exception rate; DAX measures support a Power BI build.
- **Finding:** The case models $958,707 of revenue and a 25.9% weighted contribution margin. Detroit–Cleveland is lowest at 17.6%, below the scenario's 18% target.
- **Recommendation:** Review cost-to-serve, shipment mix, contract terms, and service exceptions on Detroit–Cleveland before considering a rate action.
- **Caveat:** The data are synthetic. The finding is a review priority, not verified savings or a real customer recommendation.

## 3) Michigan Transit Cost and Productivity

- **Question:** Which agency-level operating patterns deserve management review?
- **Data:** 2024 National Transit Database records for 15 Michigan motor-bus systems, with 2019 comparisons where available.
- **Method:** Compare cost per passenger trip, passenger trips per revenue hour, and ridership recovery; use multiple metrics to avoid ranking agencies from one ratio.
- **Finding:** Cost per trip can look unfavorable for reasons that productivity and recovery measures help explain.
- **Recommendation:** Use a multi-metric review queue, then investigate service design and local operating context before drawing conclusions.
- **Caveat:** These are agency-level—not route-level—records and cannot prove that a particular route loses money.

## 4) SaaS Unit Economics and Pricing

- **Question:** How do three public SaaS companies compare on growth, gross margin, free-cash-flow margin, and Rule of 40?
- **Data:** Latest annual 10-K figures for Salesforce, ServiceNow, and Adobe.
- **Method:** Standardize fiscal-year financials, calculate each metric from cited statements, and apply one consistent Rule of 40 definition.
- **Finding:** ServiceNow leads this selected comparison at 55.3%, followed by Adobe at 52.0% and Salesforce at 44.3%.
- **Recommendation:** For Salesforce, protect recurring revenue with targeted packaging, committed-consumption bands, and value segmentation before using broad discounting.
- **Caveat:** Fiscal calendars, business mixes, and company-specific definitions reduce perfect comparability. This is portfolio analysis, not investment advice.

## Explain any project in 60 seconds

1. State the business question.
2. Name the source and whether the data are public or synthetic.
3. Explain one calculation in plain language.
4. Give the finding without overstating causality.
5. Recommend the next management action.
6. End with the most important limitation.
