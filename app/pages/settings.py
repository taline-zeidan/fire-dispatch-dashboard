from __future__ import annotations

import os
import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.markdown("## ⚙️ Settings")
st.caption("Configure bridge behavior and operator information.")

SETTINGS_URL = f"{BACKEND_URL}/api/v1/settings"


def get_settings() -> dict:
    try:
        resp = requests.get(SETTINGS_URL, timeout=5)
        if resp.status_code == 404:
            st.error(f"Settings endpoint not found: {SETTINGS_URL}")
            return {}
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        st.error(f"Could not load settings: {exc}")
        return {}


def save_settings(payload: dict) -> bool:
    try:
        resp = requests.put(SETTINGS_URL, json=payload, timeout=5)
        if resp.status_code == 404:
            st.error(f"Settings endpoint not found: {SETTINGS_URL}")
            return False
        resp.raise_for_status()
        return True
    except Exception as exc:
        st.error(f"Could not save settings: {exc}")
        return False


settings = get_settings()

performance = settings.get("performance", "moderate")
operator_name = settings.get("operator_name", "")

with st.form("settings_form"):
    selected_performance = st.radio(
        "Performance mode",
        options=["high", "moderate"],
        index=0 if performance == "high" else 1,
        help=(
            "High: streaming and offline Whisper may run in parallel. "
            "Moderate: streaming pauses while offline Whisper runs."
        ),
    )

    selected_operator = st.text_input(
        "Operator name",
        value=operator_name,
        placeholder="Enter dispatcher/operator name",
    )

    submitted = st.form_submit_button("Save settings", use_container_width=True)

if submitted:
    ok = save_settings(
        {
            "performance": selected_performance,
            "operator_name": selected_operator or None,
        }
    )

    if ok:
        st.success("Settings saved.")