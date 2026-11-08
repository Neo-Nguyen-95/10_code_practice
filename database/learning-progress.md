# Database learning progress

Last session: 2026-11-07. Resume with database inspection and checking whether `subject_id` is required.

## Goal and tutoring preferences

Learn the techniques in [CS50 SQL — Lecture 3: Writing](https://www.youtube.com/watch?v=BD08USRd2M8) through a high school science question-bank project, using PostgreSQL in Docker and SQL from both the terminal and Python.

Use the coding-tutor skill throughout the conversation. Give one manageable step at a time, let me write the code, review my attempts, and give focused hints when debugging. Do not use the museum project from the lecture.

## Environment

- Container: `science-question-db`, created from `postgres:17-bookworm`.
- Persistent volume: `science-question-data`, mounted at `/var/lib/postgresql/data`.
- Connection from Python on the Mac: `localhost:5433`.
- PostgreSQL port inside the container: `5432`.
- Database: `science_question_bank`; user: `postgres`.
- Python environment: `database/.venv`, managed with uv; Python 3.13.13.
- Installed driver: Psycopg 3.3.6 (`psycopg[binary]`).
- Use the connection credentials already in the practice scripts.

## Practised so far

- Docker images, containers, volumes, and port mapping; `docker ps` versus `docker ps -a`.
- Connecting with `psql`, listing databases with `\l`, inspecting tables with `\d questions`, and exiting with `\q`.
- Connecting from Python with `psycopg.connect()` and querying the current database and user.
- Creating a database from Python with `autocommit=True`: `CREATE DATABASE` must run outside a transaction block.
- Creating the `questions` table from Python:

  ```sql
  CREATE TABLE questions (
      id INTEGER PRIMARY KEY,
      subject TEXT,
      grade INTEGER,
      question_text TEXT NOT NULL,
      answer TEXT
  );
  ```

- Inserting, selecting, updating, and deleting questions using terminal SQL and Python.
- Parameterized SQL: `%s` placeholders with a separate tuple of values.
- Reading query results with `fetchone()` and `fetchall()`; checking affected rows with `cursor.rowcount`.
- Reading CSV files with `csv.DictReader`, converting `id` and `grade` from strings to integers, and importing rows with one connection around the loop.
- Connection context managers: successful exit commits; an exception rolls back the transaction and closes the connection.
- Created `subjects` with `id INTEGER PRIMARY KEY` and `name TEXT NOT NULL UNIQUE`; inserted Physics (1), Chemistry (2), and Biology (3).
- Inserted multiple subjects by looping through `(id, name)` tuples and passing one tuple to each `conn.execute()` call.
- Added `questions.subject_id INTEGER REFERENCES subjects(id)` and assigned subject IDs using parameterized `UPDATE ... SET ... WHERE ...` statements.
- Verified that assigning subject ID 99 raises `psycopg.errors.ForeignKeyViolation` because that ID does not exist in `subjects`.
- Discussed deletion behavior: the current foreign key blocks deleting a referenced subject. The learner prefers blocking until questions are reassigned; `ON DELETE CASCADE` was explained but not enabled. Deletion blocking was not tested.
- Used a JOIN to retrieve subject names, then filtered for Physics and selected question IDs, text, and names.
- Understood that renaming a subject changes subsequent JOIN results without updating question rows; the original `questions.subject` text is redundant and can conflict with `subject_id`.
- Queried for `subject_id IS NULL`; the learner reported no rows.
- Introduced database inspection: `pg_database`, `information_schema.tables`, and `information_schema.columns`; queries operate within the connected database, so inspecting other databases' tables requires other connections.
- Introduced `COUNT(*)`, `UNION ALL` for counts from two known tables, and `LIMIT` for previews; record-count output has not yet been shared.

## Debugging lessons

- `SHOW DATABASES;` is MySQL syntax; use `\l` in psql.
- Insert into a table (`questions`), not the database (`science_question_bank`).
- SQL text literals need single quotes; numbers do not.
- No trailing comma after the final column in `CREATE TABLE`.
- `CREATE DATABASE` returns no result rows, so do not call `fetchone()` afterward. The database was created even though the later fetch failed.
- A one-item parameter tuple is `(2,)`; `(2)` is an integer.
- Check spelling in filenames and imports (`psycopg`, `import_questions.py`).
- Keep the database connection outside the CSV loop to commit the import together.
- `NOT NULL` rejects NULL but permits an empty text string; `UNIQUE` does not validate subject spelling.
- `execute()` accepts one parameter collection per call. For multiple VALUES groups, pass one flat tuple, or loop over rows with one tuple per execution.
- `None` in Python query output represents SQL NULL.
- psql commands such as `\l`, `\dt`, and `\d questions` cannot be passed to Psycopg's `execute()`; use SQL metadata queries in Python.
- A local file named `inspect.py` can shadow Python's standard-library `inspect` module and cause a partially initialized Psycopg/circular-import error. Recommended renaming to `inspect_database.py`; check whether the old `inspect.py` still exists if this error returns.
- `column_name`, `data_type`, and `is_nullable` belong to `information_schema.columns`, not `information_schema.tables`. The latter caused an `UndefinedColumn` error; the file now uses `columns`, but successful output has not yet been shared.

## Current checkpoint

Files include `connect.py`, `create_database.py`, `create_tables.py`, `insert_question.py`, `inspect_questions.py`, `update_questions.py`, `delete_question.py`, `questions.csv`, `import_questions.py`, `insert.py`, `alter_table.py`, and `inspect_database.py` (all in this folder).

Question 1 (Physics) was inserted. Question 2 (Chemistry) was updated from grade 10 to 11, then back to 10, and its deletion was reported complete.

The CSV import was subsequently verified. Latest shared question rows, including the added subject IDs:

| ID | Subject | Grade | Question | Answer | Subject ID |
| --- | --- | --- | --- | --- | --- |
| 1 | Physics | 10 | What is the SI unit of force? | newton | 1 |
| 3 | Biology | 10 | What is the basic unit of life? | cell | 3 |
| 4 | Chemistry | 10 | What is the chemical formula for water? | H2O | 2 |
| 5 | Physics | 11 | What is the SI unit of electric current? | ampere | 1 |

The original `subject` column still exists. Removing it was discussed but has not been done. `ALTER TABLE questions ALTER COLUMN subject_id SET NOT NULL` was proposed, but execution has not been confirmed. Do not assume it was applied.

`inspect_database.py` currently lists database names and column metadata for `questions` and `subjects`. Its metadata query now correctly reads `information_schema.columns`; it orders by table name only. Suggested improvement: `ORDER BY table_name, ordinal_position` to preserve column order within each table.

Do not rerun creation, insertion, or ADD COLUMN scripts just to resume: existing objects and primary keys can cause errors. Inspect scripts before running them, especially `create_tables.py`, which has been used for several different exercises. Older insert/import scripts may need changes when `subject_id` becomes required or the original `subject` column is removed.

## Resume next session

From the repository root:

```bash
source database/.venv/bin/activate
docker ps
```

If `science-question-db` is stopped, start the existing container:

```bash
docker start science-question-db
```

Resume the pending metadata query (after checking that no conflicting local `inspect.py` remains):

```bash
python database/inspect_database.py
```

Alternatively, connect through the terminal:

```bash
docker exec -it science-question-db psql -U postgres -d science_question_bank
```

```sql
SELECT * FROM questions ORDER BY id;
```

Immediate next step: review the metadata output and check `is_nullable` for `questions.subject_id`. `YES` means NULL is still allowed; `NO` means NOT NULL is applied. If needed, guide the learner through applying SET NOT NULL after confirming no questions lack a subject ID.

Continue the learner's inspection questions by running the previously introduced record-count query if desired. Then return to completing the schema design: plan removal of redundant `questions.subject` and update affected practice scripts with the learner before changing the schema.

Foreign keys have now been practised. Remaining lecture techniques include triggers. Transactions have been introduced through connection context managers; explicit commit/rollback practice can follow. Keep one manageable step at a time and let the learner write the code.
