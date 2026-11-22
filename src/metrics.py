"""Shared KPI logic for the dashboard (dashboard/app.py) and the PDF export (src/export_dashboard_pdf.py)."""
import sqlite3
import numpy as np
import pandas as pd

DB = "db/finops.db"

def _q(sql, db=DB):
    con = sqlite3.connect(db)
    try: return pd.read_sql_query(sql, con)
    finally: con.close()

def daily_cost(db=DB):
    d = _q("SELECT d.full_date AS date, SUM(f.unblended_cost) AS cost FROM fact_cost f JOIN dim_date d USING(date_key) GROUP BY 1 ORDER BY 1", db)
    d["date"] = pd.to_datetime(d["date"]); return d

def by_category(db=DB):
    return _q("SELECT s.category, SUM(f.unblended_cost) AS cost FROM fact_cost f JOIN dim_service s USING(service_key) GROUP BY 1 ORDER BY 2 DESC", db)

def unit_cost_monthly(db=DB, biz="data/raw/business_metrics.csv"):
    c = _q("SELECT d.year_month AS month, SUM(f.unblended_cost) AS cost FROM fact_cost f JOIN dim_date d USING(date_key) GROUP BY 1", db)
    b = pd.read_csv(biz); b["month"] = pd.to_datetime(b["date"]).dt.strftime("%Y-%m")
    m = b.groupby("month").agg(api=("api_requests", "sum"), cust=("active_customers", "mean")).reset_index().merge(c, on="month")
    m["cost_per_1k_requests"] = m.cost / (m.api / 1000); m["cost_per_customer"] = m.cost / m.cust
    return m

def forecast_variance(daily, train_days=60):
    """Linear trend fitted on the first `train_days`, projected over the rest; variance = actual - forecast."""
    d = daily.copy(); x = np.arange(len(d))
    slope, icpt = np.polyfit(x[:train_days], d.cost.values[:train_days], 1)
    d["forecast"] = slope * x + icpt; d["is_test"] = x >= train_days
    t = d[d.is_test]
    return d, {"variance_usd": float((t.cost - t.forecast).sum()), "variance_pct": float((t.cost.sum() / t.forecast.sum() - 1)),
               "mape": float((abs(t.cost - t.forecast) / t.cost).mean())}

def commitment_coverage(db=DB, coverage_target=0.80):
    """MODELLED coverage (the data has no purchased RIs): committed baseline / EC2+RDS spend if the Day 11 recommendation is bought."""
    d = _q("SELECT s.service_name, d.full_date, SUM(f.unblended_cost) AS cost FROM fact_cost f JOIN dim_service s USING(service_key) JOIN dim_date d USING(date_key) WHERE s.service_name IN ('AmazonEC2','AmazonRDS') GROUP BY 1,2", db)
    base = d.groupby("service_name").cost.quantile(0.10).sum(); avg = d.groupby("service_name").cost.mean().sum()
    return {"current": 0.0, "modelled": float(base * coverage_target / avg)}

def kpis(db=DB):
    d = daily_cost(db); u = unit_cost_monthly(db); _, fv = forecast_variance(d); cov = commitment_coverage(db)
    return {"total_spend": float(d.cost.sum()), "last_30d": float(d.cost.tail(30).sum()), "prev_30d": float(d.cost.iloc[-60:-30].sum()),
            "cost_per_1k_first": float(u.cost_per_1k_requests.iloc[0]), "cost_per_1k_last": float(u.cost_per_1k_requests.iloc[-1]),
            "coverage_current": cov["current"], "coverage_modelled": cov["modelled"], **fv}

if __name__ == "__main__":
    for k, v in kpis().items(): print(f"{k}: {v:,.4f}")
