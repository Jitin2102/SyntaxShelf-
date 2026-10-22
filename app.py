import sqlite3
import streamlit as st

from lms.schema import init_schema
from lms.ui import books, common, dashboard, loans, members

PAGES = {
    "Dashboard": dashboard.render,
    "Books": books.render,
    "Members": members.render,
    "Issue & Return": loans.render,
}

st.set_page_config(page_title="Library Management System", page_icon="📚", layout="wide")

try:
    init_schema()
except sqlite3.Error as err:
    st.error(f"Cannot open the database: {err}")
    st.stop()

st.sidebar.title("📚 Library")
page = st.sidebar.radio("Menu", list(PAGES), label_visibility="collapsed")

common.show_flash()
PAGES[page]()
