# Day 9 - Tagging Audit Report

Resources scanned: 280 | Cost-weighted tag coverage: **46.1%** (policy target: 95%)

| status   |   resources |   cost_90d |   pct_of_spend |
|:---------|------------:|-----------:|---------------:|
| idle     |          20 |   12257.9  |           7.02 |
| ok       |         110 |   73095.7  |          41.87 |
| orphaned |           4 |     936.36 |           0.54 |
| untagged |         146 |   88302    |          50.58 |


## Top 5 costliest non-compliant resources

| resource_id   | status   | missing_tags   |   cost_90d |
|:--------------|:---------|:---------------|-----------:|
| ec2-0030      | untagged | env            |    1893.05 |
| ec2-0015      | idle     | env            |    1885.39 |
| ec2-0006      | untagged | cost_center    |    1788.34 |
| ec2-0037      | untagged | env            |    1729.63 |
| ec2-0008      | untagged | cost_center    |    1657.8  |


Note: this audit uses the asset *inventory* tags; Q8 in Day 2 uses *billing* cost-allocation tags. They are separate sources and can disagree, which is itself a governance finding.

Note: orphaned/idle cost is the 90-day spend of those resources and is an upper bound on savings (some may be needed).