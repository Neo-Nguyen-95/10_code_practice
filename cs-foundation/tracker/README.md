# Learning tracker

A small local website for following [the learning path](../learning-path.md) and tracking progress.

## Run it

From the repository root:

```bash
uv run --with streamlit streamlit run cs-foundation/tracker/app.py
```

It opens at <http://localhost:8501> and only accepts connections from this computer. Stop it with `Ctrl+C`.

## Pages

| Page | What it does |
|---|---|
| **Dashboard** | This week's phase and status, progress bars (phase tasks, phase time used, whole path), metrics (tasks done, hours vs target, study streak, overdue), a study-hours chart with your target line, *Next up* tasks, and a **plan map** heatmap of every week |
| **This week** | Step through weeks with ◀ ▶ / *Now*; tick theory and project tasks; log study sessions; write the weekly journal |
| **Plan** | Timeline of all phases, **search across every task**, filter All/Open/Done, switch phases, and the *Done when* checklist |
| **Learn** | Interactive lessons from [../lessons/](../lessons/): explanations, quick-check quizzes, and **SQL exercises checked automatically** (Run, hints one at a time, solution after your first try), plus a free SQL sandbox. A lesson linked to the current week gets an *Open lesson* button on **This week** |
| **Review** | Flashcards built from the recall questions in your journal. Answer first, check your notes, then mark *Got it* or *Again* |
| **Journal** | Every week's journal and study sessions; delete a session logged by mistake |

**Log a study session** (sidebar button, or on *This week*): pick Theory/Project and a duration, add a note. Hours on every page come from these sessions.

Small rewards: a toast after each tick, and balloons when you finish a week.

**Sidebar → Settings:** *Pretend today is* (preview another week) and your *weekly target hours*.

**Light/dark mode:** follows your system. Switch it in the app menu (⋮ → Settings).

## Files

| File | Role |
|---|---|
| `app.py` | Entry point: navigation, sidebar |
| `views.py` | Dashboard, This week, Plan, Review, Journal, and shared widgets |
| `learn.py` | The Learn page: lesson list, quizzes, SQL exercises, sandbox |
| `lessons.py` | Reads lessons from [../lessons/](../lessons/) (format: [lessons README](../lessons/README.md)) |
| `sqlbox.py` | Runs lesson SQL in a fresh in-memory SQLite database and checks results |
| `charts.py` | Altair charts (hours, plan map, timeline) |
| `plan.py` | Reads the plan from [../phases/](../phases/) (read-only) |
| `store.py` | Loads and saves `progress.json` |
| `.streamlit/config.toml` | Theme colors (light and dark), local-only server |
| `progress.json` | **Your progress.** Created on first use. Commit it regularly so Git keeps the history |

## How progress is saved

- **The plan** comes from the Markdown files in [../phases/](../phases/). Edit a phase file and refresh the page to see the change.
- **Ticks, study sessions, journal entries, flashcard progress and lesson results** are saved in `progress.json`. Every save writes a temporary file and swaps it in, so a crash cannot corrupt it.
- Each tick is linked to its task's **phase + track + title text**, not its row position:
  - Adding, removing or reordering rows, or moving a task to another week, is safe. Ticks stay on the right task.
  - **Rewording** a ticked task's title (the second column) breaks the link. The old tick is never moved silently. It appears on the Dashboard under *Ticks that no longer match a task*, where you can **Move** it to the reworded task or **Remove** it.
