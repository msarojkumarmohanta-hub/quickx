from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

from database.database import init_db
from pages.admin_dashboard import render_admin_dashboard
from pages.campus_map import render_campus_map
from pages.home import render_home
from pages.issue_details import render_issue_details
from pages.my_issues import render_my_issues
from pages.notifications import render_notifications
from pages.profile import render_profile
from pages.report_issue import render_report_issue
from pages.staff_dashboard import render_staff_dashboard
from utils.authentication import ensure_auth_state, get_current_user, login_user, logout_user, register_user
from utils.helpers import get_user_name
from utils.styling import inject_custom_css


st.set_page_config(
    page_title="Smart Campus QuickFix",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded",
)


inject_custom_css()


def get_nav_items(user_role):
    base = [
        ("🏠 Home", "home"),
        ("➕ Report Issue", "report_issue"),
        ("📋 My Issues", "my_issues"),
        ("🗺 Campus Map", "campus_map"),
        ("🔔 Notifications", "notifications"),
        ("👤 Profile", "profile"),
    ]
    if user_role in {"Maintenance Staff", "Administrator"}:
        base.append(("🛠 Staff Dashboard", "staff_dashboard"))
    if user_role == "Administrator":
        base.extend([
            ("📊 Admin Dashboard", "admin_dashboard"),
            ("⚙ Manage Campus", "admin_dashboard"),
        ])
    return base


def render_auth_screen():
    st.markdown("<h1 style='text-align:center;'>Smart Campus QuickFix</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#8aa2ff;'>Report. Track. Resolve.</p>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                user = login_user(email, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user.id
                    st.session_state.user_role = user.role
                    st.rerun()
                else:
                    st.error("Invalid email or password.")

        st.caption("Demo users: student@quickfix.demo, staff@quickfix.demo, admin@quickfix.demo")
        st.caption("Password: QuickFix@123")

    with tab2:
        with st.form("register_form"):
            name = st.text_input("Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            role = st.selectbox("Role", ["Student", "Campus User", "Maintenance Staff", "Administrator"])
            submitted = st.form_submit_button("Create account")
            if submitted:
                if not name or not email or not password:
                    st.error("Please fill all fields.")
                else:
                    new_user = register_user(name, email, password, role)
                    if new_user:
                        st.success("Account created successfully. Please log in.")
                    else:
                        st.error("User already exists or registration failed.")


def render_main_app():
    user = get_current_user()
    if not user:
        st.session_state.logged_in = False
        render_auth_screen()
        return

    st.sidebar.image("https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=200&q=80", width=200)
    st.sidebar.title("Smart Campus QuickFix")
    nav_items = get_nav_items(user.role)
    valid_pages = [value for _, value in nav_items]
    current_page = st.session_state.get("current_page", "home")
    if current_page == "issue_details":
        st.sidebar.button("Back to My Issues", on_click=lambda: st.session_state.__setitem__("current_page", "my_issues"))
        render_issue_details(user)
        return
    if current_page not in valid_pages:
        current_page = "home"

    page_index = 0
    for idx, (_, value) in enumerate(nav_items):
        if value == current_page:
            page_index = idx
            break

    selected = st.sidebar.radio("Navigation", [label for label, _ in nav_items], index=page_index)
    page_key = next(value for label, value in nav_items if label == selected)
    st.session_state.current_page = page_key

    st.sidebar.markdown("---")
    st.sidebar.write(f"{get_user_name(user)}")
    st.sidebar.write(user.role)
    if st.sidebar.button("Logout"):
        logout_user()
        st.rerun()

    page_map = {
        "home": render_home,
        "report_issue": render_report_issue,
        "my_issues": render_my_issues,
        "campus_map": render_campus_map,
        "notifications": render_notifications,
        "profile": render_profile,
        "staff_dashboard": render_staff_dashboard,
        "admin_dashboard": render_admin_dashboard,
        "issue_details": render_issue_details,
    }

    if page_key in page_map:
        page_map[page_key](user)


def main():
    os.makedirs("data", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)
    init_db()
    ensure_auth_state()
    if st.session_state.get("logged_in"):
        render_main_app()
    else:
        render_auth_screen()


if __name__ == "__main__":
    main()
