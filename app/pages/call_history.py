"""Call History — browse and search past incidents."""
from __future__ import annotations

import os

import pandas as pd
import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Naskh+Arabic:wght@400;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    }

    [data-testid="stAppViewContainer"] { background: #f7f8fa; }
    [data-testid="stHeader"] { background: rgba(247,248,250,0.85); backdrop-filter: blur(10px); }
    [data-testid="stStatusWidget"] { visibility: hidden; height: 0; }

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

    .panel {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 1.2rem 1.25rem;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
        margin-top: 1rem;
    }

    .panel-title {
        font-size: 1rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 0.75rem;
    }

    .detail-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.8rem;
        margin-bottom: 1rem;
    }

    .detail-item {
        background: #f9fafb;
        border: 1px solid #eef0f3;
        border-radius: 12px;
        padding: 0.85rem 0.95rem;
    }

    .detail-label {
        color: #6b7280;
        font-size: 0.72rem;
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 0.04em;
        margin-bottom: 0.25rem;
    }

    .detail-value {
        color: #111827;
        font-size: 0.92rem;
        font-weight: 500;
    }

    .transcript-block {
        background: #fbfbfc;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 1rem 1.1rem;
        color: #1f2937;
        white-space: pre-wrap;
        direction: rtl;
        text-align: right;
        font-family: 'Noto Naskh Arabic', serif;
        font-size: 1.1rem;
        line-height: 1.8;
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

st.markdown('<div class="page-title">Call History</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Search, review, and inspect archived incident records.</div>', unsafe_allow_html=True)


@st.cache_data(ttl=30)
def fetch_incidents() -> list[dict]:
    try:
        resp = requests.get(f"{BACKEND_URL}/api/v1/incidents", timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        st.error(f"Could not load incidents: {exc}")
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

rows = []
for inc in incidents:
    incident_type = ""
    if inc.get("incident_type"):
        incident_type = inc["incident_type"].get("name", "")

    rows.append(
        {
            "ID": inc["id"],
            "Type": incident_type or str(inc.get("incident_type_id", "")),
            "Status": inc.get("status", ""),
            "Priority": inc.get("priority", ""),
            "Address": inc.get("address", ""),
            "Caller": inc.get("caller_name", ""),
            "Reported At": inc.get("reported_at", "")[:16].replace("T", " "),
        }
    )

df = pd.DataFrame(rows)

st.markdown('<div class="panel"><div class="panel-title">Incident records</div>', unsafe_allow_html=True)
search = st.text_input("Search by address, caller, or type", placeholder="e.g. Tripoli, Forest Fire…")
if search:
    mask = df.apply(lambda col: col.astype(str).str.contains(search, case=False, na=False)).any(axis=1)
    df = df[mask]

st.dataframe(df, use_container_width=True, hide_index=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="panel"><div class="panel-title">Incident detail</div>', unsafe_allow_html=True)
incident_ids = [str(inc["id"]) for inc in incidents]
selected_id = st.selectbox("Select Incident ID", incident_ids)

if selected_id:
    selected = next((inc for inc in incidents if str(inc["id"]) == selected_id), None)
    if selected:
        lat = selected.get("latitude")
        lon = selected.get("longitude")
        st.markdown(
            f"""
            <div class="detail-grid">
                <div class="detail-item"><div class="detail-label">ID</div><div class="detail-value">{selected.get('id', '')}</div></div>
                <div class="detail-item"><div class="detail-label">Status</div><div class="detail-value">{selected.get('status', '')}</div></div>
                <div class="detail-item"><div class="detail-label">Priority</div><div class="detail-value">{selected.get('priority', '')}</div></div>
                <div class="detail-item"><div class="detail-label">Reported at</div><div class="detail-value">{selected.get('reported_at', '')}</div></div>
                <div class="detail-item"><div class="detail-label">Address</div><div class="detail-value">{selected.get('address', '') or '—'}</div></div>
                <div class="detail-item"><div class="detail-label">Caller</div><div class="detail-value">{selected.get('caller_name', '') or '—'} · {selected.get('caller_phone', '') or '—'}</div></div>
                <div class="detail-item"><div class="detail-label">Coordinates</div><div class="detail-value">{lat}, {lon}</div></div>
                <div class="detail-item"><div class="detail-label">Description</div><div class="detail-value">{selected.get('description', '') or '—'}</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if lat and lon:
            try:
                import folium
                from streamlit_folium import st_folium

                m = folium.Map(location=[lat, lon], zoom_start=14)
                folium.Marker(
                    [lat, lon],
                    popup=selected.get("address", "Incident"),
                    icon=folium.Icon(color="red", icon="fire", prefix="fa"),
                ).add_to(m)
                st_folium(m, width=700, height=300)
            except ImportError:
                st.caption("Install streamlit-folium to see the map.")

        transcript = selected.get("whisper_transcript")
        if transcript:
            st.markdown('<div class="panel-title">Transcript</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="transcript-block">{transcript}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
