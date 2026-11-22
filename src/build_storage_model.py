"""Day 19: storage tiering model (Excel, live formulas) driven by object age and access frequency."""
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

objs = pd.read_csv("data/raw/s3_objects.csv")
F = "Arial"; blue = Font(name=F, color="0000FF"); blk = Font(name=F); bold = Font(name=F, bold=True)
white = Font(name=F, bold=True, color="FFFFFF"); hdr = PatternFill("solid", fgColor="1F4E78"); yel = PatternFill("solid", fgColor="FFFF00")
USD = '$#,##0.00;($#,##0.00);-'; wb = Workbook(); a = wb.active; a.title = "Assumptions"
a["A1"] = "Storage Tiering Model - Assumptions"; a["A1"].font = Font(name=F, bold=True, size=14)
a["A2"] = "Blue = editable input. Prices are ILLUSTRATIVE USD per GB-month (approx. S3 list prices); verify for your region at aws.amazon.com/s3/pricing. Each access is assumed to retrieve the whole object once (conservative)."
a["A2"].font = Font(name=F, italic=True, size=9)
rows = [("S3 Standard price ($/GB-month)", 0.023, '$0.0000'), ("Standard-IA price ($/GB-month)", 0.0125, '$0.0000'), ("Glacier Flexible Retrieval price ($/GB-month)", 0.0036, '$0.0000'),
        ("Standard-IA retrieval ($/GB)", 0.01, '$0.0000'), ("Glacier retrieval ($/GB)", 0.01, '$0.0000'),
        ("Rule: move to IA when age >= (days)", 30, '0'), ("Rule: IA only if accesses in last 30d <= ", 5, '0'),
        ("Rule: move to Glacier when age >= (days)", 90, '0'), ("Rule: Glacier only if accesses in last 30d <= ", 1, '0')]
for i, (l, v, f) in enumerate(rows, 4):
    a.cell(i, 1, l).font = blk; c = a.cell(i, 2, v); c.font = blue; c.number_format = f; c.fill = yel
a.column_dimensions["A"].width = 50; a.column_dimensions["B"].width = 14
# B4 std, B5 IA, B6 GL, B7 IA retr, B8 GL retr, B9 IA age, B10 IA acc, B11 GL age, B12 GL acc
o = wb.create_sheet("Objects")
for i, h in enumerate(["Prefix", "Size (GB)", "Age (days)", "Accesses (30d)", "Assigned tier", "Current cost ($/mo, all Standard)", "Optimised storage ($/mo)", "Retrieval cost ($/mo)", "Optimised total ($/mo)", "Saving ($/mo)"], 1):
    c = o.cell(1, i, h); c.font = white; c.fill = hdr; c.alignment = Alignment(wrap_text=True, vertical="center")
o.row_dimensions[1].height = 45
for k, r in objs.iterrows():
    n = 2 + k
    for i, v in enumerate([r.object_prefix, r.size_gb, r.age_days, r.accesses_last_30d], 1): o.cell(n, i, v).font = blue
    o.cell(n, 5, f'=IF(AND(C{n}>=Assumptions!$B$11,D{n}<=Assumptions!$B$12),"Glacier",IF(AND(C{n}>=Assumptions!$B$9,D{n}<=Assumptions!$B$10),"Standard-IA","Standard"))')
    o.cell(n, 6, f"=B{n}*Assumptions!$B$4")
    o.cell(n, 7, f'=B{n}*IF(E{n}="Glacier",Assumptions!$B$6,IF(E{n}="Standard-IA",Assumptions!$B$5,Assumptions!$B$4))')
    o.cell(n, 8, f'=B{n}*D{n}*IF(E{n}="Glacier",Assumptions!$B$8,IF(E{n}="Standard-IA",Assumptions!$B$7,0))')
    o.cell(n, 9, f"=G{n}+H{n}"); o.cell(n, 10, f"=F{n}-I{n}")
    for i in range(5, 11): o.cell(n, i).font = blk
    for i in range(6, 11): o.cell(n, i).number_format = USD
last = 1 + len(objs)
for L, w in zip("ABCDEFGHIJ", [12, 11, 11, 14, 14, 20, 18, 16, 16, 14]): o.column_dimensions[L].width = w
s = wb.create_sheet("Summary")
s["A1"] = "Storage Tiering - Summary"; s["A1"].font = Font(name=F, bold=True, size=14)
for i, h in enumerate(["Tier", "Objects", "Size (GB)", "Optimised total ($/mo)"], 1):
    c = s.cell(3, i, h); c.font = white; c.fill = hdr
for i, t in enumerate(["Standard", "Standard-IA", "Glacier"], 4):
    s.cell(i, 1, t).font = blk
    s.cell(i, 2, f'=COUNTIF(Objects!$E$2:$E${last},A{i})').number_format = "0"
    s.cell(i, 3, f'=SUMIFS(Objects!$B$2:$B${last},Objects!$E$2:$E${last},A{i})').number_format = '#,##0.0'
    s.cell(i, 4, f'=SUMIFS(Objects!$I$2:$I${last},Objects!$E$2:$E${last},A{i})').number_format = USD
s["A7"] = "Total"; s["A7"].font = bold
for col, fm in ((2, "0"), (3, '#,##0.0'), (4, USD)):
    L = chr(64 + col); c = s.cell(7, col, f"=SUM({L}4:{L}6)"); c.font = bold; c.number_format = fm
s["A9"] = "Current monthly cost (all Standard)"; s["B9"] = f"=SUM(Objects!F2:F{last})"; s["B9"].number_format = USD
s["A10"] = "Optimised monthly cost (incl. retrieval)"; s["B10"] = "=D7"; s["B10"].number_format = USD
s["A11"] = "Monthly saving"; s["B11"] = "=B9-B10"; s["B11"].number_format = USD
s["A12"] = "Annual saving"; s["B12"] = "=B11*12"; s["B12"].number_format = USD
s["A13"] = "Saving %"; s["B13"] = "=IF(B9=0,0,B11/B9)"; s["B13"].number_format = "0.0%"
for r in range(9, 14): s.cell(r, 1).font = bold; s.cell(r, 2).font = blk
s.column_dimensions["A"].width = 42
for L in "BCD": s.column_dimensions[L].width = 22
wb.move_sheet("Summary", offset=-2); wb.save("outputs/storage_tiering_model.xlsx"); print("saved")
