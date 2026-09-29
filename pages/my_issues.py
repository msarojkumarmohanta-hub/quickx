from __future__ import annotations

import streamlit as st

from database.database import SessionLocal
from database.models import Issue
from services.issue_service import get_issues_for_user


def render_my_issues(user):
    st.title("My Issues")
    status_filter = st.selectbox("Filter", ["All", "Submitted", "In Progress", "Resolved"])
    issues = get_issues_for_user(user.id)

    status_map = {
        "All": None,
        "Submitted": "SUBMITTED",
        "In Progress": "IN_PROGRESS",
        "Resolved": "RESOLVED",
    }
    target_status = status_map.get(status_filter)
    if target_status:
        filtered = [issue for issue in issues if issue.status == target_status]
    else:
        filtered = issues

    if not filtered:
        st.info("No issues found for the selected filter.")
        return

    for issue in filtered:
        with st.container():
            category_name = issue.ai_category or "Other"
            st.markdown(f"<div class='card'><b>{issue.quickfix_id}</b> • {issue.title}<br>{category_name} • {issue.location_text or 'Campus'}<br><span class='status-pill priority-{issue.priority.lower()}'>{issue.priority}</span> • {issue.status}</div>", unsafe_allow_html=True)
            if st.button(f"Open {issue.quickfix_id}", key=f"open_issue_{issue.id}"):
                st.session_state.selected_issue = issue.id
                st.session_state.current_page = "issue_details"
                st.rerun()
