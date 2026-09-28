#!/usr/bin/env python3
"""Build a deterministic, synthetic driver-based FP&A planning case."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUT = ROOT / "outputs"
SEGMENTS = {
    "Core": {"base_units": 880, "price": 410, "variable_cost": 248, "fixed_cost": 89000, "opex": 61000},
    "Enterprise": {"base_units": 290, "price": 1120, "variable_cost": 605, "fixed_cost": 76000, "opex": 82000},
    "Services": {"base_units": 520, "price": 285, "variable_cost": 108, "fixed_cost": 42000, "opex": 51000},
}
SEASONAL = [0.94, 0.92, 1.00, 0.98, 1.02, 1.00, 1.01, 1.04, 1.01, 1.08, 1.13, 1.17]
SCENARIOS = {
    "Downside": {"unit_growth": -0.012, "price_growth": 0.000, "cost_inflation": 0.035, "opex_growth": 0.025},
    "Base": {"unit_growth": 0.012, "price_growth": 0.018, "cost_inflation": 0.025, "opex_growth": 0.020},
    "Upside": {"unit_growth": 0.027, "price_growth": 0.025, "cost_inflation": 0.020, "opex_growth": 0.018},
}

def money(x: float) -> float:
    return round(x, 2)

def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

def build() -> dict:
    actuals = []
    for month in range(1, 7):
        for j, (segment, p) in enumerate(SEGMENTS.items()):
            units = round(p["base_units"] * SEASONAL[month-1] * (1 + 0.006 * month + 0.004 * j))
            price = p["price"] * (1 + 0.0015 * month)
            variable = p["variable_cost"] * (1 + 0.002 * month)
            actuals.append({"month": f"2026-{month:02d}", "segment": segment, "units": units,
                "price_per_unit_usd": money(price), "variable_cost_per_unit_usd": money(variable),
                "fixed_cost_usd": money(p["fixed_cost"] * (1 + 0.001 * month)),
                "operating_expense_usd": money(p["opex"] * (1 + 0.002 * month))})
    write_csv(DATA / "synthetic_actuals_h1.csv", actuals)
    rows = []
    for scenario, a in SCENARIOS.items():
        for month in range(7, 13):
            for j, (segment, p) in enumerate(SEGMENTS.items()):
                latest = actuals[(6-1)*len(SEGMENTS)+j]
                units = round(latest["units"] * (1 + a["unit_growth"]) ** (month-6) * SEASONAL[month-1] / SEASONAL[5])
                price = latest["price_per_unit_usd"] * (1 + a["price_growth"]) ** (month-6)
                var = latest["variable_cost_per_unit_usd"] * (1 + a["cost_inflation"]) ** (month-6)
                fixed = p["fixed_cost"] * (1 + 0.001 * month) * (1 + a["cost_inflation"] * 0.35) ** (month-6)
                opex = p["opex"] * (1 + 0.002 * month) * (1 + a["opex_growth"]) ** (month-6)
                revenue = units * price
                variable_cost = units * var
                gross_profit = revenue - variable_cost
                ebitda = gross_profit - fixed - opex
                rows.append({"scenario": scenario, "month": f"2026-{month:02d}", "segment": segment,
                    "units": units, "revenue_usd": money(revenue), "variable_cost_usd": money(variable_cost),
                    "gross_profit_usd": money(gross_profit), "fixed_cost_usd": money(fixed),
                    "operating_expense_usd": money(opex), "ebitda_usd": money(ebitda),
                    "ebitda_margin": round(ebitda / revenue, 4)})
    write_csv(OUT / "h2_scenario_model.csv", rows)
    annual = []
    for scenario in SCENARIOS:
        # H1 actuals are included once; H2 is selected by scenario.
        h1_revenue = sum(x["units"] * x["price_per_unit_usd"] for x in actuals)
        h1_ebitda = sum(x["units"] * (x["price_per_unit_usd"] - x["variable_cost_per_unit_usd"]) - x["fixed_cost_usd"] - x["operating_expense_usd"] for x in actuals)
        h2 = [x for x in rows if x["scenario"] == scenario]
        revenue = h1_revenue + sum(x["revenue_usd"] for x in h2)
        ebitda = h1_ebitda + sum(x["ebitda_usd"] for x in h2)
        annual.append({"scenario": scenario, "fy2026_revenue_usd": money(revenue), "fy2026_ebitda_usd": money(ebitda),
            "fy2026_ebitda_margin": round(ebitda / revenue, 4), "h1_actual_revenue_usd": money(h1_revenue),
            "h1_actual_ebitda_usd": money(h1_ebitda), "h2_forecast_revenue_usd": money(sum(x["revenue_usd"] for x in h2)),
            "h2_forecast_ebitda_usd": money(sum(x["ebitda_usd"] for x in h2))})
    write_csv(OUT / "annual_scenario_summary.csv", annual)
    base = next(x for x in annual if x["scenario"] == "Base")
    down = next(x for x in annual if x["scenario"] == "Downside")
    up = next(x for x in annual if x["scenario"] == "Upside")
    summary = ("SYNTHETIC FP&A PLANNING CASE\nAll operating and financial values are simulated, not employer results.\n\n"
        f"Base FY2026 revenue: ${base['fy2026_revenue_usd']:,.0f}\nBase FY2026 EBITDA: ${base['fy2026_ebitda_usd']:,.0f} ({base['fy2026_ebitda_margin']:.1%} margin)\n"
        f"Downside-to-upside EBITDA range: ${down['fy2026_ebitda_usd']:,.0f} to ${up['fy2026_ebitda_usd']:,.0f}\n"
        f"H2 base forecast revenue: ${base['h2_forecast_revenue_usd']:,.0f}\nH2 base forecast EBITDA: ${base['h2_forecast_ebitda_usd']:,.0f}\n\n"
        "Leadership use: use the scenario range to set forecast guardrails, identify the unit/price/cost drivers to monitor, and agree an owner and trigger for a reforecast.\n"
        "This deterministic demonstration does not include working capital, tax, financing, product cannibalization, or actual company history.\n")
    (OUT / "executive_summary.txt").write_text(summary, encoding="utf-8")
    return {"actuals": actuals, "scenario": rows, "annual": annual, "summary": summary}

if __name__ == "__main__":
    r = build(); print(r["summary"])
