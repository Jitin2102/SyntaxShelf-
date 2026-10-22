import streamlit as st

from lms.ui.common import attempt

from .. import importer
from ..repositories import books


def _catalog() -> None:
    term = st.text_input("Search by title, author or ISBN")
    st.dataframe(books.search(term), use_container_width=True, hide_index=True)


def _add_form() -> None:
    with st.form("add_book", clear_on_submit=True):
        title = st.text_input("Title")
        author = st.text_input("Author")
        isbn = st.text_input("ISBN")
        copies = st.number_input("Copies", min_value=1, value=1)
        if st.form_submit_button("Add book"):
            attempt(lambda: books.add(title, author, isbn, int(copies)), "Book added")


def _bulk_upload() -> None:
    st.download_button(
        "Download Excel template",
        importer.template(),
        "books_template.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    file = st.file_uploader(
        "Excel file (.xlsx) with Title, Author, ISBN, Copies", type="xlsx"
    )
    if not file:
        return
    try:
        rows, invalid = importer.read_books(file)
    except ValueError as err:
        st.error(str(err))
        return
    if invalid:
        st.warning(f"{invalid} row(s) skipped: title, author and ISBN are required.")
    if not rows:
        st.info("No valid rows found.")
        return
    st.dataframe(rows, use_container_width=True, hide_index=True)
    if st.button("Import books"):
        attempt(
            lambda: books.add_many(rows),
            f"{{}} of {len(rows)} books imported (existing ISBNs were skipped)",
        )


def _manage() -> None:
    rows = books.search()
    if not rows:
        st.info("No books yet.")
        return
    book = st.selectbox(
        "Book", rows, format_func=lambda r: f"{r['title']} — {r['author']}"
    )
    key = book["id"]
    with st.form(f"edit_book_{key}"):
        title = st.text_input("Title", book["title"], key=f"title_{key}")
        author = st.text_input("Author", book["author"], key=f"author_{key}")
        isbn = st.text_input("ISBN", book["isbn"], key=f"isbn_{key}")
        copies = st.number_input(
            "Copies", min_value=1, value=int(book["total_copies"]), key=f"copies_{key}"
        )
        save, delete = st.columns(2)
        if save.form_submit_button("Save changes"):
            attempt(
                lambda: books.update(key, title, author, isbn, int(copies)),
                "Book updated",
            )
        if delete.form_submit_button("Delete book"):
            attempt(lambda: books.remove(key), "Book deleted")


def render() -> None:
    st.header("Books")
    catalog, add, bulk, manage = st.tabs(
        ["Catalog", "Add book", "Bulk upload", "Edit / remove"]
    )
    with catalog:
        _catalog()
    with add:
        _add_form()
    with bulk:
        _bulk_upload()
    with manage:
        _manage()
