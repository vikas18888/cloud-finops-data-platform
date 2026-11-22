# Day 8 - Executive Memo: Cloud Unit Cost Efficiency
**To:** Engineering & Finance leadership | **Data:** 90 days of billing (synthetic) + business metrics

## Headline metrics (latest month: 2026-10 vs first month: 2026-08)
| Metric | 2026-08 | 2026-10 | Change |
|---|---|---|---|
| Cost per 1,000 API requests | $0.88 | $1.09 | +23.3% |
| Cost per active customer | $4.47 | $5.17 | +15.7% |
| Compute cost per processing hour | $0.79 | $0.91 | +15.6% |

## Interpretation
- Business volume (requests, customers) is roughly flat over the period, while cloud cost grows (~0.4%/day in the data). Unit costs therefore **rise**, which means efficiency is getting worse, not better.
- Note: the data covers Aug 1 - Oct 29, so October has 29 days vs 31 in August. Per-request and per-hour metrics are unaffected; cost per customer (monthly cost / avg customers) is slightly understated for October, so the true increase is a bit higher.
- 19.9% of spend has no team tag, so it cannot be charged back to a tenant until tagging improves (see Day 9).

## Recommendations
1. Track cost per 1k requests as the primary efficiency KPI on the dashboard (Day 18).
2. Investigate compute growth against flat workload: candidates are over-provisioned instances and missing commitments (Days 11 and 13).
3. Fix tagging gaps so per-tenant unit cost is reliable.

*Caveat: figures come from synthetic data; the method, not the numbers, is the deliverable.*
