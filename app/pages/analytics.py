import streamlit as st
import pandas as pd


st.title("Analytics")
st.caption("Placeholder analytics page.")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Calls", 24)

with col2:
    st.metric("Fire Calls", 10)

with col3:
    st.metric("Active Calls", 2)

incident_data = pd.DataFrame({
    "Incident Type": ["Fire", "Smoke", "Rescue", "Other"],
    "Count": [10, 6, 5, 3]
})

st.subheader("Calls by Incident Type")
st.bar_chart(incident_data.set_index("Incident Type"))