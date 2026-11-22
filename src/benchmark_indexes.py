"""Day 5: measure query time + plan before/after indexing on a ~660k-row replica of fact_cost."""
import sqlite3, time, statistics, json
from pathlib import Path

DB = "db/finops.db"
QUERIES = {
  "A_filter_by_date_range": "SELECT SUM(unblended_cost) FROM fact_cost_big WHERE date_key BETWEEN 20260901 AND 20260907",
  "B_account_date_group_service": """SELECT service_key, SUM(unblended_cost) FROM fact_cost_big
        WHERE account_key = 1 AND date_key BETWEEN 20260901 AND 20260930 GROUP BY service_key""",
  "C_single_service_total": "SELECT COUNT(*), SUM(unblended_cost) FROM fact_cost_big WHERE service_key = 3",
}

def timed(con, sql, n=5):
    t = []
    for _ in range(n):
        s = time.perf_counter(); con.execute(sql).fetchall(); t.append((time.perf_counter() - s) * 1000)
    return round(statistics.median(t), 2)

def plan(con, sql):
    return "; ".join(r[3] for r in con.execute("EXPLAIN QUERY PLAN " + sql))

def main():
    con = sqlite3.connect(DB)
    con.executescript("DROP TABLE IF EXISTS fact_cost_big;")
    con.execute("CREATE TABLE fact_cost_big AS SELECT * FROM fact_cost WHERE 0")
    for i in range(60):  # replicate with unique ids -> ~662k rows
        con.execute("INSERT INTO fact_cost_big SELECT line_item_id || '-' || ?, date_key, account_key, region_key, service_key, resource_key, tag_key, usage_quantity, unblended_cost FROM fact_cost", (str(i),))
    con.commit(); con.execute("ANALYZE")
    rows = con.execute("SELECT COUNT(*) FROM fact_cost_big").fetchone()[0]
    before = {k: {"ms": timed(con, q), "plan": plan(con, q)} for k, q in QUERIES.items()}
    con.executescript(Path("sql/03_indexes.sql").read_text()); con.execute("ANALYZE")
    after = {k: {"ms": timed(con, q), "plan": plan(con, q)} for k, q in QUERIES.items()}
    lines = [f"# Day 5 - Indexing Performance Report\n\nBenchmark table: `fact_cost_big` ({rows:,} rows, SQLite {sqlite3.sqlite_version}). Median of 5 runs.\n",
             "| Query | Before (ms) | After (ms) | Speed-up | Plan before | Plan after |", "|---|---|---|---|---|---|"]
    for k in QUERIES:
        b, a = before[k], after[k]
        lines.append(f"| {k} | {b['ms']} | {a['ms']} | {b['ms']/max(a['ms'],0.01):.1f}x | {b['plan']} | {a['plan']} |")
    lines += ["\n## Notes\n- Equivalent on PostgreSQL: run `EXPLAIN (ANALYZE, BUFFERS) <query>` before/after `CREATE INDEX`; expect Seq Scan -> Index (Only) Scan.",
              "- Composite index column order follows the query: equality column first (account_key), then range (date_key), then group column (service_key).",
              "- Trade-off: each index slows inserts and uses disk; keep only indexes that serve real query patterns.",
              "- Partitioning (monthly RANGE on date_key) is described in `sql/03_indexes.sql` and requires PostgreSQL."]
    Path("reports/day05_index_report.md").write_text("\n".join(lines)); print("\n".join(lines[:8]))
    con.execute("DROP TABLE fact_cost_big"); con.commit(); con.execute("VACUUM"); con.close()

if __name__ == "__main__":
    main()
