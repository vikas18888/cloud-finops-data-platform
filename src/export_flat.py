"""Day 10 helper: export a denormalised fact table (one wide CSV) for loading into BigQuery / Snowflake."""
import sqlite3
import pandas as pd
con = sqlite3.connect("db/finops.db")
df = pd.read_sql_query("""SELECT f.line_item_id, d.full_date AS usage_date, a.account_id, rg.region_code AS region,
    s.service_name, s.category, r.resource_id, r.usage_type, tg.team AS tag_team, tg.env AS tag_env,
    f.usage_quantity, f.unblended_cost
  FROM fact_cost f JOIN dim_date d USING(date_key) JOIN dim_account a USING(account_key) JOIN dim_region rg USING(region_key)
  JOIN dim_service s USING(service_key) JOIN dim_resource r USING(resource_key) JOIN dim_tag tg USING(tag_key)""", con)
df.to_csv("outputs/fact_cost_flat.csv", index=False); print(len(df), "rows -> outputs/fact_cost_flat.csv")
