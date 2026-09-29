from __future__ import annotations

import streamlit as st

from database.database import SessionLocal
from database.models import Issue


def render_staff_dashboard(user):
    st.title("Staff Dashboard")
    session = SessionLocal()
    try:
        issues = session.query(Issue).all()
    finally:
        session.close()
    col1, col2, col3, col4 = st.columns(4)
    metrics = [
        ("Assigned Issues", len(issues)),
        ("Pending Verification", sum(1 for i in issues if i.status in {"SUBMITTED", "VERIFIED"})),
        ("High Priority", sum(1 for i in issues if i.priority in {"High", "Critical"})),
        ("Resolved Today", sum(1 for i in issues if i.status == "RESOLVED")),
    ]
    for col, (label, value) in zip(col1, metrics):
        col.markdown(f"<div class='metric-card'><div>{label}</div><h2>{value}</h2></div>", unsafe_allow_html=True)
    st.subheader("Issues to review")
    for issue in issues[:10]:
        st.markdown(f"- {issue.quickfix_id} — {issue.title} — {issue.status} — {issue.priority}")
        if st.button(f"Open {issue.quickfix_id}", key=f"staff_issue_{issue.id}"):
            st.session_state.selected_issue = issue.id
            st.session_state.current_page = "issue_details"
            st.rerun()
