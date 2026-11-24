"""Save and load my progress (progress.json next to this file).

Every change follows the same pattern: load the latest file, change it, then
write it back. Writes go to a temporary file that is then swapped in, so a
crash can never leave a half-written progress file.

Shape of progress.json (version 2):

    done      {task_id: {"date": "2026-12-01", "title": "..."}}
    logs      {"12": {"learned": "...", "recall": "...", ...}}      # weekly journal, key = global week
    sessions  [{"id": "...", "date": "...", "week": 12, "track": "theory", "minutes": 60, "note": "..."}]
    reviews   {card_id: {"box": 2, "last": "2027-03-01"}}           # flashcard progress
    lessons   {lesson_slug: {"quiz": {quiz_id: {...}}, "sql": {exercise_id: {...}}, "completed": "..."}}
    settings  {"weekly_target_hours": 9}
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import uuid
from collections import defaultdict
from datetime import date
from pathlib import Path

STATE_FILE = Path(__file__).resolve().parent / "progress.json"

DEFAULT_STATE = {
    "version": 2,
    "done": {},
    "logs": {},
    "sessions": [],
    "reviews": {},
    "lessons": {},
    "settings": {"weekly_target_hours": 9},
}
JOURNAL_FIELDS = ("learned", "recall", "broke", "confused", "next_step")


def load(path: Path = STATE_FILE) -> dict:
    state = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    for key, value in DEFAULT_STATE.items():
        state.setdefault(key, copy.deepcopy(value))
    for key, value in DEFAULT_STATE["settings"].items():
        state["settings"].setdefault(key, value)
    _migrate_v1(state)
    return state


def save(state: dict, path: Path = STATE_FILE) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    tmp.replace(path)  # replace in one step so a crash never leaves half a file


def update(change, path: Path = STATE_FILE) -> dict:
    """Load the latest state, apply change(state), save, and return it."""
    state = load(path)
    change(state)
    save(state, path)
    return state


def _migrate_v1(state: dict) -> None:
    """Version 1 kept a bare date per tick and hours inside the weekly log."""
    for task_id, tick in list(state["done"].items()):
        if isinstance(tick, str):
            state["done"][task_id] = {"date": tick, "title": ""}
    for week, log in state["logs"].items():
        for track in ("theory", "project"):
            hours = log.pop(f"{track}_hours", 0)
            if hours:
                state["sessions"].append({
                    "id": uuid.uuid4().hex[:8], "date": log.get("saved", ""), "week": int(week),
                    "track": track, "minutes": round(hours * 60), "note": "from weekly log",
                })
    state["version"] = 2


# ---------------------------------------------------------------------------
# Changes (each takes the state dict and edits it in place)
# ---------------------------------------------------------------------------

def set_done(state: dict, task_id: str, title: str, done: bool) -> None:
    if done:
        # Keep the title too, so a tick whose task was later reworded can still be shown.
        state["done"][task_id] = {"date": date.today().isoformat(), "title": title}
    else:
        state["done"].pop(task_id, None)


def move_tick(state: dict, old_id: str, new_id: str, new_title: str) -> None:
    tick = state["done"].pop(old_id)
    state["done"][new_id] = {"date": tick["date"], "title": new_title}


def add_session(state: dict, day: date, week: int, track: str, minutes: int, note: str) -> None:
    state["sessions"].append({
        "id": uuid.uuid4().hex[:8], "date": day.isoformat(), "week": week,
        "track": track, "minutes": int(minutes), "note": note.strip(),
    })


def delete_session(state: dict, session_id: str) -> None:
    state["sessions"] = [s for s in state["sessions"] if s["id"] != session_id]


def save_log(state: dict, week: int, fields: dict[str, str]) -> None:
    state["logs"][str(week)] = {**{k: fields.get(k, "") for k in JOURNAL_FIELDS},
                                "saved": date.today().isoformat()}


def review_card(state: dict, card_id: str, remembered: bool) -> None:
    """Leitner boxes: remembered -> next box (shown less often); forgot -> box 0."""
    box = state["reviews"].get(card_id, {}).get("box", 0)
    state["reviews"][card_id] = {"box": min(box + 1, 5) if remembered else 0, "last": date.today().isoformat()}


def _lesson(state: dict, slug: str) -> dict:
    entry = state["lessons"].setdefault(slug, {})
    entry.setdefault("quiz", {})
    entry.setdefault("sql", {})
    return entry


def record_quiz(state: dict, slug: str, quiz_id: str, correct: bool) -> None:
    rec = _lesson(state, slug)["quiz"].setdefault(quiz_id, {"attempts": 0, "correct": False})
    rec["attempts"] += 1
    if correct and not rec["correct"]:
        rec["correct"], rec["date"] = True, date.today().isoformat()


def record_sql(state: dict, slug: str, exercise_id: str, query: str, solved: bool) -> None:
    rec = _lesson(state, slug)["sql"].setdefault(exercise_id, {"attempts": 0, "solved": False})
    rec["attempts"] += 1
    rec["last_query"] = query
    if solved and not rec["solved"]:
        rec["solved"], rec["date"] = True, date.today().isoformat()


def record_solution_viewed(state: dict, slug: str, exercise_id: str) -> None:
    rec = _lesson(state, slug)["sql"].setdefault(exercise_id, {"attempts": 0, "solved": False})
    rec["viewed_solution"] = True


def save_sandbox(state: dict, slug: str, sandbox_id: str, query: str) -> None:
    _lesson(state, slug).setdefault("sandbox", {})[sandbox_id] = query


def lesson_done_ids(state: dict, slug: str) -> set[str]:
    """Ids of the quizzes answered correctly and exercises solved in a lesson."""
    entry = state["lessons"].get(slug, {})
    return ({k for k, v in entry.get("quiz", {}).items() if v.get("correct")}
            | {k for k, v in entry.get("sql", {}).items() if v.get("solved")})


def mark_lesson_completed(state: dict, slug: str) -> None:
    _lesson(state, slug).setdefault("completed", date.today().isoformat())


# ---------------------------------------------------------------------------
# Read-only summaries
# ---------------------------------------------------------------------------

def hours_by_week(state: dict) -> dict[int, dict[str, float]]:
    """{global_week: {"theory": h, "project": h}}"""
    out: dict[int, dict[str, float]] = defaultdict(lambda: {"theory": 0.0, "project": 0.0})
    for s in state["sessions"]:
        out[int(s["week"])][s["track"]] += s["minutes"] / 60
    return dict(out)


def streak(state: dict, current_week: int) -> int:
    """Weeks in a row with at least one study session.

    The current week only counts once it has a session, so the streak does not
    "break" on a Monday morning.
    """
    weeks = set(hours_by_week(state))
    gw = current_week if current_week in weeks else current_week - 1
    count = 0
    while gw in weeks:
        count += 1
        gw -= 1
    return count


def recall_cards(state: dict) -> list[dict]:
    """Every recall question written in the weekly journal, one card each."""
    cards = []
    for week, log in state["logs"].items():
        for line in log.get("recall", "").splitlines():
            question = re.sub(r"^\s*(?:[-*•]|\d+[.)])\s*", "", line).strip()
            if len(question) > 3:
                card_id = f"{week}:{hashlib.sha1(question.encode()).hexdigest()[:10]}"
                cards.append({"id": card_id, "week": int(week), "question": question,
                              "notes": log.get("learned", "")})
    return cards
