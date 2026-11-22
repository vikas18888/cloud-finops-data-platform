"""Load cleaned billing data into the star schema (SQLite file db/finops.db; same SQL works on Postgres)."""
import sqlite3, sys
from pathlib import Path
import pandas as pd

DB = Path("db/finops.db")

def load(db_path=DB, csv="data/processed/billing_clean.csv"):
    Path(db_path).parent.mkdir(exist_ok=True)
    df = pd.read_csv(csv, dtype={"account_id": str}).fillna({"tag_team": "untagged", "tag_env": "untagged"})
    con = sqlite3.connect(db_path); con.execute("PRAGMA foreign_keys = ON")
    con.executescript(Path("sql/01_schema.sql").read_text())

    d = pd.to_datetime(df["usage_date"]).drop_duplicates().sort_values()
    con.executemany("INSERT INTO dim_date VALUES (?,?,?,?,?,?,?,?)", [
        (int(x.strftime("%Y%m%d")), x.strftime("%Y-%m-%d"), x.year, x.month, x.day, x.weekday(),
         int(x.weekday() >= 5), x.strftime("%Y-%m")) for x in d])
    def dim(table, cols, frame):
        u = frame[cols].drop_duplicates().reset_index(drop=True); u.insert(0, "key", range(1, len(u) + 1))
        con.executemany(f"INSERT INTO {table} VALUES ({','.join('?' * (len(cols) + 1))})", u.itertuples(index=False, name=None))
        return u.rename(columns={"key": table.replace("dim_", "") + "_key"})
    acc = dim("dim_account", ["account_id"], df); reg = dim("dim_region", ["region"], df)
    svc = dim("dim_service", ["service", "category"], df)
    tag = dim("dim_tag", ["tag_team", "tag_env"], df)
    df = df.merge(acc, on="account_id").merge(reg, on="region").merge(svc, on=["service", "category"]).merge(tag, on=["tag_team", "tag_env"])
    res = dim("dim_resource", ["resource_id", "service_key", "usage_type"], df.drop_duplicates(["resource_id", "service_key"]))
    df = df.merge(res[["resource_id", "service_key", "resource_key"]], on=["resource_id", "service_key"])
    df["date_key"] = pd.to_datetime(df["usage_date"]).dt.strftime("%Y%m%d").astype(int)
    cols = ["line_item_id", "date_key", "account_key", "region_key", "service_key", "resource_key", "tag_key", "usage_quantity", "unblended_cost"]
    con.executemany("INSERT INTO fact_cost VALUES (?,?,?,?,?,?,?,?,?)", df[cols].itertuples(index=False, name=None))
    con.commit()
    n = con.execute("SELECT COUNT(*), ROUND(SUM(unblended_cost),2) FROM fact_cost").fetchone()
    print(f"fact_cost rows={n[0]} total_cost={n[1]}"); con.close()

if __name__ == "__main__":
    load()
