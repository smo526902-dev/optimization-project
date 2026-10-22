"""Run the experiment suites in parallel and save the raw results.

    python -m experiments.run --mode quick              # smoke test, a minute or two
    python -m experiments.run --mode full               # both suites, 30 runs each
    python -m experiments.run --mode full --suite main  # one suite only

Results go to experiments/results/<mode>/<suite>/:
    runs.csv     one row per run: settings, final error, success, evaluations
                 needed to succeed, runtime, local-search share
    curves.npy   best error at 1%, 2%, ..., 100% of the budget, one row per
                 row of runs.csv (for convergence plots)

Then run ``python -m experiments.analyze --mode <mode>``.
"""
from __future__ import annotations

import argparse
import json
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

from evoopt import ALGORITHMS, EVALS_PER_DIM, Problem
from experiments import WORKERS
from experiments.config import (
    ABLATION_PROBLEMS,
    ABLATIONS,
    CURVE_POINTS,
    MAIN_ALGORITHMS,
    MODES,
    SUCCESS_ERROR,
    SUITES,
    main_problems,
)

RESULTS = Path(__file__).resolve().parent / "results"


def build_jobs(suite, mode):
    """Every run of a suite as a dict: what to label it and what to execute."""
    seeds, scale = MODES[mode]["seeds"], MODES[mode]["budget_scale"]
    if suite == "main":
        plan = [("main", name, algo, params, key, d) for key, d in main_problems() for name, (algo, params) in MAIN_ALGORITHMS.items()]
    else:
        plan = [
            (experiment, label, algo, params, key, d)
            for experiment, configs in ABLATIONS.items()
            for label, (algo, params) in configs.items()
            for key, d in ABLATION_PROBLEMS
        ]
    return [
        dict(
            experiment=experiment,
            config=label,
            algorithm=algo,
            params=params,
            function=key,
            dim=d,
            seed=seed,
            max_evals=int(EVALS_PER_DIM * d * scale),
        )
        for experiment, label, algo, params, key, d in plan
        for seed in seeds
    ]


def run_key(job):
    """Runs with identical settings are identical, so each is executed once.
    Settings are compared after defaults are filled in, so that, e.g., the GA
    with selection="tournament" and the default GA count as the same run."""
    cls = ALGORITHMS[job["algorithm"]]
    if hasattr(cls, "Config"):
        settings = asdict(cls(**job["params"]).config.resolved(job["dim"]))
    else:
        settings = job["params"]
    return (job["algorithm"], tuple(sorted(settings.items())), job["function"], job["dim"], job["seed"], job["max_evals"])


def execute(job):
    algorithm = ALGORITHMS[job["algorithm"]](**job["params"])
    result = algorithm.run(Problem(job["function"], job["dim"], job["max_evals"]), seed=job["seed"])
    grid = np.linspace(job["max_evals"] / CURVE_POINTS, job["max_evals"], CURVE_POINTS)
    row = result.summary(SUCCESS_ERROR)
    # errors a hair below 0 come from rounding in f* itself; report them as 0
    row["error"] = max(row["error"], 0.0)
    row["ls_share"] = result.stats.get("ls_share", 0.0)
    return row, np.maximum(result.error_at(grid), 0.0)


def run_suite(suite, mode):
    jobs = build_jobs(suite, mode)
    unique = {}
    for job in jobs:
        unique.setdefault(run_key(job), job)
    # start the expensive runs first so the workers finish together
    order = sorted(unique, key=lambda k: (k[3], k[0] in ("ma", "de")), reverse=True)
    print(f"[{suite}] {len(jobs)} runs ({len(unique)} distinct) on {WORKERS} workers")

    done, start, outputs = 0, time.perf_counter(), {}
    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(execute, unique[k]): k for k in order}
        for future in as_completed(futures):
            outputs[futures[future]] = future.result()
            done += 1
            if done % max(1, len(unique) // 20) == 0 or done == len(unique):
                print(f"  {done:>5}/{len(unique)} ({done / len(unique):4.0%})  {time.perf_counter() - start:6.0f}s", flush=True)

    rows, curves = [], []
    for job in jobs:
        row, curve = outputs[run_key(job)]
        rows.append({"experiment": job["experiment"], "config": job["config"], **row, "max_evals": job["max_evals"]})
        curves.append(curve)

    out = RESULTS / mode / suite
    out.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out / "runs.csv", index=False)
    np.save(out / "curves.npy", np.array(curves))
    (out / "meta.json").write_text(
        json.dumps(
            {
                "mode": mode,
                "seeds": list(MODES[mode]["seeds"]),
                "budget": f"{MODES[mode]['budget_scale'] * EVALS_PER_DIM:g} * d evaluations",
                "success_error": SUCCESS_ERROR,
                "curve_points": CURVE_POINTS,
                "runs": len(jobs),
                "wall_time_s": round(time.perf_counter() - start, 1),
            },
            indent=2,
        )
    )
    print(f"[{suite}] saved {out}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mode", choices=MODES, default="quick")
    parser.add_argument("--suite", choices=SUITES + ("all",), default="all")
    args = parser.parse_args(argv)
    for suite in SUITES if args.suite == "all" else (args.suite,):
        run_suite(suite, args.mode)


if __name__ == "__main__":
    main()
