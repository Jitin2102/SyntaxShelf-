from ..db import execute, fetch_all
from ..validation import require


def search(term: str = "") -> list[dict]:
    like = f"%{term.strip()}%"
    return fetch_all(
        "SELECT id, name, email, phone FROM members "
        "WHERE name LIKE ? OR email LIKE ? ORDER BY name",
        (like, like),
    )


def add(name: str, email: str, phone: str) -> None:
    require(name=name, email=email)
    execute(
        "INSERT INTO members (name, email, phone) VALUES (?, ?, ?)",
        (name.strip(), email.strip(), phone.strip()),
    )


def update(member_id: int, name: str, email: str, phone: str) -> None:
    require(name=name, email=email)
    execute(
        "UPDATE members SET name=?, email=?, phone=? WHERE id=?",
        (name.strip(), email.strip(), phone.strip(), member_id),
    )


def remove(member_id: int) -> None:
    execute("DELETE FROM members WHERE id=?", (member_id,))
