import sqlite3
from contextlib import contextmanager

from .config import DB_PATH


@contextmanager
def _connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def fetch_all(sql: str, params: tuple = ()) -> list[dict]:
    with _connection() as conn:
        return [dict(row) for row in conn.execute(sql, params)]


def execute(sql: str, params: tuple = ()) -> int:
    with _connection() as conn:
        return conn.execute(sql, params).rowcount


def execute_many(sql: str, rows: list[tuple]) -> int:
    with _connection() as conn:
        return conn.executemany(sql, rows).rowcount
