from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "app.db"


@contextmanager
def _get_conn() -> Iterator[sqlite3.Connection]:
    """Yield a DB connection with row_factory set, auto-closing on exit."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
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


def init_db() -> None:
    with _get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS action_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER,
                text TEXT NOT NULL,
                done INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (note_id) REFERENCES notes(id)
            )
            """
        )


# --- Notes ---


def insert_note(content: str) -> int:
    with _get_conn() as conn:
        cursor = conn.execute("INSERT INTO notes (content) VALUES (?)", (content,))
        assert cursor.lastrowid is not None
        return cursor.lastrowid


def list_notes() -> list[sqlite3.Row]:
    with _get_conn() as conn:
        return list(
            conn.execute("SELECT id, content, created_at FROM notes ORDER BY id DESC").fetchall()
        )


def get_note(note_id: int) -> Optional[sqlite3.Row]:
    with _get_conn() as conn:
        return conn.execute(
            "SELECT id, content, created_at FROM notes WHERE id = ?", (note_id,)
        ).fetchone()


# --- Action Items ---


def insert_action_items(items: list[str], note_id: Optional[int] = None) -> list[int]:
    with _get_conn() as conn:
        ids: list[int] = []
        for item in items:
            cursor = conn.execute(
                "INSERT INTO action_items (note_id, text) VALUES (?, ?)",
                (note_id, item),
            )
            assert cursor.lastrowid is not None
            ids.append(cursor.lastrowid)
        return ids


def list_action_items(note_id: Optional[int] = None) -> list[sqlite3.Row]:
    with _get_conn() as conn:
        if note_id is None:
            sql = "SELECT id, note_id, text, done, created_at FROM action_items ORDER BY id DESC"
            return list(conn.execute(sql).fetchall())
        return list(
            conn.execute(
                "SELECT id, note_id, text, done, created_at FROM action_items "
                "WHERE note_id = ? ORDER BY id DESC",
                (note_id,),
            ).fetchall()
        )


def get_action_item(action_item_id: int) -> Optional[sqlite3.Row]:
    with _get_conn() as conn:
        return conn.execute(
            "SELECT id, note_id, text, done, created_at FROM action_items WHERE id = ?",
            (action_item_id,),
        ).fetchone()


def mark_action_item_done(action_item_id: int, done: bool) -> int:
    """Update done status. Returns the number of rows affected."""
    with _get_conn() as conn:
        cursor = conn.execute(
            "UPDATE action_items SET done = ? WHERE id = ?",
            (1 if done else 0, action_item_id),
        )
        return cursor.rowcount


