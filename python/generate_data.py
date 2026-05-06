"""
Financial KPI Dataset Generator
Generates realistic bank transaction, account, and product data
for an end-to-end ETL + KPI Dashboard project
"""

import csv, random
from datetime import datetime, timedelta

random.seed(99)

PRODUCTS    = ["Savings Account", "Current Account", "Personal Loan", "Credit Card", "Mortgage", "Investment Fund"]
REGIONS     = ["North", "South", "East", "West", "Central"]
BRANCHES    = {
    "North":   ["Hamburg-Mitte", "Hamburg-Nord", "Bremen-City"],
    "South":   ["Munich-Mitte", "Munich-South", "Augsburg"],
    "East":    ["Berlin-Mitte", "Berlin-East", "Dresden"],
    "West":    ["Cologne-City", "Dusseldorf", "Frankfurt"],
    "Central": ["Stuttgart", "Nuremberg", "Mannheim"]
}
CHANNELS    = ["Online", "Branch", "Mobile App", "ATM", "Phone"]
TX_TYPES    = ["Deposit", "Withdrawal", "Transfer", "Loan Payment", "Fee", "Interest"]
STATUS      = ["Completed", "Completed", "Completed", "Pending", "Failed"]

start_date = datetime(2022, 1, 1)

# ── 1. customers.csv ─────────────────────────────────────────────────────────
customers = []
segments  = ["Retail", "Premium", "Business", "Student"]
for i in range(1, 2001):
    region = random.choice(REGIONS)
    age    = random.randint(18, 75)
    customers.append([
        f"CUST{i:04d}",
        f"Customer {i}",
        random.choice(segments),
        age,
        region,
        random.choice(BRANCHES[region]),
        (start_date - timedelta(days=random.randint(30, 3000))).strftime("%Y-%m-%d")
    ])

with open("/home/claude/projects/2_etl_financial_kpi/data/customers.csv", "w", newline="") as f:
    csv.writer(f).writerows([["customer_id","name","segment","age","region","branch","join_date"]] + customers)
print(f"customers.csv → {len(customers)} rows")

# ── 2. accounts.csv ──────────────────────────────────────────────────────────
accounts = []
acc_id   = 1
for c in customers:
    num_accounts = random.randint(1, 3)
    for _ in range(num_accounts):
        product  = random.choice(PRODUCTS)
        balance  = round(random.uniform(-500, 250000), 2)
        accounts.append([
            f"ACC{acc_id:05d}", c[0], product,
            round(balance, 2),
            round(random.uniform(0, 5.5), 2),
            (start_date - timedelta(days=random.randint(10, 2500))).strftime("%Y-%m-%d"),
            "Active" if random.random() > 0.08 else "Dormant"
        ])
        acc_id += 1

with open("/home/claude/projects/2_etl_financial_kpi/data/accounts.csv", "w", newline="") as f:
    csv.writer(f).writerows([["account_id","customer_id","product","balance","interest_rate","open_date","status"]] + accounts)
print(f"accounts.csv → {len(accounts)} rows")

# ── 3. transactions.csv ──────────────────────────────────────────────────────
transactions = []
tx_id = 1
for day_offset in range(730):  # 2 years
    date = start_date + timedelta(days=day_offset)
    n    = random.randint(50, 200)
    for _ in range(n):
        acc   = random.choice(accounts)
        ttype = random.choice(TX_TYPES)
        if ttype in ["Deposit", "Transfer"]:
            amount = round(random.uniform(10, 50000), 2)
        elif ttype == "Withdrawal":
            amount = round(random.uniform(10, 5000), 2)
        elif ttype == "Loan Payment":
            amount = round(random.uniform(100, 3000), 2)
        else:
            amount = round(random.uniform(1, 200), 2)
        transactions.append([
            f"TX{tx_id:07d}", date.strftime("%Y-%m-%d"),
            acc[0], acc[1], ttype, amount,
            random.choice(CHANNELS), random.choice(STATUS)
        ])
        tx_id += 1

with open("/home/claude/projects/2_etl_financial_kpi/data/transactions.csv", "w", newline="") as f:
    csv.writer(f).writerows([["transaction_id","date","account_id","customer_id","type","amount","channel","status"]] + transactions)
print(f"transactions.csv → {len(transactions)} rows")

# ── 4. branch_targets.csv ────────────────────────────────────────────────────
targets = []
for region, branches in BRANCHES.items():
    for branch in branches:
        for month in range(1, 25):
            y = 2022 + (month - 1) // 12
            m = ((month - 1) % 12) + 1
            targets.append([
                f"{y}-{m:02d}", branch, region,
                round(random.uniform(800000, 5000000), 2),
                round(random.uniform(50, 300), 0),
                round(random.uniform(200000, 2000000), 2)
            ])

with open("/home/claude/projects/2_etl_financial_kpi/data/branch_targets.csv", "w", newline="") as f:
    csv.writer(f).writerows([["month","branch","region","revenue_target","new_accounts_target","loan_disbursement_target"]] + targets)
print(f"branch_targets.csv → {len(targets)} rows")
print("\nAll datasets generated successfully.")
