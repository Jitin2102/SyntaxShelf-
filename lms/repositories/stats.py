from ..db import fetch_all

SUMMARY = """
SELECT (SELECT COUNT(*) FROM books) AS titles,
       (SELECT COUNT(*) FROM members) AS members,
       (SELECT COUNT(*) FROM loans WHERE returned_on IS NULL) AS issued,
       (SELECT COUNT(*) FROM loans WHERE returned_on IS NULL AND due_on < date('now', 'localtime')) AS overdue
"""


def summary() -> dict:
    return fetch_all(SUMMARY)[0]
