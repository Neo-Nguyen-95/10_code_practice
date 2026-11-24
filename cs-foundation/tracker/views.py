"""Pages and shared widgets of the tracker."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import date, timedelta

import streamlit as st

import charts
import lessons as lessons_mod
import store
from plan import Phase, Plan, Task

TRACK_LABEL = {"theory": ":material/menu_book: Theory", "project": ":material/construction: Project"}


# ---------------------------------------------------------------------------
# Shared context
# ---------------------------------------------------------------------------

@dataclass
class Ctx:
    plan: Plan
    state: dict
    today: date
    pages: dict = field(default_factory=dict)

    @property
    def raw_week(self) -> int:
        return self.plan.week_on(self.today)

    @property
    def week(self) -> int:
        return self.plan.clamp(self.raw_week)

    @property
    def theme(self) -> str | None:
        return st.context.theme.type

    @property
    def target(self) -> float:
        return float(self.state["settings"]["weekly_target_hours"])

    def done(self, task: Task) -> bool:
        return task.id in self.state["done"]

    def count_done(self, tasks: list[Task]) -> int:
        return sum(self.done(t) for t in tasks)


def set_ctx(ctx: Ctx) -> None:
    st.session_state["_ctx"] = ctx


def get_ctx() -> Ctx:
    return st.session_state["_ctx"]


# ---------------------------------------------------------------------------
# Feedback (toasts survive the rerun that follows a callback)
# ---------------------------------------------------------------------------

def flash(message: str, icon: str | None = None, balloons: bool = False) -> None:
    st.session_state.setdefault("_flash", []).append((message, icon))
    if balloons:
        st.session_state["_balloons"] = True


def show_flashes() -> None:
    for message, icon in st.session_state.pop("_flash", []):
        st.toast(message, icon=icon)
    if st.session_state.pop("_balloons", False):
        st.balloons()


# ---------------------------------------------------------------------------
# Widgets
# ---------------------------------------------------------------------------

def _on_toggle(task: Task, key: str, siblings: list[str], scope: str) -> None:
    checked = st.session_state[key]
    state = store.update(lambda s: store.set_done(s, task.id, task.title, checked))
    if not checked:
        return
    n = sum(i in state["done"] for i in siblings)
    if siblings and n == len(siblings):
        flash(f"{scope.capitalize()} complete — great work!", "🎉", balloons=True)
    else:
        flash(f"Done · {n}/{len(siblings)} {scope}", "✅")


def task_row(ctx: Ctx, task: Task, page: str, details: bool = True, context: str = "") -> None:
    """A checkbox for one task, plus its details underneath."""
    phase = ctx.plan.phase(task.phase)
    if task.track == "done":
        siblings, scope = [t.id for t in phase.done_when], "of the phase checklist"
    else:
        siblings, scope = [t.id for t in phase.tasks_for(task.week)], "this week"
    key = f"{page}:{task.id}"
    tick = ctx.state["done"].get(task.id)
    label = task.title + (f"  :green[· done {date.fromisoformat(tick['date']):%d %b}]" if tick else "")
    st.checkbox(label, value=bool(tick), key=key, on_change=_on_toggle, args=(task, key, siblings, scope))
    if context:
        st.caption(context)
    if details and task.details:
        st.caption(task.details)


@st.dialog("Log a study session")
def session_dialog(ctx: Ctx) -> None:
    track = st.segmented_control("Track", ["Theory", "Project"], default="Theory", key="dlg_track") or "Theory"
    preset = st.pills("Duration", [25, 45, 60, 90, 120, "Other"], default=60, key="dlg_preset",
                      format_func=lambda m: f"{m} min" if isinstance(m, int) else m)
    minutes = st.number_input("Minutes", 5, 600, 30, 5, key="dlg_minutes") if preset in ("Other", None) else preset
    day = st.date_input("Date", date.today(), key="dlg_date", format="YYYY-MM-DD")
    note = st.text_input("What did you work on?", key="dlg_note",
                         placeholder="e.g. OSTEP ch. 4 · inverted index tests")
    week = ctx.plan.clamp(ctx.plan.week_on(day))
    st.caption(f"Counts toward {ctx.plan.week_label(week)}")
    if st.button("Save session", type="primary", icon=":material/check:", width="stretch"):
        store.update(lambda s: store.add_session(s, day, week, track.lower(), minutes, note))
        flash(f"Logged {minutes} min of {track.lower()}", "⏱️")
        st.rerun()


def unmatched_ticks(ctx: Ctx) -> None:
    """Ticks whose task text was edited in the Markdown: move or remove them."""
    by_id = {t.id for t in ctx.plan.all_items}
    orphans = {k: v for k, v in ctx.state["done"].items() if k not in by_id}
    if not orphans:
        return
    with st.container(border=True):
        st.markdown(f"#### :material/link_off: Ticks that no longer match a task ({len(orphans)})")
        st.caption("The task text was probably edited in the phase file. Move each tick to the right task, or remove it.")
        for old_id, tick in orphans.items():
            phase = ctx.plan.phase(int(old_id.split("/")[0][1:]))
            candidates = [t for t in phase.all_items if not ctx.done(t)] if phase else []
            st.markdown(f"**Was:** {tick['title'] or old_id} · ticked {tick['date']}")
            pick, move, remove = st.columns([6, 1, 1], vertical_alignment="bottom")
            choice = pick.selectbox("Move to", range(len(candidates)), key=f"orphan-pick:{old_id}",
                                    format_func=lambda i: f"[{candidates[i].track}] {candidates[i].title}",
                                    label_visibility="collapsed")
            if move.button("Move", key=f"orphan-move:{old_id}", disabled=not candidates, width="stretch"):
                target = candidates[choice]
                store.update(lambda s: store.move_tick(s, old_id, target.id, target.title))
                flash("Tick moved", "🔗")
                st.rerun()
            if remove.button("Remove", key=f"orphan-remove:{old_id}", width="stretch"):
                store.update(lambda s: s["done"].pop(old_id, None))
                st.rerun()


def _week_hours(ctx: Ctx, gw: int) -> dict[str, float]:
    return store.hours_by_week(ctx.state).get(gw, {"theory": 0.0, "project": 0.0})


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

def dashboard() -> None:
    ctx = get_ctx()
    plan, state = ctx.plan, ctx.state
    st.title("Dashboard", anchor=False)

    if ctx.raw_week < 1:
        days = (plan.start - ctx.today).days
        st.info(f"Your path starts on **{plan.start:%A %d %B %Y}** — in {days} day{'s' * (days != 1)}. "
                "Showing week 1 as a preview.", icon=":material/rocket_launch:")
    elif ctx.raw_week > plan.last_week:
        st.success("You reached the end of the plan!", icon=":material/celebration:")

    gw = ctx.week
    phase, week = plan.locate(gw)
    hours = store.hours_by_week(state)
    week_hours = sum(hours.get(gw, {}).values())
    items = plan.all_items
    n_done = ctx.count_done(items)
    overdue = [t for p in plan.phases for t in p.tasks if p.global_week(t.week) < gw and not ctx.done(t)]
    ticked_this_week = sum(1 for tick in state["done"].values()
                           if plan.week_on(date.fromisoformat(tick["date"])) == gw)

    # Hero card -----------------------------------------------------------------
    with st.container(border=True):
        left, right = st.columns([3, 2], gap="large", vertical_alignment="center")
        with left:
            start = plan.week_start(gw)
            st.caption(f"WEEK {gw} OF {plan.last_week} · {start:%d %b} – {start + timedelta(days=6):%d %b %Y}")
            st.subheader(phase.label, anchor=False)
            st.markdown(f"Week **{week}** of {phase.weeks} in this phase" if week
                        else "**Buffer week**: catch up, review, write the retro, or rest.")
            badges = st.container(horizontal=True)
            with badges:
                if overdue:
                    st.badge(f"{len(overdue)} overdue", icon=":material/schedule:", color="orange")
                else:
                    st.badge("On track", icon=":material/check:", color="green")
                st.badge(f"{week_hours:.1f} / {ctx.target:g} h this week", icon=":material/timer:", color="blue")
            st.page_link(ctx.pages["week"], label="Open this week", icon=":material/arrow_forward:")
        with right:
            phase_items = phase.all_items
            p_done = ctx.count_done(phase_items)
            span = (phase.end - phase.start).days + 1
            elapsed = min(max((ctx.today - phase.start).days + 1, 0) / span, 1.0)
            st.progress(p_done / len(phase_items), text=f"Phase tasks · {p_done}/{len(phase_items)}")
            st.progress(elapsed, text=f"Phase time used · {elapsed:.0%}")
            st.progress(n_done / len(items), text=f"Whole path · {n_done}/{len(items)}")

    # Metrics -------------------------------------------------------------------
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tasks done", n_done, f"+{ticked_this_week} this week" if ticked_this_week else None, border=True)
    c2.metric("Hours this week", f"{week_hours:.1f} / {ctx.target:g}", border=True)
    c3.metric("Study streak", f"{store.streak(state, gw)} wk", border=True,
              help="Weeks in a row with at least one logged study session.")
    c4.metric("Overdue tasks", len(overdue), border=True, help="Tasks from earlier weeks that are not ticked yet.")

    # Charts --------------------------------------------------------------------
    left, right = st.columns([3, 2], gap="large")
    with left:
        st.subheader("Study hours", anchor=False)
        if hours:
            st.altair_chart(charts.hours_chart(plan, hours, gw, ctx.target, ctx.theme), width="stretch")
        else:
            st.info("No study sessions yet. Log one and your hours chart starts here.", icon=":material/timer:")
            if st.button("Log a study session", icon=":material/timer:", key="dash-log"):
                session_dialog(ctx)
    with right:
        st.subheader("Next up", anchor=False)
        upcoming = [t for t in plan.tasks_in_week(gw) if not ctx.done(t)] or overdue[:5]
        if not upcoming:
            st.success("Nothing open this week.", icon=":material/done_all:")
        for t in upcoming[:6]:
            task_row(ctx, t, "next", details=False, context=TRACK_LABEL.get(t.track, "").split(" ", 1)[-1])

    st.subheader("Plan map", anchor=False)
    st.caption("One cell per week, shaded by the share of that week's tasks done. The outlined cell is this week. "
               "Hover a cell for details.")
    st.altair_chart(charts.plan_map(plan, state["done"], gw, ctx.theme), width="stretch")

    if overdue:
        with st.expander(f"Overdue tasks ({len(overdue)})", icon=":material/schedule:"):
            for t in overdue[:25]:
                task_row(ctx, t, "overdue", details=False,
                         context=f"Phase {t.phase} · week {t.week} · {t.track}")
            if len(overdue) > 25:
                st.caption(f"…and {len(overdue) - 25} more on the Plan page.")

    unmatched_ticks(ctx)


def this_week() -> None:
    ctx = get_ctx()
    plan = ctx.plan
    st.title("This week", anchor=False)

    if "week_sel" not in st.session_state:
        st.session_state.week_sel = ctx.week

    def shift(delta: int) -> None:
        st.session_state.week_sel = plan.clamp(st.session_state.week_sel + delta)

    def back_to_now() -> None:
        st.session_state.week_sel = ctx.week

    with st.container(horizontal=True, vertical_alignment="center"):
        st.button(":material/chevron_left:", key="wk-prev", on_click=shift, args=(-1,), help="Previous week")
        st.selectbox("Week", range(1, plan.last_week + 1), key="week_sel", label_visibility="collapsed",
                     format_func=lambda w: plan.week_label(w) + ("  · now" if w == ctx.week else ""), width=430)
        st.button(":material/chevron_right:", key="wk-next", on_click=shift, args=(1,), help="Next week")
        st.button("Now", key="wk-now", icon=":material/today:", on_click=back_to_now,
                  disabled=st.session_state.week_sel == ctx.week)

    gw = st.session_state.week_sel
    phase, week = plan.locate(gw)
    tasks = phase.tasks_for(week) if week else []
    hrs = _week_hours(ctx, gw)
    total_h = hrs["theory"] + hrs["project"]

    with st.container(border=True):
        left, right = st.columns([3, 2], gap="large", vertical_alignment="center")
        with left:
            start = plan.week_start(gw)
            st.caption(f"{start:%A %d %b} – {start + timedelta(days=6):%A %d %b %Y}")
            st.subheader(phase.label, anchor=False)
            st.markdown(f"Week **{week}** of {phase.weeks}" if week else "**Buffer week**")
            if st.button("Log a study session", icon=":material/timer:", type="primary", key="wk-log"):
                session_dialog(ctx)
        with right:
            if tasks:
                n = ctx.count_done(tasks)
                st.progress(n / len(tasks), text=f"Tasks · {n}/{len(tasks)}")
            st.progress(min(total_h / ctx.target, 1.0),
                        text=f"Hours · {total_h:.1f} / {ctx.target:g}  (theory {hrs['theory']:.1f} · "
                             f"project {hrs['project']:.1f})")

    week_lessons = [lesson for lesson in lessons_mod.load_lessons()[0]
                    if week and lesson.phase == phase.number and lesson.week == week]
    for lesson in week_lessons:
        with st.container(border=True, horizontal=True, vertical_alignment="center"):
            st.markdown(f":material/school: **Lesson this week:** {lesson.title}  :gray[· {lesson.where}]")
            if st.button("Open lesson", key=f"wk-lesson-{lesson.slug}", icon=":material/arrow_forward:"):
                st.session_state["lesson"] = lesson.slug
                st.switch_page(ctx.pages["learn"])

    if week is None:
        st.info("Buffer week: catch up on anything still open, tick the *Done when* list, "
                "write the phase retro, or rest.", icon=":material/self_improvement:")
        left_open = [t for t in phase.all_items if not ctx.done(t)]
        with st.container(border=True):
            st.markdown(f"#### Still open in Phase {phase.number} ({len(left_open)})")
            for t in left_open:
                ctx_label = "Done when" if t.track == "done" else f"Week {t.week} · {t.track}"
                task_row(ctx, t, "buffer", details=False, context=ctx_label)
    else:
        col_t, col_p = st.columns(2, gap="medium")
        for col, track in ((col_t, "theory"), (col_p, "project")):
            with col, st.container(border=True, height="stretch"):
                hours_label = f"{hrs[track]:.1f} h logged"
                st.markdown(f"#### {TRACK_LABEL[track]}  :gray[· {hours_label}]")
                for t in phase.tasks_for(week, track):
                    task_row(ctx, t, "week")

    sessions = [s for s in ctx.state["sessions"] if int(s["week"]) == gw]
    if sessions:
        with st.expander(f"Study sessions this week ({len(sessions)})", icon=":material/timer:"):
            for s in sorted(sessions, key=lambda s: s["date"]):
                _session_line(s)

    st.subheader("Journal", anchor=False)
    journal_form(ctx, gw)


def journal_form(ctx: Ctx, gw: int) -> None:
    log = ctx.state["logs"].get(str(gw), {})
    with st.form(f"journal-{gw}", border=True):
        learned = st.text_area("What I learned — in my own words", log.get("learned", ""), height=120)
        recall = st.text_area("Recall questions — one per line (they become flashcards on the Review page)",
                              log.get("recall", ""), height=100,
                              placeholder="Why is dict lookup O(1) on average?\nWhat does fork() return?")
        c1, c2 = st.columns(2)
        broke = c1.text_area("What broke and how I fixed it", log.get("broke", ""))
        confused = c2.text_area("Still confused about", log.get("confused", ""))
        next_step = st.text_input("Next step", log.get("next_step", ""))
        saved = f"Last saved {log['saved']}" if log.get("saved") else "Not saved yet"
        cols = st.columns([1, 3], vertical_alignment="center")
        submitted = cols[0].form_submit_button("Save journal", type="primary", icon=":material/save:")
        cols[1].caption(saved)
    if submitted:
        fields = {"learned": learned, "recall": recall, "broke": broke, "confused": confused, "next_step": next_step}
        store.update(lambda s: store.save_log(s, gw, fields))
        flash("Journal saved", "📝")
        st.rerun()


def _session_line(s: dict) -> None:
    with st.container(horizontal=True, vertical_alignment="center"):
        icon = TRACK_LABEL[s["track"]].split(" ")[0]
        st.markdown(f"{icon} **{s['minutes']} min** · {s['date']} · {s['note'] or ':gray[no note]'}")
        st.button(":material/delete:", key=f"del-{s['id']}", help="Delete this session", type="tertiary",
                  on_click=lambda: store.update(lambda st_: store.delete_session(st_, s["id"])))


def plan_page() -> None:
    ctx = get_ctx()
    plan = ctx.plan
    st.title("Plan", anchor=False)
    st.altair_chart(charts.timeline(plan, ctx.state["done"], ctx.today, ctx.theme), width="stretch")

    query = st.text_input("Search all tasks", key="plan_query", icon=":material/search:",
                          placeholder="e.g. Terraform, window functions, RAG", label_visibility="collapsed")
    if query.strip():
        q = query.strip().lower()
        matches = [t for t in plan.all_items if q in f"{t.title} {t.details}".lower()]
        st.caption(f"{len(matches)} match{'es' * (len(matches) != 1)} for “{query.strip()}”")
        for t in matches:
            where = f"Phase {t.phase} · " + ("Done when" if t.track == "done" else f"week {t.week} · {t.track}")
            task_row(ctx, t, "search", details=False, context=where)
        return

    current_phase, current_week = plan.locate(ctx.week)
    if "plan_phase" not in st.session_state:
        st.session_state.plan_phase = current_phase.number
    with st.container(horizontal=True, vertical_alignment="bottom"):
        chosen = st.segmented_control("Phase", [p.number for p in plan.phases], key="plan_phase",
                                      format_func=lambda n: f"P{n}")
        status = st.segmented_control("Show", ["All", "Open", "Done"], default="All", key="plan_status") or "All"
    phase = plan.phase(chosen if chosen is not None else current_phase.number)

    def visible(t: Task) -> bool:
        return status == "All" or (status == "Done") == ctx.done(t)

    items = phase.all_items
    n = ctx.count_done(items)
    with st.container(border=True):
        st.subheader(phase.label, anchor=False)
        st.caption(f"{phase.start:%d %b %Y} → {phase.end:%d %b %Y} · {phase.weeks} weeks + 1 buffer week · "
                   f"plan file `phases/{phase.path.name}`")
        st.progress(n / len(items), text=f"{n}/{len(items)} done")

    for week in range(1, phase.weeks + 1):
        week_tasks = phase.tasks_for(week)
        w_done = ctx.count_done(week_tasks)
        shown = [t for t in week_tasks if visible(t)]
        if not shown:
            continue
        gw = phase.global_week(week)
        is_now = phase is current_phase and week == current_week
        icon = ":material/check_circle:" if w_done == len(week_tasks) else (
            ":material/radio_button_checked:" if is_now else ":material/radio_button_unchecked:")
        title = f"Week {week} · W{gw} · {plan.week_start(gw):%d %b %Y} — {w_done}/{len(week_tasks)}"
        with st.expander(title + ("  · now" if is_now else ""), icon=icon, expanded=is_now):
            for track in ("theory", "project"):
                track_tasks = [t for t in shown if t.track == track]
                if track_tasks:
                    st.markdown(f"**{TRACK_LABEL[track]}**")
                    for t in track_tasks:
                        task_row(ctx, t, "plan")

    checklist = [t for t in phase.done_when if visible(t)]
    if checklist:
        with st.container(border=True):
            st.markdown("#### :material/flag: Done when")
            for t in checklist:
                task_row(ctx, t, "plan", details=False)


def review() -> None:
    ctx = get_ctx()
    st.title("Review", anchor=False)
    st.caption("Flashcards from the recall questions in your weekly journal. Answer out loud or on paper first, "
               "then check your notes and be honest.")
    cards = store.recall_cards(ctx.state)
    if not cards:
        st.info("No recall questions yet. Add some in the journal on **This week**, one question per line.",
                icon=":material/style:")
        st.page_link(ctx.pages["week"], label="Go to This week", icon=":material/arrow_forward:")
        return

    reviews = ctx.state["reviews"]

    def box(card: dict) -> int:
        return reviews.get(card["id"], {}).get("box", 0)

    mastered = sum(box(c) >= 3 for c in cards)
    c1, c2, c3 = st.columns(3)
    c1.metric("Cards", len(cards), border=True)
    c2.metric("Learning", len(cards) - mastered, border=True, help="Boxes 0–2: shown first.")
    c3.metric("Mastered", mastered, border=True, help="Box 3 or higher: remembered 3+ times in a row.")

    queue = sorted(cards, key=lambda c: (box(c), reviews.get(c["id"], {}).get("last", ""), c["id"]))
    card = next((c for c in cards if c["id"] == st.session_state.get("card_id")), queue[0])
    st.session_state.card_id = card["id"]

    def answer(remembered: bool) -> None:
        store.update(lambda s: store.review_card(s, card["id"], remembered))
        st.session_state.pop("card_id", None)
        flash("Nice — moving it to the next box" if remembered else "It will come back soon",
              "🧠" if remembered else "🔁")

    def skip() -> None:
        others = [c["id"] for c in cards if c["id"] != card["id"]]
        st.session_state.card_id = random.choice(others) if others else card["id"]

    with st.container(border=True):
        st.caption(f"From {ctx.plan.week_label(card['week'])} · box {box(card)}/5")
        st.markdown(f"### {card['question']}")
        with st.expander("Show my notes from that week", icon=":material/visibility:"):
            st.markdown(card["notes"] or "_No notes saved that week._")
        with st.container(horizontal=True):
            st.button("Again", icon=":material/replay:", on_click=answer, args=(False,), key="rv-again")
            st.button("Got it", icon=":material/check:", type="primary", on_click=answer, args=(True,), key="rv-ok")
            st.button("Skip", icon=":material/skip_next:", type="tertiary", on_click=skip, key="rv-skip")
    st.progress(mastered / len(cards), text=f"Mastered {mastered}/{len(cards)}")


def journal() -> None:
    ctx = get_ctx()
    plan, state = ctx.plan, ctx.state
    st.title("Journal", anchor=False)
    hours = store.hours_by_week(state)
    weeks = sorted({int(w) for w in state["logs"]} | set(hours), reverse=True)
    total = sum(h["theory"] + h["project"] for h in hours.values())

    c1, c2, c3 = st.columns(3)
    c1.metric("Total hours", f"{total:.1f}", border=True)
    c2.metric("Study sessions", len(state["sessions"]), border=True)
    c3.metric("Weeks journaled", len(state["logs"]), border=True)

    if not weeks:
        st.info("Nothing yet. Log a study session (sidebar) or save a journal entry on **This week**.",
                icon=":material/edit_note:")
        return

    labels = {"learned": "What I learned", "recall": "Recall questions", "broke": "What broke",
              "confused": "Still confused", "next_step": "Next step"}
    for gw in weeks:
        h = hours.get(gw, {"theory": 0.0, "project": 0.0})
        log = state["logs"].get(str(gw), {})
        with st.expander(f"{plan.week_label(gw)} — {h['theory'] + h['project']:.1f} h",
                         expanded=gw == weeks[0], icon=":material/event_note:"):
            filled = [(labels[k], log[k]) for k in store.JOURNAL_FIELDS if log.get(k)]
            for label, text in filled:
                st.markdown(f"**{label}**")
                st.markdown(text)
            if not filled:
                st.caption("No journal entry for this week.")
            sessions = sorted((s for s in state["sessions"] if int(s["week"]) == gw), key=lambda s: s["date"])
            if sessions:
                st.markdown("**Study sessions**")
                for s in sessions:
                    _session_line(s)
