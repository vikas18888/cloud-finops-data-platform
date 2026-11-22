# Day 5 - Indexing Performance Report

Benchmark table: `fact_cost_big` (662,040 rows, SQLite 3.45.1). Median of 5 runs.

| Query | Before (ms) | After (ms) | Speed-up | Plan before | Plan after |
|---|---|---|---|---|---|
| A_filter_by_date_range | 32.52 | 2.52 | 12.9x | SCAN fact_cost_big | SEARCH fact_cost_big USING COVERING INDEX idx_bench_cover (ANY(account_key) AND date_key>? AND date_key<?) |
| B_account_date_group_service | 50.69 | 13.91 | 3.6x | SCAN fact_cost_big; USE TEMP B-TREE FOR GROUP BY | SEARCH fact_cost_big USING COVERING INDEX idx_bench_cover (account_key=? AND date_key>? AND date_key<?); USE TEMP B-TREE FOR GROUP BY |
| C_single_service_total | 33.08 | 6.78 | 4.9x | SCAN fact_cost_big | SEARCH fact_cost_big USING COVERING INDEX idx_bench_cover (ANY(account_key) AND ANY(date_key) AND service_key=?) |

## Notes
- Equivalent on PostgreSQL: run `EXPLAIN (ANALYZE, BUFFERS) <query>` before/after `CREATE INDEX`; expect Seq Scan -> Index (Only) Scan.
- Composite index column order follows the query: equality column first (account_key), then range (date_key), then group column (service_key).
- Trade-off: each index slows inserts and uses disk; keep only indexes that serve real query patterns.
- Partitioning (monthly RANGE on date_key) is described in `sql/03_indexes.sql` and requires PostgreSQL.