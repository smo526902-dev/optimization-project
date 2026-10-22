"""Quick GA vs MA comparison on every benchmark, with default settings.

    python -m experiments.head_to_head --runs 10

Each algorithm gets the same evaluation budget (10,000 * d) and the same seeds.
The Wilcoxon rank-sum test (alpha = 0.05) decides whether the difference in
final error is significant; otherwise the row is a tie. As in the main
analysis, errors below 1e-8 are taken as 0 (CEC convention).
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor

import numpy as np
from scipy.stats import ranksums

from evoopt import FUNCTIONS, GeneticAlgorithm, MemeticAlgorithm, Problem
from experiments import WORKERS
from experiments.config import ERROR_FLOOR, SUCCESS_ERROR

ALPHA = 0.05


def problems():
    for key, fn in FUNCTIONS.items():
        for d in fn.dims or (10, 30):
            if not (key == "michalewicz" and d == 2):
                yield key, d


def run(job):
    algo, key, d, seed = job
    cls = GeneticAlgorithm if algo == "GA" else MemeticAlgorithm
    error = cls().run(Problem(key, d), seed=seed).error
    return 0.0 if error < ERROR_FLOOR else error


def compare(ga, ma):
    ga, ma = np.asarray(ga), np.asarray(ma)
    if np.allclose(ga, ma, rtol=0, atol=1e-14):
        return 1.0, "tie"
    p = ranksums(ga, ma).pvalue
    if p >= ALPHA:
        return p, "tie"
    return p, "MA" if np.median(ma) < np.median(ga) else "GA"


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=10)
    args = parser.parse_args(argv)

    probs = list(problems())
    jobs = [(a, k, d, s) for k, d in probs for a in ("GA", "MA") for s in range(args.runs)]
    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        errors = dict(zip(jobs, pool.map(run, jobs, chunksize=2)))

    print(f"{args.runs} runs each, budget 10,000*d, success = error <= {SUCCESS_ERROR:g}\n")
    print(f"{'function':16s} {'d':>3s} {'GA median':>11s} {'MA median':>11s} {'GA ok':>6s} {'MA ok':>6s} {'p-value':>9s}  winner")
    tally = {"MA": 0, "GA": 0, "tie": 0}
    for k, d in probs:
        ga = [errors[("GA", k, d, s)] for s in range(args.runs)]
        ma = [errors[("MA", k, d, s)] for s in range(args.runs)]
        p, winner = compare(ga, ma)
        tally[winner] += 1
        print(
            f"{FUNCTIONS[k].name:16s} {d:>3d} {np.median(ga):>11.2e} {np.median(ma):>11.2e} "
            f"{np.sum(np.array(ga) <= SUCCESS_ERROR):>4d}/{args.runs} {np.sum(np.array(ma) <= SUCCESS_ERROR):>3d}/{args.runs} "
            f"{p:>9.1e}  {winner}"
        )
    print(f"\nMA wins {tally['MA']}, GA wins {tally['GA']}, ties {tally['tie']}  (Wilcoxon rank-sum, alpha = {ALPHA})")


if __name__ == "__main__":
    main()
