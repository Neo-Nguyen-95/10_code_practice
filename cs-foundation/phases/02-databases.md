# Phase 2 — Databases

**Dates:** 2027-03-22 → 2027-05-16 (W17–W24) · **Buffer:** W25, 2027-05-17 → 2027-05-23
**Prerequisites:** Phase 1 (data structures, files/I/O, concurrency) · [← Phase 1](01-cs-foundations.md) · [Learning path](../learning-path.md) · [Next: Phase 3 →](03-backend.md)

## Goal

Move from "I can write queries" to "I can design, tune and reason about a database". Every role on the path depends on this: backend engineers design schemas, data engineers model warehouses, AI engineers store embeddings. I finish CS50 SQL and go under the hood: indexes are B-trees (Phase 1), and transactions are concurrency control (Phase 1).

The project track turns the small `science_question_bank` into the full QuizLab data model, with a million realistic attempts that later phases reuse for pipelines and ML.

## Theory track

| Week | Topic | Resource | Output |
|---|---|---|---|
| 1 | Relational model; normalization (1NF–3NF, BCNF); ER modeling | [CS50 SQL](https://cs50.harvard.edu/sql/) Lecture 2 (review) + Lecture 4 (Viewing) | Normalize one messy table step by step on paper |
| 2 | Advanced SQL: subqueries, CTEs, recursive CTEs, window functions | [PostgreSQL tutorial: window functions](https://www.postgresql.org/docs/current/tutorial-window.html) + [queries chapter](https://www.postgresql.org/docs/current/queries.html) | 5 window-function patterns I can write from memory |
| 3 | Indexes: B-tree, hash, GIN; composite & partial indexes | [Use The Index, Luke](https://use-the-index-luke.com/) ch. 1–2 + CS50 SQL Lecture 5 (Optimizing) | Explain why column order matters in a composite index |
| 4 | Query planning: `EXPLAIN ANALYZE`, scans vs seeks, join algorithms | Use The Index, Luke ch. 3–4 + [Postgres: Using EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html) | Read a real plan and predict the cost driver |
| 5 | Transactions: ACID, isolation levels, MVCC, locks, deadlocks | [CMU 15-445](https://15445.courses.cs.cmu.edu/) concurrency-control lectures + [Postgres ch. 13](https://www.postgresql.org/docs/current/mvcc.html) | Table of anomalies (dirty/non-repeatable/phantom) by isolation level |
| 6 | Storage internals: pages, buffer pool, WAL, vacuum | CMU 15-445 storage lectures (database storage, buffer pools) | Explain why Postgres needs `VACUUM` |
| 7 | Scaling: replication, partitioning, connection pooling; OLTP vs OLAP | CS50 SQL Lecture 6 (Scaling) | One-page comparison OLTP vs OLAP (prep for Phase 5) |
| 8 | Security and apps: SQL injection, roles & privileges, ORMs vs raw SQL, migrations | [Postgres: roles](https://www.postgresql.org/docs/current/user-manag.html) + [SQLAlchemy 2.0 tutorial](https://docs.sqlalchemy.org/en/20/tutorial/) (Core part) | Least-privilege plan for the QuizLab app |

## Project track (in `quizlab`)

| Week | Task | Deliverable | Skills |
|---|---|---|---|
| 1 | Design the QuizLab ERD in 3NF (see the data model in [capstone.md](../capstone.md)) | `docs/erd.md` (Mermaid ER diagram) + ADR 0003 | Data modeling |
| 2 | Set up [Alembic](https://alembic.sqlalchemy.org/); first migrations create all tables; migrate the existing rows from `science_question_bank` | `migrations/` + data migrated | Migrations |
| 3 | Constraints: `CHECK`, `NOT NULL`, `UNIQUE`, FK `ON DELETE` policies; pytest proves bad data is rejected | `tests/db/test_constraints.py` | Integrity |
| 4 | Seed with Faker: 5k students, 2k questions, **1M attempts**, generated from hidden "student ability" and "question difficulty" values, so ML in Phase 6 has real signal to find | `scripts/seed.py` (uses Phase 1 `COPY` import) | Synthetic data |
| 5 | 10 analytics queries: accuracy by topic, student streaks, class rank, question p-values, recursive topic tree | `sql/analytics/*.sql` | CTEs, window functions |
| 6 | Tune those queries: `EXPLAIN ANALYZE` before/after, composite + partial indexes | `docs/db-performance.md` with timings | Indexing |
| 7 | "Submit quiz" as one transaction; reproduce a race condition with two concurrent submissions, then fix it (`SELECT … FOR UPDATE` or isolation level); materialized view for leaderboard | Test that shows the bug and then the fix | Transactions |
| 8 | Roles: `quizlab_app` (least privilege), `quizlab_analyst` (read-only); `pg_dump` backup + restore drill; tag `v0.2.0` | `docs/db-ops.md` | Security, ops |

## Done when

- [ ] I can normalize a table to 3NF and explain each step.
- [ ] I can read an `EXPLAIN ANALYZE` plan and fix a slow query with the right index.
- [ ] I can explain isolation levels and MVCC with an example from my own project.
- [ ] QuizLab schema is managed only through Alembic migrations, seeded with 1M attempts.
- [ ] `docs/db-performance.md` shows ≥ 3 queries made ≥ 10× faster.

## Threads this phase

- **SQL:** starting now, 1 hard SQL problem/week ([LeetCode Database](https://leetcode.com/problemset/database/), hard/medium).
- **DSA:** 1 problem/week.
- **Docker:** Postgres always runs from `compose.yaml`; learn `docker compose logs`, `exec`, volumes.
- **Writing:** ADR 0003 (schema design).

## Stretch goals

- Table partitioning of `attempts` by month and measure the effect.
- Full-text search in Postgres (`tsvector`, GIN) vs my Phase 1 inverted index.
- CMU 15-445 lectures on B+ tree internals.
