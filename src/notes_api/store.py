"""Notes store: reads and writes the notes table in the SQLite file."""

import os
import sqlite3
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path

MIGRATIONS = Path(__file__).parent / "migrations"


def db_path() -> str:
    return os.environ.get("NOTES_DB_PATH", "notes.db")


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(db_path())
    conn.row_factory = sqlite3.Row
    return conn


def migrate() -> None:
    """Apply each schema change file NNNN_*.sql above PRAGMA user_version, one transaction per file."""
    with closing(connect()) as conn:
        version = conn.execute("PRAGMA user_version").fetchone()[0]
        for path in sorted(MIGRATIONS.glob("[0-9][0-9][0-9][0-9]_*.sql")):
            number = int(path.name[:4])
            if path.name.endswith(".rollback.sql") or number <= version:
                continue
            conn.executescript(f"BEGIN;\n{path.read_text()}\nPRAGMA user_version = {number};\nCOMMIT;")


def now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def create_note(title: str, body: str) -> dict:
    stamp = now()
    with closing(connect()) as conn, conn:
        cur = conn.execute(
            "INSERT INTO notes (title, body, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (title, body, stamp, stamp),
        )
    return {"id": cur.lastrowid, "title": title, "body": body, "created_at": stamp, "updated_at": stamp}


def get_note(note_id: int) -> dict | None:
    with closing(connect()) as conn:
        row = conn.execute(
            "SELECT id, title, body, created_at, updated_at FROM notes WHERE id = ?", (note_id,)
        ).fetchone()
    return dict(row) if row else None


def list_notes() -> list[dict]:
    with closing(connect()) as conn:
        rows = conn.execute(
            "SELECT id, title, body, created_at, updated_at FROM notes ORDER BY updated_at DESC, id DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def update_note(note_id: int, title: str | None, body: str | None) -> dict | None:
    """Change the given fields; None keeps the old value."""
    with closing(connect()) as conn, conn:
        row = conn.execute(
            "UPDATE notes SET title = COALESCE(?, title), body = COALESCE(?, body), updated_at = ? WHERE id = ?"
            " RETURNING id, title, body, created_at, updated_at",
            (title, body, now(), note_id),
        ).fetchone()
    return dict(row) if row else None


def delete_note(note_id: int) -> bool:
    with closing(connect()) as conn, conn:
        cur = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    return cur.rowcount > 0
