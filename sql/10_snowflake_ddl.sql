-- Day 10 (Snowflake): clustered analytical table. Snowflake has micro-partitions automatically; CLUSTER BY controls pruning.
CREATE DATABASE IF NOT EXISTS finops; USE DATABASE finops; CREATE SCHEMA IF NOT EXISTS billing; USE SCHEMA billing;

CREATE OR REPLACE FILE FORMAT csv_fmt TYPE = CSV SKIP_HEADER = 1 FIELD_OPTIONALLY_ENCLOSED_BY = '"' NULL_IF = ('');
CREATE OR REPLACE STAGE finops_stage FILE_FORMAT = csv_fmt;
-- Upload outputs/fact_cost_flat.csv to the stage (Snowsight: Data > Add Data > Load files, or: PUT file://.../fact_cost_flat.csv @finops_stage;)

CREATE OR REPLACE TABLE fact_cost_baseline (
  line_item_id STRING, usage_date DATE, account_id STRING, region STRING, service_name STRING, category STRING,
  resource_id STRING, usage_type STRING, tag_team STRING, tag_env STRING, usage_quantity NUMBER(18,4), unblended_cost NUMBER(18,4));
COPY INTO fact_cost_baseline FROM @finops_stage;

CREATE OR REPLACE TABLE fact_cost_clustered CLUSTER BY (usage_date, account_id, service_name) AS SELECT * FROM fact_cost_baseline;

-- Check clustering quality, then benchmark (turn off result cache so timings are honest)
SELECT SYSTEM$CLUSTERING_INFORMATION('fact_cost_clustered', '(usage_date, account_id, service_name)');
ALTER SESSION SET USE_CACHED_RESULT = FALSE;
SELECT service_name, ROUND(SUM(unblended_cost), 2) FROM fact_cost_clustered   -- repeat with fact_cost_baseline
WHERE usage_date BETWEEN '2026-09-01' AND '2026-09-30' AND account_id = '111111111111' GROUP BY service_name;
-- Read elapsed time and "partitions scanned / total" from Query Profile for each run.
