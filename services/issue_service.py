from __future__ import annotations

from datetime import datetime
from pathlib import Path

from sqlalchemy import desc

from database.database import SessionLocal
from database.models import Issue, IssueComment, IssueImage, IssueStatusHistory, Notification, User
from services.ai_service import analyze_issue
from services.duplicate_service import find_duplicate_issues


def save_issue_images(issue_id: int, uploaded_files):
    saved_paths = []
    if not uploaded_files:
        return saved_paths
    upload_dir = Path(__file__).resolve().parents[1] / "uploads"
    upload_dir.mkdir(exist_ok=True)

    for uploaded in uploaded_files if isinstance(uploaded_files, list) else [uploaded_files]:
        if uploaded is None:
            continue
        file_name = f"{issue_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}_{Path(uploaded.name).name}"
        safe_name = file_name.replace('..', '')
        save_path = upload_dir / safe_name
        with open(save_path, "wb") as f:
            f.write(uploaded.getvalue())
        saved_paths.append(str(save_path))

    session = SessionLocal()
    try:
        for path in saved_paths:
            session.add(IssueImage(issue_id=issue_id, image_path=path))
        session.commit()
    finally:
        session.close()
    return saved_paths


def create_issue_record(report_data: dict):
    session = SessionLocal()
    try:
        issue_count = session.query(Issue).count() + 1
        quickfix_id = f"QF-{datetime.utcnow().strftime('%Y')}-{issue_count:06d}"
        analysis = analyze_issue(report_data.get("title", ""), report_data.get("description", ""), report_data.get("category"))
        issue = Issue(
            quickfix_id=quickfix_id,
            title=report_data.get("title", "Untitled Issue"),
            description=report_data.get("description", "No description provided."),
            category_id=report_data.get("category_id"),
            campus_id=report_data.get("campus_id"),
            building_id=report_data.get("building_id"),
            location_id=report_data.get("location_id"),
            user_id=report_data.get("user_id"),
            assigned_staff_id=report_data.get("assigned_staff_id"),
            status="SUBMITTED",
            priority=report_data.get("priority", analysis["priority"]),
            smart_priority=analysis["priority"],
            severity=analysis["severity"],
            ai_category=analysis["category"],
            location_text=report_data.get("location_text"),
            qr_code=report_data.get("qr_code"),
            latitude=report_data.get("latitude"),
            longitude=report_data.get("longitude"),
        )
        session.add(issue)
        session.commit()
        session.refresh(issue)
        session.expunge(issue)

        history = IssueStatusHistory(issue_id=issue.id, status="SUBMITTED", note="Issue submitted by user")
        session.add(history)

        if report_data.get("user_id"):
            message = f"Your issue {issue.quickfix_id} has been submitted successfully."
            session.add(Notification(user_id=report_data["user_id"], issue_id=issue.id, message=message))

        session.commit()
        return issue
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_issue_by_id(issue_id: int):
    session = SessionLocal()
    try:
        return session.query(Issue).filter(Issue.id == issue_id).first()
    finally:
        session.close()


def get_issues_for_user(user_id: int):
    session = SessionLocal()
    try:
        issues = session.query(Issue).filter(Issue.user_id == user_id).order_by(desc(Issue.created_at)).all()
        session.expunge_all()
        return issues
    finally:
        session.close()


def get_all_issues():
    session = SessionLocal()
    try:
        return session.query(Issue).order_by(desc(Issue.created_at)).all()
    finally:
        session.close()


def get_unread_notification_count(user_id: int):
    session = SessionLocal()
    try:
        return session.query(Notification).filter(Notification.user_id == user_id, Notification.is_read == False).count()
    finally:
        session.close()


def update_issue_status(issue_id: int, new_status: str, note: str = "", changed_by_user_id: int | None = None):
    session = SessionLocal()
    try:
        issue = session.query(Issue).filter(Issue.id == issue_id).first()
        if not issue:
            return None
        issue.status = new_status
        issue.updated_at = datetime.utcnow()
        if new_status == "RESOLVED":
            issue.resolved_at = datetime.utcnow()
        session.add(IssueStatusHistory(issue_id=issue.id, status=new_status, note=note, changed_by_user_id=changed_by_user_id))
        session.commit()
        return issue
    finally:
        session.close()


def add_comment(issue_id: int, user_id: int, comment: str):
    session = SessionLocal()
    try:
        new_comment = IssueComment(issue_id=issue_id, user_id=user_id, comment=comment)
        session.add(new_comment)
        session.commit()
        return new_comment
    finally:
        session.close()


def get_issue_status_history(issue_id: int):
    session = SessionLocal()
    try:
        return session.query(IssueStatusHistory).filter(IssueStatusHistory.issue_id == issue_id).order_by(IssueStatusHistory.created_at.asc()).all()
    finally:
        session.close()


def get_issue_comments(issue_id: int):
    session = SessionLocal()
    try:
        return session.query(IssueComment).filter(IssueComment.issue_id == issue_id).order_by(IssueComment.created_at.asc()).all()
    finally:
        session.close()


def get_issue_images(issue_id: int):
    session = SessionLocal()
    try:
        return session.query(IssueImage).filter(IssueImage.issue_id == issue_id).order_by(IssueImage.created_at.desc()).all()
    finally:
        session.close()


def mark_notification_read(notification_id: int):
    session = SessionLocal()
    try:
        notification = session.query(Notification).filter(Notification.id == notification_id).first()
        if notification:
            notification.is_read = True
            session.commit()
        return notification
    finally:
        session.close()


def get_issue_duplicates(issue_id: int):
    issue = get_issue_by_id(issue_id)
    if not issue:
        return []
    return find_duplicate_issues(issue.title, issue.description, issue.ai_category or issue.category.name if issue.category else "Other", issue.location_text)
