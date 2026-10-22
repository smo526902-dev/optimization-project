"""Run one algorithm on one benchmark function from the command line.

    python -m experiments.run_one --algo ga --func rastrigin --dim 10
    python -m experiments.run_one --algo ga --func ackley --dim 10 --runs 10
    python -m experiments.run_one --algo ga --func sphere --dim 2 --set selection=roulette pop_size=80
    python -m experiments.run_one --algo ga --func rosenbrock --dim 10 --runs 5 --plot conv.png

A single run prints the convergence generation by generation; several runs
(seeds seed, seed+1, ...) print one row per run and summary statistics.
"""
from __future__ import annotations

import argparse

import numpy as np

from evoopt import ALGORITHMS, FUNCTIONS, Problem

SUCCESS_ERROR = 1e-4


def parse_value(text):
    lowered = text.lower()
    if lowered == "none":
        return None
    if lowered in ("true", "false"):
        return lowered == "true"
    for cast in (int, float):
        try:
            return cast(text)
        except ValueError:
            pass
    return text


def parse_params(pairs):
    params = {}
    for pair in pairs:
        key, sep, value = pair.partition("=")
        if not sep:
            raise SystemExit(f"--set expects KEY=VALUE, got {pair!r}")
        params[key] = parse_value(value)
    return params


def fmt_x(x, limit=6):
    shown = ", ".join(f"{v:.6g}" for v in x[:limit])
    return f"[{shown}{', ...' if len(x) > limit else ''}]"


def print_progress(result, rows=12):
    h = result.history
    n = len(h["generation"])
    picks = sorted(set(np.linspace(0, n - 1, rows).astype(int)))
    print(f"{'gen':>6} {'evals':>9} {'best f':>14} {'error':>11} {'pop mean':>14} {'diversity':>10}")
    for i in picks:
        print(
            f"{h['generation'][i]:>6} {h['evals'][i]:>9} {h['best'][i]:>14.8g} "
            f"{h['best'][i] - result.f_star:>11.3e} {h['pop_mean'][i]:>14.6g} {h['diversity'][i]:>10.4f}"
        )
    print()
    print(f"best x  = {fmt_x(result.best_x)}")
    x_star = FUNCTIONS[result.function].x_star(result.dim)
    if x_star is not None:
        print(f"known x*= {fmt_x(x_star[0])}")
    print(f"best f  = {result.best_f:.10g}   (f* = {result.f_star:.10g})")
    print(f"error   = {result.error:.3e}   evals = {result.n_evals}   time = {result.runtime:.2f}s")
    if result.stats.get("ls_calls"):
        print_local_search([result])


def print_local_search(results):
    calls = sum(r.stats["ls_calls"] for r in results)
    improved = sum(r.stats["ls_improved"] for r in results)
    share = np.mean([r.stats["ls_share"] for r in results])
    print(
        f"local search: {calls / len(results):.0f} calls per run, {improved / calls:.0%} improved, "
        f"{share:.0%} of the evaluation budget"
    )


def print_runs(results):
    print(f"{'seed':>6} {'best f':>16} {'error':>11} {'evals to 1e-4':>14} {'time':>7}")
    for r in results:
        hit = r.evals_to_reach(SUCCESS_ERROR)
        print(f"{r.seed:>6} {r.best_f:>16.10g} {r.error:>11.3e} {hit if hit else '-':>14} {r.runtime:>6.2f}s")
    errors = np.array([r.error for r in results])
    print()
    print(
        f"error: mean {errors.mean():.3e} | median {np.median(errors):.3e} | std {errors.std():.3e} "
        f"| best {errors.min():.3e} | worst {errors.max():.3e}"
    )
    print(f"success (error <= {SUCCESS_ERROR:g}): {np.sum(errors <= SUCCESS_ERROR)}/{len(errors)}")
    if results[0].stats.get("ls_calls"):
        print_local_search(results)


def plot_convergence(results, path):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    r0 = results[0]
    evals = np.linspace(1, r0.max_evals, 400)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for r in results:
        # errors are clamped at 1e-16 so a perfect hit still shows on a log axis
        ax.step(evals, np.maximum(r.error_at(evals), 1e-16), where="post", alpha=0.7, label=f"seed {r.seed}")
    ax.set_yscale("log")
    ax.set_xlabel("function evaluations")
    ax.set_ylabel("best error  f - f*")
    ax.set_title(f"{r0.algorithm} on {FUNCTIONS[r0.function].name}, d = {r0.dim}")
    ax.grid(True, which="both", alpha=0.3)
    if len(results) <= 10:
        ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=130, metadata={"impeccable:prompt": "Drawn by experiments/run_one.py --plot with matplotlib; no image model involved."})
    plt.close(fig)
    print(f"wrote {path}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--algo", default="ga", choices=sorted(ALGORITHMS))
    parser.add_argument("--func", default="rastrigin", choices=list(FUNCTIONS))
    parser.add_argument("--dim", type=int, default=2)
    parser.add_argument("--evals", type=int, default=None, help="evaluation budget (default 10000 * dim)")
    parser.add_argument("--seed", type=int, default=1, help="seed of the first run")
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--set", nargs="*", default=[], metavar="KEY=VALUE", help="algorithm parameters")
    parser.add_argument("--plot", metavar="PNG", help="save a convergence plot")
    args = parser.parse_args(argv)

    algorithm = ALGORITHMS[args.algo](**parse_params(args.set))
    fn = FUNCTIONS[args.func]
    print(f"{algorithm.name} on {fn.name} ({fn.category}), d = {args.dim}, {args.runs} run(s)\n")

    results = [
        algorithm.run(Problem(fn, args.dim, args.evals), seed=args.seed + i) for i in range(args.runs)
    ]
    if args.runs == 1:
        print_progress(results[0])
    else:
        print_runs(results)
    if args.plot:
        plot_convergence(results, args.plot)


if __name__ == "__main__":
    main()
