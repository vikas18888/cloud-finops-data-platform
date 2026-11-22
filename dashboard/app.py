"""Day 18: Executive FinOps dashboard (Streamlit). Run:  pip install streamlit  then  streamlit run dashboard/app.py
Uses the same KPI functions as the PDF export (src/metrics.py)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import pandas as pd
import streamlit as st
import metrics

st.set_page_config(page_title="Cloud FinOps Dashboard", layout="wide")
st.title("Cloud FinOps - Executive Dashboard")
st.caption("Synthetic AWS-style billing data, 90 days. Source: db/finops.db")

daily = metrics.daily_cost()
k = metrics.kpis()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total spend (90d)", f"${k['total_spend']:,.0f}")
c2.metric("Last 30 days", f"${k['last_30d']:,.0f}", f"{100 * (k['last_30d'] / k['prev_30d'] - 1):+.1f}% vs prior 30d", delta_color="inverse")
c3.metric("Cost per 1k API requests", f"${k['cost_per_1k_last']:.2f}", f"{100 * (k['cost_per_1k_last'] / k['cost_per_1k_first'] - 1):+.1f}% since first month", delta_color="inverse")
c4.metric("Commitment coverage (modelled)", f"{100 * k['coverage_modelled']:.0f}%")
c4.caption(f"Current: {100 * k['coverage_current']:.0f}% (no purchased RIs in the data)")

st.subheader("Daily spend vs linear forecast")
fc, fv = metrics.forecast_variance(daily)
st.pyplot(metrics.forecast_figure(fc))
st.write(f"Forecast fitted on first 60 days. Variance on last 30 days: **${fv['variance_usd']:,.0f} ({100 * fv['variance_pct']:+.1f}%)**, MAPE {100 * fv['mape']:.1f}%.")

left, right = st.columns(2)
with left:
    st.subheader("Spend by category")
    st.bar_chart(metrics.by_category().set_index("category"))
with right:
    st.subheader("Unit cost by month")
    st.line_chart(metrics.unit_cost_monthly().set_index("month")[["cost_per_1k_requests"]])

st.subheader("Anomaly alerts")
sys.path.insert(0, "src")
import anomaly_engine
found = anomaly_engine.run(notify=False)
if found:
    st.dataframe(pd.DataFrame(found)[["date", "service", "severity", "cost", "expected", "z"]].round(2), use_container_width=True)
st.caption("Commitment coverage is modelled from the Day 11 recommendation because the dataset contains no purchased RIs or Savings Plans.")
