# specx-example

A small notes API built with [SpecX](https://github.com/WIRIN-prod/specx), as a worked example: its specs, decisions, status, reviews, and pull requests are all here.

## Notes API

A JSON API for personal notes. It stores notes in one SQLite file and listens on `127.0.0.1:8000` only. It has no authentication.

### Install

Install [uv](https://docs.astral.sh/uv/) 0.12.23. Then run this command in the repository folder:

```sh
uv sync
```

uv installs Python 3.14 if necessary.

### Start the API

```sh
uv run uvicorn notes_api.main:app --app-dir src --host 127.0.0.1 --port 8000
```

The API stores notes in `notes.db` in the current folder. To use a different file, set `NOTES_DB_PATH`:

```sh
NOTES_DB_PATH=/path/to/my-notes.db uv run uvicorn notes_api.main:app --app-dir src --host 127.0.0.1 --port 8000
```

At start, the API applies new schema changes from `src/notes_api/migrations/`. Each change has a rollback file. To undo schema change 1, stop the API and run:

```sh
sqlite3 notes.db < src/notes_api/migrations/0001_create_notes.rollback.sql
```

This deletes all notes.

### Use the API

Create a note. `title` is required (1 to 200 characters after the API removes spaces at the start and the end). `body` is optional (not more than 10000 characters).

```sh
curl -X POST http://127.0.0.1:8000/notes -H 'Content-Type: application/json' -d '{"title": "Shopping", "body": "Milk"}'
```

Read a note:

```sh
curl http://127.0.0.1:8000/notes/1
```

An ID that does not exist gets status 404 with `{"detail": "Note not found"}`. Incorrect data gets status 422.

### Run the tests

```sh
uv run pytest
```
