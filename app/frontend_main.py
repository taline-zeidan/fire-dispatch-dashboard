import streamlit as st

st.set_page_config(
    page_title="AURA — Civil Defence Dispatch",
    page_icon="🚒",
    layout="wide",
    initial_sidebar_state="expanded",
)

pages = [
    st.Page("pages/live_dispatch.py", title="Live Dispatch", icon="🎙️"),
    st.Page("pages/call_history.py", title="Call History", icon="📁"),
    st.Page("pages/analytics.py", title="Analytics", icon="📊"),
]

pg = st.navigation(pages, position="sidebar")
pg.run()
