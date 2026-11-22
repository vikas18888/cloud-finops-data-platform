"""Day 20: draw docs/architecture.png (matplotlib; no external tools needed)."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

DARK, MID, ACC, BG, INK = "#0B3C49", "#1F6F78", "#F2A541", "#F6F3EC", "#1B2B30"
fig, ax = plt.subplots(figsize=(13, 6.6), facecolor=BG); ax.set_xlim(0, 13); ax.set_ylim(0, 6.6); ax.axis("off")

def box(x, y, w, h, title, sub="", fc=MID, tc="white"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12", fc=fc, ec="none"))
    ax.text(x + w / 2, y + h * (0.62 if sub else 0.5), title, ha="center", va="center", color=tc, fontsize=10, fontweight="bold")
    if sub: ax.text(x + w / 2, y + h * 0.28, sub, ha="center", va="center", color=tc, fontsize=7.5)
def arrow(x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=14, color=INK, lw=1.3))
def lane(x, label):
    ax.text(x, 6.3, label, fontsize=10, fontweight="bold", color=DARK)

ax.text(0.3, 6.55, "", fontsize=1)
lane(0.3, "1. SOURCES"); lane(3.0, "2. INGEST + QUALITY"); lane(6.0, "3. WAREHOUSE"); lane(9.0, "4. ANALYTICS + ACTION")
box(0.3, 4.6, 2.2, 1.0, "Billing logs", "CSV + JSONL (CUR-style)", fc="white", tc=INK)
box(0.3, 3.3, 2.2, 1.0, "Business metrics", "requests, customers", fc="white", tc=INK)
box(0.3, 2.0, 2.2, 1.0, "Asset + K8s + S3", "inventory, usage, objects", fc="white", tc=INK)
box(3.0, 4.6, 2.5, 1.0, "ingest_billing.py", "clean, dedupe, parse dates")
box(3.0, 3.3, 2.5, 1.0, "validate_data.py", "quality checks + quarantine", fc=ACC, tc=INK)
box(3.0, 2.0, 2.5, 1.0, "reconcile.py", "row counts + checksums", fc=ACC, tc=INK)
box(6.0, 4.0, 2.4, 1.4, "Star schema", "fact_cost + 5 dimensions\nSQLite / Postgres", fc=DARK)
box(6.0, 2.0, 2.4, 1.2, "Cloud DW", "BigQuery / Snowflake\npartitioned + clustered", fc=MID)
box(9.0, 4.9, 3.7, 0.75, "Unit economics, tagging, rate model", "", fc=MID)
box(9.0, 3.95, 3.7, 0.75, "Anomaly engine  ->  webhook alerts", "", fc=MID)
box(9.0, 3.0, 3.7, 0.75, "K8s right-sizing, storage tiering", "", fc=MID)
box(9.0, 2.05, 3.7, 0.75, "Dashboard + PDF executive view", "", fc=DARK)
box(3.0, 0.4, 9.7, 0.9, "ORCHESTRATION: Apache Airflow DAG (finops_pipeline_dag.py), daily at 06:00", "ingest -> validate -> load -> reconcile -> (unit economics || anomalies)", fc="white", tc=INK)
ax.add_patch(FancyBboxPatch((0.3, 0.4), 2.2, 0.9, boxstyle="round,pad=0.02,rounding_size=0.12", fc="white", ec="none"))
ax.text(1.4, 0.85, "CI/CD: Terraform +\nInfracost on every PR", ha="center", va="center", fontsize=8.5, color=INK, fontweight="bold")
for y in (5.1, 3.8): arrow(2.5, y, 3.0, y)
arrow(2.5, 2.5, 3.0, 2.5)
arrow(5.5, 5.1, 6.0, 4.9); arrow(5.5, 3.8, 6.0, 4.4); arrow(5.5, 2.5, 6.0, 4.1)
arrow(7.2, 4.0, 7.2, 3.2)
arrow(8.4, 4.7, 9.0, 5.2); arrow(8.4, 4.5, 9.0, 4.3); arrow(8.4, 4.3, 9.0, 3.4); arrow(8.4, 4.1, 9.0, 2.5)
fig.savefig("docs/architecture.png", dpi=130, facecolor=BG, bbox_inches="tight"); print("saved docs/architecture.png")
