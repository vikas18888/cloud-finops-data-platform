"""Day 13: Compare Kubernetes CPU/memory requests vs actual usage; estimate right-sizing savings.
Prices are ASSUMPTIONS (edit below): roughly on-demand general-purpose node pricing split between CPU and memory."""
from pathlib import Path
import numpy as np
import pandas as pd

CPU_PRICE_PER_CORE_HR = 0.0316   # USD per vCPU-hour (assumption)
MEM_PRICE_PER_GB_HR = 0.0042     # USD per GB-hour (assumption)
HEADROOM = 1.30                  # recommended request = observed usage x 1.30
HOURS_PER_MONTH = 730
THRESHOLD = 0.50                 # flag pods using < 50% of requested resources

def analyse(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["cpu_util"] = df.cpu_used_m / df.cpu_request_m
    df["mem_util"] = df.mem_used_mb / df.mem_request_mb
    df["rec_cpu_m"] = np.minimum(df.cpu_request_m, np.ceil(df.cpu_used_m * HEADROOM / 50) * 50)
    df["rec_mem_mb"] = np.minimum(df.mem_request_mb, np.ceil(df.mem_used_mb * HEADROOM / 64) * 64)
    cpu_save = (df.cpu_request_m - df.rec_cpu_m) / 1000 * CPU_PRICE_PER_CORE_HR * HOURS_PER_MONTH
    mem_save = (df.mem_request_mb - df.rec_mem_mb) / 1024 * MEM_PRICE_PER_GB_HR * HOURS_PER_MONTH
    df["monthly_cost"] = (df.cpu_request_m / 1000 * CPU_PRICE_PER_CORE_HR + df.mem_request_mb / 1024 * MEM_PRICE_PER_GB_HR) * HOURS_PER_MONTH
    df["monthly_saving"] = cpu_save + mem_save
    df["overprovisioned"] = (df.cpu_util < THRESHOLD) | (df.mem_util < THRESHOLD)
    return df

def main(out="reports"):
    df = analyse(pd.read_csv("data/raw/k8s_usage.csv"))
    Path(out).mkdir(exist_ok=True); df.round(3).to_csv(f"{out}/day13_k8s_rightsizing.csv", index=False)
    tot, sav = df.monthly_cost.sum(), df.monthly_saving.sum()
    ns = df.groupby("namespace").agg(pods=("pod", "count"), cpu_util=("cpu_util", "mean"), mem_util=("mem_util", "mean"), monthly_cost=("monthly_cost", "sum"), saving=("monthly_saving", "sum")).round(2)
    node = df.groupby("node").agg(pods=("pod", "count"), cpu_req_cores=("cpu_request_m", lambda s: s.sum() / 1000), cpu_used_cores=("cpu_used_m", lambda s: s.sum() / 1000)).round(2)
    node["cpu_util_pct"] = (100 * node.cpu_used_cores / node.cpu_req_cores).round(1)
    md = [f"# Day 13 - Kubernetes Right-Sizing Report\n", f"Pods analysed: {len(df)} | Overprovisioned (<{int(THRESHOLD*100)}% CPU or memory use): **{int(df.overprovisioned.sum())}**\n",
          f"Requested-resource cost: ${tot:,.0f}/month | Potential saving: **${sav:,.0f}/month ({100*sav/tot:.1f}%)**\n",
          f"Assumptions: ${CPU_PRICE_PER_CORE_HR}/vCPU-hr, ${MEM_PRICE_PER_GB_HR}/GB-hr, {int((HEADROOM-1)*100)}% headroom over observed usage, {HOURS_PER_MONTH} hrs/month. Usage is a single snapshot; use p95 over 2-4 weeks before applying in production.\n",
          "## By namespace\n", ns.to_markdown(), "\n\n## By node (CPU requested vs used)\n", node.to_markdown(),
          "\n\n## Top 10 pods by saving\n", df.nlargest(10, "monthly_saving")[["namespace", "pod", "cpu_request_m", "cpu_used_m", "rec_cpu_m", "mem_request_mb", "mem_used_mb", "rec_mem_mb", "monthly_saving"]].round(2).to_markdown(index=False),
          "\n\n## Recommendations\n1. Lower requests to the recommended values for the top-saving pods first.\n2. After right-sizing, consolidate nodes with low CPU utilisation (cluster autoscaler / fewer nodes).\n3. Add VPA in recommendation mode to keep requests aligned."]
    Path(f"{out}/day13_k8s_report.md").write_text("\n".join(md)); print("\n".join(md[:4]))

if __name__ == "__main__":
    main()
