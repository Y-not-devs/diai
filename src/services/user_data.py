"""SQLite-based storage for chats and messages."""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DB_PATH = Path("./data/app.db")


def _get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create tables if they don't exist."""
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                chat_id    TEXT PRIMARY KEY,
                user_id    TEXT NOT NULL,
                chat_name  TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                message_id  INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id     TEXT NOT NULL,
                role        TEXT NOT NULL,
                text        TEXT NOT NULL,
                answer_type INTEGER,
                diagnosis   TEXT,
                created_at  TEXT NOT NULL,
                FOREIGN KEY (chat_id) REFERENCES chats(chat_id)
            )
        """)
        conn.commit()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_or_update_chat(chat_id: str, user_id: str, chat_name: str) -> None:
    """Insert chat if it doesn't exist, or update its timestamp."""
    with _get_conn() as conn:
        conn.execute("""
            INSERT INTO chats (chat_id, user_id, chat_name, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(chat_id) DO UPDATE SET updated_at = excluded.updated_at
        """, (chat_id, user_id, chat_name, _now_iso()))
        conn.commit()


def get_chats(user_id: str) -> list[dict]:
    """Return all chats for a user, newest first."""
    with _get_conn() as conn:
        rows = conn.execute("""
            SELECT chat_id, chat_name, updated_at
            FROM chats
            WHERE user_id = ?
            ORDER BY updated_at DESC
        """, (user_id,)).fetchall()
    return [dict(r) for r in rows]


def save_message(
    chat_id: str,
    role: str,
    text: str,
    answer_type: Optional[int],
    diagnosis: Optional[list],
) -> Optional[int]:
    """Save a message and return its auto-generated message_id."""
    diag_json = json.dumps(diagnosis, ensure_ascii=False) if diagnosis is not None else None
    with _get_conn() as conn:
        cursor = conn.execute("""
            INSERT INTO messages (chat_id, role, text, answer_type, diagnosis, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (chat_id, role, text, answer_type, diag_json, _now_iso()))
        conn.commit()
        return cursor.lastrowid


def get_messages(
    chat_id: str,
    limit: int,
    before_id: Optional[int] = None,
) -> tuple[list[dict], bool, Optional[int]]:
    """
    Return up to `limit` messages for a chat, newest first.
    If `before_id` is provided, only return messages older than that id.

    Returns:
        (messages_asc, has_more, min_message_id)
        - messages_asc: messages sorted oldest→newest (ready to display)
        - has_more: True if there are older messages beyond this page
        - min_message_id: smallest message_id in this batch (use as next before_id)
    """
    with _get_conn() as conn:
        if before_id is not None:
            rows = conn.execute("""
                SELECT * FROM messages
                WHERE chat_id = ? AND message_id < ?
                ORDER BY message_id DESC
                LIMIT ?
            """, (chat_id, before_id, limit + 1)).fetchall()
        else:
            rows = conn.execute("""
                SELECT * FROM messages
                WHERE chat_id = ?
                ORDER BY message_id DESC
                LIMIT ?
            """, (chat_id, limit + 1)).fetchall()

    has_more = len(rows) > limit
    rows = rows[:limit]

    result = []
    for r in rows:
        d = dict(r)
        if d.get("diagnosis"):
            d["diagnosis"] = json.loads(d["diagnosis"])
        result.append(d)

    # Return in ascending order so frontend displays oldest→newest
    result.reverse()

    min_id = result[0]["message_id"] if result else None
    return result, has_more, min_id