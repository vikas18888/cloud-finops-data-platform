"""Day 8: Cloud unit economics = cloud cost / business driver. Reads warehouse + data/raw/business_metrics.csv."""
import sqlite3
from pathlib import Path
import pandas as pd

def main(db="db/finops.db", out="reports"):
    con = sqlite3.connect(db)
    cost = pd.read_sql_query("""SELECT d.full_date AS date, d.year_month AS month, s.category, tg.team, SUM(f.unblended_cost) AS cost
        FROM fact_cost f JOIN dim_date d USING(date_key) JOIN dim_service s USING(service_key) JOIN dim_tag tg USING(tag_key)
        GROUP BY d.full_date, d.year_month, s.category, tg.team""", con)
    biz = pd.read_csv("data/raw/business_metrics.csv").rename(columns={"date": "date"})
    biz["date"] = biz["date"].astype(str)
    daily = cost.groupby(["date", "month"], as_index=False)["cost"].sum().merge(biz, on="date")
    compute = cost[cost.category == "Compute"].groupby("date", as_index=False)["cost"].sum().rename(columns={"cost": "compute_cost"})
    daily = daily.merge(compute, on="date")
    m = daily.groupby("month").agg(total_cost=("cost", "sum"), compute_cost=("compute_cost", "sum"), api_requests=("api_requests", "sum"),
                                   avg_customers=("active_customers", "mean"), processing_hours=("processing_hours", "sum")).reset_index()
    m["cost_per_1k_api_requests"] = m.total_cost / (m.api_requests / 1000)
    m["cost_per_active_customer"] = m.total_cost / m.avg_customers
    m["compute_cost_per_processing_hour"] = m.compute_cost / m.processing_hours
    # Multi-tenant view: tenant = team tag; untagged cost kept visible instead of hidden
    t = cost.groupby("team", as_index=False)["cost"].sum()
    t["pct_of_total"] = 100 * t.cost / t.cost.sum()
    t["cost_per_active_customer_(90d)"] = t.cost / biz.active_customers.mean()
    Path(out).mkdir(exist_ok=True)
    m.round(4).to_csv(f"{out}/day08_unit_economics_monthly.csv", index=False)
    t.round(2).to_csv(f"{out}/day08_unit_economics_by_team.csv", index=False)
    first, last = m.iloc[0], m.iloc[-1]
    chg = lambda c: 100 * (last[c] / first[c] - 1)
    memo = f"""# Day 8 - Executive Memo: Cloud Unit Cost Efficiency
**To:** Engineering & Finance leadership | **Data:** 90 days of billing (synthetic) + business metrics

## Headline metrics (latest month: {last.month} vs first month: {first.month})
| Metric | {first.month} | {last.month} | Change |
|---|---|---|---|
| Cost per 1,000 API requests | ${first.cost_per_1k_api_requests:.2f} | ${last.cost_per_1k_api_requests:.2f} | {chg('cost_per_1k_api_requests'):+.1f}% |
| Cost per active customer | ${first.cost_per_active_customer:.2f} | ${last.cost_per_active_customer:.2f} | {chg('cost_per_active_customer'):+.1f}% |
| Compute cost per processing hour | ${first.compute_cost_per_processing_hour:.2f} | ${last.compute_cost_per_processing_hour:.2f} | {chg('compute_cost_per_processing_hour'):+.1f}% |

## Interpretation
- Business volume (requests, customers) is roughly flat over the period, while cloud cost grows (~0.4%/day in the data). Unit costs therefore **rise**, which means efficiency is getting worse, not better.
- Note: the data covers Aug 1 - Oct 29, so October has 29 days vs 31 in August. Per-request and per-hour metrics are unaffected; cost per customer (monthly cost / avg customers) is slightly understated for October, so the true increase is a bit higher.
- {t.loc[t.team=='untagged','pct_of_total'].sum():.1f}% of spend has no team tag, so it cannot be charged back to a tenant until tagging improves (see Day 9).

## Recommendations
1. Track cost per 1k requests as the primary efficiency KPI on the dashboard (Day 18).
2. Investigate compute growth against flat workload: candidates are over-provisioned instances and missing commitments (Days 11 and 13).
3. Fix tagging gaps so per-tenant unit cost is reliable.

*Caveat: figures come from synthetic data; the method, not the numbers, is the deliverable.*
"""
    Path(f"{out}/day08_executive_memo.md").write_text(memo)
    print(m.round(3).to_string(index=False)); print(t.round(2).to_string(index=False))

if __name__ == "__main__":
    main()
