"""
export_tableau_csv.py
Exports PostgreSQL data into clean Tableau-ready CSV files.
Run from the backend/ directory:
    ./venv/bin/python scripts/export_tableau_csv.py
"""

import os, csv
import psycopg2

DB_URL = "postgresql://rajeevkumar:Harshith@localhost:5432/postgres"
conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tableau_exports")
os.makedirs(OUT_DIR, exist_ok=True)

def write_csv(filename, query):
    filepath = os.path.join(OUT_DIR, filename)
    cur.execute(query)
    rows = cur.fetchall()
    col_names = [desc[0] for desc in cur.description]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(col_names)
        writer.writerows(rows)
    print(f"  {filename}  ->  {len(rows)} rows  ->  {filepath}")
    return filepath

print("\n=== Exporting Tableau CSV files ===\n")

# ── 1. Customers.csv ──────────────────────────────────────────────────────────
write_csv("Customers.csv", """
SELECT
    dc.id                   AS customer_id,
    dc.canonical_id         AS customer_code,
    dc.name                 AS customer_name,
    dc.company              AS company,
    dc.industry             AS industry,
    dc.region               AS region,
    dc.country              AS country,
    dc.tier                 AS tier,
    dc.contract_value       AS contract_value,
    dc.since_date           AS since_date,
    dc.is_active            AS is_active,
    dc.health_score         AS health_score,
    dc.churn_risk_score     AS churn_risk_score,
    dc.risk_level           AS risk_level,
    ach.trend               AS trend,
    ach.churn_probability   AS churn_probability,
    ach.ticket_count_30d    AS ticket_count_30d,
    ach.incident_count_30d  AS incident_count_30d,
    ach.sla_breach_count_30d AS sla_breach_count_30d,
    ach.avg_resolution_hours AS avg_resolution_hours,
    dc.created_at           AS created_at
FROM dim_customer dc
LEFT JOIN analytics_customer_health ach ON dc.id = ach.customer_id
ORDER BY dc.canonical_id
""")

# ── 2. SLA_Events.csv ─────────────────────────────────────────────────────────
write_csv("SLA_Events.csv", """
SELECT
    fi.id                    AS incident_id,
    fi.incident_number       AS incident_number,
    fi.customer_id           AS customer_id,
    dc.name                  AS customer_name,
    fi.title                 AS title,
    fi.severity              AS severity,
    fi.priority              AS priority,
    fi.status                AS status,
    fi.category              AS category,
    fi.subcategory           AS subcategory,
    fi.sla_breached          AS sla_breached,
    fi.occurred_at           AS occurred_at,
    fi.detected_at           AS detected_at,
    fi.resolved_at           AS resolved_at,
    fi.downtime_minutes      AS downtime_minutes,
    fi.resolution_time_hours AS resolution_time_hours,
    fi.root_cause            AS root_cause,
    fi.root_cause_category   AS root_cause_category,
    fi.affected_users_count  AS affected_users_count,
    fi.business_impact       AS business_impact,
    fi.created_at            AS created_at
FROM fact_incident fi
LEFT JOIN dim_customer dc ON fi.customer_id = dc.id
ORDER BY fi.occurred_at DESC
""")

# ── 3. Sentiment.csv ──────────────────────────────────────────────────────────
write_csv("Sentiment.csv", """
SELECT
    id                                          AS sentiment_id,
    DATE_TRUNC('month', period_start)::date     AS period_start,
    DATE_TRUNC('month', period_end)::date       AS period_end,
    period_type                                 AS period_type,
    customer_id                                 AS customer_id,
    service_id                                  AS service_id,
    product_id                                  AS product_id,
    category                                    AS category,
    total_records                               AS total_records,
    positive_count                              AS positive_count,
    neutral_count                               AS neutral_count,
    negative_count                              AS negative_count,
    ROUND(positive_pct::numeric, 2)             AS positive_pct,
    ROUND(neutral_pct::numeric, 2)              AS neutral_pct,
    ROUND(negative_pct::numeric, 2)             AS negative_pct,
    ROUND(avg_sentiment_score::numeric, 4)      AS avg_sentiment_score
FROM analytics_sentiment
ORDER BY period_start
""")

# ── Verification ──────────────────────────────────────────────────────────────
print("\n=== Dashboard Field Verification ===\n")

cur.execute("SELECT COUNT(DISTINCT id) FROM dim_customer")
total_cust = cur.fetchone()[0]
print(f"[1] KPI - Total Customers    COUNTD(customer_id) = {total_cust}  -> {'PASS' if total_cust == 10 else 'FAIL'}")

cur.execute("SELECT ROUND(AVG(health_score)::numeric,2) FROM dim_customer")
avg_h = float(cur.fetchone()[0])
print(f"[2] KPI - Avg Health Score   AVG(health_score)   = {avg_h}  -> {'PASS' if abs(avg_h-69.80)<1 else 'FAIL'}")

cur.execute("SELECT risk_level, COUNT(DISTINCT id) AS cnt FROM dim_customer GROUP BY risk_level ORDER BY risk_level")
risk_rows = cur.fetchall()
risk_pass = set(r[0] for r in risk_rows) >= {"CRITICAL","HIGH","LOW","MEDIUM"}
print(f"[3] Customer Risk            risk_level groups   = {[r[0] for r in risk_rows]}  -> {'PASS' if risk_pass else 'FAIL'}")

cur.execute("SELECT COUNT(*) FROM dim_customer WHERE contract_value IS NOT NULL AND health_score IS NOT NULL AND churn_risk_score IS NOT NULL AND risk_level IS NOT NULL")
cr = cur.fetchone()[0]
print(f"[4] Churn Risk Matrix        complete rows       = {cr}  -> {'PASS' if cr>0 else 'FAIL'}")

cur.execute("SELECT severity, sla_breached, COUNT(DISTINCT id) FROM fact_incident GROUP BY severity, sla_breached ORDER BY severity, sla_breached")
sla_rows = cur.fetchall()
sla_sevs = set(r[0] for r in sla_rows)
sla_pass = sla_sevs >= {"P1","P2","P3"}
print(f"[5] SLA Breach Analysis      severities          = {sorted(sla_sevs)}  -> {'PASS' if sla_pass else 'FAIL'}")

cur.execute("SELECT COUNT(*) FROM analytics_sentiment WHERE positive_pct IS NOT NULL AND negative_pct IS NOT NULL AND period_start IS NOT NULL")
sent = cur.fetchone()[0]
print(f"[6] Sentiment Trend          monthly rows        = {sent}  -> {'PASS' if sent>0 else 'FAIL'}")

print(f"\nAll CSV files saved to:\n  {os.path.abspath(OUT_DIR)}\n")
cur.close()
conn.close()
