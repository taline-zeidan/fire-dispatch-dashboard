import streamlit as st

st.title("Saved Calls")
st.caption("Search, filter, and review previous dispatch calls.")

calls = [
    {
        "call_id": "C-001",
        "time": "2026-03-09 09:10",
        "caller": "Unknown",
        "incident_type": "Fire",
        "location": "Main Street",
        "status": "Finalized",
        "notes": "Kitchen fire reported. Crew dispatched.",
    },
    {
        "call_id": "C-002",
        "time": "2026-03-09 09:35",
        "caller": "Sara",
        "incident_type": "Smoke",
        "location": "Green Avenue",
        "status": "Pending Review",
        "notes": "Smoke smell from apartment corridor.",
    },
    {
        "call_id": "C-003",
        "time": "2026-03-09 10:05",
        "caller": "Omar",
        "incident_type": "Rescue",
        "location": "Hill Road",
        "status": "Active",
        "notes": "Possible trapped resident.",
    },
    {
        "call_id": "C-004",
        "time": "2026-03-09 10:20",
        "caller": "Unknown",
        "incident_type": "Other",
        "location": "City Center",
        "status": "Finalized",
        "notes": "False alarm suspected.",
    },
]

#styling
st.markdown(
    """
    <style>
    .call-card {
        border-radius: 14px;
        padding: 16px 18px;
        margin-bottom: 14px;
        border-left: 10px solid #d1d5db;
        background-color: #f8f9fb;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }

    .call-card.red {
        border-left-color: #dc2626;
        background-color: #fef2f2;
    }

    .call-card.yellow {
        border-left-color: #ca8a04;
        background-color: #fefce8;
    }

    .call-card.green {
        border-left-color: #16a34a;
        background-color: #f0fdf4;
    }

    .call-card.gray {
        border-left-color: #9ca3af;
        background-color: #f9fafb;
    }

    .call-title {
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 6px;
    }

    .call-meta {
        font-size: 14px;
        margin-bottom: 4px;
    }

    .call-notes {
        font-size: 14px;
        margin-top: 10px;
    }

    .filter-box {
        padding: 10px 0 6px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

#filters
st.subheader("Search and Filter")

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    search_text = st.text_input(
        "Search",
        placeholder="Search by caller, location, call ID, or notes",
    )

with col2:
    incident_filter = st.selectbox(
        "Incident Type",
        ["All", "Fire", "Smoke", "Rescue", "Other"]
    )

with col3:
    status_filter = st.selectbox(
        "Status",
        ["All", "Active", "Pending Review", "Finalized"]
    )

#filtering logic
def matches_filters(call: dict) -> bool:
    query = search_text.strip().lower()

    text_match = (
        query == ""
        or query in call["call_id"].lower()
        or query in call["caller"].lower()
        or query in call["location"].lower()
        or query in call["notes"].lower()
        or query in call["incident_type"].lower()
    )

    incident_match = incident_filter == "All" or call["incident_type"] == incident_filter
    status_match = status_filter == "All" or call["status"] == status_filter

    return text_match and incident_match and status_match


filtered_calls = [call for call in calls if matches_filters(call)]

st.divider()
st.subheader(f"Results ({len(filtered_calls)})")

#card color mapping
def get_card_class(call: dict) -> str:
    if call["incident_type"] == "Fire":
        return "red"
    if call["incident_type"] == "Smoke":
        return "yellow"
    if call["status"] == "Finalized":
        return "green"
    return "gray"

#render cards
if not filtered_calls:
    st.info("No calls match the current search/filter settings.")
else:
    for call in filtered_calls:
        card_class = get_card_class(call)

        st.markdown(
            f"""
            <div class="call-card {card_class}">
                <div class="call-title">{call['call_id']} — {call['incident_type']}</div>
                <div class="call-meta"><b>Time:</b> {call['time']}</div>
                <div class="call-meta"><b>Caller:</b> {call['caller']}</div>
                <div class="call-meta"><b>Location:</b> {call['location']}</div>
                <div class="call-meta"><b>Status:</b> {call['status']}</div>
                <div class="call-notes"><b>Notes:</b> {call['notes']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )