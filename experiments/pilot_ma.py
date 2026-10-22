"""Pilot study used to choose the Memetic Algorithm's local-search defaults.

    python -m experiments.pilot_ma --round 1
    python -m experiments.pilot_ma --round 2

Round 1: one budget for every local-search call. Grid: ls_rate (probability a
child is refined; the best is always refined) x evaluations per call.
Round 2: the best individual keeps a long budget (20 d); grid over ls_rate x a
separate, shorter budget for refined children.

Seeds 100-104 are used, so the choice cannot leak into the main experiments
(seeds 0-29). Each cell is the mean log10(error) over the 5 seeds; configs are
ranked per problem and the ranks averaged. Tables go to experiments/results/pilot/.
"""
from __future__ import annotations

import argparse
import itertools
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from evoopt import GeneticAlgorithm, MemeticAlgorithm, Problem
from experiments import WORKERS

OUT = Path(__file__).resolve().parent / "results" / "pilot"
PROBLEMS = [
    ("rosenbrock", 10), ("rosenbrock", 30), ("griewank", 10), ("zakharov", 30), ("ackley", 30),
    ("rastrigin", 30), ("schwefel", 10), ("styblinski_tang", 10), ("michalewicz", 10), ("eggholder", 2),
]
SEEDS = range(100, 105)


def round_configs(n):
    """(label, MA parameters as multiples of d) for each config; None = plain GA."""
    configs = [("GA", None)]
    if n == 1:
        for rate, per_dim in itertools.product((0.0, 0.01, 0.05, 0.1), (5, 10, 20)):
            configs.append((f"rate={rate:<4} evals={per_dim:>2}d", dict(ls_rate=rate, best=per_dim, child=per_dim)))
    else:
        configs.append(("best only, 20d", dict(ls_rate=0.0, best=20, child=5)))
        for rate, child in itertools.product((0.02, 0.05, 0.1), (2, 5)):
            configs.append((f"20d + rate={rate:<4} child={child}d", dict(ls_rate=rate, best=20, child=child)))
    return configs


def run(job):
    (key, d), (_, params), seed = job
    if params is None:
        algo = GeneticAlgorithm()
    else:
        algo = MemeticAlgorithm(
            ls_rate=params["ls_rate"], ls_best_evals=params["best"] * d, ls_child_evals=params["child"] * d
        )
    r = algo.run(Problem(key, d), seed=seed)
    return np.log10(max(r.error, 1e-16)), r.stats.get("ls_share", 0.0)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--round", type=int, choices=(1, 2), default=2)
    args = parser.parse_args(argv)

    configs = round_configs(args.round)
    jobs = list(itertools.product(PROBLEMS, configs, SEEDS))
    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        out = list(pool.map(run, jobs, chunksize=4))

    cells, shares = {}, {}
    for (problem, (label, _), _), (log_err, share) in zip(jobs, out):
        cells.setdefault((label, problem), []).append(log_err)
        shares.setdefault(label, []).append(share)
    labels = [label for label, _ in configs]
    table = np.array([[np.mean(cells[(label, p)]) for p in PROBLEMS] for label in labels])
    ranks = np.argsort(np.argsort(table, axis=0), axis=0) + 1

    width = max(len(label) for label in labels) + 2
    lines = [f"{'config':{width}s}" + "".join(f"{k[:7] + str(d):>11s}" for k, d in PROBLEMS) + f"{'LS share':>9s}{'avg rank':>9s}"]
    for i, label in enumerate(labels):
        row = "".join(f"{v:>11.2f}" for v in table[i])
        lines.append(f"{label:{width}s}{row}{np.mean(shares[label]):>8.0%}{ranks[i].mean():>9.2f}")
    lines.append("\ncells: mean log10(error) over seeds 100-104 (lower is better; -16 = machine precision)")
    text = "\n".join(lines)
    print(text)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"round{args.round}.txt").write_text(text + "\n")


if __name__ == "__main__":
    main()
