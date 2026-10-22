"""Explore the 12 benchmark landscapes in 2-D."""
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from app_pages import ui
from evoopt import CATEGORIES, FUNCTIONS

with st.sidebar:
    key, _ = ui.pick_function("explore", default="rastrigin", allow_dim=False)

fn = FUNCTIONS[key]
st.title(fn.name)
st.html(f"<p class='lede'>{ui.esc(fn.description)}</p>")


def surface_figure(key):
    xs, ys, Z, ranks = ui.landscape_grid(key)
    x_star = FUNCTIONS[key].x_star(2)
    fig = go.Figure([
        go.Surface(x=xs, y=ys, z=Z, surfacecolor=ranks, colorscale=ui.TRAY_SCALE, showscale=False,
                   contours=dict(z=dict(show=False)), lighting=dict(ambient=0.75, diffuse=0.6, specular=0.05),
                   hovertemplate="x₁ %{x:.4g}<br>x₂ %{y:.4g}<br>f %{z:.5g}<extra></extra>"),
        go.Scatter3d(x=x_star[:, 0], y=x_star[:, 1], z=FUNCTIONS[key](x_star), mode="markers", name="global minimum",
                     marker=dict(size=6, color=ui.ELITE, line=dict(color=ui.INK, width=2)),
                     hovertemplate="global minimum<br>f* %{z:.6g}<extra></extra>"),
    ])
    axis = dict(backgroundcolor=ui.PAPER, gridcolor=ui.GRID, showbackground=True, zerolinecolor=ui.HAIRLINE,
                tickfont=dict(family=ui.MONO, size=10, color=ui.INK_DIM), title_font=dict(size=12, color=ui.INK_DIM))
    fig.update_layout(**ui.base_layout(460, margin=dict(l=0, r=0, t=0, b=0), showlegend=False),
                      scene=dict(xaxis=dict(axis, title="x₁"), yaxis=dict(axis, title="x₂"), zaxis=dict(axis, title="f"),
                                 camera=dict(eye=dict(x=1.55, y=-1.45, z=0.95)), aspectmode="manual",
                                 aspectratio=dict(x=1, y=1, z=0.62)))
    return fig


def contour_figure(key):
    lower, upper = FUNCTIONS[key].bounds(2)
    fig = go.Figure([ui.landscape_trace(key), ui.optimum_trace(key, 2)])
    fig.update_layout(**ui.base_layout(460, margin=dict(l=58, r=14, t=30, b=48)))
    fig.update_xaxes(range=[lower[0], upper[0]], title_text="x₁", showgrid=False)
    fig.update_yaxes(range=[lower[1], upper[1]], title_text="x₂", showgrid=False)
    return fig


left, right = st.columns(2, gap="medium")
with left:
    ui.show(surface_figure(key), key=f"surf_{key}")
with right:
    ui.show(contour_figure(key), key=f"cont_{key}")
st.caption("Colour follows the rank of f, so shallow ripples and deep basins both stay visible. Darker green is lower.")

lower, upper = fn.bounds(2)
x_star = fn.x_star(2)
facts, formula = st.columns([2, 3], gap="large")
with facts:
    n = ui.num
    rows = [
        ("Category", ui.esc(fn.category.lower())),
        ("Domain (2-D)", f"x₁ in {n(f'[{lower[0]:g}, {upper[0]:g}]')}, x₂ in {n(f'[{lower[1]:g}, {upper[1]:g}]')}"),
        ("Dimensions", f"any d ≥ {n(2)}" if fn.scalable else ", ".join(n(d) for d in fn.dims)),
        ("Global minimum f*", f"{n(f'{fn.f_star(2):.10g}')} at d = {n(2)}"
         + (f"; {n(f'{fn.f_opt:.6g}')} × d in general" if fn.f_opt_per_dim else "")),
        ("Minimiser x*", "; ".join(n(ui.fmt_vector(x)) for x in x_star)),
    ]
    st.html("<div class='acc'><dl>" + "".join(f"<dt>{ui.esc(k)}</dt><dd>{v}</dd>" for k, v in rows) + "</dl></div>")
with formula:
    st.latex(fn.formula)
    st.markdown(f"Definition, domain and optimum follow the [SFU Virtual Library]({fn.url}).")


@st.cache_data(show_spinner=False)
def overview_figure():
    keys = [k for c in CATEGORIES for k, f in FUNCTIONS.items() if f.category == c]
    fig = make_subplots(rows=3, cols=4, subplot_titles=[FUNCTIONS[k].name for k in keys],
                        horizontal_spacing=0.035, vertical_spacing=0.09)
    for i, k in enumerate(keys):
        xs, ys, Z, ranks = ui.landscape_grid(k, resolution=90)
        r, c = divmod(i, 4)
        fig.add_trace(go.Heatmap(x=xs, y=ys, z=ranks, colorscale=ui.TRAY_SCALE, showscale=False, hoverinfo="skip"), r + 1, c + 1)
        x_star = FUNCTIONS[k].x_star(2)
        fig.add_trace(go.Scatter(x=x_star[:, 0], y=x_star[:, 1], mode="markers", hoverinfo="skip",
                                 marker=dict(symbol="star", size=10, color=ui.PAPER, line=dict(color=ui.INK, width=1.2))), r + 1, c + 1)
    fig.update_layout(**ui.base_layout(640, margin=dict(l=10, r=10, t=34, b=10), showlegend=False))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    fig.update_annotations(font=dict(family=ui.SANS, size=12, color=ui.INK))
    return fig


st.subheader("All 12 landscapes")
ui.show(overview_figure(), key="overview")
st.caption(
    "Grouped by the SFU categories: many local minima, bowl, plate, valley, steep ridges, other. The star marks each global minimum. "
    "Easom looks flat at this scale: its one well near (π, π) covers a tiny fraction of the domain, which is what makes it hard."
)
