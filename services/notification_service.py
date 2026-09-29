from __future__ import annotations

from database.database import SessionLocal
from database.models import Notification


def add_notification(user_id: int, message: str, issue_id: int | None = None):
    session = SessionLocal()
    try:
        notification = Notification(user_id=user_id, issue_id=issue_id, message=message)
        session.add(notification)
        session.commit()
        return notification
    finally:
        session.close()


def get_notifications_for_user(user_id: int):
    session = SessionLocal()
    try:
        return session.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).all()
    finally:
        session.close()
