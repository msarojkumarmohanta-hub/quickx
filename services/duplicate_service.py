from __future__ import annotations

from typing import List

from sqlalchemy import or_

from database.database import SessionLocal
from database.models import Issue


def find_duplicate_issues(title: str, description: str, category: str, location_text: str | None = None) -> List[dict]:
    text = (title or "") + " " + (description or "")
    keywords = [word.lower() for word in text.split() if len(word) > 3]
    session = SessionLocal()
    try:
        query = session.query(Issue)
        if category:
            query = query.filter(Issue.category_id.isnot(None))
        if location_text:
            query = query.filter(or_(Issue.location_text.ilike(f"%{location_text}%"), Issue.description.ilike(f"%{location_text}%")))

        issues = query.order_by(Issue.created_at.desc()).limit(30).all()
        matches = []
        for issue in issues:
            combined = (issue.title + " " + issue.description).lower()
            score = sum(1 for keyword in keywords if keyword in combined)
            if score > 0 or issue.category and issue.category.name == category:
                matches.append({
                    "id": issue.id,
                    "quickfix_id": issue.quickfix_id,
                    "title": issue.title,
                    "category": issue.category.name if issue.category else "Other",
                    "location": issue.location_text or "Unknown",
                    "status": issue.status,
                    "date": issue.created_at,
                    "score": score,
                })
        matches = sorted(matches, key=lambda item: item["score"], reverse=True)[:5]
        return matches
    finally:
        session.close()
