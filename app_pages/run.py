"""Watch one GA or MA run: the population pinned on the landscape, generation by generation."""
import streamlit as st

from app_pages import ui
from evoopt import FUNCTIONS

AUTO_RUN_SECONDS = 3.0

with st.sidebar:
    key, dim = ui.pick_function("run", default="rastrigin", default_dim=2)
    algo = st.segmented_control(
        "Algorithm", ["GA", "MA"], default="MA", required=True, key="run_algo",
        help="GA: selection, crossover, mutation. MA: the same GA plus local search on the best and on some children.",
    )
    seed = st.number_input("Seed", min_value=0, max_value=9999, value=1, step=1, key="run_seed",
                           help="The same seed always gives the same run.")
    with st.expander("Budget and operators"):
        per_dim = ui.budget_picker("run", dim)
        params = ui.algorithm_settings("run", algo)
    seconds = ui.estimated_seconds(algo, per_dim * dim)
    clicked = st.button("Run", type="primary", icon=":material/play_arrow:", width="stretch", key="run_go")
    if seconds >= AUTO_RUN_SECONDS:
        st.caption(f"About {seconds:.0f} s per run, so this one starts when you press Run.")

fn = FUNCTIONS[key]
color = ui.ALGO_COLORS[algo]
st.title(f"{fn.name}, {dim}-D")
st.html(
    f"<p class='lede'>The {ui.ALGO_NAMES[algo]} searches for the global minimum with {per_dim * dim:,} function "
    f"evaluations. {'Each pin is one individual; the yellow pin is the best found so far.' if dim == 2 else 'Each line is one individual: its d coordinates, scaled to the domain.'}</p>"
)

cached = ui.is_cached("run", ui.run_settings(algo, key, dim, seed, per_dim, params))
if cached or clicked or seconds < AUTO_RUN_SECONDS:
    bar = None if cached else st.progress(0.0, text="Starting…")
    bundle = ui.run_cached(algo, key, dim, seed, per_dim, params, progress=bar)
    if bar is not None:
        bar.empty()

    left, right = st.columns([3, 2], gap="medium")
    with left:
        if dim == 2:
            ui.show(ui.population_figure(key, bundle, algo), key=f"pop_{key}_{algo}_{seed}")
        else:
            ui.show(ui.parallel_figure(key, dim, bundle, algo), key=f"par_{key}_{dim}_{algo}_{seed}")
    with right:
        ui.accession_label(key, dim, algo, seed, bundle)
        with st.expander("About this function"):
            st.latex(fn.formula)
            st.write(fn.description)
            st.markdown(f"Category: {fn.category.lower()} · [SFU library page]({fn.url})")

    ui.show(ui.convergence_figure({algo: (bundle["result"], color)}), key=f"conv_{key}_{dim}_{algo}_{seed}")
    st.caption("Convergence. Thick line: best error found so far. Thin line: the population's mean error. Errors below 1e-8 are drawn at 1e-8.")
else:
    ui.empty_state(
        "Ready to run",
        f"This setting takes about {seconds:.0f} seconds, so it waits for you. Press <b>Run</b> in the sidebar. "
        "Smaller budgets or d = 2 start on their own.",
    )
