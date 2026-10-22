"""An optimisation problem with a fixed function-evaluation budget.

Every algorithm in this project (GA, MA, random search, ...) only ever touches
the objective through ``Problem.evaluate``. That single entry point

* counts function evaluations (FEs),
* enforces the budget as a hard limit (points beyond it are not evaluated and
  get ``+inf``, so they can never be selected), and
* records the best solution seen so far, plus a trace of when it improved.

Because the local-search steps inside the Memetic Algorithm go through the same
counter as the GA's own evaluations, GA and MA are always compared on equal cost.
"""
from __future__ import annotations

import numpy as np

from .benchmarks import BenchmarkFunction, get_function
from .results import best_so_far

# CEC benchmark convention: a run may spend 10,000 * d function evaluations.
EVALS_PER_DIM = 10_000


class Problem:
    def __init__(self, function: BenchmarkFunction | str, dim: int, max_evals: int | None = None):
        if isinstance(function, str):
            function = get_function(function)
        self.function = function
        self.dim = dim
        self.lower, self.upper = function.bounds(dim)
        self.f_star = function.f_star(dim)
        self.max_evals = EVALS_PER_DIM * dim if max_evals is None else int(max_evals)
        self.n_evals = 0
        self.best_x = None
        self.best_f = np.inf
        # (evaluation number, best value so far), appended whenever the best improves
        self.trace: list[tuple[int, float]] = []

    def __repr__(self):
        return (
            f"Problem({self.function.name}, d={self.dim}, "
            f"evals={self.n_evals}/{self.max_evals}, best_error={self.best_error:.3g})"
        )

    # ----------------------------------------------------------------- budget
    @property
    def remaining(self):
        return self.max_evals - self.n_evals

    @property
    def exhausted(self):
        return self.n_evals >= self.max_evals

    # ------------------------------------------------------------- evaluation
    def evaluate(self, X):
        """Evaluate each row of X. Rows past the budget are skipped and get +inf."""
        X = np.atleast_2d(np.asarray(X, dtype=float))
        f = np.full(len(X), np.inf)
        n = min(len(X), self.remaining)
        if n > 0:
            f[:n] = self.function.func(X[:n])
            self._record(X[:n], f[:n])
            self.n_evals += n
        return f

    def evaluate_one(self, x):
        return float(self.evaluate(x)[0])

    def _record(self, X, f):
        i = int(np.argmin(f))
        if f[i] < self.best_f:
            self.best_f = float(f[i])
            self.best_x = X[i].copy()
            self.trace.append((self.n_evals + i + 1, self.best_f))

    # ---------------------------------------------------------------- scoring
    def error(self, f):
        """Distance above the known global minimum: f - f*."""
        return np.asarray(f) - self.f_star

    @property
    def best_error(self):
        return self.best_f - self.f_star

    def best_at(self, evals):
        """Best value found within the first ``evals`` evaluations."""
        return best_so_far(self.trace, evals)

    # ----------------------------------------------------------------- domain
    @property
    def span(self):
        return self.upper - self.lower

    def clip(self, X):
        return np.clip(X, self.lower, self.upper)

    def random_points(self, n, rng):
        """n points drawn uniformly at random from the search domain."""
        return self.lower + rng.random((n, self.dim)) * self.span
