"""Altair charts for the tracker.

Colors follow one rule each:
- Theory = blue, Project = orange (categorical, same everywhere in the app).
- "How much is done" = one blue ramp, light -> dark (sequential).
Light and dark mode each get their own validated steps, not an automatic flip.
"""

from __future__ import annotations

from datetime import date

import altair as alt
import pandas as pd

from plan import Plan

PALETTES = {
    "light": {
        "theory": "#2a78d6", "project": "#eb6834",
        "ramp": ["#cde2fb", "#184f95"],            # 0% -> 100% done
        "track": "#e3e7ee",                        # empty bar background
        "surface": "#ffffff", "ink": "#1f2430", "muted": "#6b7280",
    },
    "dark": {
        "theory": "#3987e5", "project": "#d95926",
        "ramp": ["#0d366b", "#86b6ef"],
        "track": "#2b3038",
        "surface": "#14161a", "ink": "#eceef2", "muted": "#a3a8b4",
    },
}
TRACKS = ["Theory", "Project"]


def palette(theme: str | None) -> dict:
    return PALETTES["dark" if theme == "dark" else "light"]


def _clean(chart: alt.Chart, height: int) -> alt.Chart:
    return (chart.properties(height=height)
            .configure_view(strokeWidth=0)
            .configure_axis(grid=False, domain=False, ticks=False, labelPadding=6)
            .configure_legend(orient="top", title=None, labelFontSize=12, symbolType="square"))


def hours_chart(plan: Plan, hours: dict[int, dict[str, float]], current: int, target: float,
                theme: str | None, weeks_shown: int = 12) -> alt.LayerChart:
    """Stacked bars: theory + project hours for the last N weeks, with a target line."""
    c = palette(theme)
    first = max(1, current - weeks_shown + 1)
    rows = []
    for gw in range(first, current + 1):
        h = hours.get(gw, {"theory": 0.0, "project": 0.0})
        for order, track in enumerate(TRACKS):
            rows.append({"week": f"W{gw}", "track": track, "order": order,
                         "hours": round(h[track.lower()], 2), "when": plan.week_label(gw)})
    df = pd.DataFrame(rows)
    top = max(target * 1.25, df.groupby("week")["hours"].sum().max() * 1.1, 1)

    bars = alt.Chart(df).mark_bar(stroke=c["surface"], strokeWidth=2, cornerRadius=3).encode(
        x=alt.X("week:N", sort=None, title=None, axis=alt.Axis(labelAngle=0, labelColor=c["muted"])),
        y=alt.Y("hours:Q", stack="zero", title=None, scale=alt.Scale(domain=[0, top]),
                axis=alt.Axis(labelColor=c["muted"], tickCount=4, grid=True, gridColor=c["track"])),
        color=alt.Color("track:N", scale=alt.Scale(domain=TRACKS, range=[c["theory"], c["project"]]),
                        legend=alt.Legend(labelColor=c["ink"])),
        order=alt.Order("order:Q"),
        tooltip=[alt.Tooltip("when:N", title="Week"), alt.Tooltip("track:N", title="Track"),
                 alt.Tooltip("hours:Q", title="Hours", format=".1f")],
    )
    goal = pd.DataFrame({"y": [target], "label": [f"target {target:g} h"]})
    rule = alt.Chart(goal).mark_rule(color=c["muted"], strokeDash=[4, 4]).encode(y="y:Q")
    text = alt.Chart(goal).mark_text(align="left", dx=4, dy=-7, color=c["muted"], fontSize=11).encode(
        y="y:Q", x=alt.value(0), text="label:N")
    return _clean(alt.layer(bars, rule, text), 260)


def plan_map(plan: Plan, done: dict, current: int, theme: str | None) -> alt.LayerChart:
    """Heatmap: one cell per week of the plan, shaded by the share of tasks done."""
    c = palette(theme)
    rows = []
    for p in plan.phases:
        for week in range(1, p.weeks + 1):
            tasks = p.tasks_for(week)
            n_done = sum(t.id in done for t in tasks)
            gw = p.global_week(week)
            rows.append({
                "phase": f"{p.number} · {p.name.split(' (')[0]}", "week": week, "gw": f"W{gw}",
                "starts": f"{plan.week_start(gw):%d %b %Y}", "share": n_done / len(tasks) if tasks else 0.0,
                "progress": f"{n_done}/{len(tasks)}", "now": gw == current, "future": gw > current,
            })
    df = pd.DataFrame(rows)
    order = list(dict.fromkeys(df["phase"]))
    base = alt.Chart(df).encode(
        x=alt.X("week:O", title="Week of phase",
                  axis=alt.Axis(labelAngle=0, labelColor=c["muted"], titleColor=c["muted"])),
        y=alt.Y("phase:N", sort=order, title=None, axis=alt.Axis(labelColor=c["ink"], labelLimit=260)),
    )
    cells = base.mark_rect(cornerRadius=4, stroke=c["surface"], strokeWidth=3).encode(
        color=alt.Color("share:Q", scale=alt.Scale(domain=[0, 1], range=c["ramp"]),
                        legend=alt.Legend(title="Done", format="%", orient="right", gradientLength=120,
                                          titleColor=c["ink"], labelColor=c["muted"], labelOffset=6)),
        opacity=alt.condition("datum.future", alt.value(0.4), alt.value(1.0)),  # upcoming weeks recede
        tooltip=[alt.Tooltip("phase:N", title="Phase"), alt.Tooltip("week:O", title="Week"),
                 alt.Tooltip("gw:N", title="Global week"), alt.Tooltip("starts:N", title="Starts"),
                 alt.Tooltip("progress:N", title="Tasks done")],
    )
    now = base.transform_filter("datum.now").mark_rect(
        cornerRadius=4, fill=None, stroke=c["ink"], strokeWidth=2.5)
    return (alt.layer(cells, now).properties(height=32 * len(order))
            .configure_view(strokeWidth=0)
            .configure_axis(grid=False, domain=False, ticks=False, labelPadding=6))


def timeline(plan: Plan, done: dict, today: date, theme: str | None) -> alt.LayerChart:
    """Gantt-style bars per phase; the filled part shows how much is done."""
    c = palette(theme)
    rows = []
    for p in plan.phases:
        items = p.all_items
        share = sum(t.id in done for t in items) / len(items) if items else 0.0
        span = (p.end - p.start).days + 1
        rows.append({
            "phase": f"{p.number} · {p.name.split(' (')[0]}", "start": p.start.isoformat(),
            "end": p.end.isoformat(), "filled": pd.Timestamp(p.start) + pd.Timedelta(days=span * share),
            "share": share, "dates": f"{p.start:%d %b %Y} → {p.end:%d %b %Y}",
        })
    df = pd.DataFrame(rows)
    df["filled"] = df["filled"].dt.strftime("%Y-%m-%d")
    order = list(df["phase"])
    y = alt.Y("phase:N", sort=order, title=None, axis=alt.Axis(labelColor=c["ink"], labelLimit=260))
    tooltip = [alt.Tooltip("phase:N", title="Phase"), alt.Tooltip("dates:N", title="Dates"),
               alt.Tooltip("share:Q", title="Done", format=".0%")]
    background = alt.Chart(df).mark_bar(color=c["track"], cornerRadius=4, height=16).encode(
        x=alt.X("start:T", title=None, axis=alt.Axis(format="%b %Y", labelColor=c["muted"], tickCount=8)),
        x2="end:T", y=y, tooltip=tooltip)
    filled = alt.Chart(df).mark_bar(color=c["theory"], cornerRadius=4, height=16).encode(
        x="start:T", x2="filled:T", y=y, tooltip=tooltip)
    marker = pd.DataFrame({"day": [today.isoformat()], "label": ["today"]})
    rule = alt.Chart(marker).mark_rule(color=c["ink"], strokeWidth=1.5, strokeDash=[3, 3]).encode(x="day:T")
    label = alt.Chart(marker).mark_text(color=c["ink"], dy=-6, fontWeight="bold", fontSize=11).encode(
        x="day:T", y=alt.value(0), text="label:N")
    return (alt.layer(background, filled, rule, label).properties(height=30 * len(order) + 20)
            .configure_view(strokeWidth=0)
            .configure_axis(grid=False, domain=False, ticks=False, labelPadding=6))
