"""Read the learning plan from ../phases/*.md into Python objects.

The Markdown files are the source of truth for *what* to learn. Nothing here
writes to them.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

PHASES_DIR = Path(__file__).resolve().parent.parent / "phases"


@dataclass
class Task:
    id: str          # stable id built from the text, e.g. "p1/theory/memory-stack-heap"
    phase: int
    track: str       # "theory", "project" or "done" (a "Done when" item)
    week: int        # week number inside the phase (0 for "Done when" items)
    title: str       # first column of the table row
    details: str     # the other columns, as Markdown


@dataclass
class Phase:
    number: int
    name: str
    path: Path
    start: date          # first day of the phase
    first_week: int      # global week number (W1 = first week of the path)
    last_week: int
    buffer_week: int     # the buffer (or launch) week after the phase
    tasks: list[Task] = field(default_factory=list)
    done_when: list[Task] = field(default_factory=list)

    @property
    def weeks(self) -> int:
        return self.last_week - self.first_week + 1

    @property
    def end(self) -> date:
        """Last day of the phase's study weeks (buffer week not included)."""
        return self.start + timedelta(weeks=self.weeks, days=-1)

    @property
    def label(self) -> str:
        return f"Phase {self.number} — {self.name}"

    @property
    def all_items(self) -> list[Task]:
        return self.tasks + self.done_when

    def global_week(self, week: int) -> int:
        return self.first_week + week - 1

    def tasks_for(self, week: int, track: str | None = None) -> list[Task]:
        return [t for t in self.tasks if t.week == week and (track is None or t.track == track)]


@dataclass
class Plan:
    phases: list[Phase]

    @property
    def start(self) -> date:
        return self.phases[0].start

    @property
    def last_week(self) -> int:
        return self.phases[-1].buffer_week

    @property
    def all_items(self) -> list[Task]:
        return [t for p in self.phases for t in p.all_items]

    def phase(self, number: int) -> Phase | None:
        return next((p for p in self.phases if p.number == number), None)

    def week_start(self, gw: int) -> date:
        return self.start + timedelta(weeks=gw - 1)

    def week_on(self, day: date) -> int:
        """Global week number for a date (can be < 1 before the start)."""
        return (day - self.start).days // 7 + 1

    def clamp(self, gw: int) -> int:
        return min(max(gw, 1), self.last_week)

    def locate(self, gw: int) -> tuple[Phase, int | None]:
        """Return (phase, week inside phase), or (phase, None) for its buffer week."""
        for p in self.phases:
            if p.first_week <= gw <= p.last_week:
                return p, gw - p.first_week + 1
            if gw == p.buffer_week:
                return p, None
        return (self.phases[0], 1) if gw < 1 else (self.phases[-1], None)

    def tasks_in_week(self, gw: int) -> list[Task]:
        phase, week = self.locate(gw)
        return phase.tasks_for(week) if week else []

    def week_label(self, gw: int) -> str:
        phase, week = self.locate(gw)
        where = f"Phase {phase.number} · week {week}/{phase.weeks}" if week else f"Phase {phase.number} · buffer"
        return f"W{gw} · {self.week_start(gw):%d %b %Y} · {where}"


# ---------------------------------------------------------------------------
# Markdown parsing
# ---------------------------------------------------------------------------

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


def load_plan(phases_dir: Path = PHASES_DIR) -> Plan:
    return Plan([load_phase(p) for p in sorted(phases_dir.glob("*.md"))])
