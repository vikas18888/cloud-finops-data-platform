# Day 13 - Kubernetes Right-Sizing Report

Pods analysed: 60 | Overprovisioned (<50% CPU or memory use): **43**

Requested-resource cost: $2,651/month | Potential saving: **$936/month (35.3%)**

Assumptions: $0.0316/vCPU-hr, $0.0042/GB-hr, 30% headroom over observed usage, 730 hrs/month. Usage is a single snapshot; use p95 over 2-4 weeks before applying in production.

## By namespace

| namespace   |   pods |   cpu_util |   mem_util |   monthly_cost |   saving |
|:------------|-------:|-----------:|-----------:|---------------:|---------:|
| checkout    |     19 |       0.51 |       0.55 |        1078.58 |   349.11 |
| ml          |     15 |       0.63 |       0.47 |         502.82 |   168.43 |
| platform    |     14 |       0.44 |       0.51 |         478.81 |   272.1  |
| search      |     12 |       0.54 |       0.64 |         590.94 |   146.24 |


## By node (CPU requested vs used)

| node   |   pods |   cpu_req_cores |   cpu_used_cores |   cpu_util_pct |
|:-------|-------:|----------------:|-----------------:|---------------:|
| node-0 |      8 |           10    |             3.83 |           38.3 |
| node-1 |     12 |           16    |             6.56 |           41   |
| node-2 |     12 |           25.5  |            12.8  |           50.2 |
| node-3 |      9 |            8.75 |             4.91 |           56.1 |
| node-4 |      9 |           16.75 |             9.88 |           59   |
| node-5 |     10 |           15    |             6.71 |           44.7 |


## Top 10 pods by saving

| namespace   | pod     |   cpu_request_m |   cpu_used_m |   rec_cpu_m |   mem_request_mb |   mem_used_mb |   rec_mem_mb |   monthly_saving |
|:------------|:--------|----------------:|-------------:|------------:|-----------------:|--------------:|-------------:|-----------------:|
| ml          | pod-001 |            4000 |          337 |         450 |             8192 |          7341 |         8192 |            81.89 |
| platform    | pod-035 |            4000 |          500 |         650 |             2048 |          1928 |         2048 |            77.28 |
| platform    | pod-009 |            4000 |          604 |         800 |             1024 |           376 |          512 |            75.35 |
| checkout    | pod-028 |            4000 |          715 |         950 |              512 |           404 |          512 |            70.36 |
| checkout    | pod-059 |            4000 |          928 |        1250 |             4096 |          2133 |         2816 |            67.27 |
| checkout    | pod-053 |            4000 |         1720 |        2250 |              512 |           292 |          384 |            40.75 |
| search      | pod-058 |            2000 |          160 |         250 |             4096 |          3555 |         4096 |            40.37 |
| platform    | pod-002 |            2000 |          329 |         450 |             1024 |           211 |          320 |            37.86 |
| checkout    | pod-036 |            4000 |         1813 |        2400 |              512 |           381 |          512 |            36.91 |
| ml          | pod-003 |            1000 |          338 |         450 |             8192 |          1291 |         1728 |            32.04 |


## Recommendations
1. Lower requests to the recommended values for the top-saving pods first.
2. After right-sizing, consolidate nodes with low CPU utilisation (cluster autoscaler / fewer nodes).
3. Add VPA in recommendation mode to keep requests aligned.