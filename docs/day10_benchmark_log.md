# Day 10 - Warehouse Execution Log (FILL IN FROM YOUR OWN RUNS)

Warehouse used: [ ] BigQuery sandbox  [ ] Snowflake trial   Date run: ____

Note: the sample dataset is small (~11k rows), so absolute differences will be tiny. What matters is the bytes processed / partitions scanned, which show pruning working. To see bigger gaps, append the CSV several times before loading.

| Query | Table | Elapsed time | Bytes processed (BQ) or Partitions scanned (SF) |
|---|---|---|---|
| Q-A single account, one month | baseline | | |
| Q-A single account, one month | optimized/clustered | | |
| Q-B daily trend, one service | baseline | | |
| Q-B daily trend, one service | optimized/clustered | | |

Reduction achieved: ____ %    Screenshot of job details saved as: docs/day10_screenshot.png
