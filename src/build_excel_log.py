"""Day 21: build the 21-day Excel work log TEMPLATE. Dates, hours, commit links, scores and reflections are left for the intern to fill."""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation

DAYS = [
 (1, "Enterprise Data Modeling & Dimensional Design", "ERD + DDL scripts", "sql/01_schema.sql; src/load_warehouse.py", "Why did you choose billing line item as the fact grain?"),
 (2, "Advanced SQL for Data Analytics", "8 queries + CSV output", "sql/02_analytics.sql; outputs/day02/", "Which window function was hardest and why?"),
 (3, "Python Data Ingestion & Cleansing Pipelines", "ingest_billing.py + processed dataset", "src/ingest_billing.py; data/processed/", "How did you handle the 3 date formats?"),
 (4, "Cloud Billing Data Architectures", "Profiling analysis by service/usage type", "src/profile_costs.py; reports/day04_cost_profile.md", "What does the cost distribution suggest to optimise first?"),
 (5, "Database Optimization & Indexing", "EXPLAIN comparison before/after indexing", "sql/03_indexes.sql; reports/day05_index_report.md", "Why this column order in the composite index?"),
 (6, "Automated Data Quality & Validation", "DQ report + quarantine table", "src/validate_data.py; reports/day06_data_quality_report.md", "What happens to quarantined rows downstream?"),
 (7, "Week 1 Pipeline Review & Reconciliation", "Reconciliation output + tracker + release v1.0", "src/reconcile.py; reports/day07_reconciliation.md; tag v1.0", "How do you know no data was lost?"),
 (8, "Cloud Unit Economics", "Unit cost model + executive memo", "src/unit_economics.py; reports/day08_executive_memo.md", "What does rising cost per request mean?"),
 (9, "Tagging Governance", "Tagging policy + audit_untagged.py", "docs/tagging_policy.md; src/audit_untagged.py", "How would you enforce tags at creation?"),
 (10, "Cloud Data Warehousing", "DDL with clustering + execution time logs", "sql/10_bigquery_ddl.sql; sql/10_snowflake_ddl.sql; docs/day10_benchmark_log.md (FILL IN)", "What did partition pruning save? (use YOUR numbers)"),
 (11, "Rate Optimization", "RI/Savings Plan/Spot spreadsheet model", "outputs/rate_optimization_model.xlsx", "Which assumptions drive the savings most?"),
 (12, "Anomaly Detection Engine", "anomaly_engine.py + test report", "src/anomaly_engine.py; reports/day12_anomaly_report.md", "Why exclude the current day from the baseline?"),
 (13, "Kubernetes Cost Allocation", "Container right-sizing report", "src/k8s_rightsizing.py; reports/day13_k8s_report.md", "Why use p95 usage in production?"),
 (14, "Mid-Term FinOps Audit", "Audit deck + tracker + release v2.0", "outputs/Day14_Mid-Term_Audit.pptx; tag v2.0", "How did you avoid double counting savings?"),
 (15, "Workflow Orchestration (Airflow)", "DAG file + execution graph screenshot", "dags/finops_pipeline_dag.py; docs/airflow_dag_graph.png (YOU capture)", "What should fail the DAG and what should not?"),
 (16, "Cost Amortization & Depreciation", "Amortization Excel + SQL view", "outputs/asset_amortization_model.xlsx; sql/16_depreciation.sql", "How did you check Excel against SQL?"),
 (17, "IaC Cost Estimation (Terraform + Infracost)", "main.tf + Infracost PR output", "terraform/main.tf; docs/day17_infracost_howto.md (paste YOUR output)", "How does a PR cost comment change behaviour?"),
 (18, "Executive FinOps BI Dashboard", "Dashboard code + exported PDF", "dashboard/app.py; outputs/Day18_Executive_View.pdf", "Which KPI would an executive look at first?"),
 (19, "Storage Tiering & Lifecycle Automation", "Lifecycle policy JSON + cost model", "docs/s3_lifecycle_policy.json; outputs/storage_tiering_model.xlsx", "When does moving to Glacier cost more?"),
 (20, "FinOps Data Platform Capstone", "Repo + README + architecture diagram", "README.md; docs/architecture.png", "What would you do differently in the architecture?"),
 (21, "Final Technical Presentation & Submission", "Deck + demo recording + verified log", "outputs/Day21_Final_Presentation.pptx; docs/demo_script.md; recording link (YOU)", "What is the strongest result and its caveat?"),
]
F = "Arial"; blue = Font(name=F, color="0000FF"); blk = Font(name=F); bold = Font(name=F, bold=True)
white = Font(name=F, bold=True, color="FFFFFF"); hdr = PatternFill("solid", fgColor="1F4E78"); yel = PatternFill("solid", fgColor="FFF2CC"); grey = PatternFill("solid", fgColor="F2F2F2")
thin = Side(style="thin", color="BFBFBF"); box = Border(left=thin, right=thin, top=thin, bottom=thin)
wb = Workbook(); ws = wb.active; ws.title = "Daily Log"
ws["A1"] = "PACEX 21-Day Internship - Daily Work Log (Data Engineering & Cloud FinOps)"; ws["A1"].font = Font(name=F, bold=True, size=14)
ws["A2"] = "Fill ONLY the yellow cells (E to I and K): actual date, verified hours, your commit link, self-score 1-5, your own technical reflection, status. Grey columns are pre-filled from the program plan. Log real dates and hours only."
ws["A2"].font = Font(name=F, italic=True, size=9); ws.merge_cells("A2:K2"); ws["A2"].alignment = Alignment(wrap_text=True); ws.row_dimensions[2].height = 28
ws["A3"] = "Example format (do not copy):"; ws["A3"].font = Font(name=F, italic=True, size=9)
ws["E3"] = "2026-11-24"; ws["F3"] = 5.5; ws["G3"] = "https://github.com/<user>/<repo>/commit/abc1234"; ws["H3"] = 4
ws["I3"] = "Chose line-item grain so any rollup is possible; FK constraints caught a bad key during load."
for c in ("E3", "F3", "G3", "H3", "I3"): ws[c].font = Font(name=F, italic=True, size=9, color="7F7F7F")
heads = ["Day", "Topic", "Task deliverable (required evidence)", "Evidence in repo", "Date (YYYY-MM-DD)", "Hours spent (min 5)", "Commit link", "Self-score (1-5)", "Technical reflection (your words)", "Reflection prompt (suggested)", "Status", "Hours check"]
for i, h in enumerate(heads, 1):
    c = ws.cell(5, i, h); c.font = white; c.fill = hdr; c.alignment = Alignment(wrap_text=True, vertical="center"); c.border = box
ws.row_dimensions[5].height = 34
for k, (d, topic, ev, files, prompt) in enumerate(DAYS):
    r = 6 + k
    vals = {1: d, 2: topic, 3: ev, 4: files, 10: prompt}
    for col, v in vals.items(): ws.cell(r, col, v).font = blk
    for col in range(1, 13):
        c = ws.cell(r, col); c.border = box; c.alignment = Alignment(wrap_text=True, vertical="top")
        c.fill = yel if col in (5, 6, 7, 8, 9, 11) else (grey if col in (1, 2, 3, 4, 10) else PatternFill())
    ws.cell(r, 11, "Not started").font = blue
    ws.cell(r, 12, f'=IF(F{r}="","",IF(F{r}>=5,"OK","Below 5h"))').font = blk
    ws.cell(r, 5).number_format = "yyyy-mm-dd"; ws.cell(r, 6).number_format = "0.0"
last = 5 + len(DAYS)
dv = DataValidation(type="whole", operator="between", formula1="1", formula2="5", allow_blank=True, errorTitle="Self-score", error="Enter a whole number from 1 to 5"); ws.add_data_validation(dv); dv.add(f"H6:H{last}")
dv2 = DataValidation(type="decimal", operator="between", formula1="0", formula2="16", allow_blank=True, error="Enter hours between 0 and 16"); ws.add_data_validation(dv2); dv2.add(f"F6:F{last}")
dv3 = DataValidation(type="list", formula1='"Not started,In progress,Done"', allow_blank=True); ws.add_data_validation(dv3); dv3.add(f"K6:K{last}")
t = last + 2
ws.cell(t, 1, "Summary").font = bold
ws.cell(t + 1, 2, "Total hours logged"); ws.cell(t + 1, 3, f"=SUM(F6:F{last})")
ws.cell(t + 2, 2, "Days with hours logged"); ws.cell(t + 2, 3, f"=COUNT(F6:F{last})")
ws.cell(t + 3, 2, "Days marked Done"); ws.cell(t + 3, 3, f'=COUNTIF(K6:K{last},"Done")')
ws.cell(t + 4, 2, "Days below 5 hours"); ws.cell(t + 4, 3, f'=COUNTIF(L6:L{last},"Below 5h")')
ws.cell(t + 5, 2, "Average self-score"); ws.cell(t + 5, 3, f'=IF(COUNT(H6:H{last})=0,"",AVERAGE(H6:H{last}))'); ws.cell(t + 5, 3).number_format = "0.0"
ws.cell(t + 1, 3).number_format = "0.0"
for r in range(t + 1, t + 6): ws.cell(r, 2).font = blk; ws.cell(r, 3).font = bold
for L, w in zip("ABCDEFGHIJKL", [6, 34, 30, 40, 16, 12, 30, 11, 50, 34, 13, 12]): ws.column_dimensions[L].width = w
ws.freeze_panes = "C6"
wb.save("outputs/21-Day_Excel_Work_Log.xlsx"); print("saved", len(DAYS), "rows")
