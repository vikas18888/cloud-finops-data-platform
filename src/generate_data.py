"""Generate synthetic AWS CUR-style billing data (deliberately messy) for the FinOps platform."""
import json, random
from datetime import date, timedelta
import numpy as np
import pandas as pd

random.seed(42); np.random.seed(42)
START, DAYS = date(2026, 8, 1), 90
ACCOUNTS = {"111111111111": 1.5, "222222222222": 0.4, "333333333333": 1.0}  # account -> cost scale
REGIONS = {"ap-south-1": 1.0, "us-east-1": 1.2, "eu-west-1": 0.6}
SERVICES = {  # service: (usage_type, base daily cost, unit)
    "AmazonEC2": ("BoxUsage:m5.large", 120, "Hrs"),
    "AWSLambda": ("Lambda-GB-Second", 15, "GB-Seconds"),
    "AmazonS3": ("TimedStorage-ByteHrs", 40, "GB-Mo"),
    "AmazonEBS": ("EBS:VolumeUsage.gp3", 25, "GB-Mo"),
    "AWSDataTransfer": ("DataTransfer-Out-Bytes", 30, "GB"),
    "AmazonRDS": ("InstanceUsage:db.r5.large", 90, "Hrs"),
    "AmazonDynamoDB": ("ReadCapacityUnit-Hrs", 20, "RCU-Hrs"),
}
PREFIX = {"AmazonEC2": "ec2", "AWSLambda": "lam", "AmazonS3": "s3", "AmazonEBS": "ebs", "AWSDataTransfer": "dt", "AmazonRDS": "rds", "AmazonDynamoDB": "ddb"}
TEAMS = ["checkout", "search", "ml", "platform", None]
ENVS = ["prod", "staging", "dev", None]
SPIKES = {20: ("AmazonEC2", 4.0), 47: ("AmazonS3", 3.5), 71: ("AWSDataTransfer", 5.0)}

rows, rid = [], 0
for d in range(DAYS):
    day = START + timedelta(days=d)
    weekend = day.weekday() >= 5
    for acct, a_scale in ACCOUNTS.items():
        for region, r_scale in REGIONS.items():
            for svc, (utype, base, unit) in SERVICES.items():
                for _ in range(random.randint(1, 3)):
                    rid += 1
                    f = (0.7 if weekend else 1.0) * (1 + d * 0.004) * random.uniform(0.8, 1.2)
                    f *= a_scale * r_scale / 3
                    if d in SPIKES and SPIKES[d][0] == svc and acct == "111111111111":
                        f *= SPIKES[d][1]
                    cost = round(base * f, 4)
                    tags = {"team": random.choice(TEAMS), "env": random.choice(ENVS)}
                    tags = {k: v for k, v in tags.items() if v}
                    rows.append({
                        "line_item_id": f"li-{rid:07d}",
                        "usage_date": day.isoformat(),
                        "account_id": acct, "region": region, "service": svc,
                        "usage_type": utype, "unit": unit,
                        "resource_id": f"{PREFIX[svc]}-{random.randint(1, 40):04d}",
                        "usage_quantity": round(cost / random.uniform(0.02, 0.2), 3),
                        "unblended_cost": cost,
                        "tags": json.dumps(tags) if tags else "",
                    })
df = pd.DataFrame(rows)

# --- inject real-world mess ---
def fmt(s, i):
    d = date.fromisoformat(s)
    return [d.isoformat(), d.strftime("%d/%m/%Y"), d.strftime("%Y/%m/%d")][i % 3]

idx = df.sample(frac=0.15, random_state=1).index
df.loc[idx, "usage_date"] = [fmt(s, i) for i, s in enumerate(df.loc[idx, "usage_date"])]
df.loc[df.sample(frac=0.01, random_state=2).index, "unblended_cost"] = np.nan
df.loc[df.sample(frac=0.005, random_state=3).index, "unblended_cost"] = -999.0  # invalid
df.loc[df.sample(frac=0.01, random_state=4).index, "region"] = np.nan
df.loc[df.sample(frac=0.01, random_state=5).index, "resource_id"] = np.nan
dups = df.sample(frac=0.01, random_state=6)
df = pd.concat([df, dups], ignore_index=True).sample(frac=1, random_state=7).reset_index(drop=True)

# split: 80% CSV, 20% JSON lines (unstructured source)
cut = int(len(df) * 0.8)
df.iloc[:cut].to_csv("data/raw/billing_raw.csv", index=False)
df.iloc[cut:].to_json("data/raw/billing_raw.jsonl", orient="records", lines=True)

# --- extra inputs used by later days ---
inv = pd.DataFrame({"resource_id": df["resource_id"].dropna().unique()})
n = len(inv)
inv["owner_team"] = np.random.choice(TEAMS, n)
inv["env"] = np.random.choice(ENVS, n)
inv["cost_center"] = np.random.choice(["CC-101", "CC-202", None], n)
inv["last_active_days_ago"] = np.random.choice([0, 1, 3, 10, 45, 90, 120], n, p=[.4, .2, .1, .1, .1, .05, .05])
inv.to_csv("data/raw/asset_inventory.csv", index=False)

k8s = pd.DataFrame({
    "namespace": np.random.choice(["checkout", "search", "ml", "platform"], 60),
    "pod": [f"pod-{i:03d}" for i in range(60)],
    "node": np.random.choice([f"node-{i}" for i in range(6)], 60),
    "cpu_request_m": np.random.choice([250, 500, 1000, 2000, 4000], 60),
    "mem_request_mb": np.random.choice([512, 1024, 2048, 4096, 8192], 60),
})
k8s["cpu_used_m"] = (k8s["cpu_request_m"] * np.random.uniform(0.08, 0.9, 60)).round()
k8s["mem_used_mb"] = (k8s["mem_request_mb"] * np.random.uniform(0.15, 0.95, 60)).round()
k8s.to_csv("data/raw/k8s_usage.csv", index=False)

pd.DataFrame({
    "object_prefix": [f"logs/{i}" for i in range(200)],
    "size_gb": np.random.uniform(1, 500, 200).round(1),
    "age_days": np.random.choice([5, 20, 45, 100, 200, 400], 200),
    "accesses_last_30d": np.random.choice([0, 0, 1, 5, 50, 500], 200),
}).to_csv("data/raw/s3_objects.csv", index=False)

pd.DataFrame({
    "date": pd.date_range(START, periods=DAYS).date,
    "api_requests": (np.random.uniform(0.8, 1.2, DAYS) * 2_000_000).astype(int),
    "active_customers": (np.random.uniform(0.95, 1.05, DAYS) * 12000).astype(int),
    "processing_hours": (np.random.uniform(0.8, 1.2, DAYS) * 900).round(1),
}).to_csv("data/raw/business_metrics.csv", index=False)
print("rows:", len(df), "| csv:", cut, "| jsonl:", len(df) - cut)
