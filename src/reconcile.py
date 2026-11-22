"""Day 7: source -> target reconciliation (row counts + cost checksums). Exits non-zero on any mismatch."""
import json, sqlite3, sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, "src")
from ingest_billing import extract

def main(db="db/finops.db"):
    raw = extract()
    clean = pd.read_csv("data/processed/billing_clean.csv"); quar = pd.read_csv("data/processed/billing_quarantine.csv")
    con = sqlite3.connect(db)
    fact_n, fact_sum = con.execute("SELECT COUNT(*), SUM(unblended_cost) FROM fact_cost").fetchone()
    dupes = len(raw) - raw["line_item_id"].nunique()
    checks = [
        ("raw rows = clean + quarantined + duplicates", len(raw), len(clean) + len(quar) + dupes),
        ("clean csv rows = warehouse fact rows", len(clean), fact_n),
        ("clean cost checksum = warehouse cost checksum", round(clean["unblended_cost"].sum(), 2), round(fact_sum, 2)),
        ("distinct line_item_ids clean = warehouse", clean["line_item_id"].nunique(),
         con.execute("SELECT COUNT(DISTINCT line_item_id) FROM fact_cost").fetchone()[0]),
        ("orphan fact rows (no matching dim)", 0, con.execute("""SELECT COUNT(*) FROM fact_cost f LEFT JOIN dim_resource r USING(resource_key)
                                                                  LEFT JOIN dim_date d USING(date_key) WHERE r.resource_key IS NULL OR d.date_key IS NULL""").fetchone()[0]),
    ]
    lines = ["# Day 7 - Reconciliation Report\n", "| Check | Source | Target | Result |", "|---|---|---|---|"]
    ok = True
    for name, a, b in checks:
        passed = a == b; ok &= passed
        lines.append(f"| {name} | {a} | {b} | {'PASS' if passed else 'FAIL'} |")
    lines.append(f"\n**Overall: {'ZERO DATA LOSS - ALL CHECKS PASSED' if ok else 'MISMATCH DETECTED'}**")
    Path("reports/day07_reconciliation.md").write_text("\n".join(lines)); print("\n".join(lines)); sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
