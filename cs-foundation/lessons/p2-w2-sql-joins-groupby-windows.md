---
title: Querying the question bank — JOIN, GROUP BY and window functions
phase: 2
week: 2
minutes: 60
summary: Answer real questions about students and quiz attempts with joins, aggregation, LEFT JOIN anti-joins and window functions.
---

## How to use this lesson

You'll query a small copy of the QuizLab database: **subjects**, **questions**, **students** and their quiz **attempts**. Open *Tables in this lesson* above to see every table.

Follow your [practice loop](../../docs/how-to-practice-coding.md) for each exercise:

1. Read the task and the *expected output*. Write your plan in plain words first.
2. Write the query and press **Run**. Errors are part of learning.
3. Stuck? Use **Hint**, one at a time. That's the smallest useful help.
4. **Show solution** unlocks after your first attempt. Compare it with yours, then re-type it from memory.

Every exercise runs on a fresh copy of the data, so you can't break anything.

```sql-setup
CREATE TABLE subjects (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);
INSERT INTO subjects VALUES (1, 'Physics'), (2, 'Chemistry'), (3, 'Biology');

CREATE TABLE questions (
    id            INTEGER PRIMARY KEY,
    subject_id    INTEGER REFERENCES subjects(id),   -- NULL = not assigned yet
    grade         INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    answer        TEXT NOT NULL
);
INSERT INTO questions VALUES
    (1,  1,    10, 'What is the SI unit of force?', 'newton'),
    (2,  2,    10, 'What is the chemical formula for water?', 'H2O'),
    (3,  3,    10, 'What is the basic unit of life?', 'cell'),
    (4,  1,    11, 'What is the SI unit of electric current?', 'ampere'),
    (5,  2,    11, 'What is the pH of pure water at 25 °C?', '7'),
    (6,  3,    11, 'Which organelle produces most of the cell''s ATP?', 'mitochondria'),
    (7,  1,    10, 'What is the acceleration due to gravity on Earth in m/s²?', '9.8'),
    (8,  2,    12, 'What is the most electronegative element?', 'fluorine'),
    (9,  3,    12, 'Which molecule carries genetic information?', 'DNA'),
    (10, 1,    12, 'What is the speed of light in a vacuum in km/s?', '300000'),
    (11, NULL, 10, 'Which planet is known as the Red Planet?', 'Mars');

CREATE TABLE students (
    id    INTEGER PRIMARY KEY,
    name  TEXT NOT NULL,
    grade INTEGER NOT NULL
);
INSERT INTO students VALUES (1, 'An', 10), (2, 'Bao', 11), (3, 'Chi', 10), (4, 'Dana', 12), (5, 'Eli', 11);

CREATE TABLE attempts (
    id          INTEGER PRIMARY KEY,
    student_id  INTEGER NOT NULL REFERENCES students(id),
    question_id INTEGER NOT NULL REFERENCES questions(id),
    is_correct  INTEGER NOT NULL CHECK (is_correct IN (0, 1)),
    answered_at TEXT NOT NULL
);
INSERT INTO attempts VALUES
    (1,  1, 1, 1, '2027-03-29 09:00'), (2,  1, 2, 1, '2027-03-29 09:05'), (3,  1, 3, 0, '2027-03-29 09:10'),
    (4,  1, 4, 1, '2027-03-30 19:00'), (5,  1, 5, 1, '2027-03-30 19:05'), (6,  1, 6, 1, '2027-03-30 19:10'),
    (7,  2, 1, 0, '2027-03-29 10:00'), (8,  2, 2, 1, '2027-03-29 10:04'), (9,  2, 7, 1, '2027-03-29 10:09'),
    (10, 2, 9, 0, '2027-03-31 20:00'), (11, 2, 3, 1, '2027-03-31 20:06'),
    (12, 3, 1, 1, '2027-03-29 16:00'), (13, 3, 3, 1, '2027-03-29 16:03'), (14, 3, 7, 0, '2027-03-29 16:08'),
    (15, 3, 2, 1, '2027-04-01 08:00'), (16, 3, 4, 0, '2027-04-01 08:04'), (17, 3, 6, 1, '2027-04-01 08:09'),
    (18, 4, 9, 1, '2027-03-30 21:00'), (19, 4, 5, 1, '2027-03-30 21:04'), (20, 4, 1, 1, '2027-03-30 21:07'),
    (21, 5, 2, 0, '2027-03-31 07:30'), (22, 5, 6, 1, '2027-03-31 07:34'), (23, 5, 7, 1, '2027-03-31 07:39'),
    (24, 5, 3, 1, '2027-04-02 18:00'), (25, 5, 4, 0, '2027-04-02 18:05');
```

## 1. JOIN: combine rows from two tables

`questions` only stores a `subject_id`. To show the subject's **name**, join each question to the subject whose `id` matches:

```sql
SELECT q.question_text, s.name
FROM questions AS q
JOIN subjects  AS s ON s.id = q.subject_id;
```

A plain `JOIN` (also called `INNER JOIN`) keeps only rows that **have a match** on both sides.

```quiz
Question 11 has `subject_id = NULL`. How many rows does this return?

`SELECT * FROM questions q JOIN subjects s ON s.id = q.subject_id;`
- [ ] 11
- [x] 10
- [ ] 12
- [ ] 0
> An inner join keeps only matching pairs. `NULL = 1` is not true (it's *unknown*), so question 11 matches no subject and disappears. The other 10 questions each match exactly one subject.
```

```sql-exercise
title: Grade 10 questions with their subject
List the `question_text` and subject `name` of every **grade 10** question, ordered by question `id`.
hint: Start from the JOIN above, then add a WHERE clause for the grade.
hint: Put ORDER BY q.id at the very end of the query.
order: true
---
SELECT q.question_text, s.name
FROM questions AS q
JOIN subjects AS s ON s.id = q.subject_id
WHERE q.grade = 10
ORDER BY q.id;
```

## 2. GROUP BY and HAVING: one row per group

`GROUP BY` collapses many rows into **one row per group**, and aggregate functions (`COUNT`, `SUM`, `AVG`, `MIN`, `MAX`) summarize each group.

```sql
SELECT subject_id, COUNT(*) AS questions
FROM questions
GROUP BY subject_id;
```

- `WHERE` filters **rows before** grouping.
- `HAVING` filters **groups after** grouping, so it can use aggregates such as `COUNT(*) >= 5`.

```sql-exercise
title: Questions per subject
Show each subject's `name` and its number of questions. Put the subject with the most questions first; break ties alphabetically by name.
hint: JOIN subjects to questions, then GROUP BY the subject.
hint: ORDER BY can sort on two things: `ORDER BY questions DESC, s.name`.
order: true
---
SELECT s.name, COUNT(*) AS questions
FROM subjects AS s
JOIN questions AS q ON q.subject_id = s.id
GROUP BY s.id, s.name
ORDER BY questions DESC, s.name;
```

```quiz
You want only the students with **at least 5 attempts**. Which clause do you use for `COUNT(*) >= 5`?
- [ ] WHERE
- [x] HAVING
- [ ] ORDER BY
- [ ] LIMIT
> `COUNT(*)` only exists *after* rows are grouped, and `WHERE` runs before grouping. `HAVING` is the filter for groups.
```

```sql-exercise
title: Accuracy per student
For each student with **at least 5 attempts**, show their `name`, number of `attempts`, and `accuracy_pct`: the percentage of correct attempts, **rounded to 1 decimal**. Highest accuracy first; break ties by name.
hint: `is_correct` is 1 or 0, so `SUM(is_correct)` counts the correct answers.
hint: Multiply by `100.0` (not `100`) so SQLite does decimal division instead of integer division.
hint: `ROUND(value, 1)` rounds to one decimal. Filter the groups with `HAVING COUNT(*) >= 5`.
order: true
---
SELECT st.name,
       COUNT(*) AS attempts,
       ROUND(100.0 * SUM(a.is_correct) / COUNT(*), 1) AS accuracy_pct
FROM students AS st
JOIN attempts AS a ON a.student_id = st.id
GROUP BY st.id, st.name
HAVING COUNT(*) >= 5
ORDER BY accuracy_pct DESC, st.name;
```

## 3. LEFT JOIN: keep rows that have no match

`LEFT JOIN` keeps **every row from the left table**. Where there is no match on the right, the right-hand columns are filled with `NULL`. That gives you a classic pattern, the **anti-join**: "rows in A with no partner in B".

```sql
SELECT ...
FROM a
LEFT JOIN b ON b.a_id = a.id
WHERE b.id IS NULL;   -- no partner found
```

```sql-exercise
title: Questions nobody has tried
List the `id` and `question_text` of every question that has **no attempts at all**, ordered by `id`.
hint: Start FROM questions and LEFT JOIN attempts ON the question id.
hint: Unmatched questions have NULL in every attempts column. Keep only those with `WHERE a.id IS NULL`.
order: true
---
SELECT q.id, q.question_text
FROM questions AS q
LEFT JOIN attempts AS a ON a.question_id = q.id
WHERE a.id IS NULL
ORDER BY q.id;
```

```quiz
`attempts` has 25 rows, every attempt points to an existing question, and 3 questions have no attempts. What does this return?

`SELECT COUNT(*), COUNT(a.id) FROM questions q LEFT JOIN attempts a ON a.question_id = q.id;`
- [x] 28 and 25
- [ ] 25 and 25
- [ ] 28 and 28
- [ ] 11 and 25
> The LEFT JOIN produces 25 matched rows plus 3 rows for unattempted questions, 28 in total. `COUNT(*)` counts rows (28), but `COUNT(a.id)` skips NULLs, so the 3 unmatched rows don't count (25).
```

## 4. Window functions: calculate across rows *without* collapsing them

A window function looks at a set of related rows (the **window**) but, unlike `GROUP BY`, **keeps every row**:

```sql
SELECT student_id, answered_at,
       ROW_NUMBER() OVER (PARTITION BY student_id ORDER BY answered_at) AS nth_attempt
FROM attempts;
```

- `PARTITION BY` starts the numbering again for each student (like a GROUP BY that doesn't collapse rows).
- `ORDER BY` inside `OVER (...)` decides the order within each partition.

```quiz
Compared with the input, how many rows does a query with a window function (and no GROUP BY or WHERE) return?
- [x] The same number of rows
- [ ] One row per partition
- [ ] Only the first row of each partition
> Window functions add a column to each row; they never remove rows. To keep only some rows, filter the result in an outer query or CTE (the next exercises do exactly that).
```

```sql-exercise
title: Leaderboard with ties
Show each student's `name`, their number of `correct` answers, and their rank using `RANK()` (most correct = rank 1). Order by rank, then name.
hint: First GROUP BY student and compute `SUM(a.is_correct)`.
hint: You can use an aggregate inside the window: `RANK() OVER (ORDER BY SUM(a.is_correct) DESC)`.
hint: `rank` is a reserved word in some databases. Name the column `rnk` to be safe.
order: true
---
SELECT st.name,
       SUM(a.is_correct) AS correct,
       RANK() OVER (ORDER BY SUM(a.is_correct) DESC) AS rnk
FROM students AS st
JOIN attempts AS a ON a.student_id = st.id
GROUP BY st.id, st.name
ORDER BY rnk, st.name;
```

```quiz
Three students tie on 3 correct answers, behind An (5) and Chi (4). Which functions give **all three the same number**?
- [x] RANK()
- [x] DENSE_RANK()
- [ ] ROW_NUMBER()
> `RANK()` gives 1, 2, 3, 3, 3 and would skip to 6 next. `DENSE_RANK()` gives 1, 2, 3, 3, 3 and would continue with 4. `ROW_NUMBER()` always gives distinct numbers (1, 2, 3, 4, 5), and which tied row gets which number is arbitrary.
```

```sql-exercise
title: Each student's first attempt
For every student, show their `name`, the `question_id` of their **first** attempt (earliest `answered_at`), and its `answered_at`. Order by name.
hint: Number each student's attempts with `ROW_NUMBER() OVER (PARTITION BY student_id ORDER BY answered_at)`.
hint: You can't filter on a window function in WHERE. Put the numbered query in a CTE: `WITH numbered AS (...)`.
hint: Then `SELECT ... FROM numbered JOIN students ... WHERE nth_attempt = 1`.
order: true
---
WITH numbered AS (
    SELECT a.*,
           ROW_NUMBER() OVER (PARTITION BY a.student_id ORDER BY a.answered_at) AS nth_attempt
    FROM attempts AS a
)
SELECT st.name, n.question_id, n.answered_at
FROM numbered AS n
JOIN students AS st ON st.id = n.student_id
WHERE n.nth_attempt = 1
ORDER BY st.name;
```

## 5. Sandbox: explore freely

Try your own ideas. For example: which **question** has the lowest accuracy? Which **subject** is hardest? How many attempts happened on each day?

```sql-sandbox
title: Free practice
SELECT q.id, q.question_text,
       COUNT(a.id)                AS attempts,
       ROUND(AVG(a.is_correct), 2) AS accuracy
FROM questions AS q
LEFT JOIN attempts AS a ON a.question_id = q.id
GROUP BY q.id
ORDER BY accuracy;
```

## Taking it to PostgreSQL

These queries run almost unchanged on your `science-question-db` container. Two differences to know:

- `ROUND(x, 1)` in PostgreSQL needs a `numeric` value: `ROUND((100.0 * SUM(...) / COUNT(*))::numeric, 1)`.
- PostgreSQL has a real `BOOLEAN` type. With `is_correct BOOLEAN`, count correct answers with `COUNT(*) FILTER (WHERE is_correct)` or `SUM(is_correct::int)`.

**Next step:** recreate the `students` and `attempts` tables in your Docker Postgres and run the *Accuracy per student* query there.
