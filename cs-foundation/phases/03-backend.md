# Phase 3 — Backend engineering

**Dates:** 2027-05-24 → 2027-08-01 (W26–W35) · **Buffer:** W36, 2027-08-02 → 2027-08-08
**Prerequisites:** Phase 1 (HTTP, concurrency), Phase 2 (schema, transactions) · [← Phase 2](02-databases.md) · [Learning path](../learning-path.md) · [Next: Phase 4 →](04-devops-aws.md)

## Goal

Build a production-style backend service: a clean API design, a layered architecture, auth, caching, background work, tests and observability. For a data career this matters in three ways. Data engineers build and consume APIs. ML and AI features are served through APIs. And the QuizLab API is the **source of the events** that Phase 5 pipelines will ingest.

## Theory track

| Week | Topic | Resource | Output |
|---|---|---|---|
| 1 | HTTP methods, status codes, REST resource design, versioning | [MDN HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP) + [Google API design guide](https://cloud.google.com/apis/design) | My API style rules (naming, errors, pagination) |
| 2 | FastAPI + Pydantic fundamentals; OpenAPI | [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/) (first half) | Notes: dependency injection in FastAPI |
| 3 | ORM: SQLAlchemy 2.0 ORM, sessions, lazy vs eager loading, N+1 | [SQLAlchemy ORM tutorial](https://docs.sqlalchemy.org/en/20/tutorial/) | Explain N+1 and two ways to fix it |
| 4 | Architecture: layers, repository, unit of work, service layer | [Cosmic Python](https://www.cosmicpython.com/book/preface.html) ch. 1–6 | Diagram of QuizLab layers |
| 5 | Auth: hashing, sessions vs JWT, OAuth2 flows, RBAC | [FastAPI security](https://fastapi.tiangolo.com/tutorial/security/) + [OWASP auth cheat sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html) | When to use JWT vs a session cookie |
| 6 | Testing: test pyramid, unit vs integration vs contract tests | Cosmic Python ch. 3 & 5 + [Postman CLI docs](https://learning.postman.com/docs/postman-cli/postman-cli-overview/) | My testing strategy for QuizLab |
| 7 | Caching: cache-aside, TTL, invalidation; Redis data types | [Redis docs](https://redis.io/docs/latest/develop/) + [System Design Primer: cache](https://github.com/donnemartin/system-design-primer#cache) | When caching makes things *worse* |
| 8 | Async I/O in web apps; background jobs; events, outbox pattern, idempotency | Cosmic Python ch. 8–9, 11 + [FastAPI async](https://fastapi.tiangolo.com/async/) | Explain the transactional outbox pattern |
| 9 | API security & reliability: OWASP API Top 10, rate limiting, validation | [OWASP API Security Top 10](https://owasp.org/API-Security/) | Checklist applied to QuizLab |
| 10 | Observability: structured logs, metrics, traces | [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/) getting started | Logs vs metrics vs traces: what each answers |

## Project track (in `quizlab`)

| Week | Task | Deliverable | Skills |
|---|---|---|---|
| 1 | API design doc: resources & endpoints for questions, topics, students, quiz sessions, attempts | `docs/api-design.md` | API design |
| 2 | FastAPI app skeleton, Pydantic schemas, `GET/POST /questions`, `/health` | Swagger UI at `/docs` | FastAPI |
| 3 | SQLAlchemy ORM models over the Phase 2 schema (Alembic still owns migrations); fix one N+1 with `selectinload` | `src/quizlab/api/db/` | ORM |
| 4 | Service layer + unit of work: start session → submit answer → finish session (reuse the Phase 2 transaction) | Quiz flow works end-to-end | Architecture |
| 5 | Auth: sign-up/login, argon2 hashing, JWT, roles (student, teacher); teacher-only class endpoints | Protected routes | Security |
| 6 | Tests: pytest + `httpx` against a test DB. Postman collection with test scripts per endpoint, run locally: `/Users/neonguyen/.local/bin/postman collection run postman/quizlab.postman_collection.json -e postman/local.postman_environment.json` | `tests/api/`, `postman/` | Testing, Postman CLI |
| 7 | Redis cache for question lists & leaderboard; measure p50/p95 latency before/after | Latency table in README | Caching |
| 8 | **Transactional outbox:** each answer writes an `attempt_events` row in the same transaction; a worker publishes/processes them. Phase 5 streams from this. | `src/quizlab/worker/` | Events, reliability |
| 9 | Pagination, rate limiting, consistent error schema, validation; run the OWASP checklist | `docs/security-checklist.md` | Hardening |
| 10 | JSON logging with request IDs, `/metrics` (Prometheus format); multi-stage `Dockerfile`; compose = api + worker + db + redis; tag `v0.3.0` | `docker compose up` runs everything | Observability, Docker |

## Done when

- [ ] I can design a REST API and justify my choices for status codes, pagination and errors.
- [ ] I can explain the request lifecycle in FastAPI from socket to DB and back.
- [ ] QuizLab API: auth, quiz flow, cache, outbox worker, ≥ 80% coverage.
- [ ] Postman collection passes via Postman CLI locally.
- [ ] One command (`docker compose up`) starts the whole stack.

## Threads this phase

- **Statistics (new):** 1 [StatQuest](https://www.youtube.com/@statquest) video/week, starting with the "Statistics Fundamentals" playlist.
- **DSA / SQL:** 1 problem each per week.
- **Writing:** ADR 0004 (why FastAPI + layered architecture), ADR 0005 (why outbox).

## Stretch goals

- A small web front end (HTMX or plain JS) for taking a quiz.
- WebSocket endpoint for a live class quiz.
- Load test with [Locust](https://locust.io/) (formal load testing happens in Phase 8).
