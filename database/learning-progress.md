# Database learning progress

Last session: 2026-10-25. Plan: continue tomorrow, 2026-10-26.

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

## Debugging lessons

- `SHOW DATABASES;` is MySQL syntax; use `\l` in psql.
- Insert into a table (`questions`), not the database (`science_question_bank`).
- SQL text literals need single quotes; numbers do not.
- No trailing comma after the final column in `CREATE TABLE`.
- `CREATE DATABASE` returns no result rows, so do not call `fetchone()` afterward. The database was created even though the later fetch failed.
- A one-item parameter tuple is `(2,)`; `(2)` is an integer.
- Check spelling in filenames and imports (`psycopg`, `import_questions.py`).
- Keep the database connection outside the CSV loop to commit the import together.

## Current checkpoint

Files: `connect.py`, `create_database.py`, `create_tables.py`, `insert_question.py`, `inspect_questions.py`, `update_questions.py`, `delete_question.py`, `questions.csv`, and `import_questions.py` (all in this folder).

Question 1 (Physics) was inserted. Question 2 (Chemistry) was updated from grade 10 to 11, then back to 10, and its deletion was reported complete.

The latest CSV import completed without a traceback and printed `Rows inserted: 1` three times, for:

| ID | Subject | Grade | Question | Answer |
| --- | --- | --- | --- | --- |
| 3 | Biology | 10 | What is the basic unit of life? | cell |
| 4 | Chemistry | 10 | What is the chemical formula for water? | H2O |
| 5 | Physics | 11 | What is the SI unit of electric current? | ampere |

The import script was reviewed and now uses one connection around the loop. A post-import query result has not yet been shared; expected IDs are 1, 3, 4, and 5. Do not rerun the creation or insertion scripts just to resume: existing databases, tables, or primary keys can cause duplicate-object errors.

## Resume tomorrow

From the repository root:

```bash
source database/.venv/bin/activate
docker ps
```

If `science-question-db` is stopped, start the existing container:

```bash
docker start science-question-db
```

Verify saved questions:

```bash
python database/inspect_questions.py
```

Alternatively, connect through the terminal:

```bash
docker exec -it science-question-db psql -U postgres -d science_question_bank
```

```sql
SELECT * FROM questions ORDER BY id;
```

Next topic: **foreign-key constraints**. A `subjects` table was introduced conceptually, but has not been created and no schema changes have been made for it.

Resume with the pending discussion: what problem could occur if one question stores `Physics` and another stores `Physcis`? Then gradually design a subjects table and link questions to it.

Remaining lecture techniques include foreign-key constraints and triggers. Transactions have been introduced through connection context managers; explicit commit/rollback practice can follow.
