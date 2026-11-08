import re
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from notes_api import store
from notes_api.main import app

STAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def count_notes(db_path):
    with sqlite3.connect(db_path) as conn:
        return conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0]


def test_ac1_create_trims_title_and_read_back(client):
    r = client.post("/notes", json={"title": "  Shopping  ", "body": "Milk"})
    assert r.status_code == 201
    note = r.json()
    assert note["id"] == 1
    assert note["title"] == "Shopping"
    assert note["body"] == "Milk"
    assert STAMP.match(note["created_at"])
    assert note["created_at"] == note["updated_at"]

    r = client.get("/notes/1")
    assert r.status_code == 200
    assert r.json() == note


def test_ac2_body_defaults_to_empty(client):
    r = client.post("/notes", json={"title": "Idea"})
    assert r.status_code == 201
    assert r.json()["body"] == ""


def test_body_spaces_are_kept_and_unknown_fields_ignored(client):
    r = client.post("/notes", json={"title": "T", "body": "  x  ", "color": "red"})
    assert r.status_code == 201
    assert r.json()["body"] == "  x  "
    assert "color" not in r.json()


def test_limits_are_accepted(client):
    r = client.post("/notes", json={"title": "a" * 200, "body": "b" * 10000})
    assert r.status_code == 201


def test_ac6_get_missing_note(client):
    r = client.get("/notes/99")
    assert r.status_code == 404
    assert r.json() == {"detail": "Note not found"}


def test_get_non_integer_id(client):
    r = client.get("/notes/abc")
    assert r.status_code == 422
    assert isinstance(r.json()["detail"], list)


@pytest.mark.parametrize(
    "payload",
    [
        {"title": "   "},
        {"title": "a" * 201},
        {"body": "no title"},
        {"title": "Ok", "body": "b" * 10001},
        {"title": None},
        {"title": "Ok", "body": None},
        {"title": 5},
    ],
    ids=["blank-title", "title-201", "no-title", "body-10001", "null-title", "null-body", "int-title"],
)
def test_ac7_invalid_create_changes_no_data(client, db_path, payload):
    r = client.post("/notes", json=payload)
    assert r.status_code == 422
    assert isinstance(r.json()["detail"], list)
    assert count_notes(db_path) == 0


def test_ac9_note_survives_restart(db_path):
    with TestClient(app) as c:
        note = c.post("/notes", json={"title": "Keep", "body": "me"}).json()
    with TestClient(app) as c:
        r = c.get("/notes/1")
    assert r.status_code == 200
    assert r.json() == note


def test_schema_change_rollback_and_reapply(db_path):
    store.migrate()
    rollback = Path(store.MIGRATIONS, "0001_create_notes.rollback.sql").read_text()
    with sqlite3.connect(db_path) as conn:
        conn.executescript(rollback)
        assert conn.execute("SELECT name FROM sqlite_master WHERE name LIKE 'notes%'").fetchall() == []
    store.migrate()
    assert count_notes(db_path) == 0
