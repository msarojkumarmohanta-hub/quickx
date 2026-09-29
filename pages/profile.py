from __future__ import annotations

import streamlit as st


def render_profile(user):
    st.title("Profile")
    st.markdown(f"<div class='card'><h4>{user.name}</h4><p>Email: {user.email}</p><p>Role: {user.role}</p><p>Department: {user.department or 'General'}</p></div>", unsafe_allow_html=True)
    st.selectbox("Language", ["English", "Hindi", "Odia", "Bengali"])
    st.checkbox("Notifications")
    st.selectbox("Theme", ["Light", "Dark", "Campus Classic"])
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
