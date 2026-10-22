import streamlit as st

from ..repositories import members
from .common import attempt


def _directory() -> None:
    term = st.text_input("Search by name or email")
    st.dataframe(members.search(term), use_container_width=True, hide_index=True)


def _add_form() -> None:
    with st.form("add_member", clear_on_submit=True):
        name = st.text_input("Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        if st.form_submit_button("Add member"):
            attempt(lambda: members.add(name, email, phone), "Member added")


def _manage() -> None:
    rows = members.search()
    if not rows:
        st.info("No members yet.")
        return
    member = st.selectbox("Member", rows, format_func=lambda r: f"{r['name']} ({r['email']})")
    key = member["id"]
    with st.form(f"edit_member_{key}"):
        name = st.text_input("Name", member["name"], key=f"name_{key}")
        email = st.text_input("Email", member["email"], key=f"email_{key}")
        phone = st.text_input("Phone", member["phone"] or "", key=f"phone_{key}")
        save, delete = st.columns(2)
        if save.form_submit_button("Save changes"):
            attempt(lambda: members.update(key, name, email, phone), "Member updated")
        if delete.form_submit_button("Delete member"):
            attempt(lambda: members.remove(key), "Member deleted")


def render() -> None:
    st.header("Members")
    directory, add, manage = st.tabs(["Directory", "Add member", "Edit / remove"])
    with directory:
        _directory()
    with add:
        _add_form()
    with manage:
        _manage()
