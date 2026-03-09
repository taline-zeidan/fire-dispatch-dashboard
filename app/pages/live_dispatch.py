import streamlit as st
from datetime import datetime

FAKE_CHUNKS = [
    "Hello, there is a fire in the kitchen.",
    "The smoke is spreading fast.",
    "We are on the second floor.",
    "Please send help quickly."
]

def get_new_transcript_chunk() -> str:
    if "fake_index" not in st.session_state:
        st.session_state.fake_index = 0

    if st.session_state.fake_index < len(FAKE_CHUNKS):
        chunk = FAKE_CHUNKS[st.session_state.fake_index]
        st.session_state.fake_index += 1
        return chunk

    return ""


st.title("Live Dispatch Test")

if "live_transcript" not in st.session_state:
    st.session_state.live_transcript = ""

if "call_status" not in st.session_state:
    st.session_state.call_status = "Active"

if "last_update" not in st.session_state:
    st.session_state.last_update = None

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Current Call Transcript")

with col2:
    st.metric("Call Status", st.session_state.call_status)
    if st.session_state.last_update:
        st.caption(f"Last update: {st.session_state.last_update}")


@st.fragment(run_every="1s")
def refresh_transcript():
    new_chunk = get_new_transcript_chunk()

    if new_chunk and new_chunk.strip():
        if st.session_state.live_transcript:
            st.session_state.live_transcript += " " + new_chunk.strip()
        else:
            st.session_state.live_transcript = new_chunk.strip()

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
        st.session_state.live_transcript = ""
        st.session_state.last_update = None
        st.session_state.fake_index = 0
        st.info("Test reset.")