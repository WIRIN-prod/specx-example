import pytest
from fastapi.testclient import TestClient

from notes_api.main import app


@pytest.fixture
def db_path(tmp_path, monkeypatch):
    path = tmp_path / "notes.db"
    monkeypatch.setenv("NOTES_DB_PATH", str(path))
    return path


@pytest.fixture
def client(db_path):
    with TestClient(app) as c:  # the context runs the startup schema changes
        yield c
