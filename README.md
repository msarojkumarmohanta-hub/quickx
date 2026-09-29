# Smart Campus QuickFix

Smart Campus QuickFix is a Streamlit-based campus issue reporting and management platform built for campus maintenance, student reporting, staff actions, and admin oversight.

## Features

- Student and campus user issue reporting
- Smart category detection and priority recommendation
- Photo evidence upload and camera capture
- Location tagging, manual selection, and QR-based location scanning
- Duplicate issue detection
- Notifications and issue tracking
- Staff dashboard and admin analytics
- SQLite-backed local database
- Responsive mobile-friendly Streamlit UI
- Demo authentication for quick evaluation

## Demo credentials

All demo accounts use the same password:

- QuickFix@123

Accounts:

- student@quickfix.demo
- staff@quickfix.demo
- admin@quickfix.demo

## Tech stack

- Python 3.10+
- Streamlit
- SQLite
- SQLAlchemy
- Plotly
- OpenCV
- Pillow
- qrcode
- scikit-learn
- geopy

## Project structure

- app.py
- services/
- database/
- pages/
- utils/
- data/
- uploads/
- assets/

## Installation

```bash
pip install -r requirements.txt
```

## Run locally

```bash
streamlit run app.py
```

## Streamlit Community Cloud deployment

1. Push the project to GitHub.
2. In Streamlit Community Cloud, create a new app.
3. Select the repository and branch.
4. Set the main file to `app.py`.
5. Ensure the project has `requirements.txt` and a valid Python runtime.
6. Deploy.

## known limitations

- This project uses SQLite for a local, deployable demo setup.
- QR scanning is supported through manual entry and optional image processing when dependencies are available.
- GPS is optional and only used when the browser exposes location data.
- Advanced AI integrations can be added later by swapping the rule-based analyzer for an external API.
