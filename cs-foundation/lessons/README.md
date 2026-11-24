# Lessons

Interactive lessons for the **Learn** page of the [tracker](../tracker/README.md). Each lesson is one Markdown file in this folder. The app turns special code blocks into quizzes and SQL exercises.

**File name:** `p<phase>-w<week>-<topic>.md`, for example `p2-w2-sql-joins-groupby-windows.md`. Files whose name starts with `_` and this README are ignored.

## Front matter (required)

```markdown
---
title: Querying the question bank — JOIN, GROUP BY and window functions
phase: 2          # links the lesson to that week of the plan
week: 2           # week inside the phase; the "This week" page shows a button to open it
minutes: 60
summary: One sentence shown on the lesson card.
---
```

Everything else is normal Markdown: headings, lists, tables, `code`. Normal code blocks (` ```sql `, ` ```python `) are shown as code.

## Special blocks

### `quiz`: multiple choice with explanation

````markdown
```quiz
Which clause filters groups after GROUP BY?
- [ ] WHERE
- [x] HAVING
- [ ] ORDER BY
> `HAVING` runs after grouping, so it can use aggregates like COUNT(*).
```
````

- The lines before the options are the question (Markdown is allowed).
- `- [x]` marks a correct option. **More than one `[x]`** turns it into "select all that apply".
- Lines starting with `> ` are the explanation, shown after checking.

### `sql-setup`: the lesson's database

````markdown
```sql-setup
CREATE TABLE subjects (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
INSERT INTO subjects VALUES (1, 'Physics'), (2, 'Chemistry');
```
````

The block is not displayed. Its SQL builds a fresh in-memory **SQLite** database for every query run in the lesson, so learners can't break anything. One setup block per lesson; it applies to all exercises. The app shows the tables under *Tables in this lesson*.

### `sql-exercise`: write a query, auto-checked

````markdown
```sql-exercise
title: Questions per subject
Show each subject's `name` and its number of questions, most first.
hint: JOIN subjects to questions, then GROUP BY the subject.
hint: A second, more specific hint.
order: true
---
SELECT s.name, COUNT(*) AS questions
FROM subjects s JOIN questions q ON q.subject_id = s.id
GROUP BY s.id, s.name
ORDER BY questions DESC, s.name;
```
````

- `title:` the exercise name. Other lines before `---` (except `hint:` and `order:`) are the task, in Markdown.
- `hint:` lines are revealed one at a time.
- `order: true` means row order matters (the task asks for ORDER BY). Without it, rows can come back in any order.
- After `---` comes the **solution**. The app runs it to produce the *expected output* and compares the learner's result with it: same number of columns, same values (column **names** don't matter), same order if `order: true`.
- The app checks every solution when the lesson loads and shows an error if one fails.

### `sql-sandbox`: free query box

````markdown
```sql-sandbox
title: Free practice
SELECT * FROM questions LIMIT 5;
```
````

The SQL is the starting query. Nothing is graded.

## Progress

Quiz and exercise results are saved in `tracker/progress.json` under `lessons`, keyed by the lesson's file name and each block's title or question text. Like plan tasks, **rewording** a quiz question or exercise title resets that item's progress.
