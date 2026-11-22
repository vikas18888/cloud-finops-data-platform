"""Day 18: export the executive dashboard view as a one-page PDF (same KPIs as dashboard/app.py)."""
import sys
sys.path.insert(0, "src")
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import metrics, anomaly_engine

DARK, MID, ACC, BG = "#0B3C49", "#1F6F78", "#F2A541", "#F6F3EC"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False})

def main(out="outputs/Day18_Executive_View.pdf"):
    k = metrics.kpis(); daily = metrics.daily_cost(); fc, fv = metrics.forecast_variance(daily)
    cat = metrics.by_category(); uc = metrics.unit_cost_monthly(); anomalies = anomaly_engine.run(notify=False)
    fig = plt.figure(figsize=(11.69, 8.27), facecolor=BG)
    fig.text(0.04, 0.94, "Cloud FinOps - Executive View", fontsize=20, fontweight="bold", color=DARK)
    fig.text(0.04, 0.905, "Synthetic AWS-style billing data, 90 days (2026-08-01 to 2026-10-29)", fontsize=9, color="#5B6B70")
    tiles = [("Total spend (90d)", f"${k['total_spend']:,.0f}"),
             ("Last 30 days", f"${k['last_30d']:,.0f}", f"{100*(k['last_30d']/k['prev_30d']-1):+.1f}% vs prior 30d"),
             ("Cost per 1k API requests", f"${k['cost_per_1k_last']:.2f}", f"{100*(k['cost_per_1k_last']/k['cost_per_1k_first']-1):+.1f}% since Aug"),
             ("Commitment coverage (modelled)", f"{100*k['coverage_modelled']:.0f}%", "current: 0% (no RIs in data)")]
    for i, t in enumerate(tiles):
        x = 0.04 + i * 0.235
        fig.patches.append(plt.Rectangle((x, 0.78), 0.215, 0.1, transform=fig.transFigure, facecolor="white", edgecolor="#E2DDD0"))
        fig.text(x + 0.012, 0.855, t[0], fontsize=8, color="#5B6B70")
        fig.text(x + 0.012, 0.805, t[1], fontsize=17, fontweight="bold", color=DARK)
        if len(t) > 2: fig.text(x + 0.012, 0.787, t[2], fontsize=7.5, color="#B5651D")
    ax = fig.add_axes([0.06, 0.43, 0.56, 0.30]); ax.set_facecolor(BG)
    ax.plot(fc.date, fc.cost, color=MID, lw=1.6, label="Actual"); ax.plot(fc.date, fc.forecast, color=ACC, lw=1.6, ls="--", label="Linear forecast (fit on first 60d)")
    ax.axvline(fc.date.iloc[60], color="#999", lw=0.8, ls=":"); ax.set_title("Daily spend vs forecast (USD)", loc="left", fontsize=10, color=DARK, fontweight="bold")
    ax.legend(frameon=False, fontsize=8, loc="upper left"); ax.tick_params(labelsize=8)
    v = fv["variance_usd"]; ax.set_xlabel(f"Last-30d variance vs forecast: {'-' if v < 0 else '+'}\\${abs(v):,.0f} ({100*fv['variance_pct']:+.1f}%), MAPE {100*fv['mape']:.0f}%", fontsize=8, color="#5B6B70", loc="left")
    ax2 = fig.add_axes([0.70, 0.43, 0.26, 0.30]); ax2.set_facecolor(BG)
    ax2.barh(cat.category[::-1], cat.cost[::-1], color=MID); ax2.set_title("Spend by category (USD)", loc="left", fontsize=10, color=DARK, fontweight="bold"); ax2.tick_params(labelsize=8)
    for i, v in enumerate(cat.cost[::-1]): ax2.text(v, i, f" \\${v:,.0f}", va="center", fontsize=8)
    ax2.set_xlim(0, cat.cost.max() * 1.3); ax2.set_xticks([])
    ax3 = fig.add_axes([0.06, 0.07, 0.30, 0.27]); ax3.set_facecolor(BG)
    ax3.bar(uc.month, uc.cost_per_1k_requests, color=ACC, width=0.5); ax3.set_title("Cost per 1,000 API requests (USD)", loc="left", fontsize=10, color=DARK, fontweight="bold"); ax3.tick_params(labelsize=8)
    for i, v in enumerate(uc.cost_per_1k_requests): ax3.text(i, v, f"\\${v:.2f}", ha="center", va="bottom", fontsize=8)
    ax3.set_ylim(0, uc.cost_per_1k_requests.max() * 1.2)
    fig.text(0.44, 0.33, "Anomaly alerts", fontsize=10, fontweight="bold", color=DARK)
    for i, a in enumerate(anomalies[:6]):
        col = "#B22222" if a["severity"] == "HIGH" else "#5B6B70"
        fig.text(0.44, 0.30 - i * 0.04, f"[{a['severity']}] {a['date']}  {a['service']}: \\${a['cost']:,.0f} vs \\${a['expected']:,.0f} expected (z={a['z']:.1f})", fontsize=8.5, color=col)
    fig.text(0.04, 0.02, "Commitment coverage is modelled from the Day 11 recommendation. Forecast is a simple linear trend; spikes inflate error. Data is synthetic.", fontsize=7, color="#5B6B70")
    fig.savefig(out, facecolor=BG); print("saved", out)

if __name__ == "__main__":
    main()
