# Day 12 - Anomaly Detection Test Report

Method: per-service daily cost; baseline = trailing 14-day mean/std (current day excluded); flag when z > 3.0 AND cost > 1.5x baseline.

Anomalies flagged: **6**

| Date | Service | Cost | Expected | z-score | Ratio | Severity |
|---|---|---|---|---|---|---|
| 2026-09-17 | AmazonS3 | $741.60 | $218.84 | 9.6 | 3.39x | HIGH |
| 2026-08-21 | AmazonEC2 | $1657.73 | $605.83 | 7.9 | 2.74x | HIGH |
| 2026-10-11 | AWSDataTransfer | $408.19 | $177.07 | 7.0 | 2.31x | HIGH |
| 2026-10-06 | AmazonEC2 | $1007.58 | $656.34 | 3.6 | 1.54x | LOW |
| 2026-09-03 | AmazonRDS | $682.69 | $454.52 | 3.4 | 1.50x | LOW |
| 2026-09-22 | AWSDataTransfer | $257.44 | $165.92 | 3.1 | 1.55x | LOW |

## Validation against known ground truth
The synthetic dataset contains 3 injected spikes (EC2 on 2026-08-21, S3 on 2026-09-17, DataTransfer on 2026-10-11). All 3 are flagged as HIGH (z >= 5).

LOW-severity flags (z between 3 and 5) were not injected; they are most likely normal weekday/weekend rebounds (e.g. a Monday after a low weekend baseline). Known limitation: the baseline has no day-of-week adjustment. Improvement: compare each day against the same weekday in prior weeks, or alert only on HIGH.