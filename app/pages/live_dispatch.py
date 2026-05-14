"""Live Dispatch — real-time transcript + post-call incident panel."""
from __future__ import annotations

import os

import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# If Streamlit runs in Docker and the bridge runs on your Windows host,
# use: BRIDGE_CONTROL_URL=http://host.docker.internal:5003
#
# If Streamlit and the bridge both run directly on Windows,
# use: BRIDGE_CONTROL_URL=http://localhost:5003
BRIDGE_CONTROL_URL = os.getenv(
    "BRIDGE_CONTROL_URL",
    "http://host.docker.internal:5003",
)

# ---------------------------------------------------------------------------
# Styling — old/simple dark dispatch look
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Noto+Naskh+Arabic:wght@400;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'IBM Plex Mono', monospace;
    }

    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 1100px;
    }

    .transcript-box {
        background: #0d0d0d;
        border: 1px solid #2a2a2a;
        border-radius: 4px;
        padding: 1.5rem;
        min-height: 160px;
        font-family: 'Noto Naskh Arabic', serif;
        font-size: 1.6rem;
        line-height: 1.8;
        color: #e8e8e8;
        direction: rtl;
        text-align: right;
        overflow-wrap: anywhere;
    }

    .detail-block {
        background: #0d0d0d;
        border: 1px solid #2a2a2a;
        border-radius: 4px;
        padding: 1rem 1.2rem;
        font-size: 0.9rem;
        color: #ccc;
        white-space: pre-wrap;
        direction: rtl;
        text-align: right;
    }

    .status-pill {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    .status-standby {
        background:#1a1a1a;
        color:#888;
        border:1px solid #444;
    }

    .status-process {
        background:#1a2a3a;
        color:#2196f3;
        border:1px solid #2196f3;
    }

    .status-ready {
        background:#2a1a1a;
        color:#ff5722;
        border:1px solid #ff5722;
    }

    .spinner-text {
        color:#888;
        font-size:0.85rem;
        animation: pulse 1.4s infinite;
    }

    @keyframes pulse {
        0%,100% { opacity:1 }
        50% { opacity:0.3 }
    }

    .bridge-warning {
        background: #1a1111;
        border: 1px solid #5f2a2a;
        color: #ffb4a8;
        border-radius: 6px;
        padding: 0.75rem 1rem;
        font-size: 0.85rem;
        margin-bottom: 1rem;
    }

    .bridge-success {
        background: #0f1a11;
        border: 1px solid #2f6b3c;
        color: #b7f7c2;
        border-radius: 6px;
        padding: 0.75rem 1rem;
        font-size: 0.85rem;
        margin-bottom: 1rem;
    }

    div.stButton > button {
        border-radius: 6px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("## 🎙️ Live Dispatch")

# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------

for key, default in [
    ("live_text", ""),
    ("incident_result", {}),
    ("form_submitted", False),
    ("end_call_sent", False),
    ("bridge_end_status", ""),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ---------------------------------------------------------------------------
# End Call / Reset
# ---------------------------------------------------------------------------

col_end, col_reset = st.columns([1, 1])

with col_end:
    if st.button("📵 End Call", use_container_width=True, type="primary"):
        try:
            bridge_resp = requests.post(
                f"{BRIDGE_CONTROL_URL}/end-call",
                timeout=5,
            )

            if bridge_resp.ok:
                st.session_state.bridge_end_status = "Bridge accepted end-call."
            else:
                st.session_state.bridge_end_status = (
                    f"Bridge returned HTTP {bridge_resp.status_code}: "
                    f"{bridge_resp.text}"
                )

        except Exception as exc:
            st.session_state.bridge_end_status = (
                f"Bridge control failed: {exc}. "
                f"Check BRIDGE_CONTROL_URL={BRIDGE_CONTROL_URL}"
            )

        # This only tells backend/frontend that processing has started.
        # The actual WAV finalization/offline Whisper trigger happens through port 5003.
        try:
            requests.post(
                f"{BACKEND_URL}/api/v1/transcripts/live/end",
                timeout=3,
            )
        except Exception:
            pass

        st.session_state.end_call_sent = True

with col_reset:
    if st.button("🔄 Reset", use_container_width=True):
        try:
            requests.delete(
                f"{BACKEND_URL}/api/v1/transcripts/live",
                timeout=3,
            )
        except Exception:
            pass

        st.session_state.live_text = ""
        st.session_state.incident_result = {}
        st.session_state.form_submitted = False
        st.session_state.end_call_sent = False
        st.session_state.bridge_end_status = ""

if st.session_state.bridge_end_status:
    if st.session_state.bridge_end_status.startswith("Bridge accepted"):
        st.markdown(
            f'<div class="bridge-success">{st.session_state.bridge_end_status}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="bridge-warning">{st.session_state.bridge_end_status}</div>',
            unsafe_allow_html=True,
        )

if st.session_state.end_call_sent and not st.session_state.incident_result.get("status"):
    st.info("Call ended — waiting for offline processing to start…")

st.markdown("---")

# ---------------------------------------------------------------------------
# Fragment: live transcript
# ---------------------------------------------------------------------------

st.markdown("### Live Transcript")


@st.fragment(run_every=1)
def live_transcript_fragment():
    try:
        resp = requests.get(
            f"{BACKEND_URL}/api/v1/transcripts/live",
            timeout=2,
        )
        if resp.ok:
            st.session_state.live_text = resp.json().get("text", "")
    except Exception:
        pass

    display = st.session_state.live_text or "Waiting for call…"
    st.markdown(
        f'<div class="transcript-box">{display}</div>',
        unsafe_allow_html=True,
    )


live_transcript_fragment()

st.markdown("---")

# ---------------------------------------------------------------------------
# Fragment: incident panel
# ---------------------------------------------------------------------------

st.markdown("### Post-Call Incident Panel")


@st.fragment(run_every=2)
def incident_panel_fragment():
    try:
        resp = requests.get(
            f"{BACKEND_URL}/api/v1/transcripts/live/incident",
            timeout=3,
        )
        if resp.ok:
            data = resp.json()
            if data:
                st.session_state.incident_result = data
    except Exception:
        pass

    result = st.session_state.incident_result

    if not result:
        st.markdown(
            '<span class="status-pill status-standby">STANDBY</span> '
            "Incident data appears here when a call ends.",
            unsafe_allow_html=True,
        )
        return

    status = result.get("status", "")

    if status == "processing":
        st.markdown(
            '<span class="status-pill status-process">PROCESSING</span>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="spinner-text">⠿ Cleaning transcript · Localizing · Generating record…</p>',
            unsafe_allow_html=True,
        )
        return

    if status == "error":
        st.error(f"Pipeline error: {result.get('detail', 'unknown')}")
        return

    if status != "ready":
        return

    st.markdown(
        '<span class="status-pill status-ready">READY</span> '
        "Review and submit the incident record below.",
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------------------------
    # Audio playback
    # -----------------------------------------------------------------------

    recording_path = result.get("recording_path")
    if recording_path:
        filename = recording_path.split("\\")[-1].split("/")[-1]
        audio_url = f"{BACKEND_URL}/api/v1/transcripts/audio/{filename}"

        st.markdown("#### 🎙️ Call Recording")

        try:
            audio_resp = requests.get(audio_url, timeout=5)
            if audio_resp.ok:
                st.audio(audio_resp.content, format="audio/wav")
            else:
                st.caption(f"Recording not available. HTTP {audio_resp.status_code}")
        except Exception as exc:
            st.caption(f"Could not load recording: {exc}")

    # -----------------------------------------------------------------------
    # Map / localization
    # -----------------------------------------------------------------------

    loc = result.get("localization", {})
    lat = loc.get("latitude")
    lon = loc.get("longitude")

    if lat and lon:
        st.markdown("#### 📍 Incident Location")
        st.caption(
            f"{loc.get('location_normalized', '')} — "
            f"confidence: {loc.get('confidence', '?')}"
        )

        try:
            import folium
            from streamlit_folium import st_folium

            m = folium.Map(location=[lat, lon], zoom_start=14)
            folium.Marker(
                [lat, lon],
                popup=loc.get("location_normalized", "Incident"),
                icon=folium.Icon(color="red", icon="fire", prefix="fa"),
            ).add_to(m)

            st_folium(m, width=700, height=350, key="live_map")

        except ImportError:
            st.info(
                f"Map: {lat:.5f}, {lon:.5f} — install streamlit-folium for map display"
            )
    else:
        st.warning("No coordinates returned by localization agent.")

    # -----------------------------------------------------------------------
    # Editable record form
    # -----------------------------------------------------------------------

    st.markdown("#### 📋 Incident Record")

    if st.session_state.form_submitted:
        st.success("Record submitted to database.")
        return

    incident = result.get("incident", {})
    record = result.get("record", {})
    call_data = record.get("call", {})

    with st.form("incident_form"):
        col1, col2 = st.columns(2)

        with col1:
            caller_name = st.text_input(
                "Caller Name",
                value=incident.get("caller_name") or "",
            )
            caller_phone = st.text_input(
                "Caller Phone",
                value=call_data.get("caller_phone") or incident.get("caller_phone") or "",
            )
            address = st.text_input(
                "Address",
                value=incident.get("address") or "",
            )

        with col2:
            priority_opts = ["low", "medium", "high", "critical"]
            cur_priority = incident.get("priority") or "medium"
            pri_idx = priority_opts.index(cur_priority) if cur_priority in priority_opts else 1

            priority = st.selectbox(
                "Priority",
                priority_opts,
                index=pri_idx,
            )

            status_val = st.selectbox(
                "Status",
                ["reported", "dispatched", "resolved"],
            )

            description = st.text_area(
                "Description",
                value=incident.get("description") or "",
                height=100,
            )

        st.markdown("**Cleaned Transcript**")
        st.text_area(
            "cleaned",
            value=result.get("cleaned_transcript", ""),
            height=100,
            disabled=True,
            label_visibility="collapsed",
        )

        submitted = st.form_submit_button(
            "Submit to Database",
            use_container_width=True,
        )

    if submitted:
        try:
            patch_resp = requests.patch(
                f"{BACKEND_URL}/api/v1/incidents/{incident['id']}",
                json={
                    "caller_name": caller_name or None,
                    "caller_phone": caller_phone or None,
                    "address": address or None,
                    "priority": priority,
                    "status": status_val,
                    "description": description or None,
                },
                timeout=5,
            )

            if patch_resp.ok:
                st.session_state.form_submitted = True
            else:
                st.error(f"Failed to update: {patch_resp.text}")

        except Exception as exc:
            st.error(f"Request failed: {exc}")


incident_panel_fragment()