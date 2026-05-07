from __future__ import annotations

from datetime import datetime

import requests
import streamlit as st

from config.settings import BACKEND_API_URL


TRANSCRIPT_ENDPOINT = f"{BACKEND_API_URL.rstrip('/')}/api/v1/transcripts/live"


def fetch_live_transcript() -> dict:
    try:
        response = requests.get(TRANSCRIPT_ENDPOINT, timeout=2)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        return {
            "count": 0,
            "latest": None,
            "text": "",
            "items": [],
            "error": str(exc),
        }


def clear_backend_transcript() -> bool:
    try:
        response = requests.delete(TRANSCRIPT_ENDPOINT, timeout=2)
        response.raise_for_status()
        return True
    except requests.RequestException:
        return False


st.title("Live Dispatch Test")

if "live_transcript" not in st.session_state:
    st.session_state.live_transcript = ""

if "call_status" not in st.session_state:
    st.session_state.call_status = "Active"

if "last_update" not in st.session_state:
    st.session_state.last_update = None

if "last_transcript_count" not in st.session_state:
    st.session_state.last_transcript_count = 0

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Current Call Transcript")

with col2:
    st.metric("Call Status", st.session_state.call_status)
    if st.session_state.last_update:
        st.caption(f"Last update: {st.session_state.last_update}")


@st.fragment(run_every="1s")
def refresh_transcript():
    data = fetch_live_transcript()

    if data.get("error"):
        st.warning(f"Backend connection issue: {data['error']}")
    else:
        count = data.get("count", 0)
        transcript_text = data.get("text", "")

        if count != st.session_state.last_transcript_count:
            st.session_state.live_transcript = transcript_text
            st.session_state.last_transcript_count = count
            st.session_state.last_update = datetime.now().strftime("%H:%M:%S")

    st.text_area(
        "Transcript",
        value=st.session_state.live_transcript,
        height=350,
        disabled=True,
        label_visibility="collapsed",
    )


refresh_transcript()

st.subheader("Call Details")

col_a, col_b = st.columns(2)

with col_a:
    st.text_input("Caller Name")
    st.text_input("Caller Phone")
    st.selectbox("Incident Type", ["Unknown", "Fire", "Smoke", "Rescue", "Other"])

with col_b:
    st.text_input("Location")
    st.selectbox("Status", ["Active", "Pending Review", "Finalized"])
    st.text_area("Dispatcher Notes", height=120)

col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("Finalize / Save Call", use_container_width=True):
        st.session_state.call_status = "Finalized"
        st.success("Call marked as finalized.")

with col_btn2:
    if st.button("Reset Test", use_container_width=True):
        if clear_backend_transcript():
            st.session_state.live_transcript = ""
            st.session_state.last_update = None
            st.session_state.last_transcript_count = 0
            st.info("Test reset.")
        else:
            st.error("Could not clear transcript from backend.")
