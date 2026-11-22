# Day 4 - Cost Distribution Profile

Period: 90 days | Total spend: **$174,591.97** | Line items: 11,034

## By category

| category         | spend              |
|:-----------------|:-------------------|
| Compute          | $67,807.05 (38.8%) |
| Managed Services | $57,651.27 (33.0%) |
| Storage          | $33,545.96 (19.2%) |
| Networking       | $15,587.70 (8.9%)  |


## By service

| category         | service_name    |     cost |   pct |
|:-----------------|:----------------|---------:|------:|
| Compute          | AmazonEC2       | 60041.2  |  34.4 |
| Managed Services | AmazonRDS       | 47185    |  27   |
| Storage          | AmazonS3        | 20857.2  |  11.9 |
| Networking       | AWSDataTransfer | 15587.7  |   8.9 |
| Storage          | AmazonEBS       | 12688.8  |   7.3 |
| Managed Services | AmazonDynamoDB  | 10466.3  |   6   |
| Compute          | AWSLambda       |  7765.86 |   4.4 |


## By usage type

| usage_type                |      sum |   count |   mean |   pct |
|:--------------------------|---------:|--------:|-------:|------:|
| BoxUsage:m5.large         | 60041.2  |    1521 |  39.47 | 34.39 |
| InstanceUsage:db.r5.large | 47185    |    1623 |  29.07 | 27.03 |
| TimedStorage-ByteHrs      | 20857.2  |    1580 |  13.2  | 11.95 |
| DataTransfer-Out-Bytes    | 15587.7  |    1569 |   9.93 |  8.93 |
| EBS:VolumeUsage.gp3       | 12688.8  |    1560 |   8.13 |  7.27 |
| ReadCapacityUnit-Hrs      | 10466.3  |    1592 |   6.57 |  5.99 |
| Lambda-GB-Second          |  7765.86 |    1589 |   4.89 |  4.45 |


## Observations
- Top category: **Compute** (38.8% of spend).

- Top 2 services account for 61.4% of spend, so optimisation should start there.

- Compute + Managed Services (EC2/RDS) are the main candidates for Reserved Instance / Savings Plan commitments (Day 11).
