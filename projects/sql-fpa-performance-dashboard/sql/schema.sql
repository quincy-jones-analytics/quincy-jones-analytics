PRAGMA foreign_keys = ON;

CREATE TABLE dim_account (
    account_id TEXT PRIMARY KEY,
    account_name TEXT NOT NULL,
    pnl_group TEXT NOT NULL CHECK (pnl_group IN ('Revenue', 'Cost of Services', 'Operating Expenses')),
    account_type TEXT NOT NULL CHECK (account_type IN ('Revenue', 'Expense'))
);

CREATE TABLE fact_actuals (
    period TEXT NOT NULL,
    cost_center TEXT NOT NULL,
    account_id TEXT NOT NULL REFERENCES dim_account(account_id),
    amount_usd REAL NOT NULL CHECK (amount_usd >= 0),
    PRIMARY KEY (period, cost_center, account_id)
);

CREATE TABLE fact_budget (
    period TEXT NOT NULL,
    cost_center TEXT NOT NULL,
    account_id TEXT NOT NULL REFERENCES dim_account(account_id),
    amount_usd REAL NOT NULL CHECK (amount_usd >= 0),
    PRIMARY KEY (period, cost_center, account_id)
);

CREATE TABLE fact_working_capital (
    period TEXT NOT NULL,
    scenario TEXT NOT NULL CHECK (scenario IN ('Actual', 'Budget')),
    accounts_receivable_usd REAL NOT NULL CHECK (accounts_receivable_usd >= 0),
    inventory_usd REAL NOT NULL CHECK (inventory_usd >= 0),
    accounts_payable_usd REAL NOT NULL CHECK (accounts_payable_usd >= 0),
    PRIMARY KEY (period, scenario)
);

CREATE INDEX ix_actuals_period ON fact_actuals(period);
CREATE INDEX ix_actuals_cost_center ON fact_actuals(cost_center);
CREATE INDEX ix_budget_period ON fact_budget(period);
