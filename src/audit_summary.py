"""Day 14: consolidate findings into one audit summary (JSON + markdown). Savings are netted to avoid double counting:
waste is removed first, then rate-optimisation savings are scaled to the remaining spend."""
import json, sqlite3
from pathlib import Path
import pandas as pd
from openpyxl import load_workbook

IDLE_REALISATION, ORPHAN_REALISATION = 0.50, 1.00   # assumptions: share of idle/orphaned cost actually removable
con = sqlite3.connect("db/finops.db")
total_90 = con.execute("SELECT SUM(unblended_cost) FROM fact_cost").fetchone()[0]
annual = total_90 / 90 * 365
by_cat = dict(con.execute("SELECT s.category, SUM(f.unblended_cost) FROM fact_cost f JOIN dim_service s USING(service_key) GROUP BY 1").fetchall())

aud = pd.read_csv("reports/day09_audit_findings.csv").groupby("status")["cost_90d"].sum()
waste_annual = (aud.get("orphaned", 0) * ORPHAN_REALISATION + aud.get("idle", 0) * IDLE_REALISATION) / 90 * 365

m = load_workbook("outputs/rate_optimization_model.xlsx", data_only=True)["Model"]
rate_gross = m["I8"].value                       # recommended blend annual saving
rate_net = rate_gross * (annual - waste_annual) / annual
k8s = pd.read_csv("reports/day13_k8s_rightsizing.csv").monthly_saving.sum() * 12

spikes = pd.read_csv("outputs/day02/Q7.csv"); spike_excess_90 = float((spikes.cost - spikes.trailing_avg).sum())
tagged_cov = None
res = {"annualised_spend": annual, "total_90d": total_90, "by_category_90d": by_cat,
       "waste_removal_annual": waste_annual, "rate_opt_gross_annual": rate_gross, "rate_opt_net_annual": rate_net,
       "headline_saving_annual": waste_annual + rate_net, "headline_saving_pct": (waste_annual + rate_net) / annual,
       "k8s_extra_annual": k8s, "spike_excess_90d": spike_excess_90,
       "orphaned_90d": float(aud.get("orphaned", 0)), "idle_90d": float(aud.get("idle", 0)),
       "rate_pct_by_strategy": {"RI 1-yr": m["E9"].value, "RI 3-yr": m["F9"].value, "Savings Plan 1-yr": m["G9"].value, "Spot": m["H9"].value, "Blend": m["I9"].value}}
Path("reports/day14_audit_summary.json").write_text(json.dumps(res, indent=2))
md = f"""# Day 14 - Cloud Optimisation Audit Summary

Annualised spend (from 90 days): **${annual:,.0f}**

| Finding | Annual saving | % of spend |
|---|---|---|
| Remove orphaned (100%) + idle (50%) resources | ${waste_annual:,.0f} | {100*waste_annual/annual:.1f}% |
| Rate optimisation (RI 1-yr on 80% of baseline + Spot), net of waste removal | ${rate_net:,.0f} | {100*rate_net/annual:.1f}% |
| **Total (headline)** | **${waste_annual+rate_net:,.0f}** | **{100*(waste_annual+rate_net)/annual:.1f}%** |
| Kubernetes right-sizing (separate cluster, NOT in headline) | ${k8s:,.0f} | n/a |
| Spike prevention via alerting (one-off, NOT in headline) | ${spike_excess_90:,.0f} per 90 days | n/a |

Method: waste is removed first, then rate-optimisation savings are scaled to the remaining spend to avoid double counting. Idle realisation 50% is an assumption. Discount rates are illustrative (see Excel model).
"""
Path("reports/day14_audit_summary.md").write_text(md); print(md)
