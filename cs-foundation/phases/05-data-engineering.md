# Phase 5 — Data engineering ★ (mastery focus)

**Dates:** 2027-10-25 → 2028-01-30 (W48–W61) · **Buffer:** W62, 2028-01-31 → 2028-02-06
**Prerequisites:** Phase 2 (SQL, OLTP vs OLAP), Phase 3 (outbox events), Phase 4 (AWS, Terraform, CI) · [← Phase 4](04-devops-aws.md) · [Learning path](../learning-path.md) · [Next: Phase 6 →](06-data-science-ml.md)

## Goal

This is the centre of the career path. By the end I can design and build a complete data platform. That covers ingestion (batch + streaming), a lake with open table formats, orchestration, dimensional modeling, transformation with dbt, data quality, distributed processing with Spark, and governance. I also understand the distributed-systems theory behind these tools (DDIA).

The project track turns QuizLab's operational database and attempt events into an analytics warehouse. Phase 6 (ML) and Phase 7 (AI) are both built on that warehouse.

> **Note on DDIA:** the 2nd edition reorganized chapters. The table below names chapters by **topic**, so the plan works with either edition.
> **Note on Airflow cost:** managed Airflow (MWAA) is expensive. Run Airflow locally in Docker against AWS resources. Deploying it to ECS is a stretch goal.

## Theory track

| Week | Topic | Resource | Output |
|---|---|---|---|
| 1 | The data engineering lifecycle; roles; architecture principles | *Fundamentals of Data Engineering* (FoDE) ch. 1–3 | My one-page map of the lifecycle with QuizLab examples |
| 2 | Data models, storage engines (row vs column), encoding & schema evolution | [DDIA](https://dataintensive.net/): data models, storage & retrieval, encoding chapters | Why columnar formats make analytics fast |
| 3 | Source systems & ingestion: batch, incremental, CDC, push vs pull | FoDE ch. 5 & 7 | Ingestion patterns table with pros/cons |
| 4 | Storage: lakes, Parquet/Avro, partitioning, open table formats (Iceberg, Delta) | FoDE ch. 6 + [Apache Iceberg docs](https://iceberg.apache.org/docs/latest/) (concepts) | Explain what a table format adds over plain Parquet |
| 5 | Orchestration: DAGs, idempotency, retries, backfills, sensors | [Airflow docs](https://airflow.apache.org/docs/apache-airflow/stable/index.html): fundamentals tutorial + best practices | Rules for an idempotent task |
| 6 | Dimensional modeling: facts, dimensions, grain, bus matrix | Kimball, *The Data Warehouse Toolkit* ch. 1–3 | Bus matrix for QuizLab |
| 7 | Slowly changing dimensions; fact-table types (transaction, snapshot, accumulating) | *Data Warehouse Toolkit* ch. 4–5 | SCD type 1 vs 2 vs 3 with examples |
| 8 | Analytics engineering with dbt: models, refs, materializations, incremental | [dbt Learn: dbt Fundamentals](https://learn.getdbt.com/) (free) | When to use view vs table vs incremental |
| 9 | Data quality, data contracts, testing, observability | FoDE "undercurrents" sections + [dbt data tests](https://docs.getdbt.com/docs/build/data-tests) | QuizLab data-quality checklist |
| 10 | Batch processing at scale: MapReduce → Spark; DataFrames | DDIA batch-processing chapter + [DE Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp) batch/Spark module | Explain a shuffle |
| 11 | Spark performance: partitions, skew, broadcast joins, caching | *Learning Spark* (2nd ed.) ch. 3, 7 + [PySpark docs](https://spark.apache.org/docs/latest/api/python/) | Spark tuning checklist |
| 12 | Stream processing: logs, Kafka/Kinesis, delivery guarantees, windows | DDIA stream-processing chapter + DE Zoomcamp streaming module | At-least-once vs exactly-once, and how idempotency rescues you |
| 13 | Distributed data: replication, partitioning/sharding, consistency, consensus (overview) | DDIA replication, partitioning, consistency chapters | Where these show up in S3, Kinesis, RDS |
| 14 | Serving, security, privacy (PII), governance, cost | FoDE ch. 9–10 | PII and access plan for QuizLab |

## Project track (in `quizlab/pipelines/`)

| Week | Task | Deliverable | Skills |
|---|---|---|---|
| 1 | Platform design doc: sources, layers (raw → staged → marts), tools, SLAs; local stack = Airflow (compose) + MinIO (S3-compatible) + DuckDB | `docs/data-platform.md` v1 + ADR 0008 | Architecture |
| 2 | **Batch ingestion DAG:** incremental extract of Postgres tables (`updated_at` watermark) → Parquet in `raw/`, partitioned by date; idempotent re-runs | `dags/extract_oltp.py` | Airflow, incremental loads |
| 3 | **Event ingestion:** the Phase 3 outbox worker writes versioned JSON events (JSON Schema contract) to `raw/events/` | `contracts/attempt_event.v1.json` | Data contracts |
| 4 | Terraform the AWS lake: S3 buckets + lifecycle rules, Glue catalog, Athena workgroup; staged layer as **Iceberg** tables | `infra/terraform/lake/` | Lake on AWS |
| 5 | Airflow production habits: retries, alerts, SLAs, task groups; **backfill one month** and prove re-runs don't duplicate | Backfill log + row-count check | Orchestration |
| 6 | Dimensional design: grain statement, `fct_attempts`, `fct_quiz_sessions`, `dim_student`, `dim_question`, `dim_topic`, `dim_date` | `docs/warehouse-model.md` | Kimball modeling |
| 7 | SCD type 2 for `dim_student` (class/grade changes) using dbt snapshots | Snapshot + test showing history | SCDs |
| 8 | **dbt project:** staging → intermediate → marts; runs on DuckDB locally and on Athena (`dbt-athena`) in the cloud; incremental `fct_attempts` | `pipelines/dbt/` + dbt docs site | dbt |
| 9 | Data quality: dbt tests (unique, not_null, relationships, accepted_values, freshness) + custom tests; DAG fails on bad data; **data CI** runs `dbt build` on every PR | `.github/workflows/data-ci.yml` | DQ, CI |
| 10 | **PySpark backfill:** generate 1 year of historical attempts (10M+ rows) and build daily aggregates; Spark runs locally in Docker | `pipelines/spark/backfill.py` | Spark |
| 11 | Tune that job (partitioning, broadcast join, `explain()`); run it once on AWS (EMR Serverless or Glue) and compare time/cost with local | `docs/spark-tuning.md` | Spark performance |
| 12 | **Streaming:** API events → Kinesis (local: Redpanda) → consumer writes micro-batches to S3; dedupe by `event_id`; "live class accuracy" metric updated every minute | `pipelines/streaming/` | Streaming |
| 13 | Serving: `mart_student_topic_mastery`; sync the mart back to Postgres for the API (`GET /students/{id}/progress`); quick Metabase/Streamlit view on marts | Endpoint + dashboard | Serving, reverse ETL |
| 14 | Governance: hash/pseudonymize student PII in the lake, IAM per layer, lineage via dbt docs, cost per pipeline; final `docs/data-platform.md`; tag `v0.5.0` | Platform docs complete | Governance |

## Done when

- [ ] I can whiteboard a batch + streaming platform and defend each tool choice.
- [ ] I can explain idempotency, backfills, SCD2, partitioning, shuffles and delivery guarantees using my own project.
- [ ] Airflow runs extract → load → dbt build → tests end-to-end; re-runs are idempotent.
- [ ] Warehouse star schema on Athena with ≥ 30 dbt tests; data CI is green.
- [ ] Spark backfill and streaming path both land in the same lake tables.
- [ ] `docs/data-platform.md` has an architecture diagram, SLAs, cost, and lineage.

## Threads this phase

- **SQL:** keep 1 hard problem/week, now focusing on warehouse-style queries (sessionization, funnels, retention).
- **Statistics / DSA:** 1 each per week.
- **Writing:** ADR 0008 (lake + Iceberg + Athena), ADR 0009 (Airflow vs alternatives), ADR 0010 (Kinesis vs Kafka).
- **Optional cert:** AWS Certified Data Engineer – Associate during the buffer week + 2–3 extra weeks.

## Stretch goals

- Deploy Airflow to ECS; or compare with Dagster on one DAG.
- Change data capture with Debezium from Postgres instead of watermark extracts.
- Great Expectations or Soda alongside dbt tests.
- Write a blog post: "Building a learning-analytics warehouse on S3 + Iceberg + dbt".

## Resources

- *Fundamentals of Data Engineering*: Joe Reis & Matt Housley
- *Designing Data-Intensive Applications*: Martin Kleppmann
- *The Data Warehouse Toolkit* (3rd ed.): Ralph Kimball & Margy Ross
- *Learning Spark* (2nd ed.): Damji et al.
- [DataTalksClub DE Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp): free. It uses GCP; translate each module to AWS as practice.
