-- ============================================================
-- Project 2: ETL Pipeline + Financial KPI Dashboard
-- SQL Analysis Queries (run after loading star schema tables)
-- ============================================================

-- 1. Monthly Revenue vs Target
SELECT
    f.month,
    ROUND(f.total_revenue, 2)       AS actual_revenue,
    t.revenue_target,
    ROUND(f.total_revenue / t.revenue_target * 100, 1) AS achievement_pct,
    ROUND(f.total_revenue - t.revenue_target, 2)        AS variance
FROM fact_monthly_kpis f
JOIN branch_targets t ON f.month = t.month
GROUP BY f.month, f.total_revenue, t.revenue_target
ORDER BY f.month;

-- 2. Revenue by Product and Channel
SELECT
    product,
    channel,
    COUNT(*)              AS transaction_count,
    ROUND(SUM(amount), 2) AS total_amount,
    ROUND(AVG(amount), 2) AS avg_transaction_value
FROM fact_transactions
WHERE type IN ('Deposit', 'Loan Payment', 'Fee', 'Interest')
GROUP BY product, channel
ORDER BY total_amount DESC;

-- 3. Customer Segment Analysis
SELECT
    c.segment,
    c.tenure_band,
    COUNT(DISTINCT t.customer_id)  AS customer_count,
    COUNT(t.transaction_id)        AS total_transactions,
    ROUND(SUM(t.amount), 2)        AS total_value,
    ROUND(AVG(t.amount), 2)        AS avg_transaction_value
FROM fact_transactions t
JOIN dim_customer c ON t.customer_id = c.customer_id
GROUP BY c.segment, c.tenure_band
ORDER BY total_value DESC;

-- 4. Regional Performance
SELECT
    region,
    COUNT(DISTINCT customer_id) AS active_customers,
    COUNT(transaction_id)       AS total_transactions,
    ROUND(SUM(amount), 2)       AS total_revenue,
    ROUND(AVG(amount), 2)       AS avg_tx_value
FROM fact_transactions
WHERE type IN ('Deposit', 'Loan Payment', 'Fee', 'Interest')
GROUP BY region
ORDER BY total_revenue DESC;

-- 5. Channel Mix Analysis
SELECT
    channel,
    COUNT(*)                                       AS transactions,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS channel_share_pct,
    ROUND(SUM(amount), 2)                          AS total_amount
FROM fact_transactions
GROUP BY channel
ORDER BY transactions DESC;

-- 6. Top 10 High-Value Customers
SELECT
    t.customer_id,
    c.segment,
    c.region,
    c.tenure_band,
    COUNT(t.transaction_id)  AS total_transactions,
    ROUND(SUM(t.amount), 2)  AS total_value,
    ROUND(AVG(t.amount), 2)  AS avg_tx_value
FROM fact_transactions t
JOIN dim_customer c ON t.customer_id = c.customer_id
GROUP BY t.customer_id, c.segment, c.region, c.tenure_band
ORDER BY total_value DESC
LIMIT 10;

-- 7. Month-over-Month Revenue Growth
SELECT
    month,
    total_revenue,
    LAG(total_revenue) OVER (ORDER BY month)       AS prev_month_revenue,
    ROUND(
        (total_revenue - LAG(total_revenue) OVER (ORDER BY month))
        / LAG(total_revenue) OVER (ORDER BY month) * 100, 2
    ) AS mom_growth_pct
FROM fact_monthly_kpis
ORDER BY month;

-- 8. Account Status Summary
SELECT
    product,
    status,
    COUNT(*)              AS account_count,
    ROUND(SUM(balance), 2) AS total_balance,
    ROUND(AVG(balance), 2) AS avg_balance
FROM dim_account
GROUP BY product, status
ORDER BY product, status;

-- 9. Data Quality Check (ETL Validation)
SELECT 'Null customer_id in transactions' AS check_name, COUNT(*) AS issues FROM fact_transactions WHERE customer_id IS NULL
UNION ALL
SELECT 'Orphaned account_id',              COUNT(*) FROM fact_transactions t LEFT JOIN dim_account a ON t.account_id = a.account_id WHERE a.account_id IS NULL
UNION ALL
SELECT 'Negative amounts',                 COUNT(*) FROM fact_transactions WHERE amount < 0
UNION ALL
SELECT 'Duplicate transaction_ids',        COUNT(*) - COUNT(DISTINCT transaction_id) FROM fact_transactions;
