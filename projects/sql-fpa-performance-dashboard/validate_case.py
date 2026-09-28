#!/usr/bin/env python3
"""Run dependency-free integrity, reconciliation, and reproducibility checks."""
from __future__ import annotations

import csv
import hashlib
import math
import py_compile
import xml.etree.ElementTree as ET
from pathlib import Path

import build_case

ROOT = Path(__file__).resolve().parent
CHECKS = 0


def check(label: str, condition: bool) -> None:
    global CHECKS
    CHECKS += 1
    if not condition:
        raise AssertionError(f"Check {CHECKS} failed: {label}")


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def sha(paths: list[Path]) -> dict[str, str]:
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def main() -> None:
    py_compile.compile(str(ROOT / "build_case.py"), doraise=True)
    check("builder compiles", True)
    check("README describes synthetic data", "synthetic" in (ROOT / "README.md").read_text(encoding="utf-8").lower())
    check("schema declares foreign keys", "FOREIGN KEY" in (ROOT / "sql/schema.sql").read_text(encoding="utf-8").upper() or "REFERENCES DIM_ACCOUNT" in (ROOT / "sql/schema.sql").read_text(encoding="utf-8").upper())
    sql_files = sorted((ROOT / "sql").glob("*.sql"))
    check("four analytical SQL scripts are present", len(sql_files) == 5)
    check("all analytical scripts contain SELECT", all("SELECT" in p.read_text(encoding="utf-8").upper() for p in sql_files if p.name != "schema.sql"))
    check("CTEs and window functions are demonstrated", all(token in (ROOT / "sql/monthly_performance.sql").read_text(encoding="utf-8").upper() for token in ("WITH", "LAG(", "OVER", "ROWS BETWEEN")))
    check("cost-center SQL ranks units", "DENSE_RANK()" in (ROOT / "sql/cost_center_performance.sql").read_text(encoding="utf-8").upper())
    check("variance bridge covers four lines", "UNION ALL" in (ROOT / "sql/analysis.sql").read_text(encoding="utf-8").upper())
    check("SQL practice path has six steps", len([line for line in (ROOT.parent.parent / "learning/sql-practice-path.md").read_text(encoding="utf-8").splitlines() if line.startswith(tuple(f"| {i} |" for i in range(1, 7)))]) == 6)
    dax = (ROOT / "powerbi/measures.dax").read_text(encoding="utf-8")
    check("Power BI guide is explicit about PBIX boundary", "does not include a `.pbix`" in (ROOT / "powerbi/model-guide.md").read_text(encoding="utf-8"))
    check("DAX contains EBITDA measure", "Actual EBITDA =" in dax and "Budget EBITDA =" in dax)
    check("DAX contains favorable variance measures", "EBITDA Variance Favorable =" in dax and "Revenue Variance Favorable =" in dax)
    check("DAX contains working-capital proxy measures", "Actual CCC Proxy Days =" in dax and "Actual DSO Proxy Days =" in dax)

    data = ROOT / "data"
    accounts, centers, periods = rows(data / "dim_account.csv"), rows(data / "dim_cost_center.csv"), rows(data / "dim_period.csv")
    actuals, budgets, wc = rows(data / "fact_actuals.csv"), rows(data / "fact_budget.csv"), rows(data / "fact_working_capital.csv")
    check("account dimension has six unique accounts", len(accounts) == len({r["account_id"] for r in accounts}) == 6)
    check("cost-center dimension has three unique centers", len(centers) == len({r["cost_center"] for r in centers}) == 3)
    check("period dimension has twelve unique periods", len(periods) == len({r["period"] for r in periods}) == 12)
    check("period keys are chronological ISO month keys", [r["period"] for r in periods] == sorted(r["period"] for r in periods))
    check("actual fact has complete month-center-account grain", len(actuals) == 12 * 3 * 6)
    check("budget fact has complete month-center-account grain", len(budgets) == 12 * 3 * 6)
    check("actual fact key is unique", len(actuals) == len({(r["period"], r["cost_center"], r["account_id"]) for r in actuals}))
    check("budget fact key is unique", len(budgets) == len({(r["period"], r["cost_center"], r["account_id"]) for r in budgets}))
    check("working-capital table has actual and budget for every month", len(wc) == 24 and len({(r["period"], r["scenario"]) for r in wc}) == 24)
    check("account foreign keys resolve", all(r["account_id"] in {a["account_id"] for a in accounts} for r in actuals + budgets))
    check("all financial amounts are finite and non-negative", all(math.isfinite(float(r["amount_usd"])) and float(r["amount_usd"]) >= 0 for r in actuals + budgets))
    check("revenue has non-zero activity", sum(float(r["amount_usd"]) for r in actuals if r["account_id"] == "4000") > 0)

    monthly = rows(ROOT / "outputs/monthly_performance.csv")
    cc = rows(ROOT / "outputs/cost_center_performance.csv")
    work = rows(ROOT / "outputs/working_capital.csv")
    bridge = rows(ROOT / "outputs/performance_bridge.csv")
    check("monthly query returns twelve rows", len(monthly) == 12)
    check("cost-center query returns 36 rows", len(cc) == 36)
    check("working-capital query returns twelve rows", len(work) == 12)
    check("full-year bridge returns four rows", len(bridge) == 4)
    check("query output periods are chronological", [r["period"] for r in monthly] == sorted(r["period"] for r in monthly))
    check("bridge includes revenue, costs, opex, and EBITDA", {r["bridge_step"] for r in bridge} == {"Revenue", "Cost of Services", "Operating Expenses", "EBITDA"})

    acc_group = {r["account_id"]: r["pnl_group"] for r in accounts}
    act_by = {}
    bud_by = {}
    for r in actuals:
        act_by.setdefault((r["period"], acc_group[r["account_id"]]), 0.0)
        act_by[(r["period"], acc_group[r["account_id"]])] += float(r["amount_usd"])
    for r in budgets:
        bud_by.setdefault((r["period"], acc_group[r["account_id"]]), 0.0)
        bud_by[(r["period"], acc_group[r["account_id"]])] += float(r["amount_usd"])
    for r in monthly:
        p = r["period"]
        check(f"{p}: revenue ties to source actuals", abs(float(r["actual_revenue_usd"]) - act_by[p, "Revenue"]) < 0.02)
        check(f"{p}: cost of services ties to source actuals", abs(float(r["actual_cost_of_services_usd"]) - act_by[p, "Cost of Services"]) < 0.02)
        check(f"{p}: operating expenses tie to source actuals", abs(float(r["actual_operating_expenses_usd"]) - act_by[p, "Operating Expenses"]) < 0.02)
        check(f"{p}: EBITDA identity reconciles", abs(float(r["actual_ebitda_usd"]) - (float(r["actual_revenue_usd"]) - float(r["actual_cost_of_services_usd"]) - float(r["actual_operating_expenses_usd"]))) < 0.02)
        check(f"{p}: favorable EBITDA variance formula reconciles", abs(float(r["ebitda_variance_favorable_usd"]) - (float(r["actual_ebitda_usd"]) - float(r["budget_ebitda_usd"]))) < 0.02)
        check(f"{p}: EBITDA margin is between 0 and 1", 0 < float(r["actual_ebitda_margin_pct"]) < 1)
        center_month = [c for c in cc if c["period"] == p]
        check(f"{p}: cost-center actual EBITDA ties to consolidated", abs(sum(float(c["actual_ebitda_usd"]) for c in center_month) - float(r["actual_ebitda_usd"])) < 0.02)
        check(f"{p}: cost-center budget EBITDA ties to consolidated", abs(sum(float(c["budget_ebitda_usd"]) for c in center_month) - float(r["budget_ebitda_usd"])) < 0.02)
    for i, r in enumerate(monthly):
        expected_ytd = sum(float(x["actual_ebitda_usd"]) for x in monthly[:i + 1])
        check(f"{r['period']}: YTD EBITDA reconciles", abs(float(r["ytd_actual_ebitda_usd"]) - expected_ytd) < 0.02)
        expected_roll = sum(float(x["actual_ebitda_usd"]) for x in monthly[max(0, i - 2):i + 1]) / len(monthly[max(0, i - 2):i + 1])
        check(f"{r['period']}: rolling EBITDA reconciles", abs(float(r["rolling_3m_actual_ebitda_usd"]) - expected_roll) < 0.02)
        if i:
            check(f"{r['period']}: prior-month EBITDA reconciles", abs(float(r["prior_month_actual_ebitda_usd"]) - float(monthly[i - 1]["actual_ebitda_usd"])) < 0.02)
    for r in work:
        check(f"{r['period']}: working capital identity reconciles", abs(float(r["actual_net_working_capital_usd"]) - (float(r["actual_ar_usd"]) + float(r["actual_inventory_usd"]) - float(r["actual_ap_usd"]))) < 0.02)
        check(f"{r['period']}: CCC proxy identity reconciles", abs(float(r["cash_conversion_cycle_proxy_days"]) - (float(r["dso_monthly_proxy_days"]) + float(r["dio_monthly_proxy_days"]) - float(r["dpo_monthly_proxy_days"]))) < 0.0001)
    for r in bridge:
        bridge_col = {
            "Revenue": "actual_revenue_usd", "Cost of Services": "actual_cost_of_services_usd",
            "Operating Expenses": "actual_operating_expenses_usd", "EBITDA": "actual_ebitda_usd"
        }[r["bridge_step"]]
        check(f"{r['bridge_step']}: annual bridge ties to monthly outputs", abs(float(r["actual_usd"]) - sum(float(m[bridge_col]) for m in monthly)) < 0.02)

    svg = ROOT / "outputs/dashboard-preview.svg"
    xml = ET.parse(svg).getroot()
    check("dashboard preview is valid SVG XML", xml.tag.endswith("svg"))
    svg_text = "".join(xml.itertext())
    check("dashboard shows actual-versus-budget trend", "Monthly EBITDA: actual vs budget" in svg_text)
    check("dashboard labels fictional data and proxy boundary", "Synthetic training case only" in svg_text and "monthly run-rate proxies" in svg_text)
    check("executive readout includes action-oriented review", "Review sequence" in (ROOT / "outputs/executive_readout.md").read_text(encoding="utf-8"))

    generated = sorted(list((ROOT / "data").glob("*.csv")) + list((ROOT / "outputs").glob("*.csv")) + [svg, ROOT / "outputs/executive_readout.md"])
    first = sha(generated)
    build_case.build()
    second = sha(generated)
    check("all generated CSV, SVG, and readout files are deterministic", first == second)
    print(f"SQL-FP&A case validation passed: {CHECKS} checks.")


if __name__ == "__main__":
    main()
