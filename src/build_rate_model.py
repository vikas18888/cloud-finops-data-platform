"""Day 11: build the rate-optimisation Excel model (live formulas). Workload inputs come from the warehouse."""
import sqlite3
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.comments import Comment

con = sqlite3.connect("db/finops.db")
d = pd.read_sql_query("""SELECT s.service_name, dt.full_date, SUM(f.unblended_cost) AS cost FROM fact_cost f
    JOIN dim_service s USING(service_key) JOIN dim_date dt USING(date_key)
    WHERE s.service_name IN ('AmazonEC2','AmazonRDS') GROUP BY 1,2""", con)
stats = d.groupby("service_name")["cost"].agg(avg="mean", base=lambda x: x.quantile(0.10))

F = "Arial"
blue = Font(name=F, color="0000FF"); black = Font(name=F); bold = Font(name=F, bold=True); white = Font(name=F, bold=True, color="FFFFFF")
hdr = PatternFill("solid", fgColor="1F4E78"); yellow = PatternFill("solid", fgColor="FFFF00"); grey = PatternFill("solid", fgColor="F2F2F2")
USD = '$#,##0;($#,##0);-'; PCT = '0.0%;(0.0%);-'
wb = Workbook(); ws = wb.active; ws.title = "Inputs"
ws["A1"] = "Rate Optimisation Model - Inputs"; ws["A1"].font = Font(name=F, bold=True, size=14)
ws["A2"] = "Legend: blue = editable input | black = formula | yellow fill = key assumption to review. All discount rates are ILLUSTRATIVE; verify with the AWS Pricing Calculator for your instance family/region."; ws["A2"].font = Font(name=F, italic=True)
ws.merge_cells("A2:D2"); ws["A2"].alignment = Alignment(wrap_text=True, vertical="top"); ws.row_dimensions[2].height = 45
rows = [("Discount assumptions", None, None),
        ("Reserved Instance, 1-yr (no upfront) discount", 0.30, "Illustrative; typical range 25-40%"),
        ("Reserved Instance, 3-yr discount", 0.50, "Illustrative; typical range 45-60%"),
        ("Compute Savings Plan, 1-yr discount", 0.25, "Illustrative; typical range 20-30%"),
        ("Spot discount vs On-Demand", 0.65, "Illustrative; typical range 60-90%"),
        ("Spot interruption / retry overhead", 0.05, "Cost of re-running interrupted work, as % of workload cost"),
        ("Commitment coverage of baseline", 0.80, "Commit only 80% of steady baseline to avoid over-commitment"),
        ("Fault-tolerant share of variable EC2 load", 0.50, "Share of above-baseline EC2 load that can run on Spot (batch, CI, stateless)")]
r = 4
for label, val, note in rows:
    ws.cell(r, 1, label).font = bold if val is None else black
    if val is not None:
        c = ws.cell(r, 2, val); c.font = blue; c.number_format = PCT; c.fill = yellow; ws.cell(r, 3, note).font = Font(name=F, italic=True, size=9)
    r += 1
# named positions: B5 RI1, B6 RI3, B7 SP1, B8 SPOT, B9 OVERHEAD, B10 COVERAGE, B11 FT_SHARE
ws["A13"] = "Workload baseline (from warehouse, 90 days, all accounts)"; ws["A13"].font = bold
for i, h in enumerate(["Service", "Avg daily cost ($)", "Baseline daily cost ($) = 10th percentile", "Spot eligible? (1=yes)"], 1):
    c = ws.cell(14, i, h); c.font = white; c.fill = hdr; c.alignment = Alignment(wrap_text=True)
for i, svc in enumerate(["AmazonEC2", "AmazonRDS"], 15):
    ws.cell(i, 1, svc).font = black
    for col, v, fmt in [(2, round(stats.loc[svc, "avg"], 2), '$#,##0.00'), (3, round(stats.loc[svc, "base"], 2), '$#,##0.00'), (4, 1 if svc == "AmazonEC2" else 0, '0')]:
        c = ws.cell(i, col, v); c.font = blue; c.number_format = fmt
ws["A17"] = "Source: db/finops.db (fact_cost), synthetic data. Baseline = 10th-percentile daily spend = steady load that is almost always running (safe to commit). RDS cannot use Spot."; ws["A17"].font = Font(name=F, italic=True, size=9)
ws["A18"] = "Caveat: spend grows ~0.4%/day in this data, so a 90-day P10 baseline is conservative; re-check before purchasing."; ws["A18"].font = Font(name=F, italic=True, size=9)
ws.column_dimensions["A"].width = 52; ws.column_dimensions["B"].width = 20; ws.column_dimensions["C"].width = 42; ws.column_dimensions["D"].width = 22

m = wb.create_sheet("Model")
m["A1"] = "Annual cost by pricing strategy ($)"; m["A1"].font = Font(name=F, bold=True, size=14)
heads = ["Service", "Annual On-Demand", "Annual baseline", "Annual variable", "RI 1-yr", "RI 3-yr", "Savings Plan 1-yr", "Spot (variable share only)", "Recommended blend (RI 1-yr + Spot)"]
for i, h in enumerate(heads, 1):
    c = m.cell(3, i, h); c.font = white; c.fill = hdr; c.alignment = Alignment(wrap_text=True, vertical="center")
m.row_dimensions[3].height = 45
for k, row in enumerate([4, 5]):
    i = 15 + k
    f = {1: f"=Inputs!A{i}", 2: f"=Inputs!B{i}*365", 3: f"=Inputs!C{i}*365", 4: f"=B{row}-C{row}",
         5: f"=B{row}-C{row}*Inputs!$B$10*Inputs!$B$5", 6: f"=B{row}-C{row}*Inputs!$B$10*Inputs!$B$6",
         7: f"=B{row}-C{row}*Inputs!$B$10*Inputs!$B$7",
         8: f"=B{row}-Inputs!$D{i}*D{row}*Inputs!$B$11*(Inputs!$B$8-Inputs!$B$9)",
         9: f"=B{row}-C{row}*Inputs!$B$10*Inputs!$B$5-Inputs!$D{i}*D{row}*Inputs!$B$11*(Inputs!$B$8-Inputs!$B$9)"}
    for col, v in f.items():
        c = m.cell(row, col, v); c.font = Font(name=F, color="008000") if col == 1 else black
        if col > 1: c.number_format = USD
m["A6"] = "Total"; m["A6"].font = bold
for col in range(2, 10):
    L = chr(64 + col); c = m.cell(6, col, f"=SUM({L}4:{L}5)"); c.font = bold; c.number_format = USD; c.fill = grey
m["A8"] = "Annual savings vs On-Demand ($)"; m["A8"].font = bold
m["A9"] = "Savings % vs On-Demand"; m["A9"].font = bold
for col in range(5, 10):
    L = chr(64 + col)
    c = m.cell(8, col, f"=$B$6-{L}6"); c.font = black; c.number_format = USD
    c = m.cell(9, col, f"=IF($B$6=0,0,{L}8/$B$6)"); c.font = black; c.number_format = PCT
m["A11"] = "Reading the table: RI/Savings Plans apply the discount only to the committed share of the baseline; the rest stays On-Demand. Spot applies only to the fault-tolerant share of the variable EC2 load. The blend combines both, and is the recommended strategy."; m["A11"].font = Font(name=F, italic=True, size=9)
m["A12"] = "Break-even note: a 3-yr RI saves more per hour but locks capital for 3 years; only commit what you are sure will run (see coverage input)."; m["A12"].font = Font(name=F, italic=True, size=9)
m.column_dimensions["A"].width = 34
for L in "BCDEFGHI": m.column_dimensions[L].width = 19
wb.save("outputs/rate_optimization_model.xlsx"); print("saved")
