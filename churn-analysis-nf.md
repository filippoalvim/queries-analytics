# 📋 Churn Analysis — Methodology & Queries

This document details the analytical process for defining **pre-churn**, **churn**, and **post-churn** thresholds in VR's receipt scanning product, including the three approaches tested and the evolution of the reasoning.

---

## Business Problem

VR's receipt submission product allows workers to scan their fiscal receipts and earn cashback and benefits. Re-engagement campaigns need to be triggered **at the right moment** — not too early (spamming active users), and not too late (user already lost).

The central question was:

> **After how many days without submitting a receipt should a user be classified as at churn risk?**

---

## Data Structure

The analysis base contains the receipt submission history per user (`cpf`), with the date of each scan. The goal is to compute the **gap between consecutive submissions** and derive a behavioral indicator per user.

---

## Approach 1 — Maximum Interval

### Logic

For each user, calculate the **largest recorded gap** between two consecutive receipt submissions.

```sql
WITH base_events AS (
    SELECT
        cpf AS user_id,
        submission_date AS event_date,
        LEAD(submission_date) OVER (
            PARTITION BY cpf
            ORDER BY submission_date
        ) AS next_event_date
    FROM analytics_layer.fact_nf_events
),

intervals AS (
    SELECT
        user_id,
        CASE
            WHEN next_event_date IS NULL
                THEN DATEDIFF(CURRENT_DATE, event_date)
            ELSE DATEDIFF(next_event_date, event_date)
        END AS days_between_events
    FROM base_events
),

max_per_user AS (
    SELECT
        user_id,
        MAX(days_between_events) AS max_days_between_events
    FROM intervals
    GROUP BY user_id
)

SELECT
    max_days_between_events,
    COUNT(DISTINCT user_id) AS user_count
FROM max_per_user
GROUP BY max_days_between_events
ORDER BY max_days_between_events;
```

### Why it doesn't work

The **maximum represents the user's worst moment** — a trip, a vacation period, a device change. A user who submits receipts daily but was inactive for 90 days in August would be treated as a low-frequency user.

> ❌ Maximizes the outlier and does not represent habitual behavior.

---

## Approach 2 — Mean Interval

### Logic

For each user, calculate the **average of all intervals** between consecutive submissions.

```sql
WITH base_events AS (
    SELECT
        cpf AS user_id,
        submission_date AS event_date,
        LEAD(submission_date) OVER (
            PARTITION BY cpf
            ORDER BY submission_date
        ) AS next_event_date
    FROM analytics_layer.fact_nf_events
),

intervals AS (
    SELECT
        user_id,
        CASE
            WHEN next_event_date IS NULL
                THEN DATEDIFF(CURRENT_DATE, event_date)
            ELSE DATEDIFF(next_event_date, event_date)
        END AS days_between_events
    FROM base_events
),

mean_per_user AS (
    SELECT
        user_id,
        AVG(days_between_events) AS mean_days_between_events
    FROM intervals
    GROUP BY user_id
)

SELECT
    ROUND(mean_days_between_events, 0) AS mean_days,
    COUNT(DISTINCT user_id) AS user_count
FROM mean_per_user
GROUP BY ROUND(mean_days_between_events, 0)
ORDER BY mean_days;
```

### Why it doesn't work

The mean is **sensitive to outliers**. Consider a user with 3 recorded intervals: `[2, 2, 135]`. Their mean is ~46 days — making it appear they submit receipts every month and a half, when in practice they submit almost every day. The fewer receipts a user submitted, the greater the impact of a single atypical interval on the mean.

> ❌ The mean depends on submission count and is distorted by occasional pauses.

---

## Approach 3 — Median Interval ✅

### Logic

For each user, calculate the **median of all intervals** between consecutive submissions using `PERCENTILE_APPROX`.

```sql
WITH base_events AS (
    SELECT
        user_id,
        event_date,
        LEAD(event_date) OVER (
            PARTITION BY user_id
            ORDER BY event_date
        ) AS next_event_date
    FROM analytics_layer.fact_user_events
),

intervals AS (
    SELECT
        user_id,
        CASE
            WHEN next_event_date IS NULL
                THEN DATEDIFF(CURRENT_DATE, event_date)
            ELSE DATEDIFF(next_event_date, event_date)
        END AS days_between_events
    FROM base_events
),

median_per_user AS (
    SELECT
        user_id,
        PERCENTILE_APPROX(days_between_events, 0.5) AS median_days_between_events
    FROM intervals
    GROUP BY user_id
),

distribution AS (
    SELECT
        median_days_between_events,
        COUNT(DISTINCT user_id) AS user_count
    FROM median_per_user
    GROUP BY median_days_between_events
),

cumulative AS (
    SELECT
        median_days_between_events,
        user_count,
        SUM(user_count) OVER (
            ORDER BY median_days_between_events
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_users,
        ROUND(
            SUM(user_count) OVER (
                ORDER BY median_days_between_events
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) * 100.0
            / SUM(user_count) OVER (),
        2) AS cumulative_pct
    FROM distribution
)

SELECT
    *,
    LAG(cumulative_pct) OVER (
        ORDER BY median_days_between_events
    ) AS previous_pct,
    cumulative_pct
        - LAG(cumulative_pct) OVER (
            ORDER BY median_days_between_events
        ) AS pct_difference
FROM cumulative
ORDER BY median_days_between_events;
```

### Why it works

The median represents the **central value of each user's interval distribution**. For the same example `[2, 2, 135]`, the median is **2 days** — correctly identifying this as a high-frequency user. It combines frequency with recurrence and is robust to outliers.

> ✅ Represents the user's real and habitual behavior.

---

## Distribution Results

Using the median as the base metric, the cumulative distribution curve revealed:

| Median Interval | Cumulative % of Users   |
|-----------------|-------------------------|
| ≤ 1 day         | ~40%                    |
| ≤ 5 days        | ~65%                    |
| ≤ 10 days       | ~75%                    |
| **≤ 15 days**   | **~80% ← Pareto**       |
| ≤ 30 days       | ~90%                    |

### Logarithmic Curve

The curve shape is **logarithmic**: the cumulative percentage grows very fast in the first days and progressively slows down. This confirms that:

1. The base is dominated by high-frequency users
2. Larger intervals represent an increasingly smaller and shrinking share of users
3. The marginal increment per additional day of interval brings very few new users past ~15 days

```
Cumulative %
   100% |                                                    __________
    90% |                                     ______________/
    80% |                        ____________/ ← Pareto (15 days)
    70% |               ________/
    60% |          _____/
    40% |    ______/
    20% |___/ ← 40% submit receipts every day
     0% +----+----+----+----+----+----+----+----+----+-----→ days
          0   1   2   3   4   5   7   10  12  15  20  30
```

---

## Churn Threshold Definition

Based on the Pareto curve and observed behavior, thresholds were defined as follows:

| Stage          | Criterion                                                              |
|----------------|------------------------------------------------------------------------|
| **Active**     | Within the habitual submission interval (up to the Pareto point)       |
| **Pre-Churn**  | Exceeded the habitual interval — signal of declining engagement        |
| **Churn**      | Inactive long enough to characterize habit abandonment                 |
| **Post-Churn** | Inactive for a period significantly above the churn threshold          |

The **15-day** cutoff (80th percentile of the base) was used as the anchor to calibrate these thresholds, ensuring that risk classification is **grounded in behavioral evidence** rather than an arbitrary criterion.

---

## Approach Comparison

| Metric  | Sensitive to Outliers? | Represents habitual behavior? | Recommended? |
|---------|------------------------|-------------------------------|--------------|
| Maximum | ✅ Yes                 | ❌ No                         | ❌           |
| Mean    | ✅ Yes                 | ⚠️ Partially                 | ❌           |
| Median  | ❌ No                  | ✅ Yes                        | ✅           |

---

## Technologies Used

- **SQL** — Spark SQL / Databricks
- **Window Functions** — `LEAD`, `LAG`, `SUM OVER`, `ROW_NUMBER`
- **Applied Statistics** — `PERCENTILE_APPROX`, cumulative distribution, Pareto principle
- **CTEs** — modular structure for clarity and logic reuse
