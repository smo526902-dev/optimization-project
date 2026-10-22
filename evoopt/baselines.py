"""Baselines that put the GA and MA results in context.

RandomSearch
    Uniform random sampling with the same evaluation budget. Any algorithm
    worth using must beat it; the gap shows how much the search strategy adds.

ScipyDE
    SciPy's Differential Evolution (Storn & Price, 1997) with its default
    settings, run through the same budgeted Problem. It is an outside reference
    point from a widely used library, not part of the GA-vs-MA comparison.
"""
from __future__ import annotations

import time

import numpy as np
from scipy.optimize import differential_evolution

from .problem import Problem
from .results import RunResult


class RandomSearch:
    name = "RS"

    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size

    def run(self, problem: Problem, seed=None, callback=None) -> RunResult:
        rng = np.random.default_rng(seed)
        start = time.perf_counter()
        history = {"evals": [], "best": []}
        batches = 0
        while not problem.exhausted:
            problem.evaluate(problem.random_points(min(self.batch_size, problem.remaining), rng))
            batches += 1
            history["evals"].append(problem.n_evals)
            history["best"].append(problem.best_f)
        return RunResult.from_problem(
            problem,
            self.name,
            seed,
            generations=batches,
            runtime=time.perf_counter() - start,
            history=history,
            params={"batch_size": self.batch_size},
        )


class ScipyDE:
    name = "DE"

    def __init__(self, popsize: int = 15):
        self.popsize = popsize  # SciPy's multiplier: the population is popsize * d

    def run(self, problem: Problem, seed=None, callback=None) -> RunResult:
        start = time.perf_counter()
        history = {"evals": [], "best": []}

        def objective(X):  # vectorised: X has shape (d, S)
            return problem.evaluate(X.T)

        def stop(intermediate_result):  # called once per DE generation
            history["evals"].append(problem.n_evals)
            history["best"].append(problem.best_f)
            return problem.exhausted

        res = differential_evolution(
            objective,
            list(zip(problem.lower, problem.upper)),
            popsize=self.popsize,
            maxiter=10**7,  # the evaluation budget is what stops the run
            tol=0,
            atol=0,
            polish=False,
            vectorized=True,
            updating="deferred",
            callback=stop,
            rng=seed,
        )
        return RunResult.from_problem(
            problem,
            self.name,
            seed,
            generations=int(res.nit),
            runtime=time.perf_counter() - start,
            history=history,
            params={"popsize": self.popsize, "strategy": "best1bin"},
        )
