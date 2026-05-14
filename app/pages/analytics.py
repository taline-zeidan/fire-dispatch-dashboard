"""Analytics — incident statistics from live database data."""
from __future__ import annotations

import os
from collections import Counter
from datetime import datetime

import pandas as pd
import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    }

    [data-testid="stAppViewContainer"] {
        background: #f7f8fa;
    }

    [data-testid="stHeader"] {
        background: rgba(247, 248, 250, 0.85);
        backdrop-filter: blur(10px);
    }

    [data-testid="stStatusWidget"] {
        visibility: hidden;
        height: 0;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .page-title {
        font-size: 2rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 0.25rem;
    }

    .page-subtitle {
        color: #6b7280;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }

    .metric-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 1.2rem 1.3rem;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
    }

    .metric-label {
        color: #6b7280;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 0.45rem;
    }

    .metric-val {
        color: #111827;
        font-size: 2.25rem;
        font-weight: 700;
        line-height: 1;
    }

    .section-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 1.15rem 1.25rem;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
        margin-top: 1rem;
    }

    .section-title {
        font-size: 1rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 0.85rem;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid #e5e7eb;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="page-title">Analytics</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-subtitle">Operational overview based on live incident records.</div>',
    unsafe_allow_html=True,
)


@st.cache_data(ttl=60)
def fetch_incidents() -> list[dict]:
    try:
        resp = requests.get(f"{BACKEND_URL}/api/v1/incidents", timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return []


header_left, header_right = st.columns([4, 1])
with header_right:
    if st.button("Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

incidents = fetch_incidents()

if not incidents:
    st.info("No incidents in the database yet.")
    st.stop()

for inc in incidents:
    try:
        inc["_dt"] = datetime.fromisoformat(inc["reported_at"].replace("Z", "+00:00"))
    except Exception:
        inc["_dt"] = None

years = sorted({inc["_dt"].year for inc in incidents if inc["_dt"]}, reverse=True)
selected_year = st.selectbox("Year", ["All"] + [str(y) for y in years], label_visibility="collapsed")

filtered = incidents
if selected_year != "All":
    filtered = [inc for inc in incidents if inc["_dt"] and inc["_dt"].year == int(selected_year)]

total = len(filtered)
by_status = Counter(inc.get("status", "unknown") for inc in filtered)
active = by_status.get("reported", 0) + by_status.get("dispatched", 0)
critical = sum(1 for inc in filtered if inc.get("priority") == "critical")

col1, col2, col3 = st.columns(3)
for col, val, label in [
    (col1, total, "Total incidents"),
    (col2, active, "Active / dispatched"),
    (col3, critical, "Critical priority"),
]:
    with col:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">{label}</div>'
            f'<div class="metric-val">{val}</div></div>',
            unsafe_allow_html=True,
        )

col_left, col_right = st.columns(2)

with col_left:
    st.markdown('<div class="section-card"><div class="section-title">Incidents by type</div>', unsafe_allow_html=True)
    type_counts: Counter = Counter()
    for inc in filtered:
        it = inc.get("incident_type")
        name = it.get("name", "Unknown") if it else "Unknown"
        type_counts[name] += 1

    if type_counts:
        df_type = pd.DataFrame(type_counts.items(), columns=["Type", "Count"]).sort_values("Count", ascending=False)
        st.bar_chart(df_type.set_index("Type"))
    else:
        st.info("No type data.")
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="section-card"><div class="section-title">Incidents by priority</div>', unsafe_allow_html=True)
    priority_counts: Counter = Counter(inc.get("priority", "unknown") for inc in filtered)
    if priority_counts:
        df_priority = pd.DataFrame(priority_counts.items(), columns=["Priority", "Count"])
        st.bar_chart(df_priority.set_index("Priority"))
    else:
        st.info("No priority data.")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-card"><div class="section-title">Monthly trend</div>', unsafe_allow_html=True)
monthly: Counter = Counter()
for inc in filtered:
    if inc["_dt"]:
        monthly[inc["_dt"].strftime("%Y-%m")] += 1

if monthly:
    df_monthly = pd.DataFrame(monthly.items(), columns=["Month", "Incidents"]).sort_values("Month")
    st.line_chart(df_monthly.set_index("Month"))
else:
    st.info("Not enough data for trend chart.")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-card"><div class="section-title">Status breakdown</div>', unsafe_allow_html=True)
df_status = pd.DataFrame(by_status.items(), columns=["Status", "Count"]).sort_values("Count", ascending=False)
st.dataframe(df_status, use_container_width=True, hide_index=True)
st.markdown('</div>', unsafe_allow_html=True)
