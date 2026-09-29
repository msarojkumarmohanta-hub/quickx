from __future__ import annotations

import streamlit as st
import plotly.express as px

from database.database import SessionLocal
from database.models import Issue, IssueCategory
from services.notification_service import get_notifications_for_user
from utils.helpers import pretty_date


def get_issue_metrics():
    session = SessionLocal()
    try:
        issues = session.query(Issue).all()
        total = len(issues)
        open_issues = sum(1 for i in issues if i.status not in {"RESOLVED", "CLOSED"})
        in_progress = sum(1 for i in issues if i.status == "IN_PROGRESS")
        resolved = sum(1 for i in issues if i.status == "RESOLVED")
        return total, open_issues, in_progress, resolved
    finally:
        session.close()


def render_home(user):
    st.title(f"Good morning, {user.name}")
    st.caption("Help us keep your campus safe, clean and connected.")

    if st.button("🚨 Report an Issue", use_container_width=True):
        st.session_state.current_page = "report_issue"
        st.rerun()

    total, open_issues, in_progress, resolved = get_issue_metrics()
    cards = [
        ("Total Reports", total, "#2f5bff"),
        ("Open Issues", open_issues, "#ffb703"),
        ("In Progress", in_progress, "#22c55e"),
        ("Resolved", resolved, "#16a34a"),
    ]
    cols = st.columns(4)
    for col, (label, value, color) in zip(cols, cards):
        col.markdown(
            f"<div class='metric-card'><div style='color:{color}; font-size:0.8rem;'>{label}</div><h2>{value}</h2></div>",
            unsafe_allow_html=True,
        )

    st.markdown("### Campus Health")
    session = SessionLocal()
    try:
        categories = session.query(IssueCategory).all()
        issue_map = {}
        issues = session.query(Issue).all()
        for category in categories:
            issue_map[category.name] = sum(1 for i in issues if i.category and i.category.name == category.name)
    finally:
        session.close()

    health_cards = [
        ("💡 Lighting", issue_map.get("Lighting", 0)),
        ("💧 Water", issue_map.get("Water Leakage", 0)),
        ("🧹 Cleanliness", issue_map.get("Cleanliness", 0)),
        ("🏗 Infrastructure", issue_map.get("Infrastructure", 0)),
        ("📶 Network", issue_map.get("Network/Wi-Fi", 0)),
    ]
    health_cols = st.columns(len(health_cards))
    for col, (label, value) in zip(health_cols, health_cards):
        col.markdown(f"<div class='card'><h5>{label}</h5><h3>{value}</h3></div>", unsafe_allow_html=True)

    st.markdown("### Recent Reports")
    session = SessionLocal()
    try:
        recent = session.query(Issue).order_by(Issue.created_at.desc()).limit(6).all()
        if recent:
            for issue in recent:
                category_name = issue.ai_category or "Other"
                st.markdown(
                    f"<div class='card'><b>{issue.quickfix_id}</b> • {issue.title}<br>{category_name} • {issue.location_text or 'Campus'} • {issue.status}</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.info("No reports found yet.")
    finally:
        session.close()

    st.markdown("### High Priority Issues")
    session = SessionLocal()
    try:
        high = session.query(Issue).filter(Issue.priority.in_(["High", "Critical"])).limit(5).all()
        if high:
            for issue in high:
                st.markdown(f"- {issue.quickfix_id} — {issue.title} — {issue.priority}")
        else:
            st.info("No high-priority issues.")
    finally:
        session.close()

    st.markdown("### Nearby Issues")
    st.info("Location-aware issues are highlighted here when campus data is available.")

    st.markdown("### Campus Announcement")
    st.info("Campus maintenance team is scheduled for lighting and plumbing checks today.")

    st.markdown("### Analytics")
    session = SessionLocal()
    try:
        issues = session.query(Issue).all()
        counts = {"Submitted": 0, "In Progress": 0, "Resolved": 0}
        for issue in issues:
            counts[issue.status] = counts.get(issue.status, 0) + 1
        fig = px.bar(x=list(counts.keys()), y=list(counts.values()), title="Issue Status Overview")
        st.plotly_chart(fig, use_container_width=True)
    finally:
        session.close()
