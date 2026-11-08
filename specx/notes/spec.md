---
id: NOTES
title: Notes
status: approved
version: 1
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
| `title` | string | Required. The system removes spaces at the start and the end (it trims the title). Then the title must have 1 to 200 characters. |
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
| 422 | A `PATCH` request has no `title` and no `body` | The FastAPI error format, with the message `No fields to change` |

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

## 10. Tasks

### Milestones

| ID | Goal | Done when | Tasks | Status |
|---|---|---|---|---|
| NOTES-M1 | Create and read a note | The owner starts the API, sends `POST /notes` with a title and a body with `curl`, then sends `GET /notes/{id}` and gets the same note. | NOTES-T1 | in-progress |
| NOTES-M2 | List, change, and delete notes | `GET /notes` lists all notes. `PATCH /notes/{id}` changes a note. After `DELETE /notes/{id}`, `GET` for that note gets 404. | NOTES-T2 | todo |

### NOTES-T1: Create and read a note

- **Status:** in-progress
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
- **Assumptions:** None yet.

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

### NOTES-T2: List, change, and delete notes

- **Status:** todo
- **Type:** feature
- **Story:** As the owner, I want to see all my notes, change them, and delete them, so that my notes stay correct.
- **Milestone:** NOTES-M2
- **Parent:** None
- **Depends on:** NOTES-T1
- **Covers:** NOTES-R3, NOTES-R4, NOTES-R5, NOTES-R6, NOTES-R9, NOTES-AC3, NOTES-AC4, NOTES-AC5, NOTES-AC6, NOTES-AC8
- **Decisions:** ROOT-D11, ROOT-D12, NOTES-D2, NOTES-D3
- **Files:** `README.md`, `src/notes_api/`, `tests/`
- **Model:** small, because §6.3 gives all contracts and errors
- **Branch / worktree / PR:** —
- **Assumptions:** None yet.

**Steps**

1. Add `GET /notes`, `PATCH /notes/{id}`, and `DELETE /notes/{id}` with the rules, order, and errors in §6.3.
2. Write integration tests for AC3, AC4, AC5, AC6, and AC8.
3. Add the new endpoints to `README.md`.

**Verification**

- `uv run pytest`: all tests pass.
- Start the API. Send `GET /notes`, `PATCH /notes/1`, and `DELETE /notes/1` with `curl`.

**Log**

- 2026-11-08: created.
- 2026-11-08: the user approved the task: "yes approve".

## 11. Open questions

None.

## 12. Change log

| Version | Date | Change | Approved by |
|---|---|---|---|
| 1 | 2026-11-08 | Created | user, "yes approve" |
