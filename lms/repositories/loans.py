from ..db import execute, fetch_all

LOANS = """
SELECT l.id, b.title, m.name AS member, l.issued_on, l.due_on, l.returned_on,
       CASE WHEN l.returned_on IS NOT NULL THEN 'Returned'
            WHEN l.due_on < date('now', 'localtime') THEN 'Overdue'
            ELSE 'Issued' END AS status
FROM loans l
JOIN books b ON b.id = l.book_id
JOIN members m ON m.id = l.member_id
"""

ISSUE = """
INSERT INTO loans (book_id, member_id, issued_on, due_on)
SELECT b.id, ?, date('now', 'localtime'), date('now', 'localtime', '+' || ? || ' days')
FROM books b
WHERE b.id = ?
  AND b.total_copies > (SELECT COUNT(*) FROM loans WHERE book_id = b.id AND returned_on IS NULL)
"""


def history() -> list[dict]:
    return fetch_all(LOANS + " ORDER BY l.id DESC")


def active() -> list[dict]:
    return fetch_all(LOANS + " WHERE l.returned_on IS NULL ORDER BY l.due_on")


def issue(book_id: int, member_id: int, days: int) -> None:
    if execute(ISSUE, (member_id, days, book_id)) == 0:
        raise ValueError("No copies of this book are available")


def give_back(loan_id: int) -> None:
    execute(
        "UPDATE loans SET returned_on = date('now', 'localtime') WHERE id=? AND returned_on IS NULL",
        (loan_id,),
    )
