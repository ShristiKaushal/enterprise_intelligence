# Enterprise Intelligence Dashboard — Tableau Public Recreation Guide

## CSV Files Summary

| File | Rows | Used By |
|------|------|---------|
| `Customers.csv` | 10 | KPI-Total Customers, KPI-Avg Health Score, Customer Risk, Churn Risk Matrix |
| `SLA_Events.csv` | 5 | SLA Breach Analysis |
| `Sentiment.csv` | 12 | Sentiment Trend |

---

## How to Connect Data in Tableau Public

1. Open Tableau Public Desktop
2. **Connect → Text File** → select `Customers.csv`
3. Go back to **Add a connection** → add `SLA_Events.csv`
4. Go back to **Add a connection** → add `Sentiment.csv`
5. Do **NOT** join them — keep them as **separate data sources**. Each worksheet will use its own source.

---

## Sheet 1 — KPI: Total Customers

**Data Source:** `Customers.csv`

| Setting | Value |
|---------|-------|
| Mark type | Text |
| Text / Label | `COUNTD(Customer Id)` |
| Rows | (empty) |
| Columns | (empty) |
| Aggregation | COUNT(DISTINCT) |

**Steps:**
1. Create a new worksheet, name it **KPI - Total Customers**
2. Change data source to `Customers.csv`
3. Drag `Customer Id` to the **Text** mark
4. Right-click the pill → **Measure → Count (Distinct)**
5. Change mark type to **Text**
6. Expected display: **10**

---

## Sheet 2 — KPI: Avg Health Score

**Data Source:** `Customers.csv`

| Setting | Value |
|---------|-------|
| Mark type | Text |
| Text / Label | `AVG(Health Score)` |
| Rows | (empty) |
| Columns | (empty) |
| Aggregation | AVG |
| Format | Fixed decimal, 2 places |

**Steps:**
1. Create a new worksheet, name it **KPI - Avg Health Score**
2. Drag `Health Score` to the **Text** mark
3. Right-click → **Measure → Average**
4. Right-click pill → **Format** → Fixed, 2 decimal places
5. Expected display: **69.80**

---

## Sheet 3 — Customer Risk

**Data Source:** `Customers.csv`

| Setting | Value |
|---------|-------|
| Mark type | Bar (Horizontal) |
| Columns | `COUNTD(Customer Id)` |
| Rows | `Risk Level` |
| Color | `Risk Level` |
| Sort (Rows) | By `COUNTD(Customer Id)` Descending |
| Aggregation | COUNT(DISTINCT) |

**Steps:**
1. Create a new worksheet, name it **Customer Risk**
2. Drag `Risk Level` to **Rows**
3. Drag `Customer Id` to **Columns** → right-click → **Measure → Count (Distinct)**
4. Change mark type to **Bar**
5. Drag `Risk Level` to **Color** mark
6. Right-click `Risk Level` in Rows → **Sort** → By Field: `CNTD Customer Id`, Descending
7. **Color assignments (to match original):**
   - CRITICAL → Red/Orange
   - HIGH → Orange
   - LOW → Teal/Green
   - MEDIUM → Blue/Teal
8. Axis label: *Distinct count of Id*

---

## Sheet 4 — Churn Risk Matrix

**Data Source:** `Customers.csv`

| Setting | Value |
|---------|-------|
| Mark type | Circle |
| Columns (X-axis) | `SUM(Contract Value)` |
| Rows (Y-axis) | `AVG(Health Score)` |
| Color | `Risk Level` |
| Size | `AVG(Churn Risk Score)` |
| Detail | `Customer Name` |
| Aggregation (X) | SUM |
| Aggregation (Y) | AVG |
| Aggregation (Size) | AVG |

**Steps:**
1. Create a new worksheet, name it **Churn Risk Matrix**
2. Drag `Contract Value` to **Columns** (left as SUM — green measure pill)
3. Drag `Health Score` to **Rows** (AVG — right-click → Average)
4. Drag `Risk Level` to **Color** mark
5. Drag `Churn Risk Score` to **Size** mark (AVG)
6. Drag `Customer Name` to **Detail** mark (so each customer = 1 bubble)
7. Mark type: **Circle**
8. **X-axis:** Format as numbers (0K, 100K, 200K…) — right-click axis → Format → Numbers → Custom → `0K`
9. **Color assignments (to match original):**
   - CRITICAL → Red
   - HIGH → Orange  
   - LOW → Teal
   - MEDIUM → Blue

**Calculated Field (optional, for axis display):**
```
Contract Value (K) = [Contract Value] / 1000
```
Then use `SUM(Contract Value (K))` in Columns if you want the axis to show 0K-1000K.

---

## Sheet 5 — Sentiment Trend

**Data Source:** `Sentiment.csv`

| Setting | Value |
|---------|-------|
| Mark type | Line |
| Columns (X-axis) | `Period Start` (Month — continuous) |
| Rows (Y-axis) | `Measure Values` |
| Filter on Measure Names | `Positive Pct`, `Negative Pct` only |
| Color | `Measure Names` |
| Aggregation | AVG |

**Steps:**
1. Create a new worksheet, name it **Sentiment Trend**
2. Drag `Period Start` to **Columns**
   - Right-click → select **Month** (continuous, green pill, showing Jan-Dec)
3. Drag **both** `Positive Pct` and `Negative Pct` to **Rows**
   - Tableau will create two rows; instead right-click the second pill → **Dual Axis** OR:
   - Drag `Measure Values` to **Rows** and use **Measure Names** filter
4. **Preferred approach (Measure Names / Measure Values):**
   - Drag `Measure Names` to **Rows** filter → keep only `Positive Pct` and `Negative Pct`
   - Drag `Measure Values` to **Rows**
   - Drag `Measure Names` to **Color** mark
5. Mark type: **Line**
6. **Color assignments:**
   - Positive Pct → Pink/Red (top line ~65-74%)
   - Negative Pct → Yellow/Orange (bottom line ~11-15%)
7. X-axis label: **Period Start**
8. Y-axis label: **Value**

**Aggregation used:** AVG(Positive Pct), AVG(Negative Pct)  
*(Since there is 1 row per month, AVG = the exact value)*

---

## Sheet 6 — SLA Breach Analysis

**Data Source:** `SLA_Events.csv`

| Setting | Value |
|---------|-------|
| Mark type | Bar (Horizontal) |
| Columns | `COUNTD(Incident Id)` |
| Rows | `Severity` |
| Color | `Sla Breached` |
| Aggregation | COUNT(DISTINCT) |
| Sort (Rows) | Manual: P1, P2, P3 |

**Steps:**
1. Create a new worksheet, name it **SLA Breach Analysis**
2. Drag `Severity` to **Rows**
3. Drag `Incident Id` to **Columns** → right-click → **Measure → Count (Distinct)**
4. Mark type: **Bar**
5. Drag `Sla Breached` to **Color** mark
6. Right-click `Severity` in Rows → **Sort** → Manual order: P1, P2, P3
7. **Color assignments:**
   - True (Breached) → Red
   - False (Not Breached) → Orange
8. Axis label: *Distinct count of Id (Fact Incident)*

**Expected data:**
| Severity | Breached=True | Breached=False |
|----------|--------------|----------------|
| P1 | 2 | 0 |
| P2 | 1 | 1 |
| P3 | 0 | 1 |

---

## Dashboard Assembly

1. Create a new **Dashboard**, name it **ENTERPRISE INTELLIGENCE DASHBOARD**
2. Set size: **Custom (1200 × 800)**
3. Drag sheets in this layout:
   ```
   [KPI-Total Customers] [KPI-Avg Health Score] [Customer Risk]
   [Churn Risk Matrix]                          [SLA Breach Analysis]
   [Sentiment Trend — full width at bottom]
   ```
4. Add a **Text** object at the top with title: `ENTERPRISE INTELLIGENCE DASHBOARD`
5. Add a **Legend** for Risk Level, Sla Breached, Measure Names, Churn Risk Score

---

## Verification Checklist

| # | Sheet | Expected Value | Status |
|---|-------|----------------|--------|
| 1 | KPI - Total Customers | 10 | ✅ PASS |
| 2 | KPI - Avg Health Score | 69.80 | ✅ PASS |
| 3 | Customer Risk | CRITICAL/HIGH/LOW/MEDIUM bars | ✅ PASS |
| 4 | Churn Risk Matrix | 10 bubbles, X=0-1000K, Y=0-100 | ✅ PASS |
| 5 | Sentiment Trend | Jan-Dec line chart, 2 lines | ✅ PASS |
| 6 | SLA Breach Analysis | P1(2), P2(2), P3(1) bars | ✅ PASS |
