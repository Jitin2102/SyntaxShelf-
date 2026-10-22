from ..db import execute, execute_many, fetch_all
from ..validation import require

CATALOG = """
SELECT b.id, b.title, b.author, b.isbn, b.total_copies,
       b.total_copies - COUNT(l.id) AS available
FROM books b
LEFT JOIN loans l ON l.book_id = b.id AND l.returned_on IS NULL
WHERE b.title LIKE ? OR b.author LIKE ? OR b.isbn LIKE ?
GROUP BY b.id
ORDER BY b.title
"""


def search(term: str = "") -> list[dict]:
    like = f"%{term.strip()}%"
    return fetch_all(CATALOG, (like, like, like))


def available() -> list[dict]:
    return [book for book in search() if book["available"] > 0]


def add(title: str, author: str, isbn: str, copies: int) -> None:
    require(title=title, author=author, isbn=isbn)
    execute(
        "INSERT INTO books (title, author, isbn, total_copies) VALUES (?, ?, ?, ?)",
        (title.strip(), author.strip(), isbn.strip(), copies),
    )


def update(book_id: int, title: str, author: str, isbn: str, copies: int) -> None:
    require(title=title, author=author, isbn=isbn)
    execute(
        "UPDATE books SET title=?, author=?, isbn=?, total_copies=? WHERE id=?",
        (title.strip(), author.strip(), isbn.strip(), copies, book_id),
    )


def remove(book_id: int) -> None:
    execute("DELETE FROM books WHERE id=?", (book_id,))


def add_many(rows: list[dict]) -> int:
    return execute_many(
        "INSERT OR IGNORE INTO books (title, author, isbn, total_copies) VALUES (?, ?, ?, ?)",
        [(r["title"], r["author"], r["isbn"], r["copies"]) for r in rows],
    )
