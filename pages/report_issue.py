from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

from database.database import SessionLocal
from database.models import Building, Campus, Issue, Location, QRLocation
from services.ai_service import analyze_issue
from services.duplicate_service import find_duplicate_issues
from services.issue_service import create_issue_record, save_issue_images
from services.qr_service import decode_qr_from_image

CATEGORIES = [
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


def advance_to_incomplete_report_step():
    draft = st.session_state.get("report_draft", {})
    if not str(draft.get("title", "")).strip() or not str(draft.get("description", "")).strip():
        st.session_state.report_step = "Description"
    elif any(not str(draft.get(field, "")).strip() for field in ("campus_name", "building_name", "location_text")):
        st.session_state.report_step = "Location"


def get_campus_data():
    session = SessionLocal()
    try:
        campuses = session.query(Campus).all()
        buildings = session.query(Building).all()
        locations = session.query(Location).all()
        return campuses, buildings, locations
    finally:
        session.close()


def render_report_issue(user):
    st.title("Report a Campus Issue")

    if "report_draft" not in st.session_state:
        st.session_state.report_draft = {}

    draft = st.session_state.report_draft

    if "category" not in draft:
        draft["category"] = "Infrastructure"
    if "priority" not in draft:
        draft["priority"] = "Medium"
    if "report_step" not in st.session_state:
        st.session_state.report_step = "Category"

    step = st.selectbox(
        "Issue Workflow",
        ["Category", "Description", "Evidence", "Location", "Smart Review"],
        key="report_step",
    )

    if step == "Category":
        st.subheader("Step 1 — Category")
        cols = st.columns(3)
        for i, category in enumerate(CATEGORIES):
            with cols[i % 3]:
                if st.button(category, key=f"cat_{category}", use_container_width=True):
                    draft["category"] = category
                    st.success(f"Selected: {category}")
        st.info("Selected category: %s" % draft.get("category"))

    elif step == "Description":
        st.subheader("Step 2 — Description")
        draft["title"] = st.text_input("Issue Title", value=draft.get("title", ""))
        draft["description"] = st.text_area("Detailed Description", value=draft.get("description", ""), height=180)
        draft["language"] = st.selectbox("Language", ["English", "Hindi", "Odia", "Bengali"], index=0)
        try:
            import speech_recognition as sr
            if st.button("🎤 Voice Report"):
                st.info("Voice reporting is currently unavailable. Please use text reporting.")
        except Exception:
            st.info("Voice reporting is currently unavailable. Please use text reporting.")

    elif step == "Evidence":
        st.subheader("Step 3 — Photo Evidence")
        image = st.camera_input("Take Photo")
        uploaded = st.file_uploader("Upload photo evidence", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
        if image is not None:
            draft["camera_image"] = image
            st.image(image)
        if uploaded:
            draft["uploaded_images"] = uploaded
            for file in uploaded[:3]:
                st.image(file)

    elif step == "Location":
        st.subheader("Step 4 — Location")
        campuses, buildings, locations = get_campus_data()
        campus_options = {campus.name: campus.id for campus in campuses}
        campus_name = st.selectbox("Campus", list(campus_options.keys()))
        draft["campus_name"] = campus_name
        campus_id = campus_options[campus_name]
        building_name = st.selectbox("Building", [b.name for b in buildings if b.campus_id == campus_id])
        draft["building_name"] = building_name
        floor = st.selectbox("Floor", ["Ground", "F1", "F2", "F3", "F4"])
        room = st.text_input("Room / Area", value="")
        draft["location_text"] = f"{campus_name} | {building_name} | {floor} | {room}"
        st.write(draft["location_text"])

        qr_code_text = st.text_input("Enter QR Location Code", value=draft.get("qr_code", ""))
        draft["qr_code"] = qr_code_text
        if st.button("Scan Campus QR"):
            st.info("Manual QR code entry is supported for Streamlit compatibility.")
        if st.button("Use Browser Location"):
            st.info("Browser geolocation is optional and may not be available on all deployments.")

    else:
        st.subheader("Step 5 — Smart Review")
        title = draft.get("title", "")
        description = draft.get("description", "")
        category = draft.get("category", "Other")
        analysis = analyze_issue(title, description, category)
        st.markdown(f"### Smart Recommendation: **{analysis['priority']}**")
        st.write("Reason:", analysis["recommendation"])
        st.write("Detected category:", analysis["category"])
        st.write("Detected severity:", analysis["severity"])
        st.write("Keywords:", ", ".join(analysis["keywords"]) if analysis["keywords"] else "No keywords found")

        duplicates = find_duplicate_issues(title, description, category, draft.get("location_text"))
        if duplicates:
            st.warning(f"⚠ Similar issue found: {len(duplicates)} possible duplicate report(s).")
            for item in duplicates[:3]:
                st.markdown(f"- {item['quickfix_id']} — {item['category']} — {item['location']} — {item['status']}")
        else:
            st.success("No similar issue detected.")

        st.markdown("### Review")
        st.write("Issue Title:", title)
        st.write("Category:", category)
        st.write("Description:", description)
        st.write("Location:", draft.get("location_text"))
        st.write("Priority:", draft.get("priority", analysis["priority"]))
        st.write("Smart Priority:", analysis["priority"])
        if "camera_image" in draft and draft["camera_image"] is not None:
            st.image(draft["camera_image"])
        if "uploaded_images" in draft:
            for file in draft["uploaded_images"][:3]:
                st.image(file)

    st.divider()
    if st.button(
        "Submit Report",
        type="primary",
        use_container_width=True,
        on_click=advance_to_incomplete_report_step,
    ):
        required_fields = ["title", "description", "campus_name", "building_name", "location_text"]
        missing_fields = [field for field in required_fields if not str(draft.get(field, "")).strip()]
        if missing_fields:
            if any(field in missing_fields for field in ("title", "description")):
                st.info("Add the issue title and description, then submit again.")
            else:
                st.info("Choose the campus and building, then submit again.")
        else:
            try:
                session = SessionLocal()
                campus = session.query(Campus).filter(Campus.name == draft["campus_name"]).first()
                building = session.query(Building).filter(
                    Building.name == draft["building_name"],
                    Building.campus_id == campus.id if campus else False,
                ).first()
                session.close()
                analysis = analyze_issue(draft["title"], draft["description"], draft.get("category", "Other"))
                issue = create_issue_record({
                    "title": draft["title"],
                    "description": draft["description"],
                    "category": draft.get("category", "Other"),
                    "category_id": None,
                    "campus_id": getattr(campus, "id", None),
                    "building_id": getattr(building, "id", None),
                    "location_id": None,
                    "user_id": user.id,
                    "priority": analysis["priority"],
                    "location_text": draft["location_text"],
                    "qr_code": draft.get("qr_code"),
                })
                if draft.get("camera_image") is not None:
                    save_issue_images(issue.id, [draft["camera_image"]])
                if draft.get("uploaded_images"):
                    save_issue_images(issue.id, draft["uploaded_images"])

                st.session_state.report_draft = {}
                st.session_state.current_page = "my_issues"
                st.session_state.selected_issue = issue.id
                st.rerun()
            except Exception as e:
                st.error(f"Unable to submit issue: {e}")
