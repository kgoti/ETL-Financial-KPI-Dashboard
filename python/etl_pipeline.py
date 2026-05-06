"""
ETL Pipeline – Financial KPI Dashboard
Extract → Transform → Load (Star Schema)

Reads raw CSVs, cleans and transforms data,
and outputs star schema tables ready for Power BI or SQL loading.
"""

import csv, os
from datetime import datetime
from collections import defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW  = os.path.join(BASE, "data")
OUT  = os.path.join(BASE, "data", "transformed")
os.makedirs(OUT, exist_ok=True)

def read_csv(filename):
    with open(os.path.join(RAW, filename), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def write_csv(filename, rows, headers):
    with open(os.path.join(OUT, filename), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        w.writerows(rows)
    print(f"  ✓  {filename} → {len(rows)} rows")

print("\n=== EXTRACT ===")
customers    = read_csv("customers.csv")
accounts     = read_csv("accounts.csv")
transactions = read_csv("transactions.csv")
targets      = read_csv("branch_targets.csv")
print(f"  customers: {len(customers)} | accounts: {len(accounts)} | transactions: {len(transactions)} | targets: {len(targets)}")

# ── TRANSFORM ────────────────────────────────────────────────────────────────
print("\n=== TRANSFORM ===")

## 1. dim_customer
cust_map = {c["customer_id"]: c for c in customers}
dim_customer = []
for c in customers:
    join = datetime.strptime(c["join_date"], "%Y-%m-%d")
    tenure_days = (datetime(2024, 1, 1) - join).days
    dim_customer.append({
        "customer_id":  c["customer_id"],
        "segment":      c["segment"].strip(),
        "age":          int(c["age"]),
        "age_group":    "18-25" if int(c["age"]) <= 25 else ("26-40" if int(c["age"]) <= 40 else ("41-60" if int(c["age"]) <= 60 else "60+")),
        "region":       c["region"],
        "branch":       c["branch"],
        "join_date":    c["join_date"],
        "tenure_days":  tenure_days,
        "tenure_band":  "New (<1yr)" if tenure_days < 365 else ("Growing (1-3yr)" if tenure_days < 1095 else "Loyal (3yr+)")
    })
write_csv("dim_customer.csv", dim_customer,
          ["customer_id","segment","age","age_group","region","branch","join_date","tenure_days","tenure_band"])

## 2. dim_account
dim_account = []
for a in accounts:
    balance = float(a["balance"])
    dim_account.append({
        "account_id":    a["account_id"],
        "customer_id":   a["customer_id"],
        "product":       a["product"],
        "balance":       round(balance, 2),
        "balance_band":  "Negative" if balance < 0 else ("<5k" if balance < 5000 else ("<50k" if balance < 50000 else "50k+")),
        "interest_rate": float(a["interest_rate"]),
        "open_date":     a["open_date"],
        "status":        a["status"]
    })
write_csv("dim_account.csv", dim_account,
          ["account_id","customer_id","product","balance","balance_band","interest_rate","open_date","status"])

## 3. dim_date
dates_seen = set()
dim_date = []
for t in transactions:
    d = t["date"]
    if d not in dates_seen:
        dates_seen.add(d)
        dt = datetime.strptime(d, "%Y-%m-%d")
        dim_date.append({
            "date":        d,
            "year":        dt.year,
            "quarter":     f"Q{(dt.month-1)//3+1}",
            "month":       dt.month,
            "month_name":  dt.strftime("%B"),
            "week":        dt.isocalendar()[1],
            "day_of_week": dt.weekday() + 1,
            "day_name":    dt.strftime("%A"),
            "is_weekend":  "Yes" if dt.weekday() >= 5 else "No"
        })
dim_date.sort(key=lambda x: x["date"])
write_csv("dim_date.csv", dim_date,
          ["date","year","quarter","month","month_name","week","day_of_week","day_name","is_weekend"])

## 4. fact_transactions (cleaned)
acc_map = {a["account_id"]: a for a in accounts}
fact_tx = []
skipped = 0
for t in transactions:
    if t["status"] == "Failed":  # exclude failed transactions
        skipped += 1
        continue
    acc = acc_map.get(t["account_id"], {})
    fact_tx.append({
        "transaction_id": t["transaction_id"],
        "date":           t["date"],
        "account_id":     t["account_id"],
        "customer_id":    t["customer_id"],
        "product":        acc.get("product", "Unknown"),
        "type":           t["type"],
        "amount":         round(float(t["amount"]), 2),
        "channel":        t["channel"],
        "status":         t["status"],
        "region":         cust_map.get(t["customer_id"], {}).get("region", "Unknown"),
        "branch":         cust_map.get(t["customer_id"], {}).get("branch", "Unknown"),
        "segment":        cust_map.get(t["customer_id"], {}).get("segment", "Unknown")
    })
print(f"  ✓  fact_transactions.csv → {len(fact_tx)} rows (skipped {skipped} failed)")
write_csv("fact_transactions.csv", fact_tx,
          ["transaction_id","date","account_id","customer_id","product","type","amount","channel","status","region","branch","segment"])

## 5. fact_monthly_kpis (aggregated)
monthly = defaultdict(lambda: {"revenue": 0, "tx_count": 0, "active_customers": set()})
for t in fact_tx:
    ym = t["date"][:7]
    monthly[ym]["revenue"]          += t["amount"] if t["type"] in ["Deposit", "Loan Payment", "Fee", "Interest"] else 0
    monthly[ym]["tx_count"]         += 1
    monthly[ym]["active_customers"].add(t["customer_id"])

fact_monthly = []
for ym, v in sorted(monthly.items()):
    fact_monthly.append({
        "month":            ym,
        "total_revenue":    round(v["revenue"], 2),
        "total_transactions": v["tx_count"],
        "active_customers": len(v["active_customers"])
    })
write_csv("fact_monthly_kpis.csv", fact_monthly,
          ["month","total_revenue","total_transactions","active_customers"])

print("\n=== LOAD ===")
print("  Star schema CSVs written to data/transformed/")
print("  → Import into Power BI or SQL for dashboard layer\n")
print("  Tables: dim_customer | dim_account | dim_date | fact_transactions | fact_monthly_kpis")
