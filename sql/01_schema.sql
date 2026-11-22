-- Day 1: Star schema for cloud billing (portable: runs on PostgreSQL and SQLite)
-- Facts: fact_cost (grain = one billing line item). Dimensions: date, account, region, service, resource, tag.
DROP TABLE IF EXISTS fact_cost;
DROP TABLE IF EXISTS dim_resource; DROP TABLE IF EXISTS dim_tag; DROP TABLE IF EXISTS dim_service;
DROP TABLE IF EXISTS dim_region;   DROP TABLE IF EXISTS dim_account; DROP TABLE IF EXISTS dim_date;

CREATE TABLE dim_date (
    date_key      INTEGER PRIMARY KEY,          -- yyyymmdd
    full_date     DATE NOT NULL UNIQUE,
    year          INTEGER NOT NULL, month INTEGER NOT NULL, day INTEGER NOT NULL,
    day_of_week   INTEGER NOT NULL,             -- 0=Mon
    is_weekend    INTEGER NOT NULL,
    year_month    VARCHAR(7) NOT NULL
);
CREATE TABLE dim_account (
    account_key   INTEGER PRIMARY KEY,
    account_id    VARCHAR(12) NOT NULL UNIQUE
);
CREATE TABLE dim_region (
    region_key    INTEGER PRIMARY KEY,
    region_code   VARCHAR(30) NOT NULL UNIQUE
);
CREATE TABLE dim_service (
    service_key   INTEGER PRIMARY KEY,
    service_name  VARCHAR(60) NOT NULL UNIQUE,
    category      VARCHAR(30) NOT NULL          -- Compute / Storage / Networking / Managed Services
);
CREATE TABLE dim_resource (
    resource_key  INTEGER PRIMARY KEY,
    resource_id   VARCHAR(60) NOT NULL,
    service_key   INTEGER NOT NULL,
    usage_type    VARCHAR(80),
    UNIQUE (resource_id, service_key),
    FOREIGN KEY (service_key) REFERENCES dim_service(service_key)
);
CREATE TABLE dim_tag (
    tag_key       INTEGER PRIMARY KEY,
    team          VARCHAR(40), env VARCHAR(20),
    UNIQUE (team, env)
);
CREATE TABLE fact_cost (
    line_item_id    VARCHAR(20) PRIMARY KEY,
    date_key        INTEGER NOT NULL,
    account_key     INTEGER NOT NULL,
    region_key      INTEGER NOT NULL,
    service_key     INTEGER NOT NULL,
    resource_key    INTEGER NOT NULL,
    tag_key         INTEGER NOT NULL,
    usage_quantity  DECIMAL(18,4),
    unblended_cost  DECIMAL(18,4) NOT NULL CHECK (unblended_cost >= 0),
    FOREIGN KEY (date_key)     REFERENCES dim_date(date_key),
    FOREIGN KEY (account_key)  REFERENCES dim_account(account_key),
    FOREIGN KEY (region_key)   REFERENCES dim_region(region_key),
    FOREIGN KEY (service_key)  REFERENCES dim_service(service_key),
    FOREIGN KEY (resource_key) REFERENCES dim_resource(resource_key),
    FOREIGN KEY (tag_key)      REFERENCES dim_tag(tag_key)
);
