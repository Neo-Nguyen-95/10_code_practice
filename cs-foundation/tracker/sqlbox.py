"""Run learner SQL safely and check it against the expected result.

Every run builds a brand-new in-memory SQLite database from the lesson's setup
SQL, so a query (even DELETE or DROP) can never change anything that lasts.
Queries are stopped after a time limit, and attaching other database files
is blocked.
"""

from __future__ import annotations

import sqlite3
import time
from dataclasses import dataclass, field

MAX_ROWS = 500
TIME_LIMIT_S = 2.0


@dataclass
class Result:
    columns: list[str] = field(default_factory=list)
    rows: list[tuple] = field(default_factory=list)
    error: str | None = None
    truncated: bool = False


def _authorizer(action: int, *_args) -> int:
    if action in (sqlite3.SQLITE_ATTACH, sqlite3.SQLITE_DETACH):
        return sqlite3.SQLITE_DENY
    return sqlite3.SQLITE_OK


def _is_blank(query: str) -> bool:
    code = [line for line in query.splitlines() if line.strip() and not line.strip().startswith("--")]
    return not code


def run(setup: str, query: str, time_limit: float = TIME_LIMIT_S) -> Result:
    if _is_blank(query):
        return Result(error="Write a query first.")
    con = sqlite3.connect(":memory:")
    try:
        con.executescript(setup)
        con.set_authorizer(_authorizer)
        deadline = time.monotonic() + time_limit
        con.set_progress_handler(lambda: int(time.monotonic() > deadline), 1000)
        cursor = con.execute(query.strip())
        columns = [d[0] for d in cursor.description or []]
        rows = cursor.fetchmany(MAX_ROWS + 1) if columns else []
        return Result(columns, rows[:MAX_ROWS], truncated=len(rows) > MAX_ROWS)
    except sqlite3.Error as err:
        message = str(err)
        if "interrupted" in message:
            message = (f"Query stopped after {time_limit:g} s. Is a JOIN missing its ON condition "
                       "(that multiplies every row by every row)?")
        elif "one statement at a time" in message:
            message = "Run one statement at a time. Remove everything after the first `;`."
        elif "not authorized" in message:
            message = "ATTACH/DETACH is disabled in lessons."
        return Result(error=message)
    finally:
        con.close()


def table_previews(setup: str, limit: int = 50) -> dict[str, Result]:
    """Every table created by the setup SQL, with its rows (for the schema viewer)."""
    con = sqlite3.connect(":memory:")
    try:
        con.executescript(setup)
        names = [r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY rowid")]
        previews = {}
        for name in names:
            cursor = con.execute(f'SELECT * FROM "{name}" LIMIT {limit}')
            previews[name] = Result([d[0] for d in cursor.description], cursor.fetchall())
        return previews
    finally:
        con.close()


def _normalize(rows: list[tuple]) -> list[tuple]:
    """Round floats and treat 3.0 as 3, so equal values compare equal."""
    def fix(v):
        if isinstance(v, float):
            v = round(v, 6)
            return int(v) if v.is_integer() else v
        return v
    return [tuple(fix(v) for v in row) for row in rows]


def compare(expected: Result, got: Result, ordered: bool) -> tuple[bool, str]:
    """Return (correct?, feedback message). Column names are ignored on purpose."""
    if got.error:
        return False, got.error
    if not got.columns:
        return False, "That statement returned no result. Exercises need a SELECT query."
    if len(got.columns) != len(expected.columns):
        return False, (f"Expected {len(expected.columns)} columns ({', '.join(expected.columns)}), "
                       f"but your query returned {len(got.columns)} ({', '.join(got.columns)}).")
    e, g = _normalize(expected.rows), _normalize(got.rows)
    if len(e) != len(g):
        return False, f"Expected {len(e)} rows, but your query returned {len(g)}."
    same_rows = sorted(e, key=repr) == sorted(g, key=repr)
    if ordered:
        if e == g:
            return True, "Correct!"
        if same_rows:
            return False, "Right rows, wrong order. Check your ORDER BY."
        first = next(i for i, (a, b) in enumerate(zip(e, g)) if a != b)
        return False, f"Row {first + 1} differs: expected {e[first]}, got {g[first]}."
    if same_rows:
        return True, "Correct!"
    missing = len([r for r in g if r not in e])
    return False, f"{missing} of your rows don't match the expected output."
