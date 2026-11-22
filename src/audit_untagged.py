"""Day 9: Scan the asset inventory for untagged / orphaned / idle resources and quantify their cost."""
import sqlite3
from pathlib import Path
import pandas as pd

REQUIRED_TAGS = ["owner_team", "env", "cost_center"]
ORPHAN_DAYS = 90

def audit(inv: pd.DataFrame) -> pd.DataFrame:
    inv = inv.copy()
    inv["missing_tags"] = inv[REQUIRED_TAGS].isna().apply(lambda r: ",".join(c for c in REQUIRED_TAGS if r[c]) , axis=1)
    inv["is_untagged"] = inv["missing_tags"] != ""
    inactive = inv["last_active_days_ago"] >= ORPHAN_DAYS
    inv["status"] = "ok"
    inv.loc[inv.is_untagged, "status"] = "untagged"
    inv.loc[inactive & inv.owner_team.notna(), "status"] = "idle"
    inv.loc[inactive & inv.owner_team.isna(), "status"] = "orphaned"
    return inv

def main(db="db/finops.db", out="reports"):
    inv = audit(pd.read_csv("data/raw/asset_inventory.csv"))
    con = sqlite3.connect(db)
    cost = pd.read_sql_query("""SELECT r.resource_id, SUM(f.unblended_cost) AS cost_90d FROM fact_cost f
                                JOIN dim_resource r USING(resource_key) GROUP BY r.resource_id""", con)
    inv = inv.merge(cost, on="resource_id", how="left").fillna({"cost_90d": 0})
    total = cost.cost_90d.sum()
    Path(out).mkdir(exist_ok=True)
    inv.sort_values("cost_90d", ascending=False).to_csv(f"{out}/day09_audit_findings.csv", index=False)
    s = inv.groupby("status").agg(resources=("resource_id", "count"), cost_90d=("cost_90d", "sum")).reset_index()
    s["pct_of_spend"] = 100 * s.cost_90d / total
    cov = 100 * (1 - inv.loc[inv.is_untagged, "cost_90d"].sum() / inv.cost_90d.sum())
    lines = ["# Day 9 - Tagging Audit Report\n", f"Resources scanned: {len(inv)} | Cost-weighted tag coverage: **{cov:.1f}%** (policy target: 95%)\n",
             s.round(2).to_markdown(index=False),
             "\n\n## Top 5 costliest non-compliant resources\n",
             inv[inv.status != "ok"].nlargest(5, "cost_90d")[["resource_id", "status", "missing_tags", "cost_90d"]].round(2).to_markdown(index=False),
             "\n\nNote: this audit uses the asset *inventory* tags; Q8 in Day 2 uses *billing* cost-allocation tags. They are separate sources and can disagree, which is itself a governance finding.\n\nNote: orphaned/idle cost is the 90-day spend of those resources and is an upper bound on savings (some may be needed)."]
    Path(f"{out}/day09_tagging_audit.md").write_text("\n".join(lines)); print("\n".join(lines[:5]))

if __name__ == "__main__":
    main()
