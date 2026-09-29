from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from database.models import Base, Building, Campus, Issue, IssueCategory, Location, QRLocation, User

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = BASE_DIR / "uploads"
DB_PATH = DATA_DIR / "quickfix.db"

DATA_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)

DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db_session() -> Session:
    session = SessionLocal()
    try:
        return session
    except Exception:
        session.close()
        raise


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    seed_demo_data()


def seed_demo_data() -> None:
    session = SessionLocal()
    try:
        category_names = [
            "Infrastructure",
            "Lighting",
            "Water Leakage",
            "Cleanliness",
            "Network/Wi-Fi",
            "Electrical",
            "Furniture",
            "Road/Pathway",
            "Washroom",
            "Safety",
            "Other",
        ]

        existing_categories = session.query(IssueCategory).count()
        if existing_categories == 0:
            for name in category_names:
                session.add(IssueCategory(name=name, description=name))

        if session.query(Campus).count() == 0:
            campus = Campus(name="Green Valley Campus", code="CAMPUS-A", location="North Block")
            session.add(campus)
            session.flush()

            building_names = [
                "Library",
                "Academic Block",
                "Hostel",
                "Canteen",
                "Laboratory",
                "Administrative Block",
                "Sports Ground",
                "Parking",
            ]
            for name in building_names:
                building = Building(name=name, campus_id=campus.id, floors="Ground, 1, 2")
                session.add(building)
            session.flush()

            buildings = session.query(Building).filter_by(campus_id=campus.id).all()
            for idx, building in enumerate(buildings, start=1):
                for room in ["A101", "A204", "B101", "C205", "D103"]:
                    session.add(
                        Location(
                            name=f"{building.name} - {room}",
                            campus_id=campus.id,
                            building_id=building.id,
                            floor=f"F{(idx % 3) + 1}",
                            room=room,
                            area="Main corridor",
                            qr_code=f"CAMPUS-A|{building.name}|F{(idx % 3) + 1}|{room}",
                        )
                    )

        if session.query(User).count() == 0:
            from utils.helpers import hash_password

            student = User(
                name="Aarav Sharma",
                email="student@quickfix.demo",
                password_hash=hash_password("QuickFix@123"),
                role="Student",
                department="Computer Science",
                campus_id=1,
            )
            staff = User(
                name="Priya Nair",
                email="staff@quickfix.demo",
                password_hash=hash_password("QuickFix@123"),
                role="Maintenance Staff",
                department="Facilities",
                campus_id=1,
            )
            admin = User(
                name="Rohit Kumar",
                email="admin@quickfix.demo",
                password_hash=hash_password("QuickFix@123"),
                role="Administrator",
                department="Administration",
                campus_id=1,
            )
            session.add_all([student, staff, admin])

        if session.query(Issue).count() == 0:
            sample_issues = [
                {
                    "title": "Water leaking near laboratory entrance",
                    "description": "Water is leaking near the laboratory entrance and creating a slippery floor.",
                    "category": "Water Leakage",
                    "status": "SUBMITTED",
                    "priority": "High",
                    "smart_priority": "High",
                    "severity": "High",
                    "location_text": "Laboratory - Entrance",
                    "campus": 1,
                    "building": 5,
                    "user_id": 1,
                },
                {
                    "title": "Broken light in corridor",
                    "description": "Two lights are out in the first-floor corridor near the library.",
                    "category": "Lighting",
                    "status": "IN_PROGRESS",
                    "priority": "Medium",
                    "smart_priority": "Medium",
                    "severity": "Medium",
                    "location_text": "Library - Corridor",
                    "campus": 1,
                    "building": 1,
                    "user_id": 1,
                },
                {
                    "title": "Washroom door not closing properly",
                    "description": "The washroom door is jammed and requires maintenance.",
                    "category": "Washroom",
                    "status": "RESOLVED",
                    "priority": "Low",
                    "smart_priority": "Low",
                    "severity": "Low",
                    "location_text": "Administrative Block - Washroom",
                    "campus": 1,
                    "building": 6,
                    "user_id": 1,
                },
                {
                    "title": "Crack in pedestrian path",
                    "description": "A deep crack has developed on the pedestrian path near hostel gate.",
                    "category": "Road/Pathway",
                    "status": "ASSIGNED",
                    "priority": "High",
                    "smart_priority": "High",
                    "severity": "Medium",
                    "location_text": "Hostel - Pathway",
                    "campus": 1,
                    "building": 3,
                    "user_id": 1,
                },
            ]
            categories = {item.name: item.id for item in session.query(IssueCategory).all()}
            for idx, issue_data in enumerate(sample_issues, start=1):
                issue = Issue(
                    quickfix_id=f"QF-2026-{idx:06d}",
                    title=issue_data["title"],
                    description=issue_data["description"],
                    category_id=categories.get(issue_data["category"]),
                    campus_id=issue_data["campus"],
                    building_id=issue_data["building"],
                    user_id=issue_data["user_id"],
                    status=issue_data["status"],
                    priority=issue_data["priority"],
                    smart_priority=issue_data["smart_priority"],
                    severity=issue_data["severity"],
                    ai_category=issue_data["category"],
                    location_text=issue_data["location_text"],
                )
                session.add(issue)

        if session.query(QRLocation).count() == 0:
            campus = session.query(Campus).first()
            qr_data = [
                {
                    "building": "Library",
                    "floor": "F2",
                    "room": "ROOM-204",
                    "area": "Reading Hall",
                },
                {
                    "building": "Laboratory",
                    "floor": "F1",
                    "room": "LAB-101",
                    "area": "Main Lab",
                },
                {
                    "building": "Hostel",
                    "floor": "F3",
                    "room": "H-312",
                    "area": "Corridor",
                },
            ]
            for item in qr_data:
                qr = QRLocation(
                    campus_id=campus.id,
                    building=item["building"],
                    floor=item["floor"],
                    room=item["room"],
                    area=item["area"],
                    qr_text=f"CAMPUS-A|{item['building']}|{item['floor']}|{item['room']}",
                )
                session.add(qr)

        session.commit()
    finally:
        session.close()


__all__ = ["Base", "SessionLocal", "get_db_session", "init_db", "seed_demo_data"]
