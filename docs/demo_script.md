# Day 21 - 10-minute demo script (record screen + voice)

Tip: rehearse once; keep the terminal font large; have `Day21_Final_Presentation.pptx` and VS Code open. Say clearly that the data is synthetic.

| Time | Show | Say (in your own words) |
|---|---|---|
| 0:00-0:45 | Slide 1-2 (architecture) | The problem: cloud bills are hard to explain. I built a pipeline from raw billing to executive decisions: ingest, quality, warehouse, analytics, alerts, dashboard. |
| 0:45-2:15 | Terminal: `python src/run_pipeline.py`, then `python src/reconcile.py` | Six tasks run in order. Reconciliation proves zero data loss: raw 11,545 = 11,034 clean + 397 quarantined + 114 duplicates. |
| 2:15-3:15 | `sql/01_schema.sql` + `reports/day05_index_report.md` | Star schema choice (grain = billing line item). Indexes cut query time by 3.6x to 12.9x on 662k rows. |
| 3:15-4:30 | `reports/day06_data_quality_report.md`, quarantine table | I quarantine bad rows with a reason instead of dropping them. |
| 4:30-6:00 | Slide 5 + `outputs/rate_optimization_model.xlsx` (change an input cell) | Savings model: waste removal plus commitments/Spot, netted to avoid double counting. 16.8% identified. Discounts are assumptions you can change. |
| 6:00-7:15 | `python src/anomaly_engine.py` | Z-score against a trailing 14-day baseline; 3 of 3 injected spikes caught. Be honest: 3 low-severity flags are likely weekday effects. |
| 7:15-8:30 | `streamlit run dashboard/app.py` (or `outputs/Day18_Executive_View.pdf`) | KPIs for executives: spend, cost per 1k requests, modelled coverage, forecast variance. |
| 8:30-9:15 | `dags/finops_pipeline_dag.py` (+ Airflow graph screenshot if you ran it), `.github/workflows/infracost.yml` | Orchestration and cost checks on every infrastructure PR. |
| 9:15-10:00 | Slide 8 | Lessons: reconcile, quarantine, net the savings. Next steps: real CUR data, dbt, weekday-aware baselines. |

## Questions to be ready for
- Why a star schema? (fast aggregation, clear grain, constraints)
- Why z-score and not ML? (explainable, no training data, easy to tune)
- What if the baseline includes a past spike? (use median/MAD or same-weekday baseline: next step)
- How do you avoid double counting savings? (waste removed first, rate savings scaled to the remainder)
- What is real vs assumed? (data is synthetic; discounts and prices are illustrative inputs)
