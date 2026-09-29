import streamlit as st


def inject_custom_css():
    st.markdown(
        """
        <style>
            :root {
                --bg: #f2f6f3;
                --panel: #ffffff;
                --primary: #176b56;
                --primary-hover: #105443;
                --secondary: #df795f;
                --warning: #d99827;
                --danger: #c94e52;
                --dark: #1b302d;
                --muted: #687a75;
                --border: #d9e4de;
            }
            .stApp {
                background: linear-gradient(180deg, #f2f6f3 0%, #f8f8f4 100%);
                color: var(--dark);
            }
            .block-container {
                padding-top: 1.5rem;
                padding-bottom: 2rem;
            }
            .metric-card {
                background: var(--panel);
                border: 1px solid var(--border);
                border-radius: 8px;
                padding: 1rem 1.2rem;
                box-shadow: 0 5px 16px rgba(27, 48, 45, 0.06);
            }
            .status-pill {
                display: inline-block;
                padding: 0.35rem 0.7rem;
                border-radius: 6px;
                font-size: 0.76rem;
                font-weight: 700;
                letter-spacing: 0.02em;
                text-transform: uppercase;
            }
            .card {
                background: var(--panel);
                border-radius: 8px;
                border: 1px solid var(--border);
                padding: 1rem;
                box-shadow: 0 5px 16px rgba(27, 48, 45, 0.06);
            }
            .priority-high { background: #fbe6e1; color: #9d4034; }
            .priority-medium { background: #fbf0d8; color: #805710; }
            .priority-low { background: #dcefe4; color: #236344; }
            .priority-critical { background: #c94e52; color: #ffffff; }
            .nav-link {
                background: #e5f0ea;
                border-radius: 8px;
                padding: 0.6rem 0.8rem;
            }
            [data-testid="stSidebar"] {
                background: #edf3ef;
                border-right: 1px solid var(--border);
            }
            [data-testid="stAppDeployButton"] {
                display: none;
            }
            .stButton > button {
                border-radius: 8px;
                border-color: var(--border);
                color: var(--dark);
                transition: background-color 140ms ease, border-color 140ms ease, color 140ms ease;
            }
            .stButton > button:hover {
                border-color: var(--primary);
                color: var(--primary);
            }
            .stButton > button[data-testid="stBaseButton-primary"],
            .stButton > button[kind="primary"] {
                background: var(--primary);
                border-color: var(--primary);
                color: #ffffff;
            }
            .stButton > button[data-testid="stBaseButton-primary"]:hover,
            .stButton > button[kind="primary"]:hover {
                background: var(--primary-hover);
                border-color: var(--primary-hover);
                color: #ffffff;
            }
            [data-testid="stTextInput"] input,
            [data-testid="stTextArea"] textarea,
            [data-testid="stSelectbox"] [data-baseweb="select"] > div {
                border-color: var(--border);
                border-radius: 8px;
            }
            [data-testid="stTextInput"] input:focus,
            [data-testid="stTextArea"] textarea:focus {
                border-color: var(--primary);
                box-shadow: 0 0 0 1px var(--primary);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
