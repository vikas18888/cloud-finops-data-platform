-- Day 16: monthly straight-line depreciation / amortisation view.
-- Table asset_register is loaded from data/raw/asset_register.csv by src/depreciation.py.
-- Portable recursive CTE (SQLite shown; for PostgreSQL replace date(...) with (purchase_month || '-01')::date + make_interval(months => n)).
DROP VIEW IF EXISTS v_monthly_depreciation;
CREATE VIEW v_monthly_depreciation AS
WITH RECURSIVE sched(asset_id, asset_name, asset_type, month_no, total_months, monthly_dep, cost, salvage_value, purchase_month) AS (
  SELECT asset_id, asset_name, asset_type, 1, life_years * 12, (cost - salvage_value) / (life_years * 12.0), cost, salvage_value, purchase_month
  FROM asset_register WHERE method = 'straight_line'
  UNION ALL
  SELECT asset_id, asset_name, asset_type, month_no + 1, total_months, monthly_dep, cost, salvage_value, purchase_month
  FROM sched WHERE month_no < total_months)
SELECT asset_id, asset_name, asset_type,
       strftime('%Y-%m', date(purchase_month || '-01', '+' || month_no || ' months')) AS period,   -- depreciation starts the month after purchase
       month_no,
       ROUND(monthly_dep, 2) AS depreciation,
       ROUND(monthly_dep * month_no, 2) AS accumulated_depreciation,
       ROUND(cost - monthly_dep * month_no, 2) AS net_book_value
FROM sched;
