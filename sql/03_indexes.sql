-- Day 5: indexing strategy for large billing facts (portable CREATE INDEX; Postgres notes inline)
-- Single-column B-Tree indexes for common filters
CREATE INDEX IF NOT EXISTS idx_bench_date     ON fact_cost_big (date_key);
CREATE INDEX IF NOT EXISTS idx_bench_service  ON fact_cost_big (service_key);
-- Composite index: matches the dashboard query pattern (filter by account + date range, group by service)
CREATE INDEX IF NOT EXISTS idx_bench_acct_date_svc ON fact_cost_big (account_key, date_key, service_key);
-- Covering index (includes cost so the query never touches the table)
CREATE INDEX IF NOT EXISTS idx_bench_cover ON fact_cost_big (account_key, date_key, service_key, unblended_cost);
-- PostgreSQL partitioning strategy (analysis only, not executable in SQLite):
--   CREATE TABLE fact_cost (...) PARTITION BY RANGE (date_key);
--   CREATE TABLE fact_cost_2026_08 PARTITION OF fact_cost FOR VALUES FROM (20260801) TO (20260901);
--   Monthly partitions enable partition pruning for date-range queries and cheap retention (DROP PARTITION).
