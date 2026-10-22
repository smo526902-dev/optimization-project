"""Turn the raw experiment results into tables, statistics and figures.

    python -m experiments.analyze --mode full

Reads   experiments/results/<mode>/{main,ablations}/  (written by experiments.run)
Writes  experiments/results/<mode>/tables/            Markdown and CSV tables
        report/figures/results/                       figures (quick mode: experiments/results/quick/figures/)

Statistics: for each problem, two algorithms are compared with the Wilcoxon
rank-sum test on their final errors over the independent runs (alpha = 0.05).
"+" means the first algorithm is significantly better, "-" significantly
worse, "=" no significant difference. Because one test is made per problem,
the win/tie/loss totals are also given after a Holm-Bonferroni correction.

Error floor: following the CEC benchmark rules, every error below 1e-8 is taken
as 0 before anything is summarised, tested or plotted. Without it, a run that
stops at 4e-16 would rank as "worse" than one that stops at exactly 0, which is
floating-point rounding, not a real difference in what the algorithms found.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter
from scipy.stats import ranksums

from evoopt import FUNCTIONS, GeneticAlgorithm, MemeticAlgorithm, Problem
from experiments.config import ABLATION_PROBLEMS, ABLATIONS, ERROR_FLOOR, MAIN_ALGORITHMS, MODES, SUCCESS_ERROR
from experiments.run import RESULTS

ROOT = Path(__file__).resolve().parent.parent
ALPHA = 0.05
FLOOR = ERROR_FLOOR  # on log axes, an error of 0 is drawn at the floor
FLOOR_NOTE = f"errors below {ERROR_FLOOR:g} count as 0"
ALGOS = list(MAIN_ALGORITHMS)  # GA, MA, RS, DE
COLORS = {"GA": "tab:blue", "MA": "tab:red", "DE": "tab:green", "RS": "tab:gray"}
PAIRS = [("MA", "GA"), ("GA", "RS"), ("MA", "RS"), ("MA", "DE")]
GROUPS = {"2-D": (2,), "5-D and 10-D": (5, 10), "30-D": (30,)}
KILO = FuncFormatter(lambda v, _: f"{v / 1000:.0f}k")


# ---------------------------------------------------------------- helpers
def fmt(e):
    return "0" if e == 0 else f"{e:.2e}"


def name(key, d):
    return f"{FUNCTIONS[key].name} {d}-D"


def problem_order(df):
    """(function, dim) pairs in the order of evoopt.FUNCTIONS, then by dimension."""
    keys = list(FUNCTIONS)
    pairs = df[["function", "dim"]].drop_duplicates().itertuples(index=False)
    return sorted(pairs, key=lambda p: (keys.index(p[0]), p[1]))


def compare(a, b):
    """Wilcoxon rank-sum test of final errors. Returns (p, sign) where sign is
    '+' if a is significantly better (lower), '-' if worse, '=' otherwise."""
    a, b = np.asarray(a), np.asarray(b)
    if np.allclose(a, b, rtol=0, atol=1e-14):
        return 1.0, "="
    test = ranksums(a, b)
    if test.pvalue >= ALPHA:
        return test.pvalue, "="
    return test.pvalue, "+" if test.statistic < 0 else "-"


def holm(pvalues):
    """Holm-Bonferroni adjusted p-values."""
    p = np.asarray(pvalues, dtype=float)
    order = np.argsort(p)
    adjusted = np.empty_like(p)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(p) - rank) * p[i]))
        adjusted[i] = running
    return adjusted


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


PROVENANCE = "Drawn by experiments/analyze.py with matplotlib from the saved runs in experiments/results/; no image model involved."


def save(fig, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    # the PNG carries its own origin, so a copied figure still says where it came from
    fig.savefig(path, dpi=130, bbox_inches="tight", metadata={"impeccable:prompt": PROVENANCE, "Source": "experiments/analyze.py"})
    plt.close(fig)
    print(f"wrote {path.relative_to(ROOT)}")


def apply_error_floor(errors):
    """Errors below ERROR_FLOOR become exactly 0 (CEC convention)."""
    errors = np.asarray(errors, dtype=float)
    return np.where(errors < ERROR_FLOOR, 0.0, errors)


def load(mode, suite):
    """Raw results, with the error floor applied to final errors and curves."""
    folder = RESULTS / mode / suite
    runs = pd.read_csv(folder / "runs.csv")
    runs["error"] = apply_error_floor(runs["error"])
    curves = apply_error_floor(np.load(folder / "curves.npy"))
    return runs, curves


def grid_shape(n, cols=4):
    rows = int(np.ceil(n / cols))
    return rows, min(n, cols)


# ------------------------------------------------------------- main suite
def summarise(runs):
    g = runs.groupby(["function", "dim", "algorithm"])
    s = g["error"].agg(mean="mean", std="std", median="median", best="min", worst="max")
    s["success_rate"] = g["success"].mean()
    s["evals_to_success"] = g["evals_to_success"].mean()  # over the successful runs only
    s["runtime_s"] = g["runtime"].mean()
    s["ls_share"] = g["ls_share"].mean()
    return s.reset_index()


def summary_tables(runs, summary, tables):
    summary.to_csv(tables / "summary.csv", index=False)
    lines = [
        "# Final error over all runs",
        "",
        f"Each cell: mean ± standard deviation of the final error f(x_best) - f*, and in brackets "
        f"the success rate (error <= {SUCCESS_ERROR:g}). The lowest mean in each row is in bold. "
        f"Following the CEC convention, {FLOOR_NOTE}.",
        "",
    ]
    for group, dims in GROUPS.items():
        lines += [f"## {group}", "", "| Function | d | " + " | ".join(ALGOS) + " |", "|---|---|" + "---|" * len(ALGOS)]
        for key, d in problem_order(runs):
            if d not in dims:
                continue
            rows = summary[(summary.function == key) & (summary.dim == d)].set_index("algorithm")
            best = rows["mean"].min()
            cells = []
            for a in ALGOS:
                r = rows.loc[a]
                cell = f"{fmt(r['mean'])} ± {fmt(r['std'])} ({r['success_rate']:.0%})"
                cells.append(f"**{cell}**" if r["mean"] == best else cell)
            lines.append(f"| {FUNCTIONS[key].name} | {d} | " + " | ".join(cells) + " |")
        lines.append("")

    ma = summary[summary.algorithm == "MA"]
    lines += [
        "## Cost",
        "",
        "Mean runtime per run (seconds) and, for the MA, the share of the evaluation budget spent in local search.",
        "",
        "| Function | d | " + " | ".join(f"{a} time" for a in ALGOS) + " | MA local-search share |",
        "|---|---|" + "---|" * (len(ALGOS) + 1),
    ]
    for key, d in problem_order(runs):
        rows = summary[(summary.function == key) & (summary.dim == d)].set_index("algorithm")
        share = ma[(ma.function == key) & (ma.dim == d)]["ls_share"].iloc[0]
        lines.append(
            f"| {FUNCTIONS[key].name} | {d} | " + " | ".join(f"{rows.loc[a, 'runtime_s']:.2f}" for a in ALGOS) + f" | {share:.0%} |"
        )
    write(tables / "summary.md", "\n".join(lines) + "\n")


def statistics_tables(runs, tables):
    problems = problem_order(runs)
    records = []
    for key, d in problems:
        errors = {a: runs[(runs.function == key) & (runs.dim == d) & (runs.algorithm == a)]["error"].to_numpy() for a in ALGOS}
        rec = {"function": key, "dim": d}
        for a, b in PAIRS:
            p, sign = compare(errors[a], errors[b])
            rec[f"{a} vs {b} p"] = p
            rec[f"{a} vs {b}"] = sign
        records.append(rec)
    stats = pd.DataFrame(records)
    for a, b in PAIRS:
        adjusted = holm(stats[f"{a} vs {b} p"])
        stats[f"{a} vs {b} (Holm)"] = np.where(adjusted < ALPHA, stats[f"{a} vs {b}"], "=")
    stats.to_csv(tables / "statistics.csv", index=False)

    lines = [
        "# Pairwise comparisons (Wilcoxon rank-sum test, alpha = 0.05)",
        "",
        '"+": the first algorithm has significantly lower final errors; "-": significantly higher; "=": no significant difference. '
        f"Following the CEC convention, {FLOOR_NOTE} before testing.",
        "",
        "| Function | d | " + " | ".join(f"{a} vs {b}" for a, b in PAIRS) + " |",
        "|---|---|" + "---|" * len(PAIRS),
    ]
    for rec in records:
        cells = [f"{rec[f'{a} vs {b}']} (p = {rec[f'{a} vs {b} p']:.1e})" for a, b in PAIRS]
        lines.append(f"| {FUNCTIONS[rec['function']].name} | {rec['dim']} | " + " | ".join(cells) + " |")

    def tally(column):
        counts = stats[column].value_counts()
        return f"{counts.get('+', 0)} / {counts.get('=', 0)} / {counts.get('-', 0)}"

    lines += [
        "",
        "## Totals (wins / ties / losses of the first algorithm)",
        "",
        "| Comparison | per problem | after Holm correction |",
        "|---|---|---|",
    ]
    for a, b in PAIRS:
        lines.append(f"| {a} vs {b} | {tally(f'{a} vs {b}')} | {tally(f'{a} vs {b} (Holm)')} |")
    write(tables / "statistics.md", "\n".join(lines) + "\n")


def convergence_figures(runs, curves, figures):
    for group, dims in GROUPS.items():
        problems = [p for p in problem_order(runs) if p[1] in dims]
        rows, cols = grid_shape(len(problems))
        fig, axes = plt.subplots(rows, cols, figsize=(4.4 * cols, 3.4 * rows), squeeze=False)
        for ax, (key, d) in zip(axes.ravel(), problems):
            for a in ALGOS:
                mask = ((runs.function == key) & (runs.dim == d) & (runs.algorithm == a)).to_numpy()
                c = np.maximum(curves[mask], FLOOR)
                c[~np.isfinite(c)] = np.nan
                budget = runs.loc[mask, "max_evals"].iloc[0]
                x = np.linspace(budget / c.shape[1], budget, c.shape[1])
                q25, med, q75 = np.nanpercentile(c, [25, 50, 75], axis=0)
                ax.plot(x, med, color=COLORS[a], label=a, lw=1.6)
                ax.fill_between(x, q25, q75, color=COLORS[a], alpha=0.15)
            ax.set_yscale("log")
            ax.xaxis.set_major_formatter(KILO)
            ax.set_title(name(key, d), fontsize=10)
            ax.grid(True, which="major", alpha=0.3)
        for ax in axes.ravel()[len(problems):]:
            ax.axis("off")
        axes[0, 0].legend(fontsize=8)
        for ax in axes[:, 0]:
            ax.set_ylabel("best error f - f*")
        fig.supxlabel("function evaluations")
        fig.suptitle(f"Convergence, {group} problems: median and 25-75% band ({FLOOR_NOTE})", fontsize=13)
        fig.tight_layout()
        save(fig, figures / f"convergence_{dims[-1]}d.png")


def boxplot_figures(runs, figures):
    for group, dims in GROUPS.items():
        problems = [p for p in problem_order(runs) if p[1] in dims]
        rows, cols = grid_shape(len(problems))
        fig, axes = plt.subplots(rows, cols, figsize=(3.8 * cols, 3.2 * rows), squeeze=False)
        for ax, (key, d) in zip(axes.ravel(), problems):
            data = [np.maximum(runs[(runs.function == key) & (runs.dim == d) & (runs.algorithm == a)]["error"], FLOOR) for a in ALGOS]
            box = ax.boxplot(data, tick_labels=ALGOS, patch_artist=True, widths=0.6, medianprops={"color": "black"})
            for patch, a in zip(box["boxes"], ALGOS):
                patch.set_facecolor(COLORS[a])
                patch.set_alpha(0.45)
            ax.set_yscale("log")
            ax.axhline(SUCCESS_ERROR, color="black", lw=0.8, ls="--")
            ax.set_title(name(key, d), fontsize=10)
            ax.grid(True, axis="y", alpha=0.3)
        for ax in axes.ravel()[len(problems):]:
            ax.axis("off")
        for ax in axes[:, 0]:
            ax.set_ylabel("final error f - f*")
        fig.suptitle(
            f"Final error over all runs, {group} problems (dashed: success threshold {SUCCESS_ERROR:g}; {FLOOR_NOTE})",
            fontsize=13,
        )
        fig.tight_layout()
        save(fig, figures / f"boxplots_{dims[-1]}d.png")


def success_heatmap(summary, runs, figures):
    problems = problem_order(runs)
    rates = np.array(
        [[summary[(summary.function == k) & (summary.dim == d) & (summary.algorithm == a)]["success_rate"].iloc[0] for a in ALGOS] for k, d in problems]
    )
    fig, ax = plt.subplots(figsize=(5.2, 0.32 * len(problems) + 1.2))
    ax.imshow(rates, cmap="RdYlGn", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(ALGOS)), ALGOS)
    ax.set_yticks(range(len(problems)), [name(k, d) for k, d in problems], fontsize=8)
    ax.xaxis.tick_top()
    for i in range(len(problems)):
        for j in range(len(ALGOS)):
            ax.text(j, i, f"{rates[i, j]:.0%}", ha="center", va="center", fontsize=7)
    ax.set_title(f"Success rate (error <= {SUCCESS_ERROR:g})", pad=24)
    save(fig, figures / "success_rates.png")


# --------------------------------------------------------- ablation suite
def ablation_outputs(runs, tables, figures):
    lines = [
        "# Ablation studies",
        "",
        "Each study changes one design choice and keeps every other setting at its default. "
        "The first row of each table is the default configuration. Each cell: median final error "
        "(success rate). ▲ / ▼: significantly better / worse than the default (Wilcoxon rank-sum, alpha = 0.05). "
        f"Following the CEC convention, {FLOOR_NOTE}. In the mutation study the MA rows are also compared "
        "with the default GA (the first row).",
        "",
    ]
    problems = ABLATION_PROBLEMS
    for experiment, configs in ABLATIONS.items():
        labels = list(configs)
        sub = runs[runs.experiment == experiment]
        lines += [f"## {experiment.replace('_', ' ')}", "", "| Setting | " + " | ".join(name(k, d) for k, d in problems) + " |", "|---|" + "---|" * len(problems)]
        for i, label in enumerate(labels):
            cells = []
            for key, d in problems:
                e = sub[(sub.config == label) & (sub.function == key) & (sub.dim == d)]["error"].to_numpy()
                cell = f"{fmt(np.median(e))} ({np.mean(e <= SUCCESS_ERROR):.0%})"
                if i > 0:
                    base = sub[(sub.config == labels[0]) & (sub.function == key) & (sub.dim == d)]["error"].to_numpy()
                    sign = compare(e, base)[1]
                    cell += {"+": " ▲", "-": " ▼", "=": ""}[sign]
                cells.append(cell)
            lines.append(f"| {label}{' (default)' if i == 0 else ''} | " + " | ".join(cells) + " |")
        lines.append("")

        fig, axes = plt.subplots(1, len(problems), figsize=(3.6 * len(problems), 3.6), squeeze=False)
        for ax, (key, d) in zip(axes.ravel(), problems):
            data = [np.maximum(sub[(sub.config == lab) & (sub.function == key) & (sub.dim == d)]["error"], FLOOR) for lab in labels]
            box = ax.boxplot(data, tick_labels=labels, patch_artist=True, widths=0.6, medianprops={"color": "black"})
            for j, patch in enumerate(box["boxes"]):
                patch.set_facecolor("tab:orange" if j == 0 else "tab:purple")
                patch.set_alpha(0.4)
            ax.set_yscale("log")
            ax.axhline(SUCCESS_ERROR, color="black", lw=0.8, ls="--")
            ax.set_title(name(key, d), fontsize=10)
            ax.tick_params(axis="x", labelrotation=35, labelsize=8)
            ax.grid(True, axis="y", alpha=0.3)
        axes[0, 0].set_ylabel("final error f - f*")
        fig.suptitle(f"Ablation: {experiment.replace('_', ' ')} (orange = default; {FLOOR_NOTE})", fontsize=12)
        fig.tight_layout()
        save(fig, figures / f"ablation_{experiment}.png")
    write(tables / "ablations.md", "\n".join(lines))


# ------------------------------------------------------ population pictures
def population_snapshots(figures, key, fractions=(0.0, 0.02, 0.1, 0.3, 1.0), seed=0):
    """GA and MA populations on a 2-D landscape, after the same numbers of evaluations."""
    fn = FUNCTIONS[key]
    lower, upper = fn.bounds(2)
    xs, ys = np.linspace(lower[0], upper[0], 300), np.linspace(lower[1], upper[1], 300)
    X1, X2 = np.meshgrid(xs, ys)
    Z = fn(np.column_stack([X1.ravel(), X2.ravel()])).reshape(X1.shape)
    levels = np.unique(np.quantile(Z, np.linspace(0, 1, 30)))

    fig, axes = plt.subplots(2, len(fractions), figsize=(3.3 * len(fractions), 6.8))
    for row, cls in enumerate((GeneticAlgorithm, MemeticAlgorithm)):
        result = cls(record_population=True).run(Problem(key, 2), seed=seed)
        evals = np.array(result.history["evals"])
        for ax, frac in zip(axes[row], fractions):
            g = int(np.searchsorted(evals, frac * result.max_evals))
            g = min(g, len(evals) - 1)
            pop = result.snapshots[g]
            ax.contourf(X1, X2, Z, levels=levels, cmap="viridis", alpha=0.85)
            ax.scatter(pop[:, 0], pop[:, 1], s=9, c="white", edgecolors="black", linewidths=0.4)
            x_star = fn.x_star(2)
            ax.plot(x_star[:, 0], x_star[:, 1], "r*", ms=11, mec="white")
            ax.set_title(f"{cls.name}: {evals[g]:,} evals (gen {g})", fontsize=9)
            ax.set_xticks([])
            ax.set_yticks([])
    fig.suptitle(f"Population on {fn.name} (2-D): GA (top) vs MA (bottom), seed {seed}", fontsize=12)
    fig.tight_layout()
    save(fig, figures / f"population_{key}.png")


# ------------------------------------------------------------------- main
def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mode", choices=MODES, default="quick")
    args = parser.parse_args(argv)

    tables = RESULTS / args.mode / "tables"
    figures = ROOT / "report" / "figures" / "results" if args.mode == "full" else RESULTS / args.mode / "figures"
    tables.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)

    runs, curves = load(args.mode, "main")
    summary = summarise(runs)
    summary_tables(runs, summary, tables)
    statistics_tables(runs, tables)
    convergence_figures(runs, curves, figures)
    boxplot_figures(runs, figures)
    success_heatmap(summary, runs, figures)

    ablation_runs, _ = load(args.mode, "ablations")
    ablation_outputs(ablation_runs, tables, figures)

    for key in ("rastrigin", "eggholder"):
        population_snapshots(figures, key)


if __name__ == "__main__":
    main()
