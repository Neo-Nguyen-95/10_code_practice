# Learning tracker

A small local website for following [the learning path](../learning-path.md) and tracking progress.

## Run it

From the repository root:

```bash
uv run --with streamlit streamlit run cs-foundation/tracker/app.py
```

It opens at <http://localhost:8501>. Stop it with `Ctrl+C`.

## Pages

| Page | What it does |
|---|---|
| **Dashboard** | Current week and phase, overall progress, progress per phase, hours-per-week chart, overdue tasks |
| **This week** | This week's theory and project tasks with checkboxes, plus the weekly log form (hours, what I learned, recall questions, blockers, next step) |
| **Phases** | Every week of a phase, with checkboxes and the phase's *Done when* list |
| **Weekly logs** | All saved weekly logs, newest first |

Use **Settings → Pretend today is** in the sidebar to preview another week.

## How it works

- **The plan** comes from the Markdown files in [../phases/](../phases/). Edit a phase file and refresh the page to see the change.
- **My progress** is saved in `progress.json` in this folder. Commit it regularly so Git keeps the history.
- Each tick is linked to its task's **phase + track + title text**, not its row position:
  - Adding, removing or reordering rows, or moving a task to another week, is safe. Ticks stay on the right task.
  - **Rewording** a ticked task's title (the second column) breaks the link. The old tick is never moved silently. It appears on the Dashboard under *Ticks that no longer match a task*, where you can **Move** it to the reworded task or **Remove** it.
- `progress.json` stores each tick's date and the task title at the time it was ticked, so it stays readable in Git diffs.
