# Phase 0 — Setup & habits

**Dates:** 2026-11-30 → 2026-12-13 (W1–W2) · **Buffer:** W3, 2026-12-14 → 2026-12-20
**Prerequisites:** none · [← Learning path](../learning-path.md) · [Next: Phase 1 →](01-cs-foundations.md)

## Goal

Get the tools and habits in place so the next 90 weeks run smoothly. That means comfort in the terminal, clean Git, a capstone repo that exists from day one, and a weekly review rhythm. I will also finish the open checkpoint in [database/learning-progress.md](../../database/learning-progress.md) so nothing is left hanging.

## Theory track

| Week | Topic | Resource | Output |
|---|---|---|---|
| 1 | Shell, shell tools & scripting, editors | [MIT Missing Semester](https://missing.csail.mit.edu/) lectures 1–3 | Notes + a cheat sheet of 20 commands I actually use |
| 2 | Git data model, branches, rebase vs merge; debugging & profiling | Missing Semester lectures 6–7 + [Pro Git ch. 1–3](https://git-scm.com/book/en/v2) | Explain in writing what a commit, branch and HEAD *are* |

## Project track

| Week | Task | Deliverable | Skills |
|---|---|---|---|
| 1 | Finish the open CS50 SQL checkpoint: run `inspect_database.py` with `ORDER BY table_name, ordinal_position`, decide on `subject_id NOT NULL` and drop the redundant `subject` column | Updated `database/learning-progress.md` | SQL, psycopg |
| 1 | Create the public GitHub repo `quizlab`: `uv init`, `src/` layout, `.gitignore`, MIT license, README with the one-paragraph pitch from [capstone.md](../capstone.md) | First commit | Git, uv |
| 2 | Add `pre-commit` with ruff (lint + format) and a trivial pytest test; add `compose.yaml` with Postgres 17 (copy from [database/compose.yaml](../../database/compose.yaml), but use a `.env` file for the password) | `docker compose up` + `pytest` both work | Docker, testing, secrets hygiene |
| 2 | Work on a branch, open a PR to myself, merge it | First merged PR | GitHub flow |

## Done when

- [ ] Open database checkpoint is finished and logged.
- [ ] `quizlab` repo is public, with README, license, pre-commit, one passing test.
- [ ] No passwords committed (`.env` is in `.gitignore`; `.env.example` is committed).
- [ ] [progress.md](../progress.md) has its first two weekly entries.

## Threads this phase

- **Git:** every change goes through a branch + PR from now on.
- **Writing:** start `docs/adr/0001-record-architecture-decisions.md` (why I keep ADRs).

## Stretch goals

- Configure a nice shell (zsh + starship/oh-my-zsh), `fzf`, `ripgrep`.
- Learn 10 VS Code shortcuts and the debugger.
