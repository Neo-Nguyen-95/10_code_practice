"""Learning tracker — a small local website for my learning path.

It reads the phase plans in ../phases/*.md (the Markdown files stay the source of
truth for *what* to learn) and stores *my progress* in progress.json next to this
file, so Git keeps the history.

Run from the repository root:

    uv run --with streamlit streamlit run cs-foundation/tracker/app.py
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

HERE = Path(__file__).resolve().parent
PHASES_DIR = HERE.parent / "phases"
STATE_FILE = HERE / "progress.json"

THEORY_COLOR = "#2a78d6"   # blue
PROJECT_COLOR = "#eb6834"  # orange


# ---------------------------------------------------------------------------
# Reading the plan (Markdown -> Python objects)
# ---------------------------------------------------------------------------

@dataclass
class Task:
    id: str          # stable id, e.g. "p1-theory-w3-0"
    phase: int
    track: str       # "theory" or "project"
    week: int        # week number inside the phase (1, 2, ...)
    title: str       # first column of the table row
    details: str     # the other columns, as Markdown


@dataclass
class Phase:
    number: int
    name: str
    path: Path
    start: date          # first day of the phase
    first_week: int      # global week number (W1 = 2026-11-30)
    last_week: int
    buffer_week: int     # the buffer (or launch) week after the phase
    tasks: list[Task] = field(default_factory=list)
    done_when: list[Task] = field(default_factory=list)

    @property
    def weeks(self) -> int:
        return self.last_week - self.first_week + 1

    def global_week(self, week: int) -> int:
        return self.first_week + week - 1

    def tasks_for(self, week: int, track: str) -> list[Task]:
        return [t for t in self.tasks if t.week == week and t.track == track]

    @property
    def all_items(self) -> list[Task]:
        return self.tasks + self.done_when


def split_sections(text: str) -> dict[str, str]:
    """Map each '## Heading' to the text under it."""
    sections = {}
    for chunk in re.split(r"^## ", text, flags=re.M)[1:]:
        heading, _, body = chunk.partition("\n")
        sections[heading.strip()] = body
    return sections


def parse_table(body: str) -> tuple[list[str], list[list[str]]]:
    """Return (header, rows) of the first Markdown table in body."""
    lines = [line.strip() for line in body.splitlines() if line.strip().startswith("|")]
    if len(lines) < 3:
        return [], []

    def cells(line: str) -> list[str]:
        return [c.strip() for c in line.strip("|").split("|")]

    return cells(lines[0]), [cells(line) for line in lines[2:]]  # skip the |---| row


def task_key(phase_no: int, track: str, title: str, seen: dict[str, int]) -> str:
    """Stable id built from the task's *text*, not its position in the table.

    Adding, removing, reordering or moving rows between weeks keeps every tick
    attached to the right task. Rewording a task changes its id; the old tick
    then shows up as "unmatched" on the Dashboard so it can be reassigned.
    """
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", title)       # [text](url) -> text
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:80]
    key = f"p{phase_no}/{track}/{slug}"
    seen[key] = seen.get(key, 0) + 1
    return key if seen[key] == 1 else f"{key}#{seen[key]}"  # same title twice in one phase+track


def parse_track(phase_no: int, track: str, body: str) -> list[Task]:
    header, rows = parse_table(body)
    tasks, seen = [], {}
    for row in rows:
        details = " · ".join(f"**{h}:** {c}" for h, c in zip(header[2:], row[2:]))
        key = task_key(phase_no, track, row[1], seen)
        tasks.append(Task(key, phase_no, track, int(row[0]), row[1], details))
    return tasks


def load_phase(path: Path) -> Phase:
    text = path.read_text(encoding="utf-8")
    title = re.search(r"^# Phase (\d+) — (.+)$", text, re.M)
    dates = re.search(r"\*\*Dates:\*\* (\d{4}-\d{2}-\d{2}) → \S+ \(W(\d+)–W(\d+)\)", text)
    buffer = re.search(r"\*\*(?:Buffer|Launch week):\*\* W(\d+)", text)
    if not (title and dates and buffer):
        raise ValueError(f"{path.name}: missing title, **Dates:** or **Buffer:** line")

    number = int(title.group(1))
    phase = Phase(
        number=number,
        name=title.group(2).strip(),
        path=path,
        start=date.fromisoformat(dates.group(1)),
        first_week=int(dates.group(2)),
        last_week=int(dates.group(3)),
        buffer_week=int(buffer.group(1)),
    )
    for heading, body in split_sections(text).items():
        if heading.startswith("Theory track"):
            phase.tasks += parse_track(number, "theory", body)
        elif heading.startswith("Project track"):
            phase.tasks += parse_track(number, "project", body)
        elif heading.startswith("Done when"):
            items = re.findall(r"^- \[[ xX]\] (.+)$", body, re.M)
            seen: dict[str, int] = {}
            phase.done_when = [Task(task_key(number, "done", item, seen), number, "done", 0, item, "")
                               for item in items]
    return phase


def load_phases() -> list[Phase]:
    return [load_phase(p) for p in sorted(PHASES_DIR.glob("*.md"))]


# ---------------------------------------------------------------------------
# Saving progress (progress.json)
# ---------------------------------------------------------------------------

def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"done": {}, "logs": {}}


def save_state(state: dict) -> None:
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    tmp.replace(STATE_FILE)  # replace in one step so a crash never leaves half a file


def on_toggle(task: Task, widget_key: str) -> None:
    state = load_state()
    if st.session_state[widget_key]:
        # Keep the title too, so a tick whose task was later reworded can still be shown.
        state["done"][task.id] = {"date": date.today().isoformat(), "title": task.title}
    else:
        state["done"].pop(task.id, None)
    save_state(state)


def task_checkbox(task: Task, state: dict, page: str, show_details: bool = True) -> None:
    key = f"{page}:{task.id}"
    tick = state["done"].get(task.id)
    label = task.title + (f"  ✅ *{tick['date']}*" if tick else "")
    st.checkbox(label, value=bool(tick), key=key, on_change=on_toggle, args=(task, key))
    if show_details and task.details:
        st.caption(task.details)


# ---------------------------------------------------------------------------
# Calendar helpers
# ---------------------------------------------------------------------------

def week_start(phases: list[Phase], global_week: int) -> date:
    return phases[0].start + timedelta(weeks=global_week - 1)


def global_week_on(phases: list[Phase], day: date) -> int:
    return (day - phases[0].start).days // 7 + 1


def locate(phases: list[Phase], global_week: int) -> tuple[Phase, int | None]:
    """Return (phase, week inside phase), or (phase, None) for its buffer week."""
    for p in phases:
        if p.first_week <= global_week <= p.last_week:
            return p, global_week - p.first_week + 1
        if global_week == p.buffer_week:
            return p, None
    return (phases[0], 1) if global_week < 1 else (phases[-1], None)


def week_label(phases: list[Phase], gw: int) -> str:
    phase, week = locate(phases, gw)
    where = f"Phase {phase.number} · week {week}" if week else f"Phase {phase.number} · buffer"
    return f"W{gw} · {week_start(phases, gw)} · {where}"


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

def page_dashboard(phases: list[Phase], state: dict, today: date) -> None:
    st.title("📊 Dashboard")
    gw = global_week_on(phases, today)
    last = phases[-1].buffer_week

    if gw < 1:
        st.info(f"The path starts on **{phases[0].start}** (in {(phases[0].start - today).days} days).")
    elif gw > last:
        st.success("🎉 The planned path is complete!")

    gw_now = min(max(gw, 1), last)
    phase, week = locate(phases, gw_now)

    all_tasks = [t for p in phases for t in p.all_items]  # weekly tasks + "Done when" items
    done = [t for t in all_tasks if t.id in state["done"]]
    scheduled = [t for p in phases for t in p.tasks if p.global_week(t.week) < gw_now]
    overdue = [t for t in scheduled if t.id not in state["done"]]
    hours = sum(log.get("theory_hours", 0) + log.get("project_hours", 0) for log in state["logs"].values())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Current week", f"W{gw_now}", f"Phase {phase.number}" + (f" · wk {week}" if week else " · buffer"),
              delta_color="off")
    c2.metric("Tasks done", f"{len(done)} / {len(all_tasks)}")
    c3.metric("Overdue tasks", len(overdue), "on track" if not overdue else "catch up", delta_color="off")
    c4.metric("Hours logged", f"{hours:g}")
    st.progress(len(done) / len(all_tasks) if all_tasks else 0.0, text="Overall progress")

    st.subheader("Phases")
    rows = []
    for p in phases:
        items = p.all_items
        n_done = sum(t.id in state["done"] for t in items)
        rows.append({
            "Phase": f"{p.number} — {p.name}",
            "Weeks": f"W{p.first_week}–W{p.last_week}",
            "Starts": p.start,
            "Done": f"{n_done} / {len(items)}",
            "Progress": n_done / len(items) if items else 0.0,
        })
    st.dataframe(
        pd.DataFrame(rows), hide_index=True, width="stretch",
        column_config={"Progress": st.column_config.ProgressColumn(min_value=0.0, max_value=1.0, format="percent")},
    )

    st.subheader("Hours per week")
    logs = state["logs"]
    if logs:
        df = pd.DataFrame(
            [{"Week": f"W{int(w):02d}", "Theory": v.get("theory_hours", 0), "Project": v.get("project_hours", 0)}
             for w, v in sorted(logs.items(), key=lambda kv: int(kv[0]))]
        ).set_index("Week")
        st.bar_chart(df[["Theory", "Project"]], color=[THEORY_COLOR, PROJECT_COLOR], stack=True,
                     x_label="Week", y_label="Hours")
    else:
        st.caption("No hours yet. Save a weekly log on the **This week** page.")

    if overdue:
        st.subheader(f"Overdue ({len(overdue)})")
        for t in overdue[:15]:
            task_checkbox(t, state, "overdue", show_details=False)
        if len(overdue) > 15:
            st.caption(f"…and {len(overdue) - 15} more on the Phases page.")

    unmatched_ticks(phases, state)


def unmatched_ticks(phases: list[Phase], state: dict) -> None:
    """Ticks whose task text was edited in the Markdown: reassign or remove them."""
    by_id = {t.id: t for p in phases for t in p.all_items}
    orphans = {k: v for k, v in state["done"].items() if k not in by_id}
    if not orphans:
        return
    st.subheader(f"⚠️ Ticks that no longer match a task ({len(orphans)})")
    st.caption("The task text was probably edited in the phase file. Move each tick to the right task, or remove it.")
    for old_id, tick in orphans.items():
        phase_no = int(old_id.split("/")[0][1:])
        phase = next((p for p in phases if p.number == phase_no), None)
        candidates = [t for t in phase.all_items if t.id not in state["done"]] if phase else []
        st.markdown(f"**Was:** {tick['title']}  ·  ticked {tick['date']}  ·  Phase {phase_no}")
        c1, c2, c3 = st.columns([6, 1, 1])
        choice = c1.selectbox("Move to", range(len(candidates)), key=f"orphan-pick:{old_id}",
                              format_func=lambda i: f"[{candidates[i].track}] {candidates[i].title}",
                              label_visibility="collapsed")
        if c2.button("Move", key=f"orphan-move:{old_id}", disabled=not candidates):
            fresh = load_state()
            target = candidates[choice]
            fresh["done"][target.id] = {"date": tick["date"], "title": target.title}
            fresh["done"].pop(old_id, None)
            save_state(fresh)
            st.rerun()
        if c3.button("Remove", key=f"orphan-remove:{old_id}"):
            fresh = load_state()
            fresh["done"].pop(old_id, None)
            save_state(fresh)
            st.rerun()


def page_this_week(phases: list[Phase], state: dict, today: date) -> None:
    st.title("🗓️ This week")
    last = phases[-1].buffer_week
    current = min(max(global_week_on(phases, today), 1), last)
    gw = st.selectbox("Week", range(1, last + 1), index=current - 1,
                      format_func=lambda w: week_label(phases, w) + ("  ← now" if w == current else ""))
    phase, week = locate(phases, gw)
    st.markdown(f"**Phase {phase.number} — {phase.name}** · week of {week_start(phases, gw)}")

    if week is None:
        st.info("**Buffer week.** Catch up, tick the *Done when* list, write the phase retro, or rest.")
        left = [t for t in phase.all_items if t.id not in state["done"]]
        st.subheader(f"Still open in Phase {phase.number} ({len(left)})")
        for t in left:
            task_checkbox(t, state, "buffer", show_details=False)
    else:
        col_t, col_p = st.columns(2)
        with col_t:
            st.subheader("📖 Theory")
            for t in phase.tasks_for(week, "theory"):
                task_checkbox(t, state, "week", show_details=True)
        with col_p:
            st.subheader("🛠️ Project")
            for t in phase.tasks_for(week, "project"):
                task_checkbox(t, state, "week", show_details=True)

    st.divider()
    weekly_log_form(state, gw)


def weekly_log_form(state: dict, gw: int) -> None:
    st.subheader(f"✍️ Weekly log — W{gw}")
    log = state["logs"].get(str(gw), {})
    with st.form(f"log-{gw}"):
        c1, c2 = st.columns(2)
        theory_hours = c1.number_input("Theory hours", 0.0, 40.0, float(log.get("theory_hours", 0)), 0.5)
        project_hours = c2.number_input("Project hours", 0.0, 40.0, float(log.get("project_hours", 0)), 0.5)
        learned = st.text_area("What I learned (in my own words)", log.get("learned", ""))
        recall = st.text_area("Recall questions (answer them next Sunday)", log.get("recall", ""))
        broke = st.text_area("What broke and how I fixed it", log.get("broke", ""))
        confused = st.text_area("Still confused about", log.get("confused", ""))
        next_step = st.text_input("Next step", log.get("next_step", ""))
        if st.form_submit_button("Save log", type="primary"):
            fresh = load_state()
            fresh["logs"][str(gw)] = {
                "theory_hours": theory_hours, "project_hours": project_hours, "learned": learned,
                "recall": recall, "broke": broke, "confused": confused, "next_step": next_step,
                "saved": date.today().isoformat(),
            }
            save_state(fresh)
            st.success("Saved.")


def page_phases(phases: list[Phase], state: dict, today: date) -> None:
    st.title("🧭 Phases")
    current_phase, current_week = locate(phases, global_week_on(phases, today))
    i = st.selectbox("Phase", range(len(phases)), index=phases.index(current_phase),
                     format_func=lambda i: f"Phase {phases[i].number} — {phases[i].name}")
    phase = phases[i]
    items = phase.all_items
    n_done = sum(t.id in state["done"] for t in items)
    st.progress(n_done / len(items) if items else 0.0, text=f"{n_done} / {len(items)} done")
    st.caption(f"Plan file: `{phase.path.relative_to(HERE.parent.parent)}` — edit it and refresh to update this page.")

    for week in range(1, phase.weeks + 1):
        week_tasks = [t for t in phase.tasks if t.week == week]
        w_done = sum(t.id in state["done"] for t in week_tasks)
        gw = phase.global_week(week)
        is_now = phase is current_phase and week == current_week
        with st.expander(f"Week {week} · W{gw} · {week_start(phases, gw)} — {w_done}/{len(week_tasks)}"
                         + ("  ← now" if is_now else ""), expanded=is_now):
            for track, icon in (("theory", "📖"), ("project", "🛠️")):
                st.markdown(f"**{icon} {track.title()}**")
                for t in phase.tasks_for(week, track):
                    task_checkbox(t, state, "phase", show_details=True)

    st.subheader("✅ Done when")
    for t in phase.done_when:
        task_checkbox(t, state, "phase", show_details=False)


def page_logs(phases: list[Phase], state: dict, today: date) -> None:
    st.title("📚 Weekly logs")
    logs = sorted(state["logs"].items(), key=lambda kv: int(kv[0]), reverse=True)
    if not logs:
        st.caption("No logs yet. Save one on the **This week** page.")
        return
    for w, log in logs:
        gw = int(w)
        total = log.get("theory_hours", 0) + log.get("project_hours", 0)
        with st.expander(f"{week_label(phases, gw)} — {total:g} h"):
            for field_name, label in (("learned", "Learned"), ("recall", "Recall questions"),
                                      ("broke", "What broke"), ("confused", "Still confused"),
                                      ("next_step", "Next step")):
                if log.get(field_name):
                    st.markdown(f"**{label}**")
                    st.markdown(log[field_name])


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

def main() -> None:
    st.set_page_config(page_title="Learning tracker", page_icon="📚", layout="wide")
    try:
        phases = load_phases()
    except ValueError as err:
        st.error(f"Could not read the plan: {err}")
        st.stop()
    state = load_state()

    pages = {"Dashboard": page_dashboard, "This week": page_this_week,
             "Phases": page_phases, "Weekly logs": page_logs}
    choice = st.sidebar.radio("Go to", list(pages))
    with st.sidebar.expander("Settings"):
        today = st.date_input("Pretend today is", date.today(),
                              help="Preview another week of the plan. Ticks still save with the real date.")
    st.sidebar.caption(f"Progress file: `{STATE_FILE.name}`\n\nCommit it to keep your history.")

    pages[choice](phases, state, today)


if __name__ == "__main__":
    main()
