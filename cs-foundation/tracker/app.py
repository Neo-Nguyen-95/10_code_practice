"""Learning tracker — a small local website for my learning path.

The plan comes from ../phases/*.md (plan.py); lessons from ../lessons/*.md
(lessons.py, run by learn.py and sqlbox.py). My progress is saved in
progress.json next to this file (store.py). Other pages live in views.py and
charts in charts.py.

Run from the repository root:

    uv run --with streamlit streamlit run cs-foundation/tracker/app.py
"""

from __future__ import annotations

from datetime import date

import streamlit as st

import learn
import store
import views
from plan import load_plan

st.set_page_config(page_title="Learning tracker", page_icon=":material/school:", layout="wide")

try:
    plan = load_plan()
except ValueError as err:
    st.error(f"Could not read the plan: {err}", icon=":material/error:")
    st.stop()

state = store.load()

pages = {
    "dashboard": st.Page(views.dashboard, title="Dashboard", icon=":material/dashboard:", default=True),
    "week": st.Page(views.this_week, title="This week", icon=":material/calendar_today:", url_path="week"),
    "plan": st.Page(views.plan_page, title="Plan", icon=":material/map:", url_path="plan"),
    "learn": st.Page(learn.learn_page, title="Learn", icon=":material/school:", url_path="learn"),
    "review": st.Page(views.review, title="Review", icon=":material/style:", url_path="review"),
    "journal": st.Page(views.journal, title="Journal", icon=":material/edit_note:", url_path="journal"),
}
nav = st.navigation({
    "Track": [pages["dashboard"], pages["week"], pages["plan"]],
    "Learn": [pages["learn"], pages["review"], pages["journal"]],
})

with st.sidebar:
    with st.expander("Settings", icon=":material/settings:"):
        today = st.date_input("Pretend today is", date.today(), key="pretend_today", format="YYYY-MM-DD",
                              help="Preview another week of the plan. Ticks and sessions still save real dates.")
        target = st.number_input("Weekly target (hours)", 1.0, 40.0,
                                 float(state["settings"]["weekly_target_hours"]), 0.5, key="weekly_target")
        if target != state["settings"]["weekly_target_hours"]:
            state = store.update(lambda s: s["settings"].update(weekly_target_hours=target))

ctx = views.Ctx(plan, state, today, pages)
views.set_ctx(ctx)

with st.sidebar:
    hours = store.hours_by_week(state).get(ctx.week, {"theory": 0.0, "project": 0.0})
    done_h = hours["theory"] + hours["project"]
    st.progress(min(done_h / ctx.target, 1.0), text=f"W{ctx.week} · {done_h:.1f} / {ctx.target:g} h")
    if st.button("Log a study session", icon=":material/timer:", type="primary", width="stretch", key="side-log"):
        views.session_dialog(ctx)
    st.caption(f"Progress is saved to `{store.STATE_FILE.name}`. Commit it to keep your history.")

views.show_flashes()
nav.run()
