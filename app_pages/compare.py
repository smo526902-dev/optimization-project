"""Race the GA against the MA over several seeds, with the same budget."""
import numpy as np
import plotly.graph_objects as go
import streamlit as st

from app_pages import ui
from evoopt import ALGORITHMS, FUNCTIONS, Problem
from experiments.analyze import apply_error_floor, compare

AUTO_RUN_SECONDS = 6.0
ALGOS = ("GA", "MA")

with st.sidebar:
    key, dim = ui.pick_function("race", default="rosenbrock", default_dim=5)
    n_runs = st.slider("Seeds per algorithm", 3, 30, 10, key="race_runs",
                       help="Seeds 1 to N. The GA and the MA use the same seeds.")
    per_dim = ui.budget_picker("race", dim, default=2_000)
    evals = per_dim * dim
    seconds = n_runs * sum(ui.estimated_seconds(a, evals) for a in ALGOS)
    clicked = st.button("Race GA and MA", type="primary", icon=":material/compare_arrows:", width="stretch", key="race_go")
    if seconds >= AUTO_RUN_SECONDS:
        st.caption(f"About {seconds:.0f} s, so the race starts when you press the button.")

fn = FUNCTIONS[key]
st.title(f"GA vs MA on {fn.name}, {dim}-D")


def run_plain(algo, seed):
    return ui.cached_run("race", (algo, key, dim, seed, per_dim),
                         lambda: ALGORITHMS[algo.lower()]().run(Problem(key, dim, evals), seed=seed))


seeds = list(range(1, n_runs + 1))
done = all(ui.is_cached("race", (a, key, dim, s, per_dim)) for a in ALGOS for s in seeds)
if not (done or clicked or seconds < AUTO_RUN_SECONDS):
    ui.empty_state(
        "Ready to race",
        f"{n_runs} seeds for each algorithm take about {seconds:.0f} seconds, so the race waits for you. "
        "Press <b>Race GA and MA</b> in the sidebar.",
    )
    st.stop()

bar = None if done else st.progress(0.0, text="Starting…")
results = {a: [] for a in ALGOS}
for i, s in enumerate(seeds):
    for a in ALGOS:
        results[a].append(run_plain(a, s))
    if bar is not None:
        bar.progress((i + 1) / n_runs, text=f"Seed {s} of {n_runs} done")
if bar is not None:
    bar.empty()

errors = {a: apply_error_floor([r.error for r in results[a]]) for a in ALGOS}
p, sign = compare(errors["MA"], errors["GA"])
ma_lower = int(np.sum(errors["MA"] < errors["GA"]))
ga_lower = int(np.sum(errors["GA"] < errors["MA"]))
equal = n_runs - ma_lower - ga_lower
p_text = f"<span class='nowrap'>(Wilcoxon rank-sum, p = <span class='num'>{ui.fmt_p(p)}</span>)</span>"
if sign == "+":
    verdict, chip = f"The MA ends significantly lower than the GA {p_text}.", "ok"
elif sign == "-":
    verdict, chip = f"The GA ends significantly lower than the MA {p_text}.", "no"
elif equal == n_runs:
    verdict, chip = "Both reach the same final error on every seed: a tie.", "tie"
else:
    verdict, chip = f"No significant difference between the GA and the MA {p_text}.", "tie"
label = {"ok": "MA better", "no": "GA better", "tie": "no difference"}[chip]
st.html(
    f"<p class='verdict'>{verdict}<span class='chip {chip}'>{label}</span></p>"
    f"<div class='fair'><span>Per seed: MA lower on <b class='num'>{ma_lower}</b>, GA lower on <b class='num'>{ga_lower}</b>, "
    f"equal on <b class='num'>{equal}</b></span><span>Same budget: <b class='num'>{evals:,}</b> evaluations each</span>"
    f"<span>Same seeds: <b class='num'>1–{n_runs}</b></span><span>Errors below 1e-8 count as 0</span></div>"
)


def band_figure():
    grid = np.linspace(evals / 100, evals, 100)
    fig = go.Figure()
    for a in ALGOS:
        c = ui.ALGO_COLORS[a]
        curves = np.array([np.maximum(r.error_at(grid), ui.ERROR_FLOOR) for r in results[a]])
        curves[~np.isfinite(curves)] = np.nan
        q25, med, q75 = np.nanpercentile(curves, [25, 50, 75], axis=0)
        fig.add_trace(go.Scatter(x=np.r_[grid, grid[::-1]], y=np.r_[q75, q25[::-1]], fill="toself", fillcolor=c,
                                 opacity=0.14, line=dict(width=0), hoverinfo="skip", showlegend=False))
        fig.add_trace(go.Scatter(x=grid, y=med, mode="lines", name=f"{a} median", line=dict(color=c, width=2.6),
                                 hovertemplate="%{x:,.0f} evaluations<br>median error %{y:.3g}<extra>" + a + "</extra>"))
    ui.success_line(fig)
    fig.update_layout(**ui.base_layout(380, margin=dict(l=62, r=18, t=30, b=46)))
    fig.update_xaxes(title_text="function evaluations", tickformat="~s")
    fig.update_yaxes(title_text="best error f − f*", type="log", exponentformat="e")
    return fig


ui.show(band_figure(), key=f"band_{key}_{dim}_{n_runs}_{per_dim}")
st.caption("Lines: the median best error over all seeds. Bands: the middle half of the seeds (25th to 75th percentile).")

st.subheader("Every seed")
ui.drawer([(a, list(zip(seeds, errors[a]))) for a in ALGOS])

st.html("<div style='height:.6rem'></div>")
ui.table(
    ["Algorithm", "Solved", "Median error", "Best", "Worst", "Time per run"],
    [
        [
            ui.algo_cell(a, ui.ALGO_NAMES[a]),
            ui.rate_cell(float(np.mean(errors[a] <= ui.SUCCESS_ERROR)), a),
            ui.num(ui.fmt_error(np.median(errors[a]))),
            ui.num(ui.fmt_error(errors[a].min())),
            ui.num(ui.fmt_error(errors[a].max())),
            f"{ui.num(f'{np.mean([r.runtime for r in results[a]]):.2f}')} s",
        ]
        for a in ALGOS
    ],
    right=(2, 3, 4, 5),
)
if any(r.stats.get("ls_share") for r in results["MA"]):
    share = np.mean([r.stats["ls_share"] for r in results["MA"]])
    st.caption(f"The MA spent {share:.0%} of its evaluations on local search, inside the same budget as the GA.")
