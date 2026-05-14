from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="Civil Defense Dispatch",
    page_icon="🚒",
    layout="wide",
)

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] { border-right: 1px solid rgba(148, 163, 184, 0.18); }
    .block-container { padding-top: 1.5rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

pages = [
    st.Page("pages/live_dispatch.py", title="Live Dispatch", icon="🎙️"),
    st.Page("pages/call_history.py", title="Call History", icon="📁"),
    st.Page("pages/analytics.py", title="Analytics", icon="📊"),
    st.Page("pages/settings.py", title="Settings", icon="⚙️"),
]

pg = st.navigation(pages)
pg.run()
