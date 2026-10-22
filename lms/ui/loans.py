import streamlit as st

from ..repositories import books, loans, members
from .common import attempt


def _issue() -> None:
    available, people = books.available(), members.search()
    if not available or not people:
        st.info("Add at least one available book and one member first.")
        return
    with st.form("issue_book"):
        book = st.selectbox("Book", available, format_func=lambda r: f"{r['title']} ({r['available']} left)")
        member = st.selectbox("Member", people, format_func=lambda r: f"#{r['id']} {r['name']}")
        days = st.number_input("Loan period (days)", min_value=1, max_value=90, value=14)
        if st.form_submit_button("Issue book"):
            attempt(lambda: loans.issue(book["id"], member["id"], int(days)), "Book issued")


def _return() -> None:
    open_loans = loans.active()
    if not open_loans:
        st.info("No books are currently issued.")
        return
    with st.form("return_book"):
        loan = st.selectbox(
            "Issued book",
            open_loans,
            format_func=lambda r: f"{r['title']} — {r['member']} (due {r['due_on']}, {r['status']})",
        )
        if st.form_submit_button("Return book"):
            attempt(lambda: loans.give_back(loan["id"]), "Book returned")


def render() -> None:
    st.header("Issue & Return")
    issue, give_back, history = st.tabs(["Issue", "Return", "History"])
    with issue:
        _issue()
    with give_back:
        _return()
    with history:
        st.dataframe(loans.history(), use_container_width=True, hide_index=True)
