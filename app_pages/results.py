"""Browse the saved 30-run experiment: the tables and figures written by experiments.analyze."""
import re

import pandas as pd
import streamlit as st

from app_pages import ui
from evoopt import FUNCTIONS

TABLES = ui.ROOT / "experiments" / "results" / "full" / "tables"
FIGURES = ui.ROOT / "report" / "figures" / "results"
ALGOS = ("GA", "MA", "DE", "RS")

st.title("Saved results")

if not (TABLES / "summary.csv").exists():
    ui.empty_state(
        "No saved results yet",
        "Run the full experiment, then the analysis, from the project folder:<br>"
        "<code>.venv\\Scripts\\python -m experiments.run --mode full</code><br>"
        "<code>.venv\\Scripts\\python -m experiments.analyze --mode full</code>",
    )
    st.stop()

st.html(
    "<p class='lede'>The full experiment: 30 problems, 4 algorithms, 30 seeds each, a budget of 10,000 × d evaluations, "
    "plus 8 ablation studies. Comparisons use the Wilcoxon rank-sum test at α = 0.05; errors below 1e-8 count as 0.</p>"
)

summary = pd.read_csv(TABLES / "summary.csv")
stats = pd.read_csv(TABLES / "statistics.csv")
order = list(FUNCTIONS)
stats = stats.assign(order=stats["function"].map(order.index)).sort_values(["order", "dim"])
summary = summary.assign(order=summary["function"].map(order.index)).sort_values(["order", "dim"])


def problem_name(key, d):
    return f"{ui.esc(FUNCTIONS[key].name)} {ui.num(f'{d}-D')}"


def p_cell(p):
    return "<span style='color:#4A5A52'>–</span>" if p >= 0.999 else ui.num(ui.fmt_p(p))


head, success, ablation, figures = st.tabs(["Head-to-head", "Success rates", "Ablations", "All figures"])

with head:
    rows = []
    for a, b in [("MA", "GA"), ("MA", "DE"), ("GA", "RS"), ("MA", "RS")]:
        raw, holm = stats[f"{a} vs {b}"], stats[f"{a} vs {b} (Holm)"]
        rows.append([
            f"{ui.algo_cell(a)}<span class='vs'>vs</span>{ui.algo_cell(b)}",
            ui.num((raw == "+").sum()), ui.num((raw == "=").sum()), ui.num((raw == "-").sum()),
            ui.num(f"{(holm == '+').sum()} / {(holm == '=').sum()} / {(holm == '-').sum()}"),
        ])
    ui.table(["Comparison", "Wins", "Ties", "Losses", "After Holm correction"], rows, right=(1, 2, 3, 4))
    st.caption("Wins, ties and losses of the first algorithm over the 30 problems. The Holm correction accounts for running one test per problem.")

    st.subheader("Per problem")
    ui.table(
        ["Problem", "MA vs GA", "p", "MA vs DE", "p"],
        [
            [problem_name(r["function"], r["dim"]), ui.SIGN_CHIPS[r["MA vs GA"]], p_cell(r["MA vs GA p"]),
             ui.SIGN_CHIPS[r["MA vs DE"]], p_cell(r["MA vs DE p"])]
            for r in stats.to_dict("records")
        ],
        right=(2, 4),
    )
    st.caption("better / worse: the MA's final errors are significantly lower / higher (Wilcoxon rank-sum, α = 0.05). "
               "A dash means the two samples were identical.")

with success:
    rows = []
    for (key, d), group in summary.groupby(["order", "dim"], sort=True):
        g = group.set_index("algorithm")
        fn_key = g["function"].iloc[0]
        rows.append([problem_name(fn_key, d)] + [
            f"{ui.rate_cell(g.loc[a, 'success_rate'], a)}<span class='sub'>median {ui.num(ui.fmt_error(g.loc[a, 'median']))}</span>"
            for a in ALGOS
        ])
    ui.table(["Problem"] + [ui.algo_cell(a) for a in ALGOS], rows)
    st.caption("Bar: share of the 30 runs that reached error ≤ 1e-4. Below it: the median final error.")

with ablation:
    text = (TABLES / "ablations.md").read_text(encoding="utf-8")
    sections = dict(re.findall(r"^## (.+?)\n(.*?)(?=^## |\Z)", text, flags=re.S | re.M))
    study = st.segmented_control("Study", list(sections), default=next(iter(sections)), required=True, key="ablation_study")
    lines = [ln for ln in sections[study].strip().splitlines() if ln.startswith("|")]
    header = [c.strip() for c in lines[0].strip("|").split("|")]

    def cell(text):
        text = text.strip()
        mark = ""
        if text.endswith("▲"):
            text, mark = text[:-1].strip(), " " + ui.SIGN_CHIPS["+"]
        elif text.endswith("▼"):
            text, mark = text[:-1].strip(), " " + ui.SIGN_CHIPS["-"]
        m = re.match(r"(\S+) \((\d+%)\)", text)
        if m:
            return f"{ui.num(m.group(1))} <span class='sub' style='display:inline'>({ui.num(m.group(2))})</span>{mark}"
        return ui.esc(text) + mark

    body = [[ui.esc(row[0].strip())] + [cell(c) for c in row[1:]]
            for row in ([c for c in ln.strip("|").split("|")] for ln in lines[2:])]
    ui.table([ui.esc(h) for h in header], body)
    st.caption("Each cell: median final error, with the success rate in brackets. The first row is the default setting; "
               "better / worse mark a significant difference from it (Wilcoxon rank-sum, α = 0.05).")
    image = FIGURES / f"ablation_{study.replace(' ', '_')}.png"
    if image.exists():
        st.image(str(image), width="stretch")
        st.caption(f"File: report/figures/results/{image.name}, drawn by experiments/analyze.py from the saved runs.")

with figures:
    names = {
        "success_rates.png": "Success rate, every problem and algorithm",
        "convergence_2d.png": "Convergence, 2-D problems",
        "convergence_10d.png": "Convergence, 5-D and 10-D problems",
        "convergence_30d.png": "Convergence, 30-D problems",
        "boxplots_2d.png": "Final errors, 2-D problems",
        "boxplots_10d.png": "Final errors, 5-D and 10-D problems",
        "boxplots_30d.png": "Final errors, 30-D problems",
        "population_rastrigin.png": "GA and MA populations on Rastrigin",
        "population_eggholder.png": "GA and MA populations on Eggholder",
    }
    available = [n for n in names if (FIGURES / n).exists()]
    pick = st.selectbox("Figure", available, format_func=names.get, key="figure_pick")
    st.image(str(FIGURES / pick), width="stretch")
    st.caption(f"File: report/figures/results/{pick}")
