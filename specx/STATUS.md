# Status

Where the project stands, for the user to read at a glance. The main session updates this file whenever a task, milestone, or decision changes. Task details live in the specs; if this file and a spec disagree, the spec is the record, and the difference is a problem to fix.

## Now

The roadmap is in [spec.md](spec.md), section 8. The user approved the root spec version 2 and the NOTES spec version 1. The user approved tasks NOTES-T1 and NOTES-T2. An agent built NOTES-T1 (NOTES-M1) on `specx/delivery-NOTES`. An independent agent now reviews it.

## Waiting on you

Nothing right now.
- ROOT-D4 (hosting) is open: [spec.md](spec.md), section 9. The DEPLOY phase needs it; the Core stage does not.

## Roadmap

| Stage | Phase | Milestone | Progress | Version |
|---|---|---|---|---|
| Core | NOTES | NOTES-M1: create and read a note | in progress | 0.0.1 |
| Core | NOTES | NOTES-M2: list, change, and delete notes | planned | 0.0.1 |
| Essentials | SEARCH, TAGS, EXPORT | — | later | 0.1.0 |
| Production | DEPLOY | — | later | 1.0.0 |

## Assumptions to check

Implementation details agents chose on their own since the last demo. Overturn any of them at the demo.

| Assumption | Why | Task |
|---|---|---|
| The project has no build backend. pytest and uvicorn find the code in `src` directly. | A build backend is a dependency that ROOT §6.2 does not list. | NOTES-T1 |
| `pydantic==2.14.3` is a direct dependency. | The code imports Pydantic, and ROOT §6.2 gives its version. | NOTES-T1 |
| `pyproject.toml` requires uv 0.12.23. | ROOT §6.2 gives this version. | NOTES-T1 |
| SQLite `PRAGMA user_version` records the last applied schema change. | The schema needs no extra table for this. | NOTES-T1 |
| The rollback file also sets `user_version` to 0. The owner runs it with the `sqlite3` tool. | Then the next start applies schema change 1 again (§6.13). | NOTES-T1 |
| The API opens one SQLite connection for each operation. It reads `NOTES_DB_PATH` when it opens the connection. | Each test can then use its own file. | NOTES-T1 |
| Pydantic validates the fields. A `null` value or a value that is not text gets 422. | Pydantic does this without custom code. | NOTES-T1 |
| FastAPI sends the 500 error. The code has no custom error handler. | ROOT §6.7 gives no other format. | NOTES-T1 |
| The CI workflow runs on each pull request with `uv run --locked pytest`. | `--locked` also stops CI if `uv.lock` is old. | NOTES-T1 |
| `.gitignore` ignores all `*.db` files. | Test and local database files must not go into git. | NOTES-T1 |
| The README start command gives `--host 127.0.0.1 --port 8000`. | The command then shows the values of ROOT §6.8 and §6.9. | NOTES-T1 |

## Latest review

None yet.
