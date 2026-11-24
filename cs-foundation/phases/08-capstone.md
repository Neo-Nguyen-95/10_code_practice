# Phase 8 — Capstone integration & launch

**Dates:** 2028-07-24 → 2028-09-17 (W87–W94) · **Launch week:** W95, 2028-09-18 → 2028-09-24
**Prerequisites:** Phases 0–7 · [← Phase 7](07-ai-engineering.md) · [Learning path](../learning-path.md) · [Capstone spec](../capstone.md)

## Goal

By now every QuizLab layer exists. This phase makes it **one coherent, reliable, well-documented system**, and turns it into career results: a demo, a write-up, interview-ready stories and an updated CV. The theory track moves to system design and interview preparation, using QuizLab as the example for every answer.

## Theory track

| Week | Topic | Resource | Output |
|---|---|---|---|
| 1 | System design method: requirements, estimates, components, trade-offs | [System Design Primer](https://github.com/donnemartin/system-design-primer) + DDIA reliability/scalability chapter (re-read) | My 6-step design template |
| 2 | Data system design: pipelines, warehouses, streaming at scale | DDIA re-read (batch + stream chapters) + 3 practice prompts ("design a clickstream pipeline") | 3 designs written up |
| 3 | ML/AI system design: features, training, serving, RAG at scale | [Chip Huyen's ML interviews book](https://huyenchip.com/ml-interviews-book/) (free) + *Designing ML Systems* ch. 1–2 review | 2 designs written up |
| 4 | SQL & Python interview drills | [DataLemur](https://datalemur.com/) + LeetCode SQL 50 | 20 timed problems |
| 5 | Behavioral interviews: STAR stories | Write 8 stories from QuizLab (a hard bug, a trade-off, a failure, a design decision…) | Story bank |
| 6 | Mock interviews | Peers or a mock-interview platform; 1 system design + 1 coding | Feedback notes |
| 7 | Technical writing for a portfolio | Read 3 engineering blogs I admire and outline why they work | Post outlines |
| 8 | Job search: role targeting, CV tailoring, networking | Job postings for Data Engineer / Analytics Engineer / ML-AI Engineer | Target-role matrix |

## Project track (in `quizlab`)

| Week | Task | Deliverable | Skills |
|---|---|---|---|
| 1 | **End-to-end test:** scripted student session → API → events → lake → dbt → mastery model → dashboard → tutor; fix every seam | `tests/e2e/` passes in CI | Integration |
| 2 | **Load test** with [Locust](https://locust.io/): set a target RPS, find the bottleneck, fix it (index, cache, scaling), re-test | `docs/load-test.md` | Performance |
| 3 | Unified observability: one dashboard for API, pipelines, model drift and LLM cost; alerts; **game day** (break something on purpose, recover with the runbook) | Game-day report | Reliability |
| 4 | Security review: Dependabot, secret scanning, IAM audit, OWASP + LLM checklists, threat model | `docs/security-review.md` | Security |
| 5 | Docs site with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) on GitHub Pages: architecture, ADRs, reports, runbooks | Public docs site | Writing |
| 6 | Demo environment with demo data and scheduled shutdown (cost control); **3-minute demo video** | Video link in README | Presentation |
| 7 | Portfolio write-ups: 3 posts (data platform; ML on learning data; AI tutor with evals) | Published posts | Writing |
| 8 | README polish; CV bullets with numbers (latency, rows/day, eval scores, cost); pin repo; release `v1.0.0` | v1.0.0 | Career |

## Launch week (W95)

- Publish the posts and the demo; share them on LinkedIn and relevant communities.
- Apply to the first batch of target roles.
- Write the final retrospective in [progress.md](../progress.md): what I can do now compared with 2026-11-30.

## Done when

- [ ] Every item in the [capstone demo checklist](../capstone.md#final-demo-checklist-phase-8) is ticked.
- [ ] I can present QuizLab's architecture in 5 minutes and answer "why" for every component.
- [ ] I have 8 STAR stories, 5 written system designs and a tailored CV.
- [ ] `v1.0.0` released; docs site, demo video and posts are public.

## CV bullet templates

- *Designed and built a learning-analytics data platform on AWS (S3, Iceberg, Athena, Airflow, dbt, Kinesis) processing **N** events/day with **≥ 30** automated data-quality tests.*
- *Built a FastAPI backend deployed via Terraform and GitHub Actions to ECS Fargate, with p95 latency of **N ms** at **N RPS**.*
- *Implemented IRT and mastery-prediction models (AUC **0.xx**), served in production and retrained weekly.*
- *Shipped a RAG AI tutor with citations and a CI eval harness (faithfulness **0.xx**), at **$0.00x** per request.*
