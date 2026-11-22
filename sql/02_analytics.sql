-- Day 2: 8 analytical queries (window functions, CTEs, aggregation). Each block starts with "-- Q<n>:".

-- Q1: Daily total cost with 7-day moving average and day-over-day change (SUM/AVG OVER, LAG)
WITH daily AS (
  SELECT d.full_date, SUM(f.unblended_cost) AS cost
  FROM fact_cost f JOIN dim_date d ON d.date_key = f.date_key GROUP BY d.full_date)
SELECT full_date, ROUND(cost,2) AS cost,
       ROUND(AVG(cost) OVER (ORDER BY full_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW),2) AS ma7,
       ROUND(cost - LAG(cost) OVER (ORDER BY full_date),2) AS dod_change,
       ROUND(100.0*(cost - LAG(cost) OVER (ORDER BY full_date)) / LAG(cost) OVER (ORDER BY full_date),1) AS dod_pct
FROM daily ORDER BY full_date;

-- Q2: Top 3 services per account by total cost (RANK partitioned)
WITH t AS (
  SELECT a.account_id, s.service_name, SUM(f.unblended_cost) AS cost
  FROM fact_cost f JOIN dim_account a USING(account_key) JOIN dim_service s USING(service_key)
  GROUP BY a.account_id, s.service_name),
r AS (SELECT *, RANK() OVER (PARTITION BY account_id ORDER BY cost DESC) AS rnk FROM t)
SELECT account_id, service_name, ROUND(cost,2) AS cost, rnk FROM r WHERE rnk <= 3 ORDER BY account_id, rnk;

-- Q3: Month-over-month cost by category with % growth (LAG over partition)
WITH m AS (
  SELECT d.year_month, s.category, SUM(f.unblended_cost) AS cost
  FROM fact_cost f JOIN dim_date d USING(date_key) JOIN dim_service s USING(service_key)
  GROUP BY d.year_month, s.category)
SELECT year_month, category, ROUND(cost,2) AS cost,
       ROUND(100.0*(cost - LAG(cost) OVER (PARTITION BY category ORDER BY year_month))
             / LAG(cost) OVER (PARTITION BY category ORDER BY year_month),1) AS mom_pct
FROM m ORDER BY category, year_month;

-- Q4: Running (cumulative) spend per account and share of grand total (SUM OVER)
WITH d AS (
  SELECT a.account_id, dt.full_date, SUM(f.unblended_cost) AS cost
  FROM fact_cost f JOIN dim_account a USING(account_key) JOIN dim_date dt USING(date_key)
  GROUP BY a.account_id, dt.full_date)
SELECT account_id, full_date, ROUND(cost,2) AS daily_cost,
       ROUND(SUM(cost) OVER (PARTITION BY account_id ORDER BY full_date),2) AS cumulative_cost,
       ROUND(100.0*SUM(cost) OVER (PARTITION BY account_id ORDER BY full_date) / SUM(cost) OVER (),2) AS pct_of_grand_total
FROM d WHERE full_date IN ('2026-08-31','2026-09-30','2026-10-29') ORDER BY account_id, full_date;

-- Q5: Weekend vs weekday average daily cost per service (conditional aggregation in CTE)
WITH d AS (
  SELECT s.service_name, dt.full_date, dt.is_weekend, SUM(f.unblended_cost) AS cost
  FROM fact_cost f JOIN dim_service s USING(service_key) JOIN dim_date dt USING(date_key)
  GROUP BY s.service_name, dt.full_date, dt.is_weekend)
SELECT service_name,
       ROUND(AVG(CASE WHEN is_weekend=0 THEN cost END),2) AS weekday_avg,
       ROUND(AVG(CASE WHEN is_weekend=1 THEN cost END),2) AS weekend_avg,
       ROUND(100.0*(AVG(CASE WHEN is_weekend=1 THEN cost END)/AVG(CASE WHEN is_weekend=0 THEN cost END)-1),1) AS weekend_delta_pct
FROM d GROUP BY service_name ORDER BY weekday_avg DESC;

-- Q6: Top 10 most expensive resources with rank, cost share and cumulative share (Pareto)
WITH r AS (
  SELECT sv.service_name, rs.resource_id, SUM(f.unblended_cost) AS cost
  FROM fact_cost f JOIN dim_resource rs USING(resource_key) JOIN dim_service sv ON sv.service_key = rs.service_key
  GROUP BY sv.service_name, rs.resource_id),
x AS (SELECT *, RANK() OVER (ORDER BY cost DESC) AS rnk,
             SUM(cost) OVER (ORDER BY cost DESC) / SUM(cost) OVER () AS cum_share FROM r)
SELECT rnk, service_name, resource_id, ROUND(cost,2) AS cost, ROUND(100*cum_share,1) AS cumulative_pct
FROM x WHERE rnk <= 10 ORDER BY rnk;

-- Q7: Days where a service cost exceeds 2x its trailing 14-day average (spike detection with window frame)
WITH d AS (
  SELECT s.service_name, dt.full_date, SUM(f.unblended_cost) AS cost
  FROM fact_cost f JOIN dim_service s USING(service_key) JOIN dim_date dt USING(date_key)
  GROUP BY s.service_name, dt.full_date),
w AS (SELECT *, AVG(cost) OVER (PARTITION BY service_name ORDER BY full_date ROWS BETWEEN 14 PRECEDING AND 1 PRECEDING) AS trailing_avg FROM d)
SELECT service_name, full_date, ROUND(cost,2) AS cost, ROUND(trailing_avg,2) AS trailing_avg, ROUND(cost/trailing_avg,2) AS ratio
FROM w WHERE trailing_avg IS NOT NULL AND cost > 2*trailing_avg ORDER BY ratio DESC;

-- Q8: Tagging coverage - cost and % of spend that is untagged, by team tag (CTE + window total)
WITH t AS (
  SELECT tg.team, SUM(f.unblended_cost) AS cost, COUNT(*) AS line_items
  FROM fact_cost f JOIN dim_tag tg USING(tag_key) GROUP BY tg.team)
SELECT team, ROUND(cost,2) AS cost, line_items, ROUND(100.0*cost/SUM(cost) OVER (),1) AS pct_of_spend
FROM t ORDER BY cost DESC;
