-- Day 10 (BigQuery): partitioned + clustered analytical table.
-- 1) Create dataset, then load outputs/fact_cost_flat.csv into the staging table via the console (Create table > Upload, autodetect schema, name: finops.stg_fact_cost).
CREATE SCHEMA IF NOT EXISTS finops;

-- 2) Baseline (unpartitioned) copy for comparison
CREATE OR REPLACE TABLE finops.fact_cost_baseline AS SELECT * FROM finops.stg_fact_cost;

-- 3) Optimised table: partition by usage date (monthly), cluster by the most common filter/group columns
CREATE OR REPLACE TABLE finops.fact_cost_optimized
PARTITION BY DATE_TRUNC(usage_date, MONTH)
CLUSTER BY account_id, service_name, region
OPTIONS (partition_expiration_days = NULL, description = 'Cloud billing facts, partitioned by month, clustered for cost queries')
AS SELECT * FROM finops.stg_fact_cost;

-- 4) Benchmark queries: run each on BOTH tables, note "Bytes processed" and "Elapsed time" in the job details (see docs/day10_benchmark_log.md)
-- Q-A: single-account, one-month, per-service spend
SELECT service_name, ROUND(SUM(unblended_cost), 2) AS cost
FROM finops.fact_cost_optimized   -- repeat with fact_cost_baseline
WHERE usage_date BETWEEN '2026-09-01' AND '2026-09-30' AND account_id = '111111111111'
GROUP BY service_name ORDER BY cost DESC;
-- Q-B: daily trend for one service
SELECT usage_date, SUM(unblended_cost) AS cost
FROM finops.fact_cost_optimized   -- repeat with fact_cost_baseline
WHERE service_name = 'AmazonEC2' AND usage_date >= '2026-10-01'
GROUP BY usage_date ORDER BY usage_date;
