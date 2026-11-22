"""Day 3: Extract raw CSV/JSONL billing logs, clean, standardise, split valid vs quarantined rows."""
import json
from pathlib import Path
import pandas as pd

RAW = Path("data/raw"); OUT = Path("data/processed")
CATEGORY = {"AmazonEC2": "Compute", "AWSLambda": "Compute", "AmazonS3": "Storage", "AmazonEBS": "Storage",
            "AWSDataTransfer": "Networking", "AmazonRDS": "Managed Services", "AmazonDynamoDB": "Managed Services"}
REQUIRED = ["line_item_id", "usage_date", "account_id", "region", "service", "resource_id", "unblended_cost"]

def extract() -> pd.DataFrame:
    csv = pd.read_csv(RAW / "billing_raw.csv", dtype={"account_id": str})
    js = pd.read_json(RAW / "billing_raw.jsonl", lines=True, dtype={"account_id": str})
    js["account_id"] = js["account_id"].astype(str).str.zfill(12)
    return pd.concat([csv, js], ignore_index=True)

def parse_dates(s: pd.Series) -> pd.Series:
    """Handle ISO, YYYY/MM/DD and DD/MM/YYYY explicitly (no ambiguous guessing)."""
    s = s.astype(str).str.strip()
    out = pd.to_datetime(s, format="%Y-%m-%d", errors="coerce")
    out = out.fillna(pd.to_datetime(s, format="%Y/%m/%d", errors="coerce"))
    out = out.fillna(pd.to_datetime(s, format="%d/%m/%Y", errors="coerce"))
    return out

def parse_tags(t) -> dict:
    try:
        return json.loads(t) if isinstance(t, str) and t.strip() else {}
    except json.JSONDecodeError:
        return {}

def transform(df: pd.DataFrame):
    stats = {"extracted_rows": len(df)}
    df = df.drop_duplicates(subset="line_item_id", keep="first").copy()
    stats["duplicates_removed"] = stats["extracted_rows"] - len(df)
    df["usage_date"] = parse_dates(df["usage_date"])
    df["unblended_cost"] = pd.to_numeric(df["unblended_cost"], errors="coerce")
    tags = df["tags"].map(parse_tags)
    df["tag_team"] = tags.map(lambda d: d.get("team")); df["tag_env"] = tags.map(lambda d: d.get("env"))
    df["category"] = df["service"].map(CATEGORY).fillna("Other")
    bad = df[REQUIRED].isna().any(axis=1) | (df["unblended_cost"] < 0)
    df["reject_reason"] = ""
    df.loc[df[REQUIRED].isna().any(axis=1), "reject_reason"] = "missing_required_field"
    df.loc[df["unblended_cost"] < 0, "reject_reason"] = "negative_cost"
    clean, quarantine = df[~bad].drop(columns=["reject_reason", "tags"]), df[bad]
    clean = clean.assign(usage_date=clean["usage_date"].dt.strftime("%Y-%m-%d"))
    quarantine = quarantine.assign(usage_date=quarantine["usage_date"].dt.strftime("%Y-%m-%d"))
    stats.update(clean_rows=len(clean), quarantined_rows=len(quarantine))
    return clean, quarantine, stats

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    clean, quarantine, stats = transform(extract())
    clean.to_csv(OUT / "billing_clean.csv", index=False)
    quarantine.to_csv(OUT / "billing_quarantine.csv", index=False)
    (OUT / "ingest_stats.json").write_text(json.dumps(stats, indent=2))
    print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    main()
