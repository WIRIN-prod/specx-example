# SpecX rules

The user decides. The agent executes. These rules apply to every SpecX command (`explore`, `plan`, `execute`, `review`) and to every subagent. Follow them exactly; when in doubt, stop and ask the user.

## 1. The user makes the decisions, sorted by risk

Agents never choose on the user's behalf, except for implementation details. Every choice is one of three kinds:

- **Big choices** are hard to reverse or define the product: product behavior, scope, architecture, stack, packages and versions, APIs, data storage and data models, authentication and security, tooling, test strategy, CI, and deployment. Ask the user first, one decision at a time or in small batches.
- **Small choices** are visible to the user but cheap to change: naming, theme, colors, fonts, spacing, and copy. Propose them together on one defaults sheet, which the user accepts or edits in a single reply. Nothing on the sheet applies until the user replies.
- **Implementation details** are invisible to the user, cheap to reverse, and inside an approved spec: code structure, and how to meet a contract the spec already fixes. The agent chooses. Code structure follows the project's conventions and the spec's architecture. Any other detail the spec left open is logged as an assumption in the task's **Assumptions** with its reason, and shown at the demo, where the user can overturn it.
- If it is unclear which kind a choice is, treat it as the bigger kind. A new dependency, a changed interface, a schema change, security behavior, and anything the user can see are never implementation details.
- When a big or small choice is needed, add it as an open decision to the **Decisions** section of the highest spec it applies to (project-wide choices go in `specx/spec.md`). Give the question, the realistic options, and their trade-offs, then ask the user. You may recommend an option and say why, but it stays open until the user answers.
- Work that depends on an open decision stops until the user answers. Record the answer in the user's words, with the date.
- "Continue", silence, or approval of something else is not an answer.

## 2. Confirm the source of truth

- If docs, specs, comments, and code disagree, do not pick a side. Show the user both, with file and line, and ask which is correct. Record the answer as a decision. Fix the other side only through an approved task.
- Approved specs and answered decisions are the only authority for building. Draft content, research, conventions, and your own inferences are not.

## 3. Read the whole context chain

- Specs form a tree of folders, each with one `spec.md`, like nested routes: `specx/spec.md` → `specx/auth/spec.md` → `specx/auth/login/spec.md` → `specx/auth/login/sso/spec.md`.
- Before working on any spec or task, read every `spec.md` from `specx/spec.md` down to it. A parent's **Shared with children** section and its answered decisions apply to every descendant. A child may override them only through its own answered decision.

## 4. Specs are build-ready, one phase at a time

- Work is divided into stages, phases, milestones, and tasks. Stages are maturity levels such as Core, Essentials, and Production; a phase is a feature-sized piece of work with one spec folder; a milestone is a part of a phase the user can run and check. The user approves this roadmap. In the Ongoing stage, work is single features, bugs, chores, and spikes.
- Write a full spec only for the next phase. Everything later stays one line on the roadmap until its turn.
- A spec is a complete specification and technical plan for its phase: what the system does, how it is built, and with what. It is not code. A frontier model writes it; a smaller model must be able to build every task from the spec and its context chain, choosing only implementation details.
- If an implementer would have to guess a behavior, rule, library, version, field, status code, or error message, the spec is not finished. Find the answer in an answered decision or the code, or ask the user.
- Show a spec for approval only when it meets this bar. If you find a gap while building, log it as an assumption when it is an implementation detail; otherwise stop and report it, and never fill it yourself.
- When approved work changes behavior, update the spec in the same pull request. Specs must always describe the code.

## 5. Always maintain the task list

- Tasks live in the **Tasks** section of the spec they implement. `specx/TASKS.md` is the single list of every task, with one row per task that matches the spec.
- Update the task in its spec and its row in `TASKS.md` before starting work, whenever a status changes, and before stopping. Never do work that is not on the list.
- Check the list whenever you change it: every referenced task, milestone, decision, and spec ID exists, there are no dependency cycles, and every row matches its spec.
- Keep `specx/STATUS.md` current whenever a task, milestone, or decision changes, so the user can always see what is happening, what is waiting on them, and which assumptions were made.

## 6. Nothing moves without approval

- Roadmap: the user approves its stages, phases, and milestones, and can change them at any time.
- Specs: `draft` → `approved` only when the user approves that exact spec version.
- Tasks: `draft` → `todo` when the user approves the task list; `todo` → `in-progress` only when the user approves the preview of that milestone or item.
- Milestones: each ends with a demo. The next one starts only after the user chooses to continue.
- Review: an agent never reviews its own work. An independent agent reviews each milestone and Ongoing item before its demo. If the host has no subagents, the demo must say the review was not independent.
- Merge into the main branch: only through a pull request, and only after the user approves that pull request.
- Any material change after approval needs approval again, and bumps the spec's version.

## 7. Stay in scope

- Do only what the approved task says, in the files it lists. If it needs more, stop and ask.
- Never add a dependency, change an interface, migrate data, or edit an approved spec without an answered decision.
- Preserve the user's unrelated work. Never reset, stash, clean, force-push, or delete branches you did not create.

## 8. Be honest

- Report exactly what you ran and what happened. Never claim a test, check, or review passed unless you ran it and it passed. Say what you did not check.

## 9. Preserve approved quality gates

- A binding quality gate names its criterion or threshold, exact check or command, when it runs, and whether failure blocks or warns. It must trace to an approved spec or decision.
- Do not invent thresholds, commands, or block-or-warn policies. Existing CI and test configuration are evidence of current behavior; do not silently promote them into new product requirements.
- Never weaken, disable, skip, or delete an approved gate, test, or assertion to make work pass. Ask the user before changing an approved gate.

## 10. Write in Simplified Technical English

- Write all new and changed text in SpecX documents in ASD-STE100 Simplified Technical English. This includes specs, `TASKS.md`, `STATUS.md`, review reports, and these rules. Old text changes only when you edit it.
- Write one instruction in each sentence. Use the imperative for instructions.
- Use not more than 20 words in a procedural sentence and not more than 25 words in a descriptive sentence.
- Use the active voice and simple verb tenses.
- Use not more than six sentences in a paragraph.
- Use approved STE words with their approved meanings when you know them. Use technical names and technical verbs when necessary, for example `FastAPI`, `endpoint`, and `deploy`.
- Write text in table cells in STE. Do not change table structure, code, commands, paths, or the user's quoted words to obey this rule.
- EARS keywords (`THE SYSTEM SHALL`, `WHEN`, `WHILE`, `WHERE`, `IF`, `THEN`) are technical terms. Use them in requirements.

## Layout

```text
specx/
  RULES.md                    these rules (also in CLAUDE.md and AGENTS.md)
  spec.md                     root spec: product, project-wide decisions, shared conventions
  TASKS.md                    every task, one row each
  STATUS.md                   where the project stands, for the user
  auth/spec.md                a phase
  auth/login/spec.md          a feature; shared by its children
  auth/login/sso/spec.md      a child feature
  _templates/spec.md          the spec format
  _reviews/                   review reports
```

Folders starting with `_` are not specs. If `specx/` is missing, run `/specx:plan`, `/specx:execute`, or `/specx:review`, or ask `/specx:explore` to write the framework; each creates this layout first.
