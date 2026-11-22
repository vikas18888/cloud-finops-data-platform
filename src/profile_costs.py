"""Day 4: Profile cost distribution by category / service / usage type; save charts + markdown report."""
import sqlite3
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

def main(db="db/finops.db", out="reports"):
    Path(out).mkdir(exist_ok=True)
    con = sqlite3.connect(db)
    q = """SELECT s.category, s.service_name, r.usage_type, d.year_month, f.unblended_cost AS cost
           FROM fact_cost f JOIN dim_service s USING(service_key)
           JOIN dim_resource r USING(resource_key) JOIN dim_date d USING(date_key)"""
    df = pd.read_sql_query(q, con); total = df["cost"].sum()
    by_cat = df.groupby("category")["cost"].sum().sort_values(ascending=False)
    by_svc = df.groupby(["category", "service_name"])["cost"].sum().sort_values(ascending=False).reset_index()
    by_ut = df.groupby("usage_type")["cost"].agg(["sum", "count", "mean"]).sort_values("sum", ascending=False)
    by_ut["pct"] = 100 * by_ut["sum"] / total

    fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
    by_cat.plot.pie(ax=ax[0], autopct="%1.1f%%", ylabel="", title="Spend by category")
    by_svc.set_index("service_name")["cost"].sort_values().plot.barh(ax=ax[1], title="Spend by service (USD)")
    plt.tight_layout(); plt.savefig(f"{out}/day04_cost_distribution.png", dpi=130); plt.close()

    md = [f"# Day 4 - Cost Distribution Profile\n\nPeriod: 90 days | Total spend: **${total:,.2f}** | Line items: {len(df):,}\n",
          "## By category\n", by_cat.map(lambda v: f"${v:,.2f} ({100*v/total:.1f}%)").to_frame("spend").to_markdown(),
          "\n\n## By service\n", by_svc.assign(pct=(100 * by_svc.cost / total).round(1)).round(2).to_markdown(index=False),
          "\n\n## By usage type\n", by_ut.round(2).to_markdown(),
          f"\n\n## Observations\n- Top category: **{by_cat.index[0]}** ({100*by_cat.iloc[0]/total:.1f}% of spend).",
          f"\n- Top 2 services account for {100*by_svc.cost.head(2).sum()/total:.1f}% of spend, so optimisation should start there.",
          "\n- Compute + Managed Services (EC2/RDS) are the main candidates for Reserved Instance / Savings Plan commitments (Day 11).\n"]
    Path(f"{out}/day04_cost_profile.md").write_text("\n".join(md))
    print(by_cat.round(2).to_string())

if __name__ == "__main__":
    main()
