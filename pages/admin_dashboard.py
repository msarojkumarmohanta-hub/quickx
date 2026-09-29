from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from database.database import SessionLocal
from database.models import Issue


def render_admin_dashboard(user):
    st.title("Admin Dashboard")
    session = SessionLocal()
    try:
        issues = session.query(Issue).all()
        if not issues:
            st.info("No issues in the system.")
            return
        df = pd.DataFrame([
            {
                "id": i.id,
                "status": i.status,
                "priority": i.priority,
                "category": i.category.name if i.category else "Other",
                "building": i.building.name if i.building else "Unknown",
                "created_at": i.created_at,
            }
            for i in issues
        ])
    finally:
        session.close()

    col1, col2, col3, col4, col5 = st.columns(5)
    metrics = [
        ("Total Issues", len(df)),
        ("Open", sum(1 for s in df["status"] if s not in {"RESOLVED", "CLOSED"})),
        ("In Progress", sum(1 for s in df["status"] if s == "IN_PROGRESS")),
        ("Resolved", sum(1 for s in df["status"] if s == "RESOLVED")),
        ("Critical", sum(1 for s in df["priority"] if s == "Critical")),
    ]
    for col, (label, value) in zip(col1, metrics):
        col.markdown(f"<div class='metric-card'><div>{label}</div><h2>{value}</h2></div>", unsafe_allow_html=True)

    st.subheader("Analytics")
    st.plotly_chart(px.pie(df, names="category", title="Issues by Category"), use_container_width=True)
    st.plotly_chart(px.bar(df, x="priority", title="Issues by Priority", color="priority"), use_container_width=True)
    st.plotly_chart(px.bar(df, x="status", title="Issues by Status", color="status"), use_container_width=True)
    st.plotly_chart(px.histogram(df, x="building", title="Issues by Building"), use_container_width=True)

    st.subheader("Issue Management")
    for _, row in df.head(10).iterrows():
        st.markdown(f"- {row['id']} — {row['category']} — {row['priority']} — {row['status']}")
