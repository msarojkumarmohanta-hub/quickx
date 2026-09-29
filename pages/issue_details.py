from __future__ import annotations

import streamlit as st

from database.database import SessionLocal
from database.models import Issue, IssueComment
from services.issue_service import add_comment, get_issue_comments, get_issue_status_history, update_issue_status


def render_issue_details(user):
    issue_id = st.session_state.get("selected_issue")
    if not issue_id:
        st.info("No issue selected.")
        return
    session = SessionLocal()
    try:
        issue = session.query(Issue).filter(Issue.id == issue_id).first()
        reporter_name = issue.user.name if issue and issue.user else "Unknown"
        category_name = issue.ai_category or "Other" if issue else "Other"
    finally:
        pass
    if not issue:
        st.warning("Issue not found.")
        return

    st.title(f"{issue.quickfix_id} • {issue.title}")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write("Category:", category_name)
        st.write("Description:", issue.description)
        st.write("Priority:", issue.priority)
        st.write("Location:", issue.location_text or "N/A")
        st.write("Status:", issue.status)
    with col2:
        st.write("Reported by:", reporter_name)
        st.write("Reported date:", issue.created_at)
        st.write("Assigned staff:", issue.assigned_staff_id or "Not assigned")

    st.subheader("Timeline")
    history = get_issue_status_history(issue.id)
    for entry in history:
        st.write(f"- {entry.created_at} • {entry.status} • {entry.note or 'No note'}")

    st.subheader("Comments")
    comments = get_issue_comments(issue.id)
    for comment in comments:
        st.write(f"- {comment.created_at} • {comment.comment}")

    new_comment = st.text_area("Add a comment")
    if st.button("Post Comment"):
        if new_comment:
            add_comment(issue.id, user.id, new_comment)
            st.success("Comment added.")
            st.rerun()

    if user.role in {"Maintenance Staff", "Administrator"}:
        st.subheader("Update Status")
        new_status = st.selectbox("Set status", ["SUBMITTED", "VERIFIED", "ASSIGNED", "IN_PROGRESS", "RESOLVED", "CLOSED"])
        note = st.text_input("Update note")
        if st.button("Apply Status Update"):
            update_issue_status(issue.id, new_status, note, user.id)
            st.success("Status updated.")
            st.rerun()

    session.close()
