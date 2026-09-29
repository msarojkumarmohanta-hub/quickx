from __future__ import annotations

import streamlit as st

from database.database import SessionLocal
from database.models import User
from utils.helpers import hash_password


def ensure_auth_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "user_role" not in st.session_state:
        st.session_state.user_role = None
    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"


def get_current_user():
    if not st.session_state.get("logged_in"):
        return None
    user_id = st.session_state.get("user_id")
    if not user_id:
        return None
    session = SessionLocal()
    try:
        return session.query(User).filter(User.id == user_id).first()
    finally:
        session.close()


def login_user(email: str, password: str):
    email = (email or "").strip().lower()
    password = password or ""
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.email == email).first()
        if user and user.password_hash == hash_password(password):
            st.session_state.logged_in = True
            st.session_state.user_id = user.id
            st.session_state.user_role = user.role
            return user
        return None
    finally:
        session.close()


def register_user(name: str, email: str, password: str, role: str):
    name = (name or "").strip()
    email = (email or "").strip().lower()
    password = password or ""
    if not name or not email or len(password) < 4:
        return None
    session = SessionLocal()
    try:
        existing = session.query(User).filter(User.email == email).first()
        if existing:
            return None
        user = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role=role,
            department="General",
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    finally:
        session.close()


def logout_user():
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_role = None
    st.session_state.current_page = "home"
