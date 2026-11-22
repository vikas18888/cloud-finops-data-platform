# Day 14 - Cloud Optimisation Audit Summary

Annualised spend (from 90 days): **$708,067**

| Finding | Annual saving | % of spend |
|---|---|---|
| Remove orphaned (100%) + idle (50%) resources | $28,654 | 4.0% |
| Rate optimisation (RI 1-yr on 80% of baseline + Spot), net of waste removal | $90,338 | 12.8% |
| **Total (headline)** | **$118,992** | **16.8%** |
| Kubernetes right-sizing (separate cluster, NOT in headline) | $11,231 | n/a |
| Spike prevention via alerting (one-off, NOT in headline) | $1,806 per 90 days | n/a |

Method: waste is removed first, then rate-optimisation savings are scaled to the remaining spend to avoid double counting. Idle realisation 50% is an assumption. Discount rates are illustrative (see Excel model).
