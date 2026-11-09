# Review: NOTES-M1 fixes (NOTES-T3)

## Scope

- Milestone re-review after fixes. Diff `1feeb5f..9e8bbb5 -- src tests pyproject.toml uv.lock` on `specx/delivery-NOTES`. Code commit `1e0e052`.
- Text: the NOTES-T3 section of `specx/notes/spec.md` and `specx/STATUS.md` in `1feeb5f..c08e409`.
- Specs: ROOT version 3 (§6.2, §6.3, §6.7, §6.12, ROOT-D16 to ROOT-D19), NOTES version 2 (NOTES-R11, NOTES-R12, NOTES-AC10, NOTES-AC11, the error table, NOTES-T3).
- Prior review: [2026-11-08-NOTES-M1.md](2026-11-08-NOTES-M1.md).

## Reviewer

An independent agent. It did not build this work. It changed no file except this report. It made no commit.

## Verdict

The fixes are correct. All six NOTES-T3 steps are done. Only files in the **Files** list changed. NOTES-R11, NOTES-AC10, NOTES-R12, and NOTES-AC11 work as the specs say. Each SQLite connection in `store.py` now closes, also on errors. The quality gate passes. There are no critical or high findings. There are 1 medium and 6 low findings. The medium finding is about the proof, not the code.

## What the reviewer ran

All runs used user ID 1000 (not root). Temporary files were in a scratch folder outside the repository. The reviewer removed them after the runs.

1. `uv run --locked pytest`: 18 passed, 1 warning (the known `httpx` deprecation, ROOT-D17).
2. `uv run --locked pytest -W default -p no:cacheprovider`: 18 passed, no `ResourceWarning`.
3. Old code without `git stash`, `checkout`, or `reset`:
   - `old`: `git archive 8a18465` (old code and old tests).
   - `mixed`: `git archive 9e8bbb5` with `git show 8a18465:src/notes_api/store.py` (old store, new tests).
   - `oldsrc`: `git archive 9e8bbb5` with `git archive 8a18465 src` (old code, new tests).
4. Leak checks in the new tree, `mixed`, and `old`, with `.venv/bin/python -m pytest -q -p no:cacheprovider` and these options:

   | Option | New | `mixed` | `old` |
   |---|---|---|---|
   | `-W error::ResourceWarning` | pass | pass | pass |
   | `-W error::pytest.PytestUnraisableExceptionWarning` | pass | pass | pass |
   | both options together | pass | pass | pass |
   | `python -X dev` with both options | pass | pass | pass |
   | `-W always::ResourceWarning`, then `grep -c "unclosed database"` | 0 | 1 | 9 |

   No pytest option makes the run fail. pytest reports the warning at the end of the session, outside a test. Only the count of `unclosed database` lines finds the leak.
5. A direct script, run as `.venv/bin/python -I` against each `src`. It sets `warnings.simplefilter("always", ResourceWarning)` and records each warning and unraisable error. Then it calls `migrate`, `create_note`, and `get_note` with success, a read-only file, and a folder as the database path. It exits 1 on a leak. Result: new code exit 0 with 0 leaks; old code exit 1 with 1 leak (in `create_note` on the read-only file).
6. `get_note` on a database with no `notes` table, with `-W always::ResourceWarning`: new code gives no warning; old code gives `ResourceWarning: unclosed database`.
7. New tests against `oldsrc`: 1 failed (`test_ac10_database_error_after_start`, the body is not JSON), 17 passed.
8. The API by hand: `uv run --locked uvicorn notes_api.main:app --app-dir src --host 127.0.0.1 --port <free port>` with `NOTES_DB_PATH` in the scratch folder.
   - `POST /notes` `{"title":"First"}`: 201.
   - `chmod 444` on the file, then `POST /notes` `{"title":"A"}`: 500, `content-type: application/json`, body `{"detail":"Internal Server Error"}`.
   - `GET /notes/1`: 200 with note 1. The failed write changed no data.
   - The log has the access line, `ERROR: Exception in ASGI application`, and the `sqlite3.OperationalError` traceback.
9. NOTES-AC11 by hand: the same command with `NOTES_DB_PATH` in a folder that does not exist. Exit code 3. The log has `unable to open database file` and `Application startup failed. Exiting.` `curl` to the port after the exit got no connection.
10. A read error after the start through `TestClient(app, raise_server_exceptions=False)`: `chmod 0` on the file, then `GET /notes/1` gave 500 with the JSON body. `GET /notes/abc` still gave 422. `GET /notes/99` still gave 404 with `{"detail":"Note not found"}`.
11. `cd tests && ../.venv/bin/python -m pytest -q -p no:cacheprovider -k ac11`: 1 failed.
12. `unshare -r` to run the NOTES-AC10 test as root: the system refused it (`Operation not permitted`).

## Findings

| ID | Severity | Where | Problem | Failure scenario | Remedy |
|---|---|---|---|---|---|
| F1 | medium | `specx/notes/spec.md`, NOTES-T3 **Done when** and **Verification** | The verification command `uv run --locked pytest -W error::ResourceWarning` cannot find a leak. The old code passes it. No test or gate finds the leak from review L3. | A later change opens a connection without `closing`. All tests and the gate still pass. The leak stays hidden. | Ask the user. Option A: change the verification to the count of `unclosed database` lines with `-W always::ResourceWarning` (must be 0). Option B: add a test that records `ResourceWarning` around a failed `create_note`. Option B adds a test, not a gate. |
| F2 | low | `tests/test_notes.py:112-119` | The NOTES-AC10 test uses mode `0o444`. Root can write to that file. The task log records this. The reviewer could not run it as root. | A developer or a container runs the tests as root. The `POST` gets 201, and the test fails. The gate blocks a correct change. | Ask the user: accept the limit, or skip the test when `os.geteuid() == 0` with a clear reason. |
| F3 | low | `tests/test_notes.py:122-130` | The NOTES-AC11 test gives `--app-dir src` as a relative path. It works only when the current folder is the repository root. The test also removes all other environment variables. | `cd tests && pytest -k ac11` fails, because uvicorn cannot import `notes_api`. CI runs from the root, so CI passes. | Use a path from `Path(__file__).parent.parent / "src"`, or give `cwd=` to `subprocess.run`. |
| F4 | low | ROOT §6.7, NOTES-T3 assumption 2 | ROOT §6.7 says "FastAPI writes the error to the log". uvicorn writes it (`ERROR: Exception in ASGI application`). The assumption says this correctly. The approved spec and the code disagree in wording only. | A reader looks for a FastAPI log setting that does not exist. | Show the user. If the user agrees, change the word to "uvicorn" in the next approved ROOT change. |
| F5 | low | `specx/STATUS.md`, assumptions table | The table shows 3 of the 6 NOTES-T3 assumptions. It does not show assumptions 2, 4, and 6 (rule 5). | The user cannot overturn an assumption that they do not see at the demo. | Add the three missing rows. |
| F6 | low | `tests/test_notes.py:37-40, 122-130` | The title-trim test and the NOTES-AC11 test also pass on the old code. The behavior already existed. Thus these tests guard against regression only. They do not prove a fix. This is correct for ROOT-D16 and ROOT-D19. | None now. The demo must not show these tests as proof of a code change. | Say this at the demo. |
| F7 | low | `specx/notes/spec.md`, NOTES-T3 Log | STE: "Thus" is not an approved STE word. The new **Assumptions** lines start "Reason:" with a lowercase word. NOTES-T1 uses an uppercase word. | None. Small style break (rule 10). | Use "Because of this," and start each reason with an uppercase letter. |

`specx/STATUS.md` has no STE finding.

### Step check

| Step | Result |
|---|---|
| 1. JSON body for 500 | Done. `@app.exception_handler(Exception)` in `main.py`. Verified by hand and by test. |
| 2. Close connections in the store | Done. `contextlib.closing` in `migrate`, `create_note`, and `get_note`. Verified with the direct script. |
| 3. Close connections in the tests | Done. `count_notes` and the rollback test use `closing`. 0 `unclosed database` lines. |
| 4. `requires-python = "==3.14.*"` and `uv lock` | Done. `uv.lock` drops the `cp315` wheels and the `python_full_version < '3.15'` marker. `--locked` passes. |
| 5. Tests for NOTES-AC10 and NOTES-AC11 | Done. See F2 and F3. |
| 6. Test for tabs and line breaks in a title | Done. See F6. |

Changed files: `pyproject.toml`, `uv.lock`, `src/notes_api/main.py`, `src/notes_api/store.py`, `tests/test_notes.py`, and the SpecX records. All code files are in the **Files** list.

### Assumptions

| Assumption | Result |
|---|---|
| 1. The handler catches each `Exception`. | Implementation detail. ROOT §6.3 gives one 500 body. 404 and 422 still work (run 10). |
| 2. Starlette raises the error again, and uvicorn logs it. | Correct (run 8). It is a fact about the framework, not a choice. See F4. |
| 3. The NOTES-AC10 test uses mode `0o444`. | Implementation detail. It has a limit for root. See F2. |
| 4. The NOTES-AC10 test checks that the count stays 1. | Implementation detail. Correct. |
| 5. The NOTES-AC11 test runs uvicorn in a separate process with `--port 0`. | Implementation detail. It depends on the current folder. See F3. |
| 6. The NOTES-AC11 test checks the exit code and two log lines. | Implementation detail. Correct. If start does not fail, the 30-second timeout stops the test. |

No assumption is a big or small choice. No assumption is wrong.

## What the reviewer did not check

- The NOTES-AC10 test as a root user. The system did not allow `unshare -r`.
- The CI workflow on GitHub.
- `specx/TASKS.md` against the specs.
- STE in text outside the NOTES-T3 section and `specx/STATUS.md`.
- Concurrent requests and connection leaks under load.
- A dependency audit and a secret scan.
- The change to `uv.lock` beyond `uv run --locked` and the diff.
