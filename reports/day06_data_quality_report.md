# Day 6 - Data Quality Report

Rows checked: 11,545 | Checks: 11 | Failed: 5 | Quarantined rows: 511

| Check | Status | Detail |
|---|---|---|
| schema_drift | PASS | missing=[] extra=[] |
| duplicate_line_item_id | FAIL | 114 duplicate rows |
| not_null:line_item_id | PASS | 0 nulls |
| not_null:usage_date | PASS | 0 nulls |
| not_null:account_id | PASS | 0 nulls |
| not_null:region | FAIL | 118 nulls |
| not_null:service | PASS | 0 nulls |
| not_null:resource_id | FAIL | 115 nulls |
| not_null:unblended_cost | FAIL | 114 nulls |
| cost_non_negative | FAIL | 58 negative |
| date_parseable | PASS | 0 unparseable |

## Quarantine breakdown

| dq_reason     |   rows |
|:--------------|-------:|
| null_required |    340 |
| duplicate     |    114 |
| negative_cost |     57 |