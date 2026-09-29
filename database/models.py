from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(200), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(80), default="Student")
    department: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    campus_id: Mapped[Optional[int]] = mapped_column(ForeignKey("campuses.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    campus = relationship("Campus", back_populates="users")
    issues = relationship("Issue", foreign_keys="Issue.user_id", back_populates="user")
    assigned_issues = relationship("Issue", foreign_keys="Issue.assigned_staff_id", back_populates="assigned_staff")


class Campus(Base):
    __tablename__ = "campuses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    code: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="campus")
    buildings = relationship("Building", back_populates="campus")
    issues = relationship("Issue", back_populates="campus")


class Building(Base):
    __tablename__ = "buildings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    campus_id: Mapped[int] = mapped_column(ForeignKey("campuses.id"), nullable=False)
    floors: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    campus = relationship("Campus", back_populates="buildings")
    locations = relationship("Location", back_populates="building")
    issues = relationship("Issue", back_populates="building")


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    campus_id: Mapped[int] = mapped_column(ForeignKey("campuses.id"), nullable=False)
    building_id: Mapped[Optional[int]] = mapped_column(ForeignKey("buildings.id"), nullable=True)
    floor: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    room: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    area: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    qr_code: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    building = relationship("Building", back_populates="locations")
    issues = relationship("Issue", back_populates="location")


class IssueCategory(Base):
    __tablename__ = "issue_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    issues = relationship("Issue", back_populates="category")


class Issue(Base):
    __tablename__ = "issues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    quickfix_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("issue_categories.id"), nullable=True)
    campus_id: Mapped[Optional[int]] = mapped_column(ForeignKey("campuses.id"), nullable=True)
    building_id: Mapped[Optional[int]] = mapped_column(ForeignKey("buildings.id"), nullable=True)
    location_id: Mapped[Optional[int]] = mapped_column(ForeignKey("locations.id"), nullable=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    assigned_staff_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(60), default="SUBMITTED")
    priority: Mapped[str] = mapped_column(String(40), default="Medium")
    smart_priority: Mapped[str] = mapped_column(String(40), default="Medium")
    severity: Mapped[str] = mapped_column(String(40), default="Medium")
    ai_category: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    location_text: Mapped[Optional[str]] = mapped_column(String(250), nullable=True)
    qr_code: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    category = relationship("IssueCategory", back_populates="issues")
    campus = relationship("Campus", back_populates="issues")
    building = relationship("Building", back_populates="issues")
    location = relationship("Location", back_populates="issues")
    user = relationship("User", foreign_keys=[user_id], back_populates="issues")
    assigned_staff = relationship("User", foreign_keys=[assigned_staff_id], back_populates="assigned_issues")
    status_history = relationship("IssueStatusHistory", back_populates="issue")
    comments = relationship("IssueComment", back_populates="issue")
    images = relationship("IssueImage", back_populates="issue")
    assignments = relationship("IssueAssignment", back_populates="issue")
    notifications = relationship("Notification", back_populates="issue")


class IssueImage(Base):
    __tablename__ = "issue_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    issue_id: Mapped[int] = mapped_column(ForeignKey("issues.id"), nullable=False)
    image_path: Mapped[str] = mapped_column(String(500), nullable=False)
    caption: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    issue = relationship("Issue", back_populates="images")


class IssueStatusHistory(Base):
    __tablename__ = "issue_status_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    issue_id: Mapped[int] = mapped_column(ForeignKey("issues.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(80), nullable=False)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    changed_by_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    issue = relationship("Issue", back_populates="status_history")


class IssueComment(Base):
    __tablename__ = "issue_comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    issue_id: Mapped[int] = mapped_column(ForeignKey("issues.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    issue = relationship("Issue", back_populates="comments")


class IssueAssignment(Base):
    __tablename__ = "issue_assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    issue_id: Mapped[int] = mapped_column(ForeignKey("issues.id"), nullable=False)
    assigned_to_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    assigned_by_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(80), default="ASSIGNED")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    issue = relationship("Issue", back_populates="assignments")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    issue_id: Mapped[Optional[int]] = mapped_column(ForeignKey("issues.id"), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    issue = relationship("Issue", back_populates="notifications")


class QRLocation(Base):
    __tablename__ = "qr_locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    campus_id: Mapped[int] = mapped_column(ForeignKey("campuses.id"), nullable=False)
    building: Mapped[str] = mapped_column(String(120), nullable=False)
    floor: Mapped[str] = mapped_column(String(50), nullable=False)
    room: Mapped[str] = mapped_column(String(80), nullable=False)
    area: Mapped[str] = mapped_column(String(120), nullable=False)
    qr_text: Mapped[str] = mapped_column(String(250), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AIAnalysis(Base):
    __tablename__ = "ai_analysis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    issue_id: Mapped[Optional[int]] = mapped_column(ForeignKey("issues.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(120), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    recommended_priority: Mapped[str] = mapped_column(String(50), nullable=False)
    keywords: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DuplicateMatch(Base):
    __tablename__ = "duplicate_matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_issue_id: Mapped[int] = mapped_column(ForeignKey("issues.id"), nullable=False)
    matched_issue_id: Mapped[int] = mapped_column(ForeignKey("issues.id"), nullable=False)
    match_score: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
