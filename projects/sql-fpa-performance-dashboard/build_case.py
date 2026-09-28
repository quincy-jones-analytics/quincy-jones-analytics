#!/usr/bin/env python3
"""Create a synthetic SQL-first FP&A performance and working-capital case."""
from __future__ import annotations

import csv
import html
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUT = ROOT / "outputs"
SQL = ROOT / "sql"
PERIODS = [f"2025-{month:02d}" for month in range(1, 13)]
CENTERS = ["Dedicated Fleet", "Freight Brokerage", "Corporate"]
ACCOUNTS = [
    ("4000", "Transportation Revenue", "Revenue", "Revenue"),
    ("5000", "Direct Labor", "Cost of Services", "Expense"),
    ("5100", "Fuel and Maintenance", "Cost of Services", "Expense"),
    ("6000", "Operating Payroll", "Operating Expenses", "Expense"),
    ("6100", "Technology and Systems", "Operating Expenses", "Expense"),
    ("6200", "General and Administrative", "Operating Expenses", "Expense"),
]
SEASON = [0.94, 0.97, 1.00, 1.02, 1.04, 1.01, 1.03, 1.02, 1.06, 1.08, 1.12, 1.18]
WEIGHTS = {"Dedicated Fleet": 0.55, "Freight Brokerage": 0.35, "Corporate": 0.10}


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def money(value: float) -> float:
    return round(value, 2)


def make_inputs() -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    account_rows = [dict(account_id=a, account_name=n, pnl_group=g, account_type=t) for a, n, g, t in ACCOUNTS]
    actuals, budgets = [], []
    revenue_factors = {"Dedicated Fleet": 0.61, "Freight Brokerage": 0.39, "Corporate": 0.0}
    expense_factors = {
        "5000": {"Dedicated Fleet": 0.53, "Freight Brokerage": 0.32, "Corporate": 0.15},
        "5100": {"Dedicated Fleet": 0.72, "Freight Brokerage": 0.28, "Corporate": 0.0},
        "6000": {"Dedicated Fleet": 0.43, "Freight Brokerage": 0.32, "Corporate": 0.25},
        "6100": {"Dedicated Fleet": 0.36, "Freight Brokerage": 0.34, "Corporate": 0.30},
        "6200": {"Dedicated Fleet": 0.25, "Freight Brokerage": 0.25, "Corporate": 0.50},
    }
    monthly_base = {"4000": 1_150_000, "5000": 338_000, "5100": 205_000, "6000": 188_000, "6100": 51_000, "6200": 67_000}
    # Small deterministic pattern makes actuals differ from budget without random seeds.
    for mi, period in enumerate(PERIODS):
        season = SEASON[mi]
        for account_id, _, _, _ in ACCOUNTS:
            base_actual_factor = {
                "4000": [1.01, .99, 1.03, 1.00, .98, 1.02, 1.01, 1.04, .99, 1.03, 1.02, 1.05],
                "5000": [1.00, 1.02, 1.01, .99, 1.03, 1.02, 1.00, 1.04, 1.02, 1.01, 1.05, 1.03],
                "5100": [1.04, 1.03, 1.01, 1.06, 1.05, 1.02, 1.04, 1.03, 1.07, 1.04, 1.06, 1.05],
                "6000": [1.00, 1.00, 1.01, 1.00, 1.00, 1.02, 1.01, 1.00, 1.01, 1.02, 1.02, 1.01],
                "6100": [1.03, 1.00, 1.02, 1.00, 1.03, 1.00, 1.02, 1.00, 1.03, 1.00, 1.02, 1.00],
                "6200": [1.00, 1.02, 1.00, .99, 1.01, 1.00, 1.02, 1.00, 1.00, 1.03, 1.01, 1.00],
            }[account_id][mi]
            for center in CENTERS:
                factor = revenue_factors[center] if account_id == "4000" else expense_factors[account_id][center]
                budget = monthly_base[account_id] * season * factor
                actual = budget * base_actual_factor
                # Dedicated fleet is less productive in high fuel months; corporate expense is stable.
                if account_id == "5100" and center == "Dedicated Fleet" and mi in (5, 8, 10):
                    actual *= 1.025
                actuals.append({"period": period, "cost_center": center, "account_id": account_id, "amount_usd": money(actual)})
                budgets.append({"period": period, "cost_center": center, "account_id": account_id, "amount_usd": money(budget)})

    wc_actual, wc_budget = [], []
    for mi, period in enumerate(PERIODS):
        actual_rev = sum(r["amount_usd"] for r in actuals if r["period"] == period and r["account_id"] == "4000")
        budget_rev = sum(r["amount_usd"] for r in budgets if r["period"] == period and r["account_id"] == "4000")
        actual_cost = sum(r["amount_usd"] for r in actuals if r["period"] == period and r["account_id"] in ("5000", "5100"))
        budget_cost = sum(r["amount_usd"] for r in budgets if r["period"] == period and r["account_id"] in ("5000", "5100"))
        for scenario, rev, cost, rows in (("Actual", actual_rev, actual_cost, wc_actual), ("Budget", budget_rev, budget_cost, wc_budget)):
            rows.append({
                "period": period,
                "scenario": scenario,
                "accounts_receivable_usd": money(rev * (38 + (mi % 3)) / 30),
                "inventory_usd": money(cost * 17 / 30),
                "accounts_payable_usd": money(cost * 32 / 30),
            })
    period_rows = [
        {"period": p, "period_start": p + "-01", "fiscal_year": int(p[:4]), "quarter": f"Q{(int(p[5:]) - 1) // 3 + 1}", "month_num": int(p[5:])}
        for p in PERIODS
    ]
    center_rows = [{"cost_center": center} for center in CENTERS]
    return account_rows, actuals, budgets, wc_actual + wc_budget, period_rows, center_rows


def build_visuals() -> None:
    with (OUT / "monthly_performance.csv").open(newline="", encoding="utf-8") as f:
        monthly = list(csv.DictReader(f))
    with (OUT / "performance_bridge.csv").open(newline="", encoding="utf-8") as f:
        bridge = {r["bridge_step"]: r for r in csv.DictReader(f)}
    revenue = sum(float(r["actual_revenue_usd"]) for r in monthly)
    ebitda = sum(float(r["actual_ebitda_usd"]) for r in monthly)
    ebitda_var = float(bridge["EBITDA"]["favorable_variance_usd"])
    money_fmt = lambda n: f"${n / 1_000_000:.2f}M"
    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="760" viewBox="0 0 1280 760">',
        '<rect width="1280" height="760" fill="#f3f6fa"/><rect width="1280" height="132" fill="#10233f"/>',
        '<text x="42" y="56" fill="#fff" font-family="Arial" font-size="30" font-weight="700">FP&amp;A Performance &amp; Working Capital</text>',
        '<text x="42" y="91" fill="#c4d2e3" font-family="Arial" font-size="16">Synthetic transportation services company · FY2025 · Actual vs budget</text>',
        '<text x="42" y="117" fill="#74dbc6" font-family="Arial" font-size="12" font-weight="700">MONTHLY FINANCE REVIEW</text>',
    ]
    def txt(x, y, text, size=14, color="#19304c", weight="400"):
        svg.append(f'<text x="{x}" y="{y}" fill="{color}" font-family="Arial" font-size="{size}" font-weight="{weight}">{html.escape(str(text))}</text>')
    for x, label, value, sub in [
        (40, "FY REVENUE", money_fmt(revenue), "Synthetic actuals"),
        (452, "FY EBITDA", money_fmt(ebitda), f"{ebitda / revenue:.1%} margin"),
        (864, "EBITDA VS BUDGET", ("+" if ebitda_var >= 0 else "−") + money_fmt(abs(ebitda_var)), "Favorable variance convention"),
    ]:
        svg.append(f'<rect x="{x}" y="154" width="376" height="102" rx="12" fill="#fff" stroke="#d9e2ee"/>')
        txt(x + 20, 183, label, 12, "#60738c", "700"); txt(x + 20, 222, value, 29, "#10233f", "700"); txt(x + 20, 244, sub, 12, "#74859b")
    svg.append('<rect x="40" y="278" width="760" height="330" rx="12" fill="#fff" stroke="#d9e2ee"/><rect x="820" y="278" width="420" height="330" rx="12" fill="#fff" stroke="#d9e2ee"/>')
    txt(64, 314, "Monthly EBITDA: actual vs budget", 18, "#10233f", "700"); txt(64, 337, "USD · positive variance is favorable", 12, "#74859b")
    plot_x, plot_y, plot_w, plot_h = 90, 372, 660, 180
    max_v = max(float(r[k]) for r in monthly for k in ("actual_ebitda_usd", "budget_ebitda_usd"))
    svg.append(f'<line x1="{plot_x}" y1="{plot_y + plot_h}" x2="{plot_x + plot_w}" y2="{plot_y + plot_h}" stroke="#cbd6e3"/>')
    for i, r in enumerate(monthly):
        actual, budget = float(r["actual_ebitda_usd"]), float(r["budget_ebitda_usd"])
        group_w = plot_w / 12; bar_w = 16; base_x = plot_x + i * group_w + 9
        for bx, value, color in ((base_x, actual, "#168c89"), (base_x + bar_w + 3, budget, "#9fb2c8")):
            h = value / max_v * plot_h
            svg.append(f'<rect x="{bx:.1f}" y="{plot_y + plot_h - h:.1f}" width="{bar_w}" height="{h:.1f}" rx="3" fill="{color}"/>')
        txt(base_x + 2, plot_y + plot_h + 22, r["period"][5:], 10, "#74859b")
    svg.append('<rect x="610" y="322" width="10" height="10" rx="2" fill="#168c89"/><rect x="688" y="322" width="10" height="10" rx="2" fill="#9fb2c8"/>')
    txt(625, 331, "Actual", 11, "#60738c"); txt(703, 331, "Budget", 11, "#60738c")
    txt(64, 584, "Source: synthetic monthly GL-style actuals and budget · amounts are USD", 11, "#74859b")
    txt(844, 314, "Full-year variance bridge", 18, "#10233f", "700"); txt(844, 337, "USD · favorable variance", 12, "#74859b")
    for i, name in enumerate(("Revenue", "Cost of Services", "Operating Expenses", "EBITDA")):
        r = bridge[name]; y = 382 + i * 47; v = float(r["favorable_variance_usd"])
        txt(844, y, name, 13, "#526780", "700" if name == "EBITDA" else "400")
        txt(844, y + 20, ("+" if v >= 0 else "−") + money_fmt(abs(v)), 18, "#168c89" if v >= 0 else "#c86549", "700")
    svg.append('<rect x="40" y="632" width="1200" height="84" rx="12" fill="#fff7ef" stroke="#f1d8bf"/>')
    txt(64, 665, "Management focus", 14, "#644522", "700")
    txt(64, 689, "Review fuel and maintenance variance by operating unit; confirm working-capital days before changing the cash outlook.", 13, "#644522")
    txt(40, 744, "Synthetic training case only · no employer data · working-capital days are monthly run-rate proxies", 11, "#74859b")
    svg.append('</svg>')
    (OUT / "dashboard-preview.svg").write_text("\n".join(svg), encoding="utf-8")
    with (OUT / "working_capital.csv").open(newline="", encoding="utf-8") as f:
        wc = list(csv.DictReader(f))
    peak_gap = max(wc, key=lambda r: abs(float(r["nwc_variance_usd"])))
    (OUT / "executive_readout.md").write_text(
        "# Management readout — synthetic case\n\n"
        f"- FY2025 actual revenue: **{money_fmt(revenue)}**.\n"
        f"- FY2025 actual EBITDA: **{money_fmt(ebitda)}** ({ebitda / revenue:.1%} margin).\n"
        f"- EBITDA favorable variance to budget: **{('+' if ebitda_var >= 0 else '−') + money_fmt(abs(ebitda_var))}**.\n"
        f"- Largest monthly net working-capital gap vs budget: **{peak_gap['period']}**, {money_fmt(float(peak_gap['nwc_variance_usd']))}.\n\n"
        "**Review sequence:** use the cost-center ranking to isolate cost drivers; validate fuel, maintenance, labor, and service assumptions; then refresh receivable, inventory, and payable timing before revising the cash outlook. Favorable variance signs are normalized by financial-statement line. All inputs are generated and illustrative.\n",
        encoding="utf-8",
    )


def export_query(connection: sqlite3.Connection, query_path: Path, output_path: Path) -> int:
    rows = connection.execute(query_path.read_text(encoding="utf-8")).fetchall()
    fields = [column[0] for column in connection.execute(query_path.read_text(encoding="utf-8")).description]
    write_csv(output_path, fields, [dict(zip(fields, row)) for row in rows])
    return len(rows)


def build() -> None:
    DATA.mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)
    accounts, actuals, budgets, wc, periods, centers = make_inputs()
    write_csv(DATA / "dim_account.csv", ["account_id", "account_name", "pnl_group", "account_type"], accounts)
    write_csv(DATA / "fact_actuals.csv", ["period", "cost_center", "account_id", "amount_usd"], actuals)
    write_csv(DATA / "fact_budget.csv", ["period", "cost_center", "account_id", "amount_usd"], budgets)
    write_csv(DATA / "fact_working_capital.csv", ["period", "scenario", "accounts_receivable_usd", "inventory_usd", "accounts_payable_usd"], wc)
    write_csv(DATA / "dim_period.csv", ["period", "period_start", "fiscal_year", "quarter", "month_num"], periods)
    write_csv(DATA / "dim_cost_center.csv", ["cost_center"], centers)

    db = sqlite3.connect(":memory:")
    db.executescript((SQL / "schema.sql").read_text(encoding="utf-8"))
    for table, rows in (("dim_account", accounts), ("fact_actuals", actuals), ("fact_budget", budgets), ("fact_working_capital", wc)):
        db.executemany(f"INSERT INTO {table} ({','.join(rows[0].keys())}) VALUES ({','.join('?' for _ in rows[0])})", [tuple(row.values()) for row in rows])
    export_query(db, SQL / "monthly_performance.sql", OUT / "monthly_performance.csv")
    export_query(db, SQL / "cost_center_performance.sql", OUT / "cost_center_performance.csv")
    export_query(db, SQL / "working_capital.sql", OUT / "working_capital.csv")
    export_query(db, SQL / "analysis.sql", OUT / "performance_bridge.csv")
    db.close()
    build_visuals()


if __name__ == "__main__":
    build()
