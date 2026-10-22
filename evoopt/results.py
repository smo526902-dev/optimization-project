"""The record every algorithm returns at the end of a run."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


def best_so_far(trace, evals):
    """Look up a best-so-far trace at the given evaluation counts.

    ``trace`` is a list of (evaluation number, best value) pairs, appended each
    time the best value improved. The result is a step function: for each entry
    of ``evals``, the best value found within that many evaluations (+inf if none).
    This is what lets convergence curves from different runs and different
    algorithms be averaged on one common x-axis of function evaluations.
    """
    evals = np.asarray(evals)
    if not trace:
        return np.full(evals.shape, np.inf)
    fe, fv = np.array(trace).T
    idx = np.searchsorted(fe, evals, side="right") - 1
    return np.where(idx >= 0, fv[np.maximum(idx, 0)], np.inf)


@dataclass
class RunResult:
    algorithm: str
    function: str
    dim: int
    seed: int | None
    best_x: np.ndarray
    best_f: float
    f_star: float
    n_evals: int
    max_evals: int
    generations: int
    runtime: float
    trace: list[tuple[int, float]]
    # Per-generation statistics: generation, evals, best (so far), pop_best,
    # pop_mean, diversity (mean per-gene std of the population / domain width).
    history: dict[str, list] = field(default_factory=dict)
    params: dict = field(default_factory=dict)
    # Every generation's population, kept only when asked (2-D animations).
    snapshots: list[np.ndarray] | None = None
    # Algorithm-specific counters, e.g. the MA's local-search usage.
    stats: dict = field(default_factory=dict)

    @classmethod
    def from_problem(cls, problem, algorithm, seed, generations, runtime, **extra):
        """Build a result from the state a finished run left in ``problem``."""
        return cls(
            algorithm=algorithm,
            function=problem.function.key,
            dim=problem.dim,
            seed=seed,
            best_x=problem.best_x.copy(),
            best_f=problem.best_f,
            f_star=problem.f_star,
            n_evals=problem.n_evals,
            max_evals=problem.max_evals,
            generations=generations,
            runtime=runtime,
            trace=list(problem.trace),
            **extra,
        )

    @property
    def error(self):
        """How far the best solution is above the global minimum: f - f*."""
        return self.best_f - self.f_star

    def best_at(self, evals):
        return best_so_far(self.trace, evals)

    def error_at(self, evals):
        return self.best_at(evals) - self.f_star

    def evals_to_reach(self, error):
        """Function evaluations needed to get within ``error`` of f*, or None."""
        for fe, f in self.trace:
            if f - self.f_star <= error:
                return fe
        return None

    def summary(self, success_error=1e-4):
        """One flat row for a results table."""
        return {
            "algorithm": self.algorithm,
            "function": self.function,
            "dim": self.dim,
            "seed": self.seed,
            "best_f": self.best_f,
            "error": self.error,
            "success": self.error <= success_error,
            "evals_to_success": self.evals_to_reach(success_error),
            "n_evals": self.n_evals,
            "generations": self.generations,
            "runtime": self.runtime,
        }
