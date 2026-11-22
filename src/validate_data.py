"""Day 6: Data-quality suite (plain Python checks). Flags schema drift, duplicates, nulls, bad values.
Corrupted rows are written to a quarantine table in the warehouse and a report is produced."""
import json, sqlite3, sys
from pathlib import Path
import pandas as pd

EXPECTED_COLUMNS = ["line_item_id", "usage_date", "account_id", "region", "service", "usage_type", "unit",
                    "resource_id", "usage_quantity", "unblended_cost", "tags"]
NOT_NULL = ["line_item_id", "usage_date", "account_id", "region", "service", "resource_id", "unblended_cost"]

def check_schema(df):
    missing, extra = set(EXPECTED_COLUMNS) - set(df.columns), set(df.columns) - set(EXPECTED_COLUMNS)
    return {"check": "schema_drift", "passed": not missing and not extra, "detail": f"missing={sorted(missing)} extra={sorted(extra)}"}

def run(raw_df: pd.DataFrame, db="db/finops.db", out="reports"):
    results = [check_schema(raw_df)]
    dup_mask = raw_df.duplicated("line_item_id", keep="first")
    results.append({"check": "duplicate_line_item_id", "passed": not dup_mask.any(), "detail": f"{int(dup_mask.sum())} duplicate rows"})
    for c in NOT_NULL:
        n = int(raw_df[c].isna().sum())
        results.append({"check": f"not_null:{c}", "passed": n == 0, "detail": f"{n} nulls"})
    cost = pd.to_numeric(raw_df["unblended_cost"], errors="coerce")
    neg = cost < 0
    results.append({"check": "cost_non_negative", "passed": not neg.any(), "detail": f"{int(neg.sum())} negative"})
    dates = pd.concat([pd.to_datetime(raw_df["usage_date"], format=f, errors="coerce") for f in ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y")], axis=1).notna().any(axis=1)
    results.append({"check": "date_parseable", "passed": bool(dates.all()), "detail": f"{int((~dates).sum())} unparseable"})
    null_any = raw_df[NOT_NULL].isna().any(axis=1)
    bad = raw_df[dup_mask | null_any | neg].copy()
    bad["dq_reason"] = ["duplicate" if d else "null_required" if n else "negative_cost" for d, n in zip(dup_mask[bad.index], null_any[bad.index])]
    con = sqlite3.connect(db); bad.astype(str).to_sql("quarantine_billing", con, if_exists="replace", index=False); con.close()
    failed = [r for r in results if not r["passed"]]
    lines = ["# Day 6 - Data Quality Report\n", f"Rows checked: {len(raw_df):,} | Checks: {len(results)} | Failed: {len(failed)} | Quarantined rows: {len(bad):,}\n",
             "| Check | Status | Detail |", "|---|---|---|"] + [f"| {r['check']} | {'PASS' if r['passed'] else 'FAIL'} | {r['detail']} |" for r in results]
    lines += ["\n## Quarantine breakdown\n", bad["dq_reason"].value_counts().to_frame("rows").to_markdown()]
    Path(out).mkdir(exist_ok=True); Path(f"{out}/day06_data_quality_report.md").write_text("\n".join(lines))
    return results, bad

if __name__ == "__main__":
    sys.path.insert(0, "src"); from ingest_billing import extract
    res, bad = run(extract())
    print(f"failed checks: {sum(not r['passed'] for r in res)} | quarantined: {len(bad)}")
    # exit code lets an orchestrator (Airflow) fail the task when quality is bad
