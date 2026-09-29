from __future__ import annotations

import streamlit as st

from database.database import SessionLocal
from database.models import Notification


def render_notifications(user):
    st.title("Notifications")
    session = SessionLocal()
    try:
        notifications = session.query(Notification).filter(Notification.user_id == user.id).order_by(Notification.created_at.desc()).all()
        if not notifications:
            st.info("No notifications yet.")
            return
        for item in notifications:
            if item.is_read:
                st.markdown(f"<div class='card'><small>{item.created_at}</small><br>{item.message}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='card' style='border-left: 4px solid #2f5bff;'><small>{item.created_at}</small><br><b>{item.message}</b></div>", unsafe_allow_html=True)
                if st.button(f"Mark read {item.id}", key=f"read_{item.id}"):
                    item.is_read = True
                    session.commit()
                    st.rerun()
    finally:
        session.close()
