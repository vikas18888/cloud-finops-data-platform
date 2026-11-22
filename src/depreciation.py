"""Day 16: asset depreciation / amortisation. Loads the asset register, creates the SQL view, exports the schedule,
and builds an Excel model with live formulas (outputs/asset_amortization_model.xlsx)."""
import sqlite3
from pathlib import Path
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

def build_db(db="db/finops.db"):
    con = sqlite3.connect(db)
    pd.read_csv("data/raw/asset_register.csv").to_sql("asset_register", con, if_exists="replace", index=False)
    con.executescript(Path("sql/16_depreciation.sql").read_text()); con.commit()
    sched = pd.read_sql_query("SELECT * FROM v_monthly_depreciation ORDER BY asset_id, month_no", con)
    sched.to_csv("outputs/day16_depreciation_schedule.csv", index=False)
    by_month = pd.read_sql_query("SELECT period, ROUND(SUM(depreciation),2) AS total_depreciation FROM v_monthly_depreciation GROUP BY period ORDER BY period", con)
    return sched, by_month

def build_excel(path="outputs/asset_amortization_model.xlsx"):
    assets = pd.read_csv("data/raw/asset_register.csv")
    F = "Arial"; blue = Font(name=F, color="0000FF"); blk = Font(name=F); bold = Font(name=F, bold=True)
    white = Font(name=F, bold=True, color="FFFFFF"); hdr = PatternFill("solid", fgColor="1F4E78"); yel = PatternFill("solid", fgColor="FFFF00")
    USD = '$#,##0;($#,##0);-'
    wb = Workbook(); ws = wb.active; ws.title = "Assets"
    ws["A1"] = "Asset Depreciation / Amortisation Model"; ws["A1"].font = Font(name=F, bold=True, size=14)
    ws["A2"] = "Blue = editable input | black = formula | yellow = as-of date. Straight-line method; depreciation starts the month after purchase. Software rows are capitalised development cost (amortised)."
    ws["A2"].font = Font(name=F, italic=True, size=9)
    ws["A3"] = "As-of month (first day):"; ws["A3"].font = bold; ws["C3"] = pd.Timestamp("2026-11-01").to_pydatetime(); ws["C3"].number_format = "yyyy-mm-dd"; ws["C3"].font = blue; ws["C3"].fill = yel
    heads = ["Asset ID", "Asset", "Type", "Purchase date", "Cost ($)", "Salvage ($)", "Life (years)", "Monthly depreciation ($)", "Months elapsed", "Accumulated ($)", "Net book value ($)"]
    for i, h in enumerate(heads, 1):
        c = ws.cell(5, i, h); c.font = white; c.fill = hdr; c.alignment = Alignment(wrap_text=True, vertical="center")
    ws.row_dimensions[5].height = 32
    for k, a in assets.iterrows():
        r = 6 + k
        vals = [a.asset_id, a.asset_name, a.asset_type, pd.Timestamp(a.purchase_month + "-01").to_pydatetime(), a.cost, a.salvage_value, a.life_years]
        for i, v in enumerate(vals, 1):
            c = ws.cell(r, i, v); c.font = blue
            if i == 4: c.number_format = "yyyy-mm-dd"
            if i in (5, 6): c.number_format = USD
        ws.cell(r, 8, f"=(E{r}-F{r})/(G{r}*12)").number_format = '$#,##0.00'
        ws.cell(r, 9, f"=MAX(0,MIN(G{r}*12,(YEAR($C$3)-YEAR(D{r}))*12+MONTH($C$3)-MONTH(D{r})))").number_format = "0"
        ws.cell(r, 10, f"=H{r}*I{r}").number_format = USD
        ws.cell(r, 11, f"=E{r}-J{r}").number_format = USD
        for i in range(8, 12): ws.cell(r, i).font = blk
    last = 5 + len(assets); t = last + 1
    ws.cell(t, 1, "Total").font = bold
    for col in (5, 6, 8, 10, 11):
        L = chr(64 + col); c = ws.cell(t, col, f"=SUM({L}6:{L}{last})"); c.font = bold; c.number_format = USD
    for L, w in zip("ABCDEFGHIJK", [9, 40, 11, 14, 12, 12, 10, 16, 12, 15, 16]): ws.column_dimensions[L].width = w
    ws2 = wb.create_sheet("Next 12 months")
    ws2["A1"] = "Projected monthly depreciation, next 12 months from the as-of month ($)"; ws2["A1"].font = Font(name=F, bold=True, size=12)
    ws2.cell(3, 1, "Asset").font = white; ws2.cell(3, 1).fill = hdr
    for m in range(12):
        c = ws2.cell(3, 2 + m, f"=EDATE(Assets!$C$3,{m})"); c.number_format = "mmm-yy"; c.font = white; c.fill = hdr
    for k in range(len(assets)):
        r = 4 + k; src = 6 + k
        ws2.cell(r, 1, f"=Assets!B{src}").font = Font(name=F, color="008000")
        for m in range(12):
            # months remaining after the as-of month = total - elapsed - m ; depreciate while > 0
            c = ws2.cell(r, 2 + m, f"=IF(Assets!$G{src}*12-Assets!$I{src}-{m}>0,Assets!$H{src},0)"); c.number_format = USD; c.font = blk
    tr = 4 + len(assets); ws2.cell(tr, 1, "Total").font = bold
    for m in range(12):
        L = chr(66 + m); c = ws2.cell(tr, 2 + m, f"=SUM({L}4:{L}{tr-1})"); c.number_format = USD; c.font = bold
    ws2.column_dimensions["A"].width = 40
    wb.save(path)

if __name__ == "__main__":
    s, m = build_db(); build_excel()
    print(len(s), "schedule rows;", len(m), "months"); print(m.head(3).to_string(index=False))
