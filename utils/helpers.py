from __future__ import annotations

import hashlib
import uuid
from datetime import datetime
from pathlib import Path

import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]
UPLOAD_DIR = BASE_DIR / "uploads"


def ensure_upload_dir():
    UPLOAD_DIR.mkdir(exist_ok=True)
    return UPLOAD_DIR


def hash_password(password: str) -> str:
    return hashlib.sha256(password.strip().encode("utf-8")).hexdigest()


def verify_password(password: str, hashed_password: str) -> bool:
    return hash_password(password) == hashed_password


def generate_unique_filename(original_name: str) -> str:
    ext = Path(original_name).suffix.lower() if Path(original_name).suffix else ".jpg"
    return f"{uuid.uuid4().hex}{ext}"


def get_user_name(user) -> str:
    return user.name if user else "Campus User"


def safe_text(value, default="N/A"):
    return value if value not in (None, "") else default


def format_status(status: str) -> str:
    if not status:
        return "SUBMITTED"
    return status.upper()


def pretty_date(value):
    if not value:
        return "--"
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            return value
    return value.strftime("%d %b %Y")


def get_case_insensitive(text: str):
    return (text or "").lower().strip()


def set_session_value(key, value):
    st.session_state[key] = value


def get_session_value(key, default=None):
    return st.session_state.get(key, default)
