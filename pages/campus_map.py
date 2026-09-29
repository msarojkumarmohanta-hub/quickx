from __future__ import annotations

import streamlit as st


def render_campus_map(user):
    st.title("Campus Map")
    st.info("Map view is available when mapping libraries are present. Otherwise, the issue map is displayed using campus cards and filters.")
    col1, col2, col3 = st.columns(3)
    for col, label in zip([col1, col2, col3], ["Academic Block", "Library", "Hostel"]):
        col.markdown(f"<div class='card'><h4>{label}</h4><p>Open issues: 2</p><p>Priority alerts: 1</p></div>", unsafe_allow_html=True)
    st.selectbox("Filter", ["All", "Infrastructure", "Water", "Lighting", "Cleanliness", "Network", "Safety"])
