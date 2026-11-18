import gc
import os
import re
import sqlite3
import subprocess
import sys
from contextlib import closing
import warnings
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from notes_api import store
from notes_api.main import app

SRC = Path(__file__).resolve().parent.parent / "src"
STAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def count_notes(db_path):
    with closing(sqlite3.connect(db_path)) as conn:
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


def test_title_tabs_and_line_breaks_are_removed(client):
    r = client.post("/notes", json={"title": "\t\n Shopping \r\n\t"})
    assert r.status_code == 201
    assert r.json()["title"] == "Shopping"


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


def set_updated_at(db_path, note_id, stamp):
    with closing(sqlite3.connect(db_path)) as conn, conn:
        conn.execute("UPDATE notes SET updated_at = ? WHERE id = ?", (stamp, note_id))


def test_list_empty(client):
    r = client.get("/notes")
    assert r.status_code == 200
    assert r.json() == []


def test_ac3_list_latest_updated_first(client, db_path):
    client.post("/notes", json={"title": "One"})
    client.post("/notes", json={"title": "Two"})
    set_updated_at(db_path, 1, "2026-11-08T10:00:00Z")
    set_updated_at(db_path, 2, "2026-11-08T11:00:00Z")
    r = client.get("/notes")
    assert r.status_code == 200
    assert [n["id"] for n in r.json()] == [2, 1]
    assert r.json()[0] == client.get("/notes/2").json()


def test_list_same_updated_at_higher_id_first(client, db_path):
    for title in ("One", "Two", "Three"):
        client.post("/notes", json={"title": title})
    for note_id in (1, 2, 3):
        set_updated_at(db_path, note_id, "2026-11-08T10:00:00Z")
    set_updated_at(db_path, 1, "2026-11-08T12:00:00Z")
    assert [n["id"] for n in client.get("/notes").json()] == [1, 3, 2]


def test_ac4_patch_changes_only_given_fields(client, db_path):
    client.post("/notes", json={"title": "Old", "body": "Text"})
    set_updated_at(db_path, 1, "2000-01-01T00:00:00Z")
    r = client.patch("/notes/1", json={"title": "  New  "})
    assert r.status_code == 200
    note = r.json()
    assert note["title"] == "New"
    assert note["body"] == "Text"
    assert STAMP.match(note["updated_at"])
    assert note["updated_at"] >= note["created_at"]
    assert client.get("/notes/1").json() == note


def test_patch_body_only_keeps_spaces(client):
    client.post("/notes", json={"title": "Old", "body": "Text"})
    r = client.patch("/notes/1", json={"body": "  x  "})
    assert r.status_code == 200
    assert r.json()["title"] == "Old"
    assert r.json()["body"] == "  x  "


def test_ac8_patch_no_fields(client):
    note = client.post("/notes", json={"title": "Old", "body": "Text"}).json()
    for payload in ({}, {"color": "red"}):
        r = client.patch("/notes/1", json=payload)
        assert r.status_code == 422
        assert r.json() == {
            "detail": [{"type": "value_error", "loc": ["body"], "msg": "No fields to change", "input": payload}]
        }
    assert client.get("/notes/1").json() == note


@pytest.mark.parametrize(
    "payload",
    [
        {"title": "   "},
        {"title": "a" * 201},
        {"body": "b" * 10001},
        {"title": None},
        {"body": None},
        {"title": 5},
        {"title": "Ok", "body": None},
    ],
    ids=["blank-title", "title-201", "body-10001", "null-title", "null-body", "int-title", "ok-title-null-body"],
)
def test_invalid_patch_changes_no_data(client, payload):
    note = client.post("/notes", json={"title": "Old", "body": "Text"}).json()
    r = client.patch("/notes/1", json=payload)
    assert r.status_code == 422
    assert isinstance(r.json()["detail"], list)
    assert client.get("/notes/1").json() == note


def test_patch_title_and_body(client):
    client.post("/notes", json={"title": "Old", "body": "Text"})
    r = client.patch("/notes/1", json={"title": "New", "body": "Other"})
    assert r.status_code == 200
    assert (r.json()["title"], r.json()["body"]) == ("New", "Other")
    assert client.get("/notes/1").json() == r.json()


def test_patch_no_fields_unknown_id_is_422(client):
    r = client.patch("/notes/99", json={})
    assert r.status_code == 422
    assert r.json()["detail"][0]["msg"] == "No fields to change"


def test_patch_keeps_created_at(client, db_path):
    client.post("/notes", json={"title": "Old"})
    with closing(sqlite3.connect(db_path)) as conn, conn:
        conn.execute("UPDATE notes SET created_at = '2000-01-01T00:00:00Z', updated_at = created_at WHERE id = 1")
    r = client.patch("/notes/1", json={"title": "New"})
    assert r.json()["created_at"] == "2000-01-01T00:00:00Z"
    assert r.json()["updated_at"] != "2000-01-01T00:00:00Z"


def test_second_delete_is_404(client):
    client.post("/notes", json={"title": "Gone"})
    assert client.delete("/notes/1").status_code == 204
    r = client.delete("/notes/1")
    assert r.status_code == 404
    assert r.json() == {"detail": "Note not found"}


def test_ac5_delete(client):
    client.post("/notes", json={"title": "Gone"})
    r = client.delete("/notes/1")
    assert r.status_code == 204
    assert r.content == b""
    r = client.get("/notes/1")
    assert r.status_code == 404
    assert r.json() == {"detail": "Note not found"}
    assert client.get("/notes").json() == []


@pytest.mark.parametrize(
    "method, kwargs",
    [("get", {}), ("patch", {"json": {"title": "A"}}), ("delete", {})],
)
def test_ac6_missing_note(client, method, kwargs):
    r = client.request(method, "/notes/99", **kwargs)
    assert r.status_code == 404
    assert r.json() == {"detail": "Note not found"}


@pytest.mark.parametrize("method", ["patch", "delete"])
def test_patch_delete_non_integer_id(client, method):
    r = client.request(method, "/notes/abc", json={"title": "A"})
    assert r.status_code == 422
    assert isinstance(r.json()["detail"], list)


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
    with closing(sqlite3.connect(db_path)) as conn:
        conn.executescript(rollback)
        assert conn.execute("SELECT name FROM sqlite_master WHERE name LIKE 'notes%'").fetchall() == []
    store.migrate()
    assert count_notes(db_path) == 0


@pytest.mark.skipif(hasattr(os, "geteuid") and os.geteuid() == 0, reason="root can write to a read-only file")
def test_ac10_database_error_after_start(db_path):
    with TestClient(app, raise_server_exceptions=False) as c:
        assert c.post("/notes", json={"title": "First"}).status_code == 201
        db_path.chmod(0o444)  # the API can only read the file now
        r = c.post("/notes", json={"title": "A"})
    assert r.status_code == 500
    assert r.json() == {"detail": "Internal Server Error"}
    assert count_notes(db_path) == 1


@pytest.mark.skipif(hasattr(os, "geteuid") and os.geteuid() == 0, reason="root can write to a read-only file")
@pytest.mark.parametrize("method, kwargs", [("patch", {"json": {"title": "A"}}), ("delete", {})])
def test_patch_delete_database_error_after_start(db_path, method, kwargs):
    with TestClient(app, raise_server_exceptions=False) as c:
        note = c.post("/notes", json={"title": "First"}).json()
        db_path.chmod(0o444)  # the API can only read the file now
        r = c.request(method, "/notes/1", **kwargs)
        assert c.get("/notes/1").json() == note
    assert r.status_code == 500
    assert r.json() == {"detail": "Internal Server Error"}


def test_ac11_start_fails_when_database_cannot_open(tmp_path):
    env = {"NOTES_DB_PATH": str(tmp_path / "missing" / "notes.db")}
    result = subprocess.run(
        [sys.executable, "-m", "uvicorn", "notes_api.main:app", "--app-dir", str(SRC), "--port", "0"],
        env=env, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode != 0
    assert "unable to open database file" in result.stderr
    assert "Application startup failed" in result.stderr


def test_store_closes_connections_leak(db_path):
    def fails(call):
        with pytest.raises(sqlite3.DatabaseError):
            call()

    gc.collect()  # earlier tests' leaks must not count here
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        store.migrate()
        note = store.create_note("T", "B")
        assert store.get_note(note["id"]) == note
        assert store.get_note(99) is None
        assert store.list_notes() == [note]
        assert store.update_note(note["id"], "T2", None)["title"] == "T2"
        assert store.update_note(99, "T2", None) is None
        assert store.delete_note(note["id"]) is True
        assert store.delete_note(note["id"]) is False

        db_path.unlink()
        sqlite3.connect(db_path).close()  # an empty database with no notes table
        fails(lambda: store.create_note("T", "B"))
        fails(lambda: store.get_note(1))
        fails(store.list_notes)
        fails(lambda: store.update_note(1, "T", None))
        fails(lambda: store.delete_note(1))

        db_path.write_bytes(b"not a database" * 100)
        fails(store.migrate)

        gc.collect()  # each open connection gives its warning now
    leaks = [str(w.message) for w in caught if "unclosed database" in str(w.message)]
    assert leaks == []
