"""Read interactive lessons from ../lessons/*.md.

A lesson is Markdown with front matter plus special fenced blocks
(quiz, sql-setup, sql-exercise, sql-sandbox). See ../lessons/README.md for the format.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import sqlbox

LESSONS_DIR = Path(__file__).resolve().parent.parent / "lessons"
SPECIAL = ("quiz", "sql-setup", "sql-exercise", "sql-sandbox")
FENCE = re.compile(r"^```(" + "|".join(SPECIAL) + r")[ \t]*\n(.*?)^```[ \t]*$", re.M | re.S)


class LessonError(ValueError):
    pass


@dataclass
class Quiz:
    id: str
    question: str
    options: list[str]
    correct: set[int]
    explanation: str

    @property
    def multi(self) -> bool:
        return len(self.correct) > 1


@dataclass
class Exercise:
    id: str
    title: str
    prompt: str
    hints: list[str]
    solution: str
    ordered: bool


@dataclass
class Sandbox:
    id: str
    title: str
    starter: str


Block = str | Quiz | Exercise | Sandbox   # str = plain Markdown


@dataclass
class Lesson:
    slug: str
    path: Path
    title: str
    phase: int | None
    week: int | None
    minutes: int | None
    summary: str
    setup: str = ""
    blocks: list[Block] = field(default_factory=list)

    @property
    def graded(self) -> list[Quiz | Exercise]:
        return [b for b in self.blocks if isinstance(b, (Quiz, Exercise))]

    @property
    def where(self) -> str:
        parts = []
        if self.phase is not None:
            parts.append(f"Phase {self.phase}" + (f" · week {self.week}" if self.week else ""))
        if self.minutes:
            parts.append(f"~{self.minutes} min")
        return " · ".join(parts)


def slugify(text: str) -> str:
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60] or "item"


def _unique(base: str, seen: dict[str, int]) -> str:
    seen[base] = seen.get(base, 0) + 1
    return base if seen[base] == 1 else f"{base}-{seen[base]}"


def parse_front_matter(text: str, name: str) -> tuple[dict[str, str], str]:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        raise LessonError(f"{name}: missing front matter (--- title: ... ---) at the top")
    meta = {}
    for line in match.group(1).splitlines():
        key, sep, value = line.partition(":")
        if sep:
            key = key.strip()
            # "phase: 2   # comment" is allowed for the number fields
            meta[key] = value.split("#")[0].strip() if key in ("phase", "week", "minutes") else value.strip()
    if not meta.get("title"):
        raise LessonError(f"{name}: front matter needs a title")
    return meta, text[match.end():]


def parse_quiz(body: str, seen: dict[str, int], where: str) -> Quiz:
    question, options, correct, explanation = [], [], set(), []
    for line in body.splitlines():
        option = re.match(r"^- \[( |x|X)\] (.+)$", line)
        if option:
            if option.group(1) != " ":
                correct.add(len(options))
            options.append(option.group(2).strip())
        elif line.startswith(">"):
            explanation.append(line[1:].strip())
        elif not options:
            question.append(line)
    question_md = "\n".join(question).strip()
    if not question_md or len(options) < 2 or not correct:
        raise LessonError(f"{where}: a quiz needs a question, 2+ options and at least one `- [x]`")
    return Quiz(_unique("q-" + slugify(question_md), seen), question_md, options, correct, "\n".join(explanation))


def parse_exercise(body: str, seen: dict[str, int], where: str) -> Exercise:
    head, sep, solution = body.partition("\n---\n")
    if not sep or not solution.strip():
        raise LessonError(f"{where}: an sql-exercise needs a `---` line followed by the solution query")
    title, hints, ordered, prompt = "", [], False, []
    for line in head.splitlines():
        key = re.match(r"^(title|hint|order):\s*(.*)$", line)
        if not key:
            prompt.append(line)
        elif key.group(1) == "title":
            title = key.group(2).strip()
        elif key.group(1) == "hint":
            hints.append(key.group(2).strip())
        else:
            ordered = key.group(2).strip().lower() in ("true", "yes", "1")
    prompt_md = "\n".join(prompt).strip()
    title = title or prompt_md.split("\n")[0][:60]
    return Exercise(_unique("s-" + slugify(title), seen), title, prompt_md, hints, solution.strip(), ordered)


def parse_sandbox(body: str, seen: dict[str, int]) -> Sandbox:
    lines = body.splitlines()
    title = "Sandbox"
    if lines and lines[0].startswith("title:"):
        title = lines.pop(0).partition(":")[2].strip()
    return Sandbox(_unique("x-" + slugify(title), seen), title, "\n".join(lines).strip())


def load_lesson(path: Path) -> Lesson:
    meta, body = parse_front_matter(path.read_text(encoding="utf-8"), path.name)

    def as_int(key: str) -> int | None:
        value = meta.get(key, "")
        return int(value) if value.isdigit() else None

    lesson = Lesson(path.stem, path, meta["title"], as_int("phase"), as_int("week"), as_int("minutes"),
                    meta.get("summary", ""))
    seen: dict[str, int] = {}
    position = 0
    for n, match in enumerate(FENCE.finditer(body), start=1):
        before = body[position:match.start()].strip()
        if before:
            lesson.blocks.append(before)
        kind, content = match.group(1), match.group(2)
        where = f"{path.name}, block {n} ({kind})"
        if kind == "quiz":
            lesson.blocks.append(parse_quiz(content, seen, where))
        elif kind == "sql-exercise":
            lesson.blocks.append(parse_exercise(content, seen, where))
        elif kind == "sql-sandbox":
            lesson.blocks.append(parse_sandbox(content, seen))
        else:
            lesson.setup += content
        position = match.end()
    rest = body[position:].strip()
    if rest:
        lesson.blocks.append(rest)
    return lesson


def check_lesson(lesson: Lesson) -> list[str]:
    """Problems an author should fix: broken setup SQL or a failing solution."""
    if not lesson.setup and any(isinstance(b, (Exercise, Sandbox)) for b in lesson.blocks):
        return ["The lesson has SQL exercises but no sql-setup block."]
    problems = []
    for block in lesson.blocks:
        if isinstance(block, Exercise):
            result = sqlbox.run(lesson.setup, block.solution)
            if result.error:
                problems.append(f"Solution of “{block.title}” fails: {result.error}")
    return problems


def load_lessons(lessons_dir: Path = LESSONS_DIR) -> tuple[list[Lesson], list[str]]:
    """Return (lessons sorted by phase/week, error messages for files that failed)."""
    lessons, errors = [], []
    for path in sorted(lessons_dir.glob("*.md")):
        if path.name.lower() == "readme.md" or path.name.startswith("_"):
            continue
        try:
            lessons.append(load_lesson(path))
        except LessonError as err:
            errors.append(str(err))
    lessons.sort(key=lambda l: (l.phase if l.phase is not None else 99, l.week or 0, l.slug))
    return lessons, errors
