---
id: NOTES
title: Notes
status: approved
version: 5
parent: ROOT
depends_on: []
---

# NOTES: Notes

## 1. Overview

**Purpose:** The owner creates, reads, changes, deletes, and lists notes through a JSON API. Each note has a title and a body. This phase is the Core stage, version 0.0.1.

**In scope:**

- The five endpoints in §6.3.
- The `notes` table in SQLite.
- Integration tests and a GitHub Actions workflow for the tests.

**Out of scope:**

- Search. SEARCH owns it.
- Tags. TAGS owns it.
- Export and import. EXPORT owns it.
- Hosting, logs, and backups. DEPLOY owns them.

## 2. Context chain

Inherits everything in [specx/spec.md](../spec.md).

**Overrides:** None.

## 3. Current state

None: new work. The repository has only `README.md` and the SpecX files.

## 4. Requirements

| ID | Type | Requirement | Source |
|---|---|---|---|
| NOTES-R1 | Functional | WHEN the owner sends `POST /notes` with a correct title and body, THE SYSTEM SHALL save the note and send it back with status 201. | user, 2026-11-07 |
| NOTES-R2 | Functional | WHEN the owner sends `GET /notes/{id}` for a saved note, THE SYSTEM SHALL send that note with status 200. | user, 2026-11-07 |
| NOTES-R3 | Functional | WHEN the owner sends `GET /notes`, THE SYSTEM SHALL send all notes with status 200, with the latest `updated_at` first. | NOTES-D3 |
| NOTES-R4 | Functional | WHEN the owner sends `PATCH /notes/{id}` with correct fields, THE SYSTEM SHALL change only those fields and `updated_at`, and send status 200. | user, 2026-11-07; ROOT-D12 |
| NOTES-R5 | Functional | WHEN the owner sends `DELETE /notes/{id}` for a saved note, THE SYSTEM SHALL delete the note and send status 204 with no body. | user, 2026-11-07 |
| NOTES-R6 | Functional | IF a request names an ID that does not exist, THEN THE SYSTEM SHALL send status 404 with `{"detail": "Note not found"}`. | ROOT-D11, ROOT-D12 |
| NOTES-R7 | Validation | IF the trimmed title has fewer than 1 or more than 200 characters, THEN THE SYSTEM SHALL send status 422 and change no data. | NOTES-D2 |
| NOTES-R8 | Validation | IF the body has more than 10000 characters, THEN THE SYSTEM SHALL send status 422 and change no data. | NOTES-D2 |
| NOTES-R9 | Validation | IF a `PATCH` request has no `title` and no `body`, THEN THE SYSTEM SHALL send status 422 with the message `No fields to change`. | ROOT-D12 |
| NOTES-R11 | Resilience | IF the API cannot read or write the SQLite file after the start, THEN THE SYSTEM SHALL send status 500 with `{"detail": "Internal Server Error"}`. | ROOT-D19 |
| NOTES-R12 | Resilience | IF the API cannot open the SQLite file at start, THEN THE SYSTEM SHALL write the error to the log and stop. | ROOT-D16 |
| NOTES-R10 | Data | THE SYSTEM SHALL keep the notes in the SQLite file after the API stops and starts again. | ROOT-D2 |

## 5. Acceptance criteria

**NOTES-AC1** (R1, R2) · integration

- Given an empty database
- When the owner sends `POST /notes` with `{"title": "  Shopping  ", "body": "Milk"}`
- Then the status is 201, and the response has `id` 1, `title` `"Shopping"`, `body` `"Milk"`, and the same value in `created_at` and `updated_at`
- And `GET /notes/1` sends the same note with status 200

**NOTES-AC2** (R1) · integration

- Given an empty database
- When the owner sends `POST /notes` with `{"title": "Idea"}`
- Then the status is 201 and `body` is `""`

**NOTES-AC3** (R3) · integration

- Given note 1 with `updated_at` `2026-11-08T10:00:00Z` and note 2 with `updated_at` `2026-11-08T11:00:00Z`
- When the owner sends `GET /notes`
- Then the status is 200 and the list has note 2, then note 1

**NOTES-AC4** (R4) · integration

- Given note 1 with title `"Old"` and body `"Text"`
- When the owner sends `PATCH /notes/1` with `{"title": "New"}`
- Then the status is 200, the title is `"New"`, the body is `"Text"`, and `updated_at` is not earlier than `created_at`

**NOTES-AC5** (R5, R6) · integration

- Given note 1
- When the owner sends `DELETE /notes/1`
- Then the status is 204 with no body, and `GET /notes/1` sends 404 with `{"detail": "Note not found"}`

**NOTES-AC6** (R6) · integration

- Given an empty database
- When the owner sends `GET /notes/99`, `PATCH /notes/99` with `{"title": "A"}`, or `DELETE /notes/99`
- Then each status is 404 with `{"detail": "Note not found"}`

**NOTES-AC7** (R7, R8) · integration

- Given an empty database
- When the owner sends `POST /notes` with a title of `"   "`, a title of 201 characters, no title, or a body of 10001 characters
- Then each status is 422 and the database has no notes

**NOTES-AC8** (R9) · integration

- Given note 1
- When the owner sends `PATCH /notes/1` with `{}`
- Then the status is 422, the response has `No fields to change`, and note 1 does not change

**NOTES-AC9** (R10) · integration

- Given a database file with note 1
- When the API stops and starts again with the same `NOTES_DB_PATH`
- Then `GET /notes/1` sends note 1

**NOTES-AC10** (R11) · integration

- Given note 1 in a database file that the API can only read
- When the owner sends `POST /notes` with `{"title": "A"}`
- Then the status is 500 and the body is `{"detail": "Internal Server Error"}`

**NOTES-AC11** (R12) · integration

- Given `NOTES_DB_PATH` in a folder that does not exist
- When the API starts
- Then the start fails with an error, and the API does not accept requests

## 6. Design

### 6.1 Architecture

Inherited: ROOT §6.1. The API has one part for HTTP and one part for the `notes` table.

| Component | Responsibility | Talks to |
|---|---|---|
| Notes API | Receives requests, validates data, sends responses and errors | Notes store |
| Notes store | Reads and writes the `notes` table | SQLite file |

### 6.2 Technology

Inherited: ROOT §6.2. This phase adds nothing.

### 6.3 Interfaces

A **note** in a response has these fields:

| Field | Type | Rules |
|---|---|---|
| `id` | integer | Given by SQLite |
| `title` | string | 1 to 200 characters, with no spaces at the start or the end |
| `body` | string | 0 to 10000 characters |
| `created_at` | string | UTC time, `YYYY-MM-DDTHH:MM:SSZ` |
| `updated_at` | string | UTC time, `YYYY-MM-DDTHH:MM:SSZ` |

**`POST /notes`**: creates a note.

| Input | Type | Rules |
|---|---|---|
| `title` | string | Required. The system removes whitespace (spaces, tabs, and line breaks) at the start and the end. Then the title must have 1 to 200 characters. |
| `body` | string | Optional. The default is `""`. Not more than 10000 characters. The system does not remove spaces. |

Response: status 201 and the new note. `created_at` and `updated_at` have the same value.

**`GET /notes/{id}`**: sends one note. `id` is an integer. Response: status 200 and the note.

**`GET /notes`**: sends all notes. Response: status 200 and a JSON list of notes, with the latest `updated_at` first. If two notes have the same `updated_at`, the note with the higher `id` is first. An empty database gives `[]`.

**`PATCH /notes/{id}`**: changes a note.

| Input | Type | Rules |
|---|---|---|
| `title` | string | Optional. The same rules as in `POST /notes`. |
| `body` | string | Optional. The same rules as in `POST /notes`. |

Response: status 200 and the changed note. `updated_at` is the time of the change. A `null` value for a field gets status 422.

**`DELETE /notes/{id}`**: deletes a note. Response: status 204 with no body.

**Errors** (ROOT-D11):

| Status | When | Body |
|---|---|---|
| 404 | The ID does not exist | `{"detail": "Note not found"}` |
| 422 | A field breaks a rule, or `id` in the path is not an integer | The FastAPI list of field errors in `detail` |
| 422 | A `PATCH` request has no `title` and no `body` | The FastAPI list of field errors in `detail`, with one item: `{"type": "value_error", "loc": ["body"], "msg": "No fields to change", "input": <the request body>}` (NOTES-D6) |
| 500 | The API cannot read or write the SQLite file | `{"detail": "Internal Server Error"}` |

### 6.4 Data model

`notes`: one row for each note.

| Field | Type | Null | Default | Notes |
|---|---|---|---|---|
| `id` | INTEGER | no | given by SQLite | Primary key, `AUTOINCREMENT`, so the system does not use the ID of a deleted note again |
| `title` | TEXT | no | — | 1 to 200 characters |
| `body` | TEXT | no | `''` | 0 to 10000 characters |
| `created_at` | TEXT | no | — | UTC, `YYYY-MM-DDTHH:MM:SSZ` |
| `updated_at` | TEXT | no | — | UTC, `YYYY-MM-DDTHH:MM:SSZ`; indexed for the list order |

Schema change 1: create `notes` and its index on `updated_at`. Rollback: drop the index and `notes`.

### 6.5 Flows

1. The owner sends a request.
2. FastAPI validates the path and the body. If the data is not correct, the API sends 422.
3. The API reads or writes the `notes` table in one SQLite transaction.
4. If the note does not exist, the API sends 404. If not, the API sends the result.

### 6.6 State and lifecycle

None: a note has no states. It exists until the owner deletes it.

### 6.7 Error handling and resilience

Inherited: ROOT §6.7.

### 6.8 Security and privacy

Inherited: ROOT §6.8.

### 6.9 Configuration

Inherited: ROOT §6.9.

### 6.10 Observability

Inherited: ROOT §6.10.

### 6.11 Performance and limits

- A title has not more than 200 characters. A body has not more than 10000 characters (NOTES-D2).
- A list has no pagination (NOTES-D3).
- Speed targets: Deferred: DEPLOY.

### 6.12 Testing strategy

Inherited: ROOT §6.12. Each acceptance criterion has one or more integration tests. Each test uses a new SQLite file in a temporary folder through `NOTES_DB_PATH`.

### 6.13 Migration and rollout

Schema change 1 runs when the API starts for the first time. Rollback: stop the API and delete the database file, or apply the rollback of schema change 1.

## 7. Shared with children

None: no children.

## 8. Children

None.

## 9. Decisions

### NOTES-D1: Note ID

- **Status:** answered (2026-11-08)
- **Question:** What format do note IDs have?
- **Answer:** "Integer, 1, 2, 3… (Recommended)". (user, 2026-11-08)
- **Affects:** §6.3, §6.4

### NOTES-D2: Field rules

- **Status:** answered (2026-11-08)
- **Question:** What rules apply to the fields of a note?
- **Answer:** "Title required, limits (Recommended)": the title is required, with 1 to 200 characters after the system removes spaces. The body is optional, with not more than 10000 characters. A break gets 422. The server sets `created_at` and `updated_at` in UTC. (user, 2026-11-08)
- **Affects:** NOTES-R7, NOTES-R8, §6.3, §6.4

### NOTES-D3: List order

- **Status:** answered (2026-11-08)
- **Question:** How does `GET /notes` send the list?
- **Answer:** "Newest first, no paging (Recommended)". (user, 2026-11-08)
- **Affects:** NOTES-R3, §6.3

### NOTES-D4: Fixes from the NOTES-M1 re-review

- **Status:** answered (2026-11-09)
- **Question:** How do the tests guard against an open SQLite connection? What happens to review findings F2 and F3?
- **Answer:** "Add a leak test (Recommended)", "Fix both (Recommended)", and "New task NOTES-T4 in M1 (Recommended)". (user, 2026-11-09)
- **Affects:** NOTES-T4, the tests

### NOTES-D5: Leak test for new store functions

- **Status:** answered (2026-11-09)
- **Question:** The NOTES-T4 review found F1 and F2. What happens to the leak test in NOTES-T2?
- **Answer:** "Add both to NOTES-T2 (Recommended)". (user, 2026-11-09)
- **Affects:** NOTES-T2

### NOTES-D6: Body of the `No fields to change` error, and missing tests

- **Status:** answered (2026-11-09)
- **Question:** The NOTES-M2 review found F1 and F2. Which body does the `No fields to change` error have? Do the five untested behaviors get tests?
- **Answer:** "List format, like other 422s (Recommended)" and "Add all five (Recommended)". (user, 2026-11-09)
- **Affects:** §6.3 error table, NOTES-T5

## 10. Tasks

### Milestones

| ID | Goal | Done when | Tasks | Status |
|---|---|---|---|---|
| NOTES-M1 | Create and read a note | The owner starts the API, sends `POST /notes` with a title and a body with `curl`, then sends `GET /notes/{id}` and gets the same note. | NOTES-T1, NOTES-T3, NOTES-T4 | in-review |
| NOTES-M2 | List, change, and delete notes | `GET /notes` lists all notes. `PATCH /notes/{id}` changes a note. After `DELETE /notes/{id}`, `GET` for that note gets 404. | NOTES-T2, NOTES-T5 | in-review |

### NOTES-T1: Create and read a note

- **Status:** in-review
- **Type:** feature
- **Story:** As the owner, I want to save a note and read it again, so that I keep my notes in one place.
- **Milestone:** NOTES-M1
- **Parent:** None
- **Depends on:** None
- **Covers:** NOTES-R1, NOTES-R2, NOTES-R6 (for `GET`), NOTES-R7, NOTES-R8, NOTES-R10, NOTES-AC1, NOTES-AC2, NOTES-AC6 (for `GET`), NOTES-AC7, NOTES-AC9
- **Decisions:** ROOT-D1, ROOT-D2, ROOT-D3, ROOT-D6 to ROOT-D12, NOTES-D1, NOTES-D2
- **Files:** `pyproject.toml`, `uv.lock`, `.python-version`, `.gitignore`, `README.md`, `.github/workflows/`, `src/notes_api/`, `tests/`
- **Model:** small, because §6.3 and §6.4 give all contracts and data
- **Branch / worktree / PR:** `specx/NOTES-T1` / `/home/w1/specx-example-NOTES-T1` / —
- **Assumptions:**
  - The project has no build backend. pytest and uvicorn find the code in `src` directly. Reason: A build backend is a dependency that ROOT §6.2 does not list.
  - `pydantic==2.14.3` is a direct dependency. Reason: The code imports Pydantic, and ROOT §6.2 gives its version.
  - `pyproject.toml` requires uv 0.12.23. Reason: ROOT §6.2 gives this version.
  - SQLite `PRAGMA user_version` records the last applied schema change. Reason: The schema needs no extra table for this.
  - The rollback file also sets `user_version` to 0. The owner runs it with the `sqlite3` tool. Reason: Then the next start applies schema change 1 again (§6.13).
  - The API opens one SQLite connection for each operation. It reads `NOTES_DB_PATH` when it opens the connection. Reason: Each test can then use its own file.
  - Pydantic validates the fields. A `null` value or a value that is not text gets 422. Reason: Pydantic does this without custom code.
  - FastAPI sends the 500 error. The code has no custom error handler. Reason: ROOT §6.7 gives no other format.
  - The CI workflow runs on each pull request with `uv run --locked pytest`. Reason: `--locked` also stops CI if `uv.lock` is old.
  - `.gitignore` ignores all `*.db` files. Reason: Test and local database files must not go into git.
  - The README start command gives `--host 127.0.0.1 --port 8000`. Reason: The command then shows the values of ROOT §6.8 and §6.9.

**Steps**

1. Make a uv project for Python 3.14 with the package `notes_api` and the exact versions in ROOT §6.2. Commit `uv.lock`.
2. Add schema change 1 and its rollback (§6.4). The API applies new schema changes when it starts (ROOT §6.4).
3. Add `POST /notes` and `GET /notes/{id}` with the rules and errors in §6.3. Use `NOTES_DB_PATH` and listen on `127.0.0.1:8000` (ROOT §6.8, §6.9).
4. Write integration tests for AC1, AC2, AC6 (for `GET`), AC7, and AC9 (§6.12).
5. Add a GitHub Actions workflow that runs `uv run pytest` on each pull request (ROOT §6.12).
6. In `README.md`, tell the owner how to install, start the API, and run the tests.

**Verification**

- `uv run pytest`: all tests pass.
- Start the API with the command in `README.md`. Send `POST /notes` and `GET /notes/1` with `curl`.

**Log**

- 2026-11-08: created.
- 2026-11-08: the user approved the task: "yes approve".
- 2026-11-08: the user approved the NOTES-M1 preview: "Approve and build".
- 2026-11-08: The start point is `749f223`.
- 2026-11-08: An agent built NOTES-T1 in commit `b1d1fda`. The main session ran `uv run --locked pytest` in the worktree: 15 passed, 1 warning. The warning: Starlette marks the use of `httpx` with `TestClient` as deprecated. The main session merged the task into `specx/delivery-NOTES`.
- 2026-11-08: The independent review is [2026-11-08-NOTES-M1.md](../_reviews/2026-11-08-NOTES-M1.md). At the demo, the user answered the findings: "Refuse to start", "Keep httpx 0.28.1", "Accept all four", and "Accept all". The fixes go to NOTES-T3.

### NOTES-T2: List, change, and delete notes

- **Status:** in-review
- **Type:** feature
- **Story:** As the owner, I want to see all my notes, change them, and delete them, so that my notes stay correct.
- **Milestone:** NOTES-M2
- **Parent:** None
- **Depends on:** NOTES-T1, NOTES-T4
- **Covers:** NOTES-R3, NOTES-R4, NOTES-R5, NOTES-R6, NOTES-R9, NOTES-AC3, NOTES-AC4, NOTES-AC5, NOTES-AC6, NOTES-AC8
- **Decisions:** ROOT-D11, ROOT-D12, NOTES-D2, NOTES-D3, NOTES-D5
- **Files:** `README.md`, `src/notes_api/`, `tests/`
- **Model:** small, because §6.3 gives all contracts and errors
- **Branch / worktree / PR:** `specx/NOTES-T2`, `../specx-example-NOTES-T2`, #1
- **Assumptions:**
  - The `No fields to change` error has the body `{"detail": "No fields to change"}`. Reason: The §6.3 error table gives this row its own body.
  - A `PATCH` with no fields gets 422 before the ID check. Reason: §6.5 puts validation before the 404 check.
  - A `PATCH` with only unknown fields gets 422 `No fields to change`. Reason: The API ignores unknown fields.
  - A `PATCH` field with an explicit `null` gets 422. A missing field keeps its old value. Reason: §6.3 requires 422 for `null`.
  - A `PATCH` sets `updated_at` also when the values do not change. Reason: §6.3 says that `updated_at` is the time of the change.
  - One SQL `UPDATE … RETURNING` statement changes the note and reads it. Reason: The change and the read are then in one transaction.

**Steps**

1. Add `GET /notes`, `PATCH /notes/{id}`, and `DELETE /notes/{id}` with the rules, order, and errors in §6.3.
2. Write integration tests for AC3, AC4, AC5, AC6, and AC8.
3. Add the new endpoints to `README.md`.
4. Add each new store function to the leak test, on success and on failure (NOTES-D5).
5. Run `gc.collect()` once before the warning block of the leak test (NOTES-D5).

**Verification**

- `uv run --locked pytest`: all tests pass (ROOT §6.12).
- Start the API. Send `GET /notes`, `PATCH /notes/1`, and `DELETE /notes/1` with `curl`.

**Log**

- 2026-11-08: created.
- 2026-11-08: the user approved the task: "yes approve".
- 2026-11-09: steps 4 and 5 added from NOTES-D5. The gate command now matches ROOT §6.12.
- 2026-11-09: the user approved the NOTES-M2 preview: "yes approve".
- 2026-11-09: an agent built the task in commit `ec15e89`. The main session merged it. `uv run --locked pytest` gives 37 passed.
- 2026-11-09: the build agent removed `closing` from `delete_note` in a copy of the code outside the repository. The leak test then failed.
- 2026-11-09: the independent review is [2026-11-09-NOTES-M2.md](../_reviews/2026-11-09-NOTES-M2.md). The review found that the spec already fixes assumptions 2 to 5. Assumption 1 is a conflict between the specs (review F1).

### NOTES-T3: Fixes from the NOTES-M1 review

- **Status:** in-review
- **Type:** chore
- **Why:** the NOTES-M1 review found M3, L1, L3, L4, L5, and L6. The user chose the fixes (ROOT-D16 to ROOT-D19).
- **Done when:** NOTES-AC10 and NOTES-AC11 have tests that pass, the tests show no `ResourceWarning`, and `requires-python` is `==3.14.*`.
- **Milestone:** NOTES-M1
- **Parent:** None
- **Depends on:** NOTES-T1
- **Covers:** NOTES-R11, NOTES-R12, NOTES-AC10, NOTES-AC11
- **Decisions:** ROOT-D16, ROOT-D17, ROOT-D18, ROOT-D19
- **Files:** `pyproject.toml`, `uv.lock`, `src/notes_api/`, `tests/`
- **Model:** small, because the spec gives each change
- **Branch / worktree / PR:** `specx/NOTES-T3`, `../specx-example-NOTES-T3`, #1
- **Assumptions:**
  - The error handler catches each `Exception`, not only `sqlite3.Error`. Reason: ROOT §6.3 gives one body for all 500 errors.
  - Starlette raises the error again after the handler sends the response. Reason: Uvicorn then writes the error to the log (ROOT §6.7).
  - The NOTES-AC10 test sets the database file to mode `0o444` after the start. Reason: The API can then only read the file.
  - The NOTES-AC10 test also checks that the number of notes stays 1. Reason: The test shows that the failed write changes no data.
  - The NOTES-AC11 test starts uvicorn as a separate process with `--port 0`. Reason: The test sees the real exit code and log.
  - The NOTES-AC11 test checks for a non-zero exit code and two log lines. Reason: These show that the API wrote the error and stopped.

**Steps**

1. Send `{"detail": "Internal Server Error"}` for a 500 error (§6.3).
2. Close each SQLite connection, also when a query fails (review L3).
3. Close each SQLite connection in the tests (review L4).
4. Set `requires-python` to `==3.14.*`, then run `uv lock`.
5. Write integration tests for NOTES-AC10 and NOTES-AC11.
6. Write a test that whitespace (tabs and line breaks) at the start and the end of a title is removed.

**Verification**

- `uv run --locked pytest -W error::ResourceWarning`: all tests pass.

**Log**

- 2026-11-08: created from the NOTES-M1 review.
- 2026-11-09: the user approved the task and its start: "Yes approve".
- 2026-11-09: the build starts in worktree `../specx-example-NOTES-T3`.
- 2026-11-09: an agent built the task in commit `1e0e052`. The main session merged it. `uv run --locked pytest -W error::ResourceWarning` gives 18 passed.
- 2026-11-09: the old code also passes with `-W error::ResourceWarning`. This command does not prove that each connection closes. The review must check this.
- 2026-11-09: the independent review is [2026-11-09-NOTES-M1-fixes.md](../_reviews/2026-11-09-NOTES-M1-fixes.md). The demo waits for the user.
- 2026-11-09: the NOTES-AC10 test fails when a root user runs it, because root can write to a file with mode `0o444`.

### NOTES-T4: Leak test and test fixes from the NOTES-M1 re-review

- **Status:** in-review
- **Type:** chore
- **Why:** The re-review found F1, F2, and F3. The user chose the fixes (NOTES-D4).
- **Done when:** The leak test fails on the old `store.py` and passes on the new one. The AC10 and AC11 tests work as root and from `tests/`.
- **Milestone:** NOTES-M1
- **Parent:** None
- **Depends on:** NOTES-T3
- **Covers:** NOTES-R11, NOTES-R12
- **Decisions:** NOTES-D4
- **Files:** `tests/`
- **Model:** small, because the spec gives each change
- **Branch / worktree / PR:** `specx/NOTES-T4`, `../specx-example-NOTES-T4`, #1
- **Assumptions:**
  - The failed reads and writes use a database with no `notes` table. Reason: The failure then does not depend on file mode or root.
  - The failed `migrate` uses a file that is not a SQLite database. Reason: `connect` succeeds, and the first `PRAGMA` then fails.
  - Each failure case must raise `sqlite3.DatabaseError`. Reason: If a call does not fail, the test does not check the failure path.
  - The root skip also checks that `os.geteuid` exists. Reason: Windows does not have `os.geteuid`.

**Steps**

1. Write a test that calls `migrate`, `create_note`, and `get_note` when they succeed and when they fail.
2. Make this test record all `ResourceWarning` warnings. The test fails if a warning says `unclosed database`.
3. Run garbage collection in the test before the check, so that each open connection makes its warning.
4. Skip the AC10 test when the user is root. Give the reason "root can write to a read-only file".
5. Give the AC11 test an absolute path to `src`, found from the test file.

**Verification**

- `uv run --locked pytest`: all tests pass.
- The leak test fails on the old `store.py` from commit `8a18465`. Run it from a copy outside the repository.
- `cd tests && uv run --locked pytest -k ac11`: the test passes.

**Log**

- 2026-11-09: created from the NOTES-M1 re-review.
- 2026-11-09: the user approved the task and its start: "yes".
- 2026-11-09: an agent built the task in commit `6bfb95a`. The main session merged it. `uv run --locked pytest` gives 19 passed.
- 2026-11-09: the main session ran the leak test on the old `store.py` from `8a18465`. The test fails, as the task requires. The AC11 test passes from `tests/`.
- 2026-11-09: the independent review is [2026-11-09-NOTES-T4.md](../_reviews/2026-11-09-NOTES-T4.md). The NOTES-M1 demo waits for the user.
- 2026-11-09: at the demo, the user chose "Continue to NOTES-M2 (Recommended)". The task waits for the phase pull request.

### NOTES-T5: Fixes from the NOTES-M2 review

- **Status:** in-review
- **Type:** bug
- **Why:** The NOTES-M2 review found F1 and F2. The user chose the fixes (NOTES-D6).
- **Done when:** `PATCH` with no fields sends the body in the §6.3 error table, and the five new tests pass.
- **Milestone:** NOTES-M2
- **Parent:** None
- **Depends on:** NOTES-T2
- **Covers:** NOTES-R4, NOTES-R5, NOTES-R9, NOTES-R11, NOTES-AC8
- **Decisions:** ROOT-D11, NOTES-D6
- **Files:** `README.md`, `src/notes_api/`, `tests/`
- **Model:** small, because the spec gives the exact body
- **Branch / worktree / PR:** `specx/NOTES-T5`, `../specx-example-NOTES-T5`, #1
- **Assumptions:**
  - `input` holds the request body as the client sent it, also with unknown fields. Reason: The §6.3 row says "the request body".

**Steps**

1. Send the `No fields to change` error with the body in the §6.3 error table. Keep status 422.
2. Make sure that `PATCH` with no fields to an unknown ID still sends 422, not 404 (§6.5).
3. Change the AC8 test to check the full new body.
4. Write a test: `PATCH` with `title` and `body` changes both fields.
5. Write a test: `PATCH /notes/99` with `{}` sends 422.
6. Write a test: a second `DELETE` of the same note sends 404.
7. Write a test: `PATCH` and `DELETE` send the JSON 500 body when the database file is read-only. Skip it for root, as in the AC10 test.
8. Write a test: `created_at` does not change after `PATCH`.
9. If `README.md` shows this error, change it to the new body.

**Verification**

- `uv run --locked pytest`: all tests pass.
- Start the API. Send `PATCH /notes/1` with `{}` with `curl`. The body agrees with the §6.3 error table.

**Log**

- 2026-11-09: created from the NOTES-M2 review.
- 2026-11-09: the user approved the task and its start: "yes approve".
- 2026-11-09: an agent built the task in commit `b5d95ef`. The main session merged it. `uv run --locked pytest` gives 43 passed.
- 2026-11-09: `curl` with `PATCH /notes/1` and `{}` gave the body in the §6.3 error table.
- 2026-11-09: the build agent ran `pkill -f "port $PORT"` with an empty `PORT`. The command stopped `buildx-api.service`, `openclaw-gateway.service`, and `openclaw-gateway-quota-test.service`. systemd started them again. The main session told the user.
- 2026-11-09: the independent review is [2026-11-09-NOTES-T5.md](../_reviews/2026-11-09-NOTES-T5.md). The review found that §6.3 fixes the `input` assumption.
- 2026-11-09: at the NOTES-M2 demo, the user chose "Keep as built (Recommended)" for review F1 and "Open the PR (Recommended)".
- 2026-11-09: the main session opened pull request [#1](https://github.com/WIRIN-prod/specx-example/pull/1).

## 11. Open questions

None.

## 12. Change log

| Version | Date | Change | Approved by |
|---|---|---|---|
| 1 | 2026-11-08 | Created | user, "yes approve" |
| 2 | 2026-11-08 | NOTES-R11, NOTES-R12, NOTES-AC10, NOTES-AC11, the 500 error, the title trim, and NOTES-T3, from the NOTES-M1 review | user, "Yes approve" |
| 3 | 2026-11-09 | NOTES-D4 and task NOTES-T4, from the NOTES-M1 re-review | user, "yes" |
| 4 | 2026-11-09 | NOTES-D5; NOTES-T2 steps 4 and 5; NOTES-T2 gate command | user, "yes approve" |
| 5 | 2026-11-09 | NOTES-D6, the body of the `No fields to change` error, and task NOTES-T5, from the NOTES-M2 review | user, "yes approve" |
