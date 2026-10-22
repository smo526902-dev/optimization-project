"""Shared look and helpers for the Streamlit app.

The visual world is a natural-history specimen cabinet: a cabinet-green rail
for navigation and controls, a cool tray ground, white unit trays, and every
candidate solution drawn as a pinned specimen whose pin-head colour names the
algorithm. Words are set in Archivo, every number in JetBrains Mono.
"""
from __future__ import annotations

import html
import time
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
import streamlit as st
from scipy.stats import rankdata

from evoopt import ALGORITHMS, CATEGORIES, EVALS_PER_DIM, FUNCTIONS, Problem
from evoopt import operators as ops
from evoopt.local_search import LOCAL_SEARCHES
from evoopt.ma import LEARNING_MODELS

ROOT = Path(__file__).resolve().parent.parent

# ------------------------------------------------------------------ palette
CABINET = "#1E4D3F"
TRAY = "#EEF2EC"
PAPER = "#FFFFFF"
INK = "#15201B"
INK_DIM = "#4A5A52"
HAIRLINE = "#C8D2CB"
GRID = "#E4EAE5"
ELITE = "#E3B323"
SANS = "Archivo, sans-serif"
MONO = "JetBrains Mono, monospace"

ALGO_COLORS = {"GA": "#2E5BD8", "MA": "#D9412B", "DE": "#B7861A", "RS": "#7A8580"}
ALGO_NAMES = {"GA": "Genetic Algorithm", "MA": "Memetic Algorithm", "DE": "Differential Evolution", "RS": "Random search"}

LS_NAMES = {"hooke_jeeves": "Hooke–Jeeves pattern search", "hill_climbing": "stochastic hill climbing"}

SUCCESS_ERROR = 1e-4
ERROR_FLOOR = 1e-8


def estimated_seconds(algo, evals):
    """Rough single-run time on a laptop, measured in the Stage 4 experiments."""
    return evals * (3e-5 if algo == "MA" else 1e-5)

# Landscape tint: deep cabinet green at the lowest values, tray white at the highest.
TRAY_SCALE = [
    [0.0, "#123329"],
    [0.18, "#1E4D3F"],
    [0.42, "#5E8A77"],
    [0.68, "#A9C2B5"],
    [1.0, "#F4F7F3"],
]

CSS = f"""
<style>
::selection {{ background: {ELITE}66; color: {INK}; }}
html {{ scrollbar-color: #A9B7AE transparent; }}
[data-testid="stHeader"] {{ height: 2.6rem; background: {TRAY}; }}
[data-testid="stMainBlockContainer"] {{ padding-top: 3rem; padding-bottom: 3rem; }}
[data-testid="stSidebarUserContent"] {{ padding-top: .25rem; }}
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {{ color: {INK}; font-weight: 650; }}
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"]:hover {{ color: {INK}; background: #FFFFFF; border-color: #FFFFFF; }}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {{ color: #BFD2C6; }}
[data-testid="stPlotlyChart"] {{ border: 1px solid {HAIRLINE}; border-radius: 4px; overflow: hidden; background: {PAPER}; }}
h1 {{ letter-spacing: -.015em; }}
.brand {{ margin: 0 0 .25rem; }}
.brand b {{ font-size: 1.05rem; letter-spacing: -.01em; }}
.brand span {{ display: block; color: #BFD2C6; font-size: .82rem; margin-top: 2px; }}
.num, .tray .val {{ font-family: {MONO}; font-variant-numeric: tabular-nums; font-size: .94em; }}
.lede {{ color: {INK_DIM}; margin: -.5rem 0 .7rem; max-width: 72ch; }}
.pin {{ display: inline-block; width: 12px; height: 12px; border-radius: 50%; background: var(--c);
        box-shadow: inset 0 0 0 2px rgba(255,255,255,.85), 0 0 0 1px var(--c); flex: none; }}
.pin.hollow {{ background: {PAPER}; box-shadow: 0 0 0 1.5px var(--c); }}
.acc {{ background: {PAPER}; border: 1px solid {HAIRLINE}; border-radius: 4px; padding: 14px 16px 10px; }}
.acc-head {{ display: flex; justify-content: space-between; align-items: baseline; gap: 12px;
             border-bottom: 1.5px solid {INK}; padding-bottom: 8px; }}
.acc h3 {{ margin: 0; padding: 0; font-size: 1.05rem; display: flex; align-items: center; gap: 9px; }}
.acc-no {{ color: {INK_DIM}; font-size: .8rem; white-space: nowrap; }}
.acc .meta {{ color: {INK_DIM}; font-size: .8rem; margin: 6px 0 2px; }}
.acc dl {{ display: grid; grid-template-columns: max-content 1fr; column-gap: 16px; margin: 4px 0 0; }}
.acc dt, .acc dd {{ padding: 6px 0; border-top: 1px solid {GRID}; font-size: .86rem; }}
.acc dl > :nth-child(1), .acc dl > :nth-child(2) {{ border-top: 0; }}
.acc dt {{ color: {INK_DIM}; }}
.acc dd {{ margin: 0; overflow-wrap: anywhere; }}
.tbl-wrap {{ background: {PAPER}; border: 1px solid {HAIRLINE}; border-radius: 4px; overflow-x: auto; }}
.tbl {{ width: 100%; border-collapse: collapse; font-size: .86rem; }}
.tbl th {{ text-align: left; font-weight: 600; color: {INK_DIM}; font-size: .78rem; padding: 9px 12px; border-bottom: 1.5px solid {INK}; white-space: nowrap; }}
.tbl td {{ padding: 7px 12px; border-top: 1px solid {GRID}; vertical-align: middle; }}
.tbl tr:first-child td {{ border-top: 0; }}
.tbl .r {{ text-align: right; }}
.tbl .who {{ display: inline-flex; align-items: center; gap: 8px; white-space: nowrap; }}
.tbl .chip {{ margin-left: 0; }}
.vs {{ margin: 0 6px; color: {INK_DIM}; font-size: .8rem; }}
.tbl .sub {{ display: block; color: {INK_DIM}; font-size: .76rem; margin-top: 2px; }}
.bar {{ display: inline-block; width: 56px; height: 6px; border-radius: 3px; background: {GRID}; overflow: hidden;
        vertical-align: middle; margin-right: 8px; }}
.bar i {{ display: block; height: 100%; background: var(--c); }}
.chip {{ display: inline-block; padding: 0 8px; border-radius: 999px; font-family: {SANS}; font-size: .74rem;
         line-height: 1.55; border: 1px solid; margin-left: 6px; vertical-align: 1px; }}
.chip.ok {{ color: #22603A; background: #E3F1E8; border-color: #B9DCC6; }}
.chip.no {{ color: #8E2A1A; background: #F8E5E1; border-color: #EBC0B7; }}
.chip.tie {{ color: {INK_DIM}; background: {TRAY}; border-color: {HAIRLINE}; }}
.fair {{ display: flex; flex-wrap: wrap; gap: 6px 18px; color: {INK_DIM}; font-size: .86rem; margin: 2px 0 14px; }}
.fair b {{ color: {INK}; font-weight: 600; }}
.verdict {{ font-size: 1.2rem; font-weight: 600; line-height: 1.35; margin: 0 0 6px; max-width: 60ch; }}
.drawer {{ display: grid; grid-template-columns: 76px 1fr; gap: 12px 14px; align-items: start; margin-top: .3rem; }}
.drawer .who {{ display: flex; align-items: center; gap: 8px; font-weight: 650; padding-top: 6px; }}
.drawer .who small {{ display: block; font-weight: 400; color: {INK_DIM}; font-size: .74rem; }}
.trays {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(74px, 1fr)); gap: 6px; }}
.nowrap {{ white-space: nowrap; }}
.tray {{ position: relative; background: {PAPER}; border: 1px solid {HAIRLINE}; border-radius: 3px; padding: 6px 6px 8px; min-height: 54px; }}
.tray .seed {{ font-size: .72rem; color: {INK_DIM}; }}
.tray .val {{ font-size: .76rem; margin-top: 7px; white-space: nowrap; }}
.tray .pin {{ position: absolute; top: 7px; right: 7px; width: 10px; height: 10px; }}
.tray.hit {{ background: color-mix(in srgb, var(--c) 8%, {PAPER}); border-color: color-mix(in srgb, var(--c) 42%, {PAPER}); }}
.legend-line {{ color: {INK_DIM}; font-size: .82rem; margin: .5rem 0 0; }}
.empty {{ background: {PAPER}; border: 1px dashed {HAIRLINE}; border-radius: 4px; padding: 22px 24px; color: {INK_DIM}; }}
.empty b {{ color: {INK}; }}
</style>
"""


def inject_css():
    st.html(CSS)


# ------------------------------------------------------------- formatting
def fmt_error(e):
    """Final error as shown everywhere: values below the CEC floor count as 0."""
    if not np.isfinite(e):
        return "∞"
    if e < ERROR_FLOOR:
        return "0"
    return f"{e:.2e}" if e < 1e-2 or e >= 1e4 else f"{e:.4g}"


def fmt_value(v):
    return f"{v:.6g}"


def fmt_vector(x, limit=6):
    shown = ", ".join(f"{v:.4g}" for v in x[:limit])
    return f"[{shown}{', …' if len(x) > limit else ''}]"


def esc(text):
    return html.escape(str(text))


# ------------------------------------------------------------ controls
def function_label(key):
    fn = FUNCTIONS[key]
    return f"{fn.name}  ·  {fn.category.lower()}"


def dims_for(key):
    fn = FUNCTIONS[key]
    return list(fn.dims) if fn.dims else [2, 5, 10, 30]


def pick_function(prefix, default="rastrigin", default_dim=2, allow_dim=True):
    """Function and dimension selectors for the sidebar."""
    keys = [k for c in CATEGORIES for k, f in FUNCTIONS.items() if f.category == c]
    key = st.selectbox("Benchmark function", keys, index=keys.index(default), format_func=function_label, key=f"{prefix}_fn")
    if not allow_dim:
        return key, 2
    options = dims_for(key)
    dim = st.selectbox(
        "Dimension d",
        options,
        index=options.index(default_dim) if default_dim in options else 0,
        key=f"{prefix}_dim_{key}",
        help="Number of variables. Only d = 2 can be drawn as a landscape.",
    )
    return key, dim


def algorithm_settings(prefix, algo):
    """Operator settings (call inside an expander); returns keyword arguments for the algorithm."""
    params = {}
    params["selection"] = st.selectbox("Selection", ops.SELECTIONS, key=f"{prefix}_sel",
                                       help="Tournament: best of 3 random individuals. Roulette: chance proportional to fitness. Rank: chance by rank.")
    params["crossover"] = st.selectbox("Crossover", ops.CROSSOVERS, key=f"{prefix}_cx",
                                       format_func={"sbx": "SBX", "blx": "BLX-α", "arithmetic": "arithmetic"}.get)
    params["mutation"] = st.selectbox("Mutation", ops.MUTATIONS, key=f"{prefix}_mut",
                                      help="Uniform reset keeps the population spread out; polynomial makes small steps.")
    pop = st.select_slider("Population size", ["auto", 20, 50, 100, 200], value="auto", key=f"{prefix}_pop",
                           help="auto: 50 for d < 10, otherwise 100.")
    if pop != "auto":
        params["pop_size"] = int(pop)
    if algo == "MA":
        params["local_search"] = st.selectbox("Local search", list(LOCAL_SEARCHES), key=f"{prefix}_ls", format_func=LS_NAMES.get)
        params["learning"] = st.selectbox("Learning", LEARNING_MODELS, key=f"{prefix}_learn",
                                          format_func=str.capitalize,
                                          help="Lamarckian writes the improved genes back; Baldwinian keeps only the improved fitness.")
        params["ls_rate"] = st.select_slider("Children refined by local search", [0.0, 0.02, 0.05, 0.1, 0.2], value=0.05,
                                             key=f"{prefix}_lsr", format_func=lambda r: f"{r:.0%}",
                                             help="The best individual is always refined.")
    return params


def budget_picker(prefix, dim, default=EVALS_PER_DIM):
    per_dim = st.select_slider(
        "Evaluation budget",
        [1_000, 2_000, 5_000, 10_000],
        value=default,
        key=f"{prefix}_budget",
        format_func=lambda v: f"{v:,} × d",
        help="Function evaluations allowed per run. Local search spends from the same budget.",
    )
    st.caption(f"= {per_dim * dim:,} evaluations per run")
    return per_dim


# ---------------------------------------------------------------- running
def run_with_frames(algo, key, dim, seed, per_dim, params, progress=None, max_frames=90):
    """Run GA or MA and keep up to ``max_frames`` evenly spaced generations."""
    algorithm = ALGORITHMS[algo.lower()](**params)
    problem = Problem(key, dim, per_dim * dim)
    frames, last = [], {}
    state = {"stride": 1, "tick": 0.0}

    def capture(s):
        snap = (s["generation"], s["n_evals"], s["population"].copy(), s["best_x"].copy(), s["best_f"])
        last["snap"] = snap
        if s["generation"] % state["stride"] == 0:
            frames.append(snap)
            if len(frames) > 2 * max_frames:
                del frames[1::2]
                state["stride"] *= 2
        if progress is not None and time.perf_counter() - state["tick"] > 0.12:
            state["tick"] = time.perf_counter()
            progress.progress(min(s["n_evals"] / problem.max_evals, 1.0),
                              text=f"Generation {s['generation']:,} · {s['n_evals']:,} of {problem.max_evals:,} evaluations")

    result = algorithm.run(problem, seed=seed, callback=capture)
    if last and (not frames or frames[-1][0] != last["snap"][0]):
        frames.append(last["snap"])
    if len(frames) > max_frames:
        idx = np.unique(np.linspace(0, len(frames) - 1, max_frames).round().astype(int))
        frames = [frames[i] for i in idx]
    return {"result": result, "frames": frames, "params": dict(params)}


@st.cache_resource
def shared_cache():
    """Finished runs, shared by every browser session while the app is running.
    A run is fully determined by its settings and seed, so sharing is safe."""
    return {}


def cached_run(kind, settings, compute, limit=600):
    cache = shared_cache().setdefault(kind, {})
    if settings not in cache:
        cache[settings] = compute()
        while len(cache) > limit:
            cache.pop(next(iter(cache)))
    return cache[settings]


def is_cached(kind, settings):
    return settings in shared_cache().get(kind, {})


def run_settings(algo, key, dim, seed, per_dim, params):
    return (algo, key, dim, seed, per_dim, tuple(sorted(params.items())))


def run_cached(algo, key, dim, seed, per_dim, params, progress=None):
    return cached_run("run", run_settings(algo, key, dim, seed, per_dim, params),
                      lambda: run_with_frames(algo, key, dim, seed, per_dim, params, progress), limit=24)


# ------------------------------------------------------------------ charts
def base_layout(height, **extra):
    axis = dict(gridcolor=GRID, linecolor=HAIRLINE, zeroline=False, ticks="outside", tickcolor=HAIRLINE,
                tickfont=dict(family=MONO, size=11, color=INK_DIM), title_font=dict(size=12, color=INK_DIM))
    layout = dict(
        height=height,
        font=dict(family=SANS, size=13, color=INK),
        paper_bgcolor=PAPER,
        plot_bgcolor=PAPER,
        margin=dict(l=62, r=18, t=18, b=48),
        hoverlabel=dict(bgcolor=INK, bordercolor=INK, font=dict(family=MONO, size=12, color="#FFFFFF")),
        legend=dict(orientation="h", x=0, y=1.0, yanchor="bottom", bgcolor="rgba(0,0,0,0)", font=dict(size=12)),
        xaxis=dict(axis),
        yaxis=dict(axis),
    )
    layout.update(extra)
    return layout


def show(fig, key=None):
    st.plotly_chart(fig, theme=None, width="stretch", key=key,
                    config={"displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"]})


@st.cache_data(show_spinner=False)
def landscape_grid(key, resolution=180):
    """f on a grid over the 2-D domain, plus a rank-scaled copy for even colouring."""
    fn = FUNCTIONS[key]
    lower, upper = fn.bounds(2)
    xs = np.linspace(lower[0], upper[0], resolution)
    ys = np.linspace(lower[1], upper[1], resolution)
    X1, X2 = np.meshgrid(xs, ys)
    Z = fn(np.column_stack([X1.ravel(), X2.ravel()])).reshape(X1.shape)
    # Rank after rounding, so values that differ only by rounding noise (Easom's
    # flat plain is ~1e-300 everywhere) share one rank and one colour.
    ranks = rankdata(np.round(Z, 9), method="average").reshape(Z.shape)
    ranks = (ranks - ranks.min()) / max(ranks.max() - ranks.min(), 1)
    return xs, ys, Z, ranks


def landscape_trace(key, showlines=True):
    xs, ys, Z, ranks = landscape_grid(key)
    return go.Contour(
        x=xs, y=ys, z=ranks, customdata=Z, colorscale=TRAY_SCALE, showscale=False, ncontours=26,
        contours=dict(coloring="heatmap", showlines=showlines),
        line=dict(width=0.6, color="rgba(244,247,243,0.35)"),
        hovertemplate="x₁ %{x:.4g}<br>x₂ %{y:.4g}<br>f %{customdata:.5g}<extra></extra>",
    )


def optimum_trace(key, dim):
    x_star = FUNCTIONS[key].x_star(dim)
    return go.Scatter(
        x=x_star[:, 0], y=x_star[:, 1], mode="markers", name="global minimum x*",
        marker=dict(symbol="star", size=17, color=PAPER, line=dict(color=INK, width=1.6)),
        hovertemplate="global minimum x*<extra></extra>",
    )


def player_controls(frame_names, prefix="Generation "):
    """Play button and generation slider in the cabinet's palette."""
    def step(name):
        return dict(method="animate", label=name,
                    args=[[name], dict(mode="immediate", frame=dict(duration=0, redraw=False), transition=dict(duration=0))])

    updatemenus = [dict(
        type="buttons", direction="left", x=0, y=-0.34, xanchor="left", yanchor="top", showactive=False,
        pad=dict(r=10, t=0), bgcolor=CABINET, bordercolor=CABINET, borderwidth=1,
        font=dict(family=SANS, size=13, color="#FFFFFF"),
        buttons=[
            dict(label="  Play generations  ", method="animate",
                 args=[None, dict(frame=dict(duration=150, redraw=False), transition=dict(duration=120, easing="cubic-out"),
                                  fromcurrent=False, mode="immediate")]),
            dict(label="  Pause  ", method="animate",
                 args=[[None], dict(frame=dict(duration=0, redraw=False), transition=dict(duration=0), mode="immediate")]),
        ],
    )]
    sliders = [dict(
        active=len(frame_names) - 1, x=0, len=1, y=-0.17, yanchor="top", pad=dict(t=0, b=0),
        bgcolor=TRAY, activebgcolor=CABINET, bordercolor=HAIRLINE, borderwidth=1, tickcolor="rgba(0,0,0,0)", ticklen=0,
        # the readout above the rail names the generation, so per-step tick labels are hidden
        font=dict(family=MONO, size=1, color="rgba(0,0,0,0)"),
        currentvalue=dict(prefix=prefix, font=dict(family=MONO, size=12, color=INK), xanchor="right"),
        steps=[step(n) for n in frame_names],
    )]
    return updatemenus, sliders


def best_tag(x, y, f, f_star):
    value = f"<span style='font-family:{MONO}'>{fmt_error(f - f_star)}</span>"
    return dict(x=x, y=y, xref="x", yref="y", text=f"best: error {value}", showarrow=True,
                arrowhead=0, arrowwidth=1.2, arrowcolor=INK, ax=46, ay=-34, bgcolor=PAPER, bordercolor=ELITE,
                borderwidth=1.5, borderpad=4, font=dict(family=SANS, size=12, color=INK))


def population_figure(key, bundle, algo):
    """2-D landscape with the population pinned on it, one frame per kept generation."""
    result, frames = bundle["result"], bundle["frames"]
    color = ALGO_COLORS[algo]
    lower, upper = FUNCTIONS[key].bounds(2)

    def pins(fr):
        pop = fr[2]
        return [
            go.Scatter(x=pop[:, 0], y=pop[:, 1], mode="markers", name=f"{algo} population",
                       marker=dict(size=9, color=color, line=dict(color=PAPER, width=1.3)),
                       hovertemplate="x₁ %{x:.4g}<br>x₂ %{y:.4g}<extra>individual</extra>"),
            go.Scatter(x=[fr[3][0]], y=[fr[3][1]], mode="markers", name="best so far",
                       marker=dict(size=15, color=ELITE, line=dict(color=INK, width=1.6)),
                       hovertemplate="best so far<br>x₁ %{x:.6g}<br>x₂ %{y:.6g}<extra></extra>"),
        ]

    names = [f"{fr[0]:,}" for fr in frames]
    fig = go.Figure(data=[landscape_trace(key), optimum_trace(key, 2), *pins(frames[-1])])
    fig.frames = [
        go.Frame(name=n, data=pins(fr), traces=[2, 3], layout=dict(annotations=[best_tag(fr[3][0], fr[3][1], fr[4], result.f_star)]))
        for n, fr in zip(names, frames)
    ]
    menus, sliders = player_controls(names)
    fig.update_layout(**base_layout(
        455, margin=dict(l=58, r=14, t=14, b=146), updatemenus=menus, sliders=sliders,
        annotations=[best_tag(frames[-1][3][0], frames[-1][3][1], frames[-1][4], result.f_star)],
        legend=dict(orientation="h", x=0, y=1.0, yanchor="bottom", bgcolor="rgba(0,0,0,0)", font=dict(size=12)),
    ))
    fig.update_xaxes(range=[lower[0], upper[0]], title_text="x₁", title_standoff=4, showgrid=False)
    fig.update_yaxes(range=[lower[1], upper[1]], title_text="x₂", title_standoff=4, showgrid=False)
    return fig


def parallel_figure(key, dim, bundle, algo):
    """For d > 2: each individual as one line across its d coordinates."""
    result, frames = bundle["result"], bundle["frames"]
    lower, upper = FUNCTIONS[key].bounds(dim)
    span = upper - lower
    axis_x = np.arange(1, dim + 1)
    color = ALGO_COLORS[algo]

    def lines(pop):
        norm = (pop - lower) / span
        xs = np.concatenate([np.append(axis_x, np.nan) for _ in norm])
        ys = np.concatenate([np.append(row, np.nan) for row in norm])
        return xs, ys

    def traces(fr):
        xs, ys = lines(fr[2])
        best = (fr[3] - lower) / span
        return [
            go.Scatter(x=xs, y=ys, mode="lines", name=f"{algo} population", line=dict(color=color, width=1), opacity=0.28,
                       hoverinfo="skip"),
            go.Scatter(x=axis_x, y=best, mode="lines+markers", name="best so far", line=dict(color=ELITE, width=3),
                       marker=dict(size=7, color=ELITE, line=dict(color=INK, width=1.2)),
                       hovertemplate="x%{x}: %{customdata:.5g}<extra>best so far</extra>", customdata=fr[3]),
        ]

    x_star = FUNCTIONS[key].x_star(dim)
    star = [go.Scatter(x=axis_x, y=(x_star[0] - lower) / span, mode="lines", name="global minimum x*",
                       line=dict(color=INK, width=1.4, dash="dot"), hoverinfo="skip")] if x_star is not None else []
    names = [f"{fr[0]:,}" for fr in frames]
    fig = go.Figure(data=[*star, *traces(frames[-1])])
    offset = len(star)
    fig.frames = [go.Frame(name=n, data=traces(fr), traces=[offset, offset + 1]) for n, fr in zip(names, frames)]
    menus, sliders = player_controls(names)
    fig.update_layout(**base_layout(455, margin=dict(l=62, r=14, t=14, b=146), updatemenus=menus, sliders=sliders))
    fig.update_xaxes(title_text="variable i", title_standoff=4, tickmode="linear" if dim <= 12 else "auto", dtick=1 if dim <= 12 else None, showgrid=False)
    fig.update_yaxes(title_text="position in domain (0 = lower bound, 1 = upper)", range=[-0.03, 1.03])
    return fig


def success_line(fig):
    """Dashed line at the success threshold on a log-scaled error axis.
    Plotly places annotations on a log axis in log10 units, shapes in data units."""
    fig.add_hline(y=SUCCESS_ERROR, line=dict(color=INK_DIM, width=1, dash="dash"))
    fig.add_annotation(x=1, xref="paper", y=np.log10(SUCCESS_ERROR), yref="y", text="success 1e-4", showarrow=False,
                       xanchor="right", yanchor="bottom", font=dict(family=MONO, size=10, color=INK_DIM))


def fmt_p(p):
    return f"{p:.2g}" if p >= 1e-3 else f"{p:.1e}"


def convergence_figure(runs, height=170, log=True):
    """Best error against evaluations. ``runs`` maps a label to (RunResult, colour)."""
    fig = go.Figure()
    for label, (result, color) in runs.items():
        h = result.history
        err = np.maximum(np.array(h["best"]) - result.f_star, ERROR_FLOOR)
        fig.add_trace(go.Scatter(x=h["evals"], y=err, mode="lines", name=f"{label} best", line=dict(color=color, width=2.4, shape="hv"),
                                 hovertemplate="%{x:,} evaluations<br>error %{y:.3g}<extra>" + label + "</extra>"))
        mean = np.maximum(np.array(h["pop_mean"]) - result.f_star, ERROR_FLOOR)
        fig.add_trace(go.Scatter(x=h["evals"], y=mean, mode="lines", name=f"{label} population mean", line=dict(color=color, width=1),
                                 opacity=0.45, hovertemplate="%{x:,} evaluations<br>mean error %{y:.3g}<extra>" + label + "</extra>"))
    success_line(fig)
    fig.update_layout(**base_layout(height, margin=dict(l=62, r=18, t=30, b=44)))
    fig.update_xaxes(title_text="function evaluations", tickformat="~s")
    fig.update_yaxes(title_text="error f − f*", type="log" if log else "linear", exponentformat="e")
    return fig


# --------------------------------------------------------- signature parts
def num(value):
    """A number set in the tabular monospace face."""
    return f"<span class='num'>{esc(value)}</span>"


def accession_label(key, dim, algo, seed, bundle):
    """The best specimen's typed label: words in Archivo, numbers in JetBrains Mono."""
    r = bundle["result"]
    params = bundle["params"]
    error = r.error
    solved = error <= SUCCESS_ERROR
    found = r.evals_to_reach(error + 1e-12) or r.n_evals
    gen_found = int(np.searchsorted(r.history["evals"], found))
    status = f"<span class='chip {'ok' if solved else 'no'}'>{'solved' if solved else 'not solved'}</span>"
    rows = [
        ("f(x)", num(fmt_value(r.best_f))),
        ("known f*", num(fmt_value(r.f_star))),
        ("error f − f*", f"{num(fmt_error(error))} {status}"),
        ("best x", num(fmt_vector(r.best_x))),
        ("found at", f"evaluation {num(f'{found:,}')}, generation {num(f'{gen_found:,}')}"),
        ("budget used", f"{num(f'{r.n_evals:,}')} of {num(f'{r.max_evals:,}')} evaluations"),
        ("generations", num(f"{r.generations:,}")),
    ]
    if algo == "MA":
        ls = LS_NAMES[params.get("local_search", "hooke_jeeves")]
        share = f"{r.stats['ls_share']:.0%}"
        rows.append(("local search", f"{num(share)} of evaluations, {esc(ls)}"))
    rows.append(("time", f"{num(f'{r.runtime:.2f}')} s"))
    body = "".join(f"<dt>{esc(k)}</dt><dd>{v}</dd>" for k, v in rows)
    st.html(
        f"<div class='acc'><div class='acc-head'><h3><span class='pin' style='--c:{ELITE}'></span>Best specimen</h3>"
        f"<span class='acc-no num'>{algo}·s{seed}·g{r.generations}</span></div>"
        f"<div class='meta'>{esc(ALGO_NAMES[algo])}, seed {num(seed)}. Solved means error ≤ {num('1e-4')}; "
        f"below {num('1e-8')} counts as {num(0)}.</div>"
        f"<dl>{body}</dl></div>"
    )


def algo_cell(algo, label=None):
    return f"<span class='who'><span class='pin' style='--c:{ALGO_COLORS[algo]}'></span>{esc(label or algo)}</span>"


SIGN_CHIPS = {"+": "<span class='chip ok'>better</span>", "=": "<span class='chip tie'>tie</span>",
              "-": "<span class='chip no'>worse</span>"}


def rate_cell(rate, algo):
    return (f"<span class='bar' style='--c:{ALGO_COLORS[algo]}'><i style='width:{rate:.0%}'></i></span>"
            f"{num(f'{rate:.0%}')}")


def table(headers, rows, right=()):
    """An in-world table. ``rows`` hold ready HTML; columns in ``right`` align right."""
    cls = lambda i: " class='r'" if i in right else ""
    head = "".join(f"<th{cls(i)}>{h}</th>" for i, h in enumerate(headers))
    body = "".join("<tr>" + "".join(f"<td{cls(i)}>{c}</td>" for i, c in enumerate(r)) + "</tr>" for r in rows)
    st.html(f"<div class='tbl-wrap'><table class='tbl'><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>")


def drawer(rows):
    """One unit tray per seed. ``rows`` is a list of (algo, [(seed, error), ...])."""
    parts = []
    for algo, results in rows:
        c = ALGO_COLORS[algo]
        hits = sum(e <= SUCCESS_ERROR for _, e in results)
        trays = "".join(
            f"<div class='tray{' hit' if e <= SUCCESS_ERROR else ''}' style='--c:{c}'>"
            f"<span class='pin{'' if e <= SUCCESS_ERROR else ' hollow'}' style='--c:{c}'></span>"
            f"<div class='seed'>seed {s}</div><div class='val'>{fmt_error(e)}</div></div>"
            for s, e in results
        )
        parts.append(
            f"<div class='who'><span class='pin' style='--c:{c}'></span><div>{algo}<small><span class='num'>{hits}/{len(results)}</span> solved</small></div></div>"
            f"<div class='trays'>{trays}</div>"
        )
    st.html(f"<div class='drawer'>{''.join(parts)}</div>"
            "<p class='legend-line'>Each tray is one seed, showing its final error. A filled tray and a solid pin mean the run solved the problem (error ≤ 1e-4).</p>")


def empty_state(title, body):
    st.html(f"<div class='empty'><b>{esc(title)}</b><br>{body}</div>")


def sidebar_brand():
    st.sidebar.html("<div class='brand'><b>Project 27</b><span>Genetic and Memetic Algorithms on 12 benchmark functions</span></div>")
