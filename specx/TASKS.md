# Tasks

Every task in this project, one row each. Task details live in the **Tasks** section of the spec linked in each row; keep both in step. For where the project stands, read [STATUS.md](STATUS.md).

Statuses: `draft` → `todo` → `in-progress` → `in-review` → `done`, plus `blocked` and `cancelled`. Types: `feature`, `bug`, `chore`, `spike`.

| Task | Title | Type | Milestone | Spec | Status | Parent | Depends on | PR |
|---|---|---|---|---|---|---|---|---|
| NOTES-T1 | Create and read a note | feature | NOTES-M1 | [NOTES](notes/spec.md) | in-review | — | — | — |
| NOTES-T2 | List, change, and delete notes | feature | NOTES-M2 | [NOTES](notes/spec.md) | in-progress | — | NOTES-T1, NOTES-T4 | — |
| NOTES-T3 | Fixes from the NOTES-M1 review | chore | NOTES-M1 | [NOTES](notes/spec.md) | in-review | — | NOTES-T1 | — |
| NOTES-T4 | Leak test and test fixes from the NOTES-M1 re-review | chore | NOTES-M1 | [NOTES](notes/spec.md) | in-review | — | NOTES-T3 | — |
| NOTES-T5 | Fixes from the NOTES-M2 review | bug | NOTES-M2 | [NOTES](notes/spec.md) | in-progress | — | NOTES-T2 | — |
