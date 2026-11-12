import sqlite3
from contextlib import contextmanager
from datetime import datetime

DB_PATH = "olimpiada.db"


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER,
                full_name TEXT NOT NULL,
                district TEXT NOT NULL,
                school TEXT NOT NULL,
                grade INTEGER NOT NULL,
                parent_phone TEXT NOT NULL,
                registered_by_admin INTEGER NOT NULL DEFAULT 0,
                admin_id INTEGER,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_registrations_telegram_id
            ON registrations(telegram_id) WHERE telegram_id IS NOT NULL
            """
        )
        conn.commit()


def is_registered(telegram_id: int) -> bool:
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT 1 FROM registrations WHERE telegram_id = ?", (telegram_id,)
        )
        return cur.fetchone() is not None


def add_registration(
    full_name: str,
    district: str,
    school: str,
    grade: int,
    parent_phone: str,
    telegram_id: int | None = None,
    registered_by_admin: bool = False,
    admin_id: int | None = None,
) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO registrations
                (telegram_id, full_name, district, school, grade, parent_phone,
                 registered_by_admin, admin_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                telegram_id,
                full_name,
                district,
                school,
                grade,
                parent_phone,
                1 if registered_by_admin else 0,
                admin_id,
                datetime.now().isoformat(timespec="seconds"),
            ),
        )
        conn.commit()


def get_all_registrations() -> list[tuple]:
    with get_conn() as conn:
        cur = conn.execute(
            """
            SELECT full_name, district, school, grade, parent_phone,
                   registered_by_admin, created_at
            FROM registrations ORDER BY id
            """
        )
        return cur.fetchall()


def count_registrations() -> int:
    with get_conn() as conn:
        cur = conn.execute("SELECT COUNT(*) FROM registrations")
        return cur.fetchone()[0]
