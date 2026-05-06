# 🏦 End-to-End ETL Pipeline + Financial KPI Dashboard

**Tools:** Python · SQL · Power BI · DAX
**Domain:** Banking & Financial Services
**Level:** Intermediate–Advanced

---

## 📌 Project Overview

A complete end-to-end data project simulating a real-world banking analytics workflow:

**Extract** raw data (customers, accounts, transactions, branch targets)
→ **Transform** into a clean star schema (ETL pipeline in Python)
→ **Load** into Power BI for executive-level KPI reporting

This project demonstrates the full analyst-to-engineer pipeline that most BI job descriptions require.

---

## 📁 Repository Structure

```
2_etl_financial_kpi/
│
├── data/
│   ├── customers.csv          # 2,000 customers across 5 regions
│   ├── accounts.csv           # 4,034 accounts (1–3 per customer)
│   ├── transactions.csv       # 92,207 raw transactions (2 years)
│   ├── branch_targets.csv     # Monthly targets by branch
│   └── transformed/           # Star schema output (ETL output)
│       ├── dim_customer.csv
│       ├── dim_account.csv
│       ├── dim_date.csv
│       ├── fact_transactions.csv
│       └── fact_monthly_kpis.csv
│
├── python/
│   ├── generate_data.py       # Raw dataset generator
│   └── etl_pipeline.py        # ETL: Extract → Transform → Load
│
├── sql/
│   └── analysis_queries.sql   # KPI queries, MoM growth, data quality checks
│
└── README.md
```

---

## 🔄 ETL Pipeline

```
Raw CSVs
   │
   ├── EXTRACT    → Read customers, accounts, transactions, targets
   │
   ├── TRANSFORM  → Clean nulls, filter failed transactions,
   │                enrich with age bands, tenure bands, balance bands,
   │                build star schema dimensions
   │
   └── LOAD       → Write star schema CSVs to data/transformed/
                    (ready for Power BI or SQL import)
```

**Records processed:** 92,207 raw → 73,747 valid transactions (18,460 failed excluded)

---

## 📊 Star Schema

```
                    ┌─────────────┐
                    │  dim_date   │
                    └──────┬──────┘
                           │
┌──────────────┐    ┌──────▼──────────┐    ┌──────────────┐
│ dim_customer ├────┤ fact_transactions├────┤ dim_account  │
└──────────────┘    └─────────────────┘    └──────────────┘
```

---

## 🚀 How to Run

```bash
# Step 1 – Generate raw data
python python/generate_data.py

# Step 2 – Run ETL pipeline
python python/etl_pipeline.py

# Step 3 – Load data/transformed/ into Power BI
# Step 4 – Run SQL queries from sql/analysis_queries.sql
```

---

## 💡 Key KPIs Tracked

| KPI                       | Description                              |
|--------------------------|------------------------------------------|
| Monthly Revenue          | Total income-generating transactions     |
| Revenue vs Target        | Actual vs branch target achievement %    |
| Active Customers         | Unique customers transacting per month   |
| MoM Revenue Growth       | Month-over-month growth %                |
| Channel Mix              | Online vs Branch vs Mobile App split     |
| Customer Segment Value   | Revenue breakdown by Retail/Premium/Business |

---

*Built as part of a Data & BI Analyst portfolio targeting the German job market.*
