# Status

Where the project stands, for the user to read at a glance. The main session updates this file whenever a task, milestone, or decision changes. Task details live in the specs; if this file and a spec disagree, the spec is the record, and the difference is a problem to fix.

## Now

The roadmap is in [spec.md](spec.md), section 8. The user approved the root spec version 4 and the NOTES spec version 4. Agents built NOTES-T1, NOTES-T3, and NOTES-T4 (NOTES-M1) on `specx/delivery-NOTES`. Independent agents reviewed each change. At the NOTES-M1 demo, the user chose to continue to NOTES-M2. The user approved the NOTES-M2 preview. An agent built NOTES-T2. An independent agent reviewed NOTES-M2. The NOTES-M2 demo waits for the user.

## Waiting on you

- Choose the body of the `No fields to change` 422 error (NOTES-M2 review F1).
- ROOT-D4 (hosting) is open: [spec.md](spec.md), section 9. The DEPLOY phase needs it; the Core stage does not.

## Roadmap

| Stage | Phase | Milestone | Progress | Version |
|---|---|---|---|---|
| Core | NOTES | NOTES-M1: create and read a note | demo done; waits for the phase pull request | 0.0.1 |
| Core | NOTES | NOTES-M2: list, change, and delete notes | in progress | 0.0.1 |
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
| The error handler catches each `Exception`, not only `sqlite3.Error`. | ROOT §6.3 gives one body for all 500 errors. | NOTES-T3 |
| Starlette raises the error again after the handler sends the response. | uvicorn then writes the error to the log (ROOT §6.7). | NOTES-T3 |
| The NOTES-AC10 test makes the database file read-only after the start. | The API can then only read the file. | NOTES-T3 |
| The NOTES-AC10 test also checks that the number of notes stays 1. | The test shows that the failed write changes no data. | NOTES-T3 |
| The NOTES-AC11 test starts uvicorn as a separate process. | The test sees the real exit code and log. | NOTES-T3 |
| The NOTES-AC11 test checks for a non-zero exit code and two log lines. | These show that the API wrote the error and stopped. | NOTES-T3 |
| The leak test causes errors with a database that has no `notes` table. | The failure then does not depend on file mode or root. | NOTES-T4 |
| The failed `migrate` uses a file that is not a SQLite database. | `connect` succeeds, and the first `PRAGMA` then fails. | NOTES-T4 |
| Each failure case must raise `sqlite3.DatabaseError`. | If a call does not fail, the test does not check the failure path. | NOTES-T4 |
| The root skip also checks that `os.geteuid` exists. | Windows does not have `os.geteuid`. | NOTES-T4 |
| One SQL `UPDATE … RETURNING` statement changes the note and reads it. | The change and the read are then in one transaction. | NOTES-T2 |

## Latest review

[2026-11-09-NOTES-M2.md](_reviews/2026-11-09-NOTES-M2.md)
