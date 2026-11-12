from datetime import datetime
from typing import Optional

import libsql_client

from config import TURSO_AUTH_TOKEN, TURSO_DATABASE_URL

_client: Optional[libsql_client.Client] = None


def get_client() -> libsql_client.Client:
    global _client
    if _client is None:
        _client = libsql_client.create_client(
            url=TURSO_DATABASE_URL, auth_token=TURSO_AUTH_TOKEN
        )
    return _client


async def close_db() -> None:
    global _client
    if _client is not None:
        await _client.close()
        _client = None


async def init_db() -> None:
    client = get_client()
    await client.execute(
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
    await client.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_registrations_telegram_id
        ON registrations(telegram_id) WHERE telegram_id IS NOT NULL
        """
    )


async def is_registered(telegram_id: int) -> bool:
    client = get_client()
    rs = await client.execute(
        "SELECT 1 FROM registrations WHERE telegram_id = ?", [telegram_id]
    )
    return len(rs.rows) > 0


async def add_registration(
    full_name: str,
    district: str,
    school: str,
    grade: int,
    parent_phone: str,
    telegram_id: Optional[int] = None,
    registered_by_admin: bool = False,
    admin_id: Optional[int] = None,
) -> None:
    client = get_client()
    await client.execute(
        """
        INSERT INTO registrations
            (telegram_id, full_name, district, school, grade, parent_phone,
             registered_by_admin, admin_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            telegram_id,
            full_name,
            district,
            school,
            grade,
            parent_phone,
            1 if registered_by_admin else 0,
            admin_id,
            datetime.now().isoformat(timespec="seconds"),
        ],
    )


async def get_all_registrations() -> list[tuple]:
    client = get_client()
    rs = await client.execute(
        """
        SELECT full_name, district, school, grade, parent_phone,
               registered_by_admin, created_at
        FROM registrations ORDER BY id
        """
    )
    return [row.astuple() for row in rs.rows]


async def count_registrations() -> int:
    client = get_client()
    rs = await client.execute("SELECT COUNT(*) FROM registrations")
    return rs.rows[0][0]
