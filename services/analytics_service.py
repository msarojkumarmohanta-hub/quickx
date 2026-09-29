from __future__ import annotations

from datetime import datetime

import pandas as pd

from database.database import SessionLocal
from database.models import Issue, IssueCategory


def get_analytics_summary():
    session = SessionLocal()
    try:
        issues = session.query(Issue).all()
        df = pd.DataFrame([
            {
                "id": i.id,
                "status": i.status,
                "priority": i.priority,
                "category": i.category.name if i.category else "Other",
                "building": i.building.name if i.building else "Unknown",
                "created_at": i.created_at,
                "updated_at": i.updated_at,
            }
            for i in issues
        ])
        return df
    finally:
        session.close()


def get_category_counts(df):
    if df.empty:
        return pd.DataFrame(columns=["category", "count"])
    return df.groupby("category").size().reset_index(name="count")


def get_priority_counts(df):
    if df.empty:
        return pd.DataFrame(columns=["priority", "count"])
    return df.groupby("priority").size().reset_index(name="count")


def get_status_counts(df):
    if df.empty:
        return pd.DataFrame(columns=["status", "count"])
    return df.groupby("status").size().reset_index(name="count")


def get_building_counts(df):
    if df.empty:
        return pd.DataFrame(columns=["building", "count"])
    return df.groupby("building").size().reset_index(name="count")


def get_resolution_time_days(df):
    if df.empty:
        return 0
    times = []
    for _, row in df.iterrows():
        if row.get("status") == "RESOLVED":
            created = row.get("created_at")
            updated = row.get("updated_at")
            if created and updated:
                delta = updated - created
                times.append(delta.total_seconds() / 86400)
    return round(sum(times) / len(times), 2) if times else 0
