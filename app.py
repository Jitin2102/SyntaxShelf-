import base64
import mimetypes
import sqlite3
from datetime import date
from pathlib import Path

import streamlit as st

from lms.schema import init_schema
from lms.ui import books, common, dashboard, loans, members

APP_TITLE = "Library Management System"

_HERE = Path(__file__).resolve().parent
_ASSET_DIRS = [_HERE / "lms" / "assets", _HERE / "assets"]


def find_asset(*names: str) -> Path | None:
    for folder in _ASSET_DIRS:
        for name in names:
            path = folder / name
            if path.exists():
                return path
    return None


LOGO = find_asset("logo.jpg", "logo.png", "logo.jpeg")
BANNER = find_asset("banner.jpg", "banner.png", "banner.jpeg")

PAGES = {
    "Dashboard": ("📊", dashboard.render),
    "Books": ("📖", books.render),
    "Members": ("👥", members.render),
    "Issue & Return": ("🔄", loans.render),
}

# Tweak these two to taste
LOGO_HEIGHT = "3.5rem"  # sidebar logo size
BG_OPACITY = 0.12  # banner visibility behind the page (0 = hidden, 1 = full)

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(show_spinner=False)
def image_to_data_uri(path: str) -> str:
    mime = mimetypes.guess_type(path)[0] or "image/jpeg"
    data = base64.b64encode(Path(path).read_bytes()).decode()
    return f"data:{mime};base64,{data}"


# ---------- Styling (applies to every page) ----------
bg_css = ""
if BANNER:
    bg_css = f"""
        .stApp::before {{
            content: "";
            position: fixed;
            inset: 0;
            background: url("{image_to_data_uri(str(BANNER))}") center / cover no-repeat;
            opacity: {BG_OPACITY};
            pointer-events: none;
            z-index: 0;
        }}
    """

st.markdown(
    f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
        {bg_css}
        .block-container {{padding-top: 2rem; padding-bottom: 2rem;}}
        [data-testid="stSidebar"] {{border-right: 1px solid rgba(128,128,128,.2);}}
        [data-testid="stMetric"] {{
            background: rgba(128,128,128,.12);
            border-radius: 12px;
            padding: 12px 16px;
        }}
        .stButton > button {{border-radius: 8px;}}
        [data-testid="stImage"] img {{border-radius: 12px;}}

        /* Logo size: fixed height, width follows aspect ratio */
        [data-testid="stLogo"],
        [data-testid="stSidebarHeader"] img {{
            height: {LOGO_HEIGHT} !important;
            max-height: {LOGO_HEIGHT} !important;
            width: auto !important;
            object-fit: contain;
        }}
        footer {{visibility: hidden;}}

        /* ---------- Text ---------- */
        html, body, [class*="css"], .stMarkdown, .stText, label, p {{
            font-family: 'Poppins', 'Segoe UI', sans-serif;
        }}
        h1 {{font-weight: 700; letter-spacing: -0.5px;}}
        h2, h3 {{
            font-weight: 600;
            padding-bottom: .35rem;
            border-bottom: 2px solid rgba(255, 75, 75, .55);
            width: fit-content;
        }}
        p, li, label {{line-height: 1.6;}}
        [data-testid="stMetricValue"] {{font-weight: 700;}}
        [data-testid="stMetricLabel"] {{opacity: .75; font-weight: 500;}}

        /* ---------- Tables ---------- */
        [data-testid="stDataFrame"],
        [data-testid="stTable"] {{
            border: 1px solid rgba(128,128,128,.25);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,.08);
        }}
        [data-testid="stTable"] table {{
            width: 100%;
            border-collapse: collapse;
        }}
        [data-testid="stTable"] thead th {{
            background: rgba(255, 75, 75, .15);
            font-weight: 600;
            text-align: left;
            padding: 10px 14px;
        }}
        [data-testid="stTable"] tbody td {{padding: 9px 14px;}}
        [data-testid="stTable"] tbody tr:nth-child(even) {{
            background: rgba(128,128,128,.07);
        }}
        [data-testid="stTable"] tbody tr:hover {{
            background: rgba(255, 75, 75, .10);
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

if LOGO and hasattr(st, "logo"):
    st.logo(str(LOGO))


@st.cache_resource(show_spinner="Setting up database…")
def setup_database() -> bool:
    init_schema()
    return True


try:
    setup_database()
except sqlite3.Error as err:
    st.error(f"Cannot open the database: {err}")
    st.stop()

with st.sidebar:
    st.title("📚 Library")
    st.caption("Manage books, members and loans")
    st.divider()

    page = st.radio(
        "Menu",
        list(PAGES),
        format_func=lambda name: f"{PAGES[name][0]}  {name}",
        label_visibility="collapsed",
        key="nav_page",
    )

    st.divider()
    st.caption(f"📅 {date.today():%A, %d %B %Y}")

icon, render = PAGES[page]

common.show_flash()

try:
    render()
except sqlite3.Error as err:
    st.error(f"A database error occurred: {err}")
except Exception as err:
    st.error("Something went wrong while loading this page.")
    with st.expander("Technical details"):
        st.exception(err)
