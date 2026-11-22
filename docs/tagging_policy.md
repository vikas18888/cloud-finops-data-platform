# Cloud Tagging Governance Policy (v1.0)

## 1. Purpose
Every cloud resource must be attributable to a team, environment and budget so costs can be charged back, optimised and audited.

## 2. Mandatory tags
| Tag key | Allowed values | Owner | Example |
|---|---|---|---|
| `owner_team` | checkout, search, ml, platform (extend via change request) | Engineering manager | `checkout` |
| `env` | prod, staging, dev | Resource creator | `prod` |
| `cost_center` | `CC-` + 3 digits | Finance | `CC-101` |

## 3. Rules
1. Tags are applied **at creation** (Terraform `default_tags` / launch templates); untagged creation is blocked by policy where the cloud supports it.
2. Tag keys are lowercase, `snake_case`; values are from the allowed list only (no free text).
3. Shared resources (networking, logging) use `owner_team=platform` and are allocated proportionally.
4. Tag values may only be changed by the owning team or FinOps.

## 4. Compliance and enforcement
| Item | Target | Cadence |
|---|---|---|
| Tag coverage (cost-weighted) | >= 95% | Weekly audit (`src/audit_untagged.py`) |
| Untagged resources | Tagged within 7 days of detection | Owner notified by FinOps |
| Orphaned resources (no activity 90+ days, no owner) | Review, then terminate/snapshot within 14 days | Monthly |

## 5. Orphan definition
A resource is **orphaned** when it has no `owner_team` AND has not been active for 90 or more days. Resources with an owner but idle for 90+ days are flagged **idle** for owner review.

## 6. Roles
- **FinOps:** runs audit, reports coverage, escalates.
- **Resource owners:** fix tags, justify or remove idle resources.
- **Engineering managers:** accountable for team compliance.
