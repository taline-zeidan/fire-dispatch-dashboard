import streamlit as st

st.set_page_config(
    page_title="Fire Dispatch Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Optional shared session state defaults
if "live_transcript" not in st.session_state:
    st.session_state.live_transcript = ""

if "call_status" not in st.session_state:
    st.session_state.call_status = "Active"

pages = [
    st.Page("pages/live_dispatch.py", title="Live Transcript", icon="🎙️"),
    st.Page("pages/call_history.py", title="Call History", icon="📁"),
    st.Page("pages/analytics.py", title="Analytics", icon="📊"),
]

pg = st.navigation(pages, position="sidebar")
pg.run()