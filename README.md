# 📊 Churn Analysis — Receipt Scanning (VR)

This repository documents the **behavioral churn analysis** of users in VR's receipt scanning product, focused on defining **pre-churn**, **churn**, and **post-churn** thresholds based on real user submission patterns.

## 📊 Interactive Dashboard

> **[🔗 Open interactive visualization](https://htmlpreview.github.io/?https://raw.githubusercontent.com/filippoalvim/churn-analisys-receipt/main/assets/churn-dashboard.html)**
>
> Explore the logarithmic distribution curve, filter by day interval, and see user count and cumulative percentage indicators in real time.

---

## 🧩 Problem Context

VR's receipt submission product allows workers to scan their fiscal receipts and earn cashback and benefits. To trigger re-engagement campaigns with precision, the key question was:

> **"How many days without submitting a receipt characterizes a user at risk of churn?"**

The answer required understanding each user's **submission frequency pattern** — not an arbitrary threshold based on intuition.

---

## 🔬 Statistical Approach Evolution

To define the typical interval between submissions per user, **three statistical approaches** were tested, each with its own limitations:

### 1️⃣ Maximum — "The worst-case scenario"

The first attempt was to calculate the **largest gap** between two consecutive receipt submissions per user.

**Problem:** the maximum represents the user's worst moment, not their habitual behavior. A user who submits receipts daily but went 90 days without submitting during a vacation would be classified as a late-churn user — completely distorting the analysis.

> ❌ Maximizes the outlier. Does not represent actual behavior.

---

### 2️⃣ Mean — "Skewed by extremes"

The second approach was to calculate the **average of all intervals** between submissions.

**Problem:** the mean is highly sensitive to outliers. A user who submitted 3 receipts — two with a 2-day gap and one with a 135-day gap — would have an average of ~46 days, masking that they are, in practice, a frequent user.

> ❌ Distorted by atypical intervals. Penalizes recurring users who had occasional pauses.

---

### 3️⃣ Median — "The user's real frequency"

The final approach was to calculate the **median of all intervals** between consecutive submissions per user.

The median combines **frequency** with **recurrence**: it represents the most typical interval for that user, ignoring extreme peaks and valleys. It is robust to outliers and faithfully reflects the user's submission rhythm.

> ✅ Represents the user's central behavior. The ideal choice for churn definition.

---

## 📈 User Distribution by Median Interval

With the median calculated per user, a **cumulative distribution curve** was built — percentage of users per day-interval bucket.

### Key findings:

```
Interval (days)   | Cumulative % of Users
------------------|------------------------
≤ 1 day           | ~40%
≤ 5 days          | ~65%
≤ 10 days         | ~75%
≤ 15 days         | ~80%   ← Pareto Point
≤ 30 days         | ~90%
```

### Logarithmic Curve

The cumulative distribution chart forms a **logarithmic curve**, revealing a clear pattern:

> **The longer the submission interval, the smaller the incremental gain of new users in that group.**

Growth is fast in the first few days and progressively slows down — a typical behavior of a user base concentrated in highly frequent users.

```
Cumulative %
   100% |                                          ___________
    80% |                          _______________/
    60% |               __________/
    40% |    ___________/
    20% |___/
     0% +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+---→ days
        0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
```

---

## 🎯 Conclusions & Churn Threshold Definition

### Pareto Point (80/20)

Applying the **Pareto principle**, we identified that **80% of users have a median submission interval of up to 15 days**. This is the inflection point that anchors the churn definition:

| Stage          | Definition                                                                |
|----------------|---------------------------------------------------------------------------|
| **Active**     | User within their habitual submission interval                            |
| **Pre-Churn**  | User who exceeded their habitual interval but hasn't reached the critical threshold |
| **Churn**      | User who reached the Pareto-based threshold (≥ 15 days for 80% of the base) |
| **Post-Churn** | User inactive for a period significantly above the churn threshold        |

### High-Frequency Insight

> **40% of users have a median interval of ≤ 1 day**, meaning **4 out of 10 users submit receipts every single day.**

This data reinforces that the user base has a core of highly engaged users — making the churn definition even more critical to avoid triggering premature re-engagement alerts for this group.

---

## 🛠️ Techniques & Tools

| Category            | Technology / Technique                          |
|---------------------|-------------------------------------------------|
| Language            | SQL (Spark SQL / Databricks)                    |
| Window Functions    | `LEAD`, `LAG`, `SUM OVER`, `ROW_NUMBER`         |
| Statistics          | `PERCENTILE_APPROX` (median), mean, maximum     |
| Query structure     | Layered CTEs for separation of concerns         |
| Validation          | Excel with synthetic data                       |

---

## 📁 Files

| File | Description |
|------|-------------|
| [`churn-analysis`](./churn-analysis) | Final SQL query with median calculation, distribution and cumulative percentage |
| [`churn-analysis-nf.md`](./churn-analysis-nf.md) | Full methodology document with all 3 SQL approaches and conclusions |
| [`tb_nfs_ofertas_campanhas.ipynb`](./tb_nfs_ofertas_campanhas.ipynb) | Complete NF campaign processing pipeline (Databricks) |
| [`portfolio_distribuicao_dias_sem_envio_sintetico.xlsx`](./portfolio_distribuicao_dias_sem_envio_sintetico.xlsx) | Synthetic distribution data used for portfolio validation |

---

## 📬 Contact

* LinkedIn: [filippocupolillo](https://www.linkedin.com/in/filippocupolillo/)
* Email: filippoalvim@gmail.com
