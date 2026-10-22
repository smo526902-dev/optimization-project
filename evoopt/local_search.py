"""Local searches (the "memes") used by the Memetic Algorithm.

Each method refines a single point and stops when it has used ``max_evals``
evaluations, when the global budget runs out, or when its step size has become
negligible. Both are derivative-free: they only compare function values.

They take the starting step size (one per variable) and return the final one,
so the Memetic Algorithm can resume a search later where it stopped instead of
starting over with a large step (the "local-search chain" idea of
Molina et al., 2010).

Every evaluation goes through ``Problem.evaluate``, so local search is charged
to exactly the same budget as the GA's own evaluations.
"""
from __future__ import annotations

import numpy as np

# Below this step size (relative to the domain width) a search has converged.
MIN_STEP = 1e-10


def converged(step, problem):
    return bool(np.all(step < MIN_STEP * problem.span))


def hooke_jeeves(problem, x, fx, step, max_evals, rng=None, shrink=0.5):
    """Hooke-Jeeves pattern search (Hooke & Jeeves, 1961).

    1. Exploratory move: for each variable in turn, try x_i + h_i and then
       x_i - h_i, keeping a change as soon as it lowers f.
    2. Pattern move: if exploring improved on the base point, jump again in
       the direction that worked, to x_new + (x_new - x_base), and explore
       around there. Repeated pattern moves accelerate along valleys.
    3. If exploring found nothing better, halve every step size h_i.

    Deterministic; ``rng`` is accepted only for a uniform signature.
    """
    stop_at = min(problem.n_evals + max_evals, problem.max_evals)
    step = np.array(step, dtype=float)
    base, f_base = np.array(x, dtype=float), float(fx)
    while problem.n_evals < stop_at and not converged(step, problem):
        new, f_new = _explore(problem, base, f_base, step, stop_at)
        if f_new < f_base:
            while True:  # keep making pattern moves while they pay off
                pattern = problem.clip(2 * new - base)
                base, f_base = new, f_new
                if problem.n_evals >= stop_at:
                    break
                f_pattern = problem.evaluate_one(pattern)
                new, f_new = _explore(problem, pattern, f_pattern, step, stop_at)
                if f_new >= f_base:
                    break
        else:
            step = step * shrink
    return base, f_base, step


def _explore(problem, x, fx, step, stop_at):
    """The exploratory move of Hooke-Jeeves: improve x one variable at a time."""
    x = x.copy()
    for i in range(len(x)):
        for delta in (step[i], -step[i]):
            if problem.n_evals >= stop_at:
                return x, fx
            trial = x.copy()
            trial[i] = min(max(x[i] + delta, problem.lower[i]), problem.upper[i])
            if trial[i] == x[i]:  # already against the bound in this direction
                continue
            f_trial = problem.evaluate_one(trial)
            if f_trial < fx:
                x, fx = trial, f_trial
                break
    return x, fx


def hill_climbing(problem, x, fx, step, max_evals, rng, grow=1.5):
    """Stochastic hill climbing with an adaptive step size: a (1+1) evolution
    strategy using Rechenberg's 1/5 success rule.

    Each iteration adds Gaussian noise N(0, h_i^2) to every variable and keeps
    the move only if f improves. A success multiplies the step by ``grow``, a
    failure by grow^(-1/4), so the step settles where about one move in five
    succeeds: it grows on open slopes and shrinks close to a minimum.
    """
    stop_at = min(problem.n_evals + max_evals, problem.max_evals)
    step = np.array(step, dtype=float)
    x, fx = np.array(x, dtype=float), float(fx)
    shrink = grow**-0.25
    while problem.n_evals < stop_at and not converged(step, problem):
        trial = problem.clip(x + rng.normal(size=len(x)) * step)
        f_trial = problem.evaluate_one(trial)
        if f_trial < fx:
            x, fx = trial, f_trial
            step = np.minimum(step * grow, problem.span)
        else:
            step = step * shrink
    return x, fx, step


LOCAL_SEARCHES = {
    "hooke_jeeves": hooke_jeeves,
    "hill_climbing": hill_climbing,
}
