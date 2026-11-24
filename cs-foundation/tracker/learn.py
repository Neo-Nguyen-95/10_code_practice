"""The Learn page: interactive lessons from ../lessons/*.md."""

from __future__ import annotations

import re

import pandas as pd
import streamlit as st

import lessons as lessons_mod
import sqlbox
import store
from lessons import Exercise, Lesson, Quiz, Sandbox
from views import Ctx, flash, get_ctx

# Monospace font in the SQL editors (each editor sits in a container keyed "sqled-...").
EDITOR_CSS = """<style>
[class*="st-key-sqled-"] textarea {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 0.88rem; line-height: 1.5;
}
</style>"""
DEFAULT_QUERY = "-- Write your query here\n"


def _md(text: str) -> str:
    """Relative links point at files in the repo and can't open in the app: show them as bold text."""
    return re.sub(r"\[([^\]]+)\]\((?!https?://|#)[^)]*\)", r"**\1**", text)


def _table(result: sqlbox.Result) -> None:
    columns, seen = [], {}
    for name in result.columns:  # SELECT * over a JOIN can repeat names like "id"
        seen[name] = seen.get(name, 0) + 1
        columns.append(name if seen[name] == 1 else f"{name} ({seen[name]})")
    st.dataframe(pd.DataFrame(result.rows, columns=columns), hide_index=True, width="stretch")
    st.caption(f"{len(result.rows)} row{'s' * (len(result.rows) != 1)}"
               + (f" (showing the first {sqlbox.MAX_ROWS})" if result.truncated else ""))


def _lesson_entry(ctx: Ctx, slug: str) -> dict:
    return ctx.state["lessons"].get(slug, {})


def _after_record(lesson: Lesson, state: dict) -> None:
    """Celebrate (once) when every quiz and exercise in the lesson is done."""
    graded = {b.id for b in lesson.graded}
    entry = state["lessons"].get(lesson.slug, {})
    if graded and graded <= store.lesson_done_ids(state, lesson.slug) and not entry.get("completed"):
        store.update(lambda s: store.mark_lesson_completed(s, lesson.slug))
        flash("Lesson complete — well done!", "🎓", balloons=True)


def _open(slug: str) -> None:
    st.session_state["lesson"] = slug


def _close() -> None:
    st.session_state.pop("lesson", None)
    st.query_params.clear()


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------

def learn_page() -> None:
    ctx = get_ctx()
    all_lessons, errors = lessons_mod.load_lessons()
    for error in errors:
        st.error(error, icon=":material/error:")
    by_slug = {lesson.slug: lesson for lesson in all_lessons}
    slug = st.session_state.get("lesson") or st.query_params.get("lesson")
    if slug in by_slug:
        st.session_state["lesson"] = slug
        st.query_params["lesson"] = slug   # so a browser refresh keeps the lesson open
        lesson_view(ctx, by_slug[slug])
    else:
        lesson_list(ctx, all_lessons)


def lesson_list(ctx: Ctx, all_lessons: list[Lesson]) -> None:
    st.title("Learn", anchor=False)
    st.caption("Interactive lessons: read, answer quick checks, and write real queries that are checked automatically.")
    if not all_lessons:
        st.info("No lessons yet. Add a Markdown file to `cs-foundation/lessons/` (see the README there).",
                icon=":material/school:")
    current_phase, current_week = ctx.plan.locate(ctx.week)
    columns = st.columns(2, gap="medium")
    for i, lesson in enumerate(all_lessons):
        graded = [b.id for b in lesson.graded]
        done = len(store.lesson_done_ids(ctx.state, lesson.slug) & set(graded))
        completed = _lesson_entry(ctx, lesson.slug).get("completed")
        with columns[i % 2], st.container(border=True):
            st.markdown(f"#### {lesson.title}")
            with st.container(horizontal=True):
                if lesson.where:
                    st.badge(lesson.where, icon=":material/schedule:", color="gray")
                if lesson.phase == current_phase.number and lesson.week == current_week:
                    st.badge("This week", icon=":material/today:", color="blue")
                if completed:
                    st.badge(f"Completed {completed}", icon=":material/check:", color="green")
            if lesson.summary:
                st.caption(lesson.summary)
            if graded:
                st.progress(done / len(graded), text=f"{done}/{len(graded)} checks done")
            st.button("Continue" if done and not completed else ("Review" if completed else "Start"),
                      key=f"open-{lesson.slug}", on_click=_open, args=(lesson.slug,),
                      type="primary", icon=":material/arrow_forward:")

    readme = lessons_mod.LESSONS_DIR / "README.md"
    if readme.exists():
        with st.expander("How to write a lesson", icon=":material/edit_note:"):
            st.markdown(_md(readme.read_text(encoding="utf-8")))


def lesson_view(ctx: Ctx, lesson: Lesson) -> None:
    st.html(EDITOR_CSS)
    st.button("All lessons", icon=":material/arrow_back:", on_click=_close, type="tertiary", key="lesson-back")
    st.title(lesson.title, anchor=False)
    if lesson.where:
        st.caption(lesson.where)
    for problem in lessons_mod.check_lesson(lesson):
        st.error(problem, icon=":material/error:")

    graded = [b.id for b in lesson.graded]
    done = store.lesson_done_ids(ctx.state, lesson.slug) & set(graded)
    if graded:
        st.progress(len(done) / len(graded), text=f"{len(done)}/{len(graded)} quick checks and exercises done")

    if lesson.setup:
        with st.expander("Tables in this lesson", icon=":material/table_chart:"):
            previews = sqlbox.table_previews(lesson.setup)
            tabs = st.tabs([f"{name} ({len(r.rows)})" for name, r in previews.items()])
            for tab, result in zip(tabs, previews.values()):
                with tab:
                    _table(result)
            if st.toggle("Show the SQL that builds these tables", key=f"setup-sql:{lesson.slug}"):
                st.code(lesson.setup.strip(), language="sql")

    for block in lesson.blocks:
        if isinstance(block, str):
            st.markdown(_md(block))
        elif isinstance(block, Quiz):
            quiz_block(ctx, lesson, block)
        elif isinstance(block, Exercise):
            exercise_block(ctx, lesson, block)
        elif isinstance(block, Sandbox):
            sandbox_block(ctx, lesson, block)

    if _lesson_entry(ctx, lesson.slug).get("completed"):
        st.success("You finished this lesson. Come back in a week and redo the exercises from a blank editor.",
                   icon=":material/school:")


# ---------------------------------------------------------------------------
# Blocks
# ---------------------------------------------------------------------------

def quiz_block(ctx: Ctx, lesson: Lesson, quiz: Quiz) -> None:
    key = f"quiz:{lesson.slug}:{quiz.id}"
    rec = _lesson_entry(ctx, lesson.slug).get("quiz", {}).get(quiz.id, {})
    with st.container(border=True):
        st.markdown(":material/quiz: **Quick check**"
                    + ("  :green-badge[:material/check: answered]" if rec.get("correct") else ""))
        st.markdown(_md(quiz.question))
        if quiz.multi:
            st.caption("Select all that apply.")
            chosen = {i for i, option in enumerate(quiz.options) if st.checkbox(option, key=f"{key}:opt{i}")}
        else:
            pick = st.radio("Answer", range(len(quiz.options)), index=None, key=f"{key}:pick",
                            format_func=lambda i: quiz.options[i], label_visibility="collapsed")
            chosen = set() if pick is None else {pick}

        if st.button("Check", key=f"{key}:check", disabled=not chosen, icon=":material/done:"):
            correct = chosen == quiz.correct
            state = store.update(lambda s: store.record_quiz(s, lesson.slug, quiz.id, correct))
            st.session_state[f"{key}:result"] = correct
            _after_record(lesson, state)
            st.rerun()

        result = st.session_state.get(f"{key}:result")
        attempts = rec.get("attempts", 0)
        if result is True:
            st.success("Correct!", icon=":material/check_circle:")
        elif result is False:
            st.error(f"Not quite. Have another look. (attempt {attempts})", icon=":material/cancel:")
        if quiz.explanation:
            if result is True or (result is None and rec.get("correct")):
                st.info(_md(quiz.explanation), icon=":material/lightbulb:")
            elif result is False and st.toggle("Show the explanation", key=f"{key}:explain"):
                st.info(_md(quiz.explanation), icon=":material/lightbulb:")


def _bump(key: str) -> None:
    st.session_state[key] = st.session_state.get(key, 0) + 1


def _toggle_solution(slug: str, exercise_id: str, key: str) -> None:
    showing = not st.session_state.get(key, False)
    st.session_state[key] = showing
    if showing:
        store.update(lambda s: store.record_solution_viewed(s, slug, exercise_id))


def _editor(key: str, initial: str) -> str:
    if key not in st.session_state:
        st.session_state[key] = initial
    with st.container(key="sqled-" + re.sub(r"[^a-zA-Z0-9-]", "-", key)):
        return st.text_area("SQL", key=key, height=170, label_visibility="collapsed")


def exercise_block(ctx: Ctx, lesson: Lesson, ex: Exercise) -> None:
    key = f"sql:{lesson.slug}:{ex.id}"
    rec = _lesson_entry(ctx, lesson.slug).get("sql", {}).get(ex.id, {})
    expected = sqlbox.run(lesson.setup, ex.solution)
    with st.container(border=True):
        st.markdown(f"#### :material/terminal: {ex.title}"
                    + ("  :green-badge[:material/check: solved]" if rec.get("solved") else ""))
        st.markdown(_md(ex.prompt))
        st.caption(("Row order matters here. " if ex.ordered else "Row order doesn't matter here. ")
                   + "Column names don't matter; column order and values do.")
        with st.expander("Expected output", icon=":material/visibility:"):
            _table(expected)

        query = _editor(f"{key}:q", rec.get("last_query") or DEFAULT_QUERY)
        hints_key, solution_key = f"{key}:hints", f"{key}:solution"
        hints_shown = st.session_state.get(hints_key, 0)
        attempted = rec.get("attempts", 0) > 0
        with st.container(horizontal=True):
            run = st.button("Run", icon=":material/play_arrow:", type="primary", key=f"{key}:run")
            if ex.hints:
                st.button(f"Hint {min(hints_shown + 1, len(ex.hints))}/{len(ex.hints)}", key=f"{key}:hint",
                          icon=":material/lightbulb:", disabled=hints_shown >= len(ex.hints),
                          on_click=_bump, args=(hints_key,))
            showing = st.session_state.get(solution_key, False)
            st.button("Hide solution" if showing else "Show solution", key=f"{key}:sol", icon=":material/key:",
                      disabled=not attempted, help=None if attempted else "Try at least once first.",
                      on_click=_toggle_solution, args=(lesson.slug, ex.id, solution_key), type="tertiary")

        for i, hint in enumerate(ex.hints[:hints_shown], start=1):
            st.info(f"**Hint {i}:** {_md(hint)}", icon=":material/lightbulb:")

        if run:
            got = sqlbox.run(lesson.setup, query)
            ok, message = sqlbox.compare(expected, got, ex.ordered)
            state = store.update(lambda s: store.record_sql(s, lesson.slug, ex.id, query, ok))
            st.session_state[f"{key}:out"] = (got, ok, message)
            if ok:
                flash("Exercise solved!", "✅")
            _after_record(lesson, state)
            st.rerun()

        out = st.session_state.get(f"{key}:out")
        if out:
            got, ok, message = out
            if ok:
                st.success(message, icon=":material/check_circle:")
            else:
                st.error(message, icon=":material/cancel:")
            if got.columns:
                _table(got)

        if st.session_state.get(solution_key):
            st.code(ex.solution, language="sql")
            st.caption("Compare it with yours, then hide it and re-type the idea from memory.")


def sandbox_block(ctx: Ctx, lesson: Lesson, box: Sandbox) -> None:
    key = f"sbx:{lesson.slug}:{box.id}"
    saved = _lesson_entry(ctx, lesson.slug).get("sandbox", {}).get(box.id)

    def reset() -> None:
        st.session_state[f"{key}:q"] = box.starter
        st.session_state.pop(f"{key}:out", None)

    with st.container(border=True):
        st.markdown(f"#### :material/science: {box.title}")
        query = _editor(f"{key}:q", saved or box.starter)
        with st.container(horizontal=True):
            run = st.button("Run", icon=":material/play_arrow:", type="primary", key=f"{key}:run")
            st.button("Reset", icon=":material/restart_alt:", key=f"{key}:reset", on_click=reset, type="tertiary")
        if run:
            store.update(lambda s: store.save_sandbox(s, lesson.slug, box.id, query))
            st.session_state[f"{key}:out"] = sqlbox.run(lesson.setup, query)
        result = st.session_state.get(f"{key}:out")
        if result:
            if result.error:
                st.error(result.error, icon=":material/cancel:")
            elif result.columns:
                _table(result)
            else:
                st.caption("Statement ran. It returned no rows. (Changes are thrown away after each run.)")
