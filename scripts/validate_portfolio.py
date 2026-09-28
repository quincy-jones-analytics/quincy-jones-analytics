#!/usr/bin/env python3
"""Build every portfolio case and run dependency-free integrity checks."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = sorted(p for p in (ROOT / "projects").iterdir() if p.is_dir() and (p / "build_case.py").exists())
CHECKS = 0


def check(label: str, condition: bool) -> None:
    global CHECKS
    CHECKS += 1
    if not condition:
        raise AssertionError(f"Check {CHECKS} failed: {label}")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    check(f"{path.relative_to(ROOT)} exists and has rows", bool(rows))
    return rows


def run_builds() -> dict[str, str]:
    hashes: dict[str, str] = {}
    for project in PROJECTS:
        builder = project / "build_case.py"
        compile(builder.read_text(encoding="utf-8"), str(builder), "exec")
        check(f"{project.name}: Python syntax", True)
        readme = project / "README.md"
        check(f"{project.name}: README present", readme.is_file() and readme.stat().st_size > 100)
        check(f"{project.name}: synthetic-data boundary stated", "synthetic" in readme.read_text(encoding="utf-8").lower())
        sql = project / "sql" / "analysis.sql"
        check(f"{project.name}: SQL review queries present", sql.is_file() and sql.read_text(encoding="utf-8").upper().count("SELECT") >= 1)
        subprocess.run([sys.executable, str(builder)], cwd=project, check=True, capture_output=True, text=True)
        csvs = sorted((project / "outputs").glob("*.csv"))
        check(f"{project.name}: generated CSV outputs", bool(csvs))
        for path in csvs:
            rows = read_csv(path)
            for row in rows:
                for value in row.values():
                    try:
                        check(f"{path.name}: numeric values finite", math.isfinite(float(value)))
                    except (ValueError, TypeError):
                        continue
            hashes[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def domain_checks(first_hashes: dict[str, str]) -> None:
    p = ROOT / "projects"
    bs = read_csv(p / "monthly-three-statement-planning/outputs/balance_sheet_rollforward.csv")
    cash = read_csv(p / "monthly-three-statement-planning/outputs/monthly_income_cashflow.csv")
    check("three-statement model has 12 periods", len(bs) == len(cash) == 12)
    check("monthly balance sheet balances", all(abs(float(r["balance_check_usd"])) <= 0.02 for r in bs))
    check("monthly income-to-cash ending balance agrees", all(abs(float(a["ending_cash_usd"]) - float(b["cash_usd"])) <= 0.02 for a, b in zip(cash, bs)))

    credit = read_csv(p / "commercial-credit-underwriting/outputs/borrower_credit_screen.csv")
    stress = read_csv(p / "commercial-credit-underwriting/outputs/downside_sensitivity.csv")
    check("credit screen has three borrowers", len(credit) == 3)
    check("credit screen has three stress cases per borrower", len(stress) == 9)
    check("credit leverage is positive", all(float(r["gross_leverage_x"]) > 0 for r in credit))
    check("credit debt-capacity bridge reconciles", all(abs(float(r["debt_headroom_usd"]) - (float(r["illustrative_3x_debt_capacity_usd"]) - float(r["debt_usd"]))) < 0.02 for r in credit))
    check("borrower downside reduces modeled EBITDA", all(float(r["stressed_ebitda_usd"]) <= float(next(x["ebitda_usd"] for x in credit if x["borrower"] == r["borrower"])) for r in stress))

    journals = read_csv(p / "erp-close-controls-bi/outputs/journal_balance_checks.csv")
    exceptions = read_csv(p / "erp-close-controls-bi/outputs/close_exceptions.csv")
    check("ERP controls identify a deliberately unbalanced journal", sum(int(r["balanced_flag"]) == 0 for r in journals) == 1)
    check("ERP controls flag unmapped accounts", any(r["control"] == "Account mapping" for r in exceptions))
    check("ERP output has an actionable exception field", all(len(r.get("action", "")) > 5 for r in exceptions))

    procurement = read_csv(p / "procurement-spend-sourcing-bi/data/synthetic_procurement_transactions.csv")
    categories = read_csv(p / "procurement-spend-sourcing-bi/outputs/category_opportunity.csv")
    monthly = read_csv(p / "procurement-spend-sourcing-bi/outputs/monthly_spend.csv")
    check("procurement source has 96 purchase orders", len(procurement) == 96)
    source_total = sum(float(r["spend_usd"]) for r in procurement)
    check("procurement category spend ties to source", abs(sum(float(r["spend_usd"]) for r in categories) - source_total) < 0.05)
    check("procurement monthly spend ties to source", abs(sum(float(r["spend_usd"]) for r in monthly) - source_total) < 0.05)
    dash = p / "procurement-spend-sourcing-bi/dashboard"
    check("interactive BI dashboard files exist", (dash / "index.html").is_file() and (dash / "dashboard-preview.svg").is_file() and (dash / "data.js").is_file())
    embedded = json.loads((dash / "data.js").read_text(encoding="utf-8").split("=", 1)[1].strip().rstrip(";"))
    check("interactive dashboard embeds all synthetic records", len(embedded) == len(procurement))
    html = (dash / "index.html").read_text(encoding="utf-8")
    check("dashboard provides all three filters", all(f'id="{name}"' in html for name in ("supplier", "category", "month")))
    check("dashboard labels benchmark values as directional", "not realized savings" in html.lower())

    risk = read_csv(p / "portfolio-risk-factor-attribution/outputs/portfolio_risk_metrics.csv")
    risk_map = {r["metric"]: float(r["value"]) for r in risk}
    check("risk simulation uses 252 observations", len(read_csv(p / "portfolio-risk-factor-attribution/data/synthetic_daily_returns.csv")) == 252)
    check("risk volatility is positive", risk_map["annualized_volatility"] > 0)
    check("portfolio CVaR is at least VaR", risk_map["historical_cvar_95_daily_loss"] >= risk_map["historical_var_95_daily_loss"] > 0)
    check("drawdown lies in [0, 1)", 0 <= risk_map["maximum_drawdown"] < 1)

    options = read_csv(p / "monte-carlo-option-pricing/outputs/option_pricing_results.csv")
    check("option model prices five strikes", len(options) == 5)
    check("Monte Carlo calls agree within four standard errors", all(abs(float(r["mc_call_usd"]) - float(r["analytic_call_usd"])) <= 4 * float(r["call_standard_error_usd"]) + 0.00001 for r in options))
    check("analytical call-put parity reconciles", all(abs(float(r["analytic_call_usd"]) - float(r["analytic_put_usd"]) - (100 - float(r["strike_usd"]) * math.exp(-0.04))) < 0.000002 for r in options))
    check("option Greeks are positive and bounded", all(0 < float(r["delta_call"]) < 1 and float(r["gamma"]) > 0 and float(r["vega_per_1pct_vol"]) > 0 for r in options))

    # Make sure every project can regenerate byte-identical output tables.
    second = run_builds()
    differences = sorted(path for path in first_hashes.keys() | second.keys() if first_hashes.get(path) != second.get(path))
    check(f"all project CSV outputs regenerate deterministically ({differences})", not differences)


if __name__ == "__main__":
    check("portfolio contains at least six project cases", len(PROJECTS) >= 6)
    first_hashes = run_builds()
    domain_checks(first_hashes)
    print(f"Portfolio validation passed: {CHECKS} checks across {len(PROJECTS)} projects.")
