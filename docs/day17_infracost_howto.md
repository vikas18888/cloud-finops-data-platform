# Day 17 - Infracost in CI/CD (how to produce your evidence)

Terraform and Infracost were not available where this code was written, so run these yourself and paste the real output below.

1. Install Terraform and Infracost (https://www.infracost.io/docs/), then `infracost auth login` (free key).
2. Baseline estimate:
   `infracost breakdown --path terraform`
3. Create a branch, change the `app_instance_type` default to `m5.2xlarge` in `terraform/main.tf`, then:
   `infracost diff --path terraform --compare-to baseline.json` (create baseline.json first with `infracost breakdown --path terraform --format json --out-file baseline.json` on main).
4. Push the branch and open a pull request. Add the repo secret `INFRACOST_API_KEY`; the workflow `.github/workflows/infracost.yml` posts the cost-change comment automatically.
5. Screenshot the PR comment and paste the `infracost diff` output in the section below.

## Evidence (paste here)
```
<paste infracost breakdown / diff output here>
```
