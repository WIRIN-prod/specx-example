# Tasks

Every task in this project, one row each. Task details live in the **Tasks** section of the spec linked in each row; keep both in step. For where the project stands, read [STATUS.md](STATUS.md).

Statuses: `draft` → `todo` → `in-progress` → `in-review` → `done`, plus `blocked` and `cancelled`. Types: `feature`, `bug`, `chore`, `spike`.

| Task | Title | Type | Milestone | Spec | Status | Parent | Depends on | PR |
|---|---|---|---|---|---|---|---|---|
| NOTES-T1 | Create and read a note | feature | NOTES-M1 | [NOTES](notes/spec.md) | in-progress | — | — | — |
| NOTES-T2 | List, change, and delete notes | feature | NOTES-M2 | [NOTES](notes/spec.md) | todo | — | NOTES-T1 | — |
