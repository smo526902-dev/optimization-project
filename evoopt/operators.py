"""Genetic operators for a real-coded Genetic Algorithm.

Conventions used throughout:

* A population is an array of shape (n, d): one row per individual (chromosome),
  one column per variable (gene). Genes are real numbers, not bit strings.
* Fitness is the objective value f(x), and LOWER IS BETTER (we minimise).
* ``lower`` and ``upper`` are arrays of length d giving the search domain.
* The random generator ``rng`` is always passed in explicitly, so a whole run is
  reproducible from a single seed.
"""
from __future__ import annotations

import numpy as np

# --------------------------------------------------------------------------- #
# Selection: return the indices of n parents, favouring low f(x)
# --------------------------------------------------------------------------- #


def _finite(f):
    """Replace +inf (points past the evaluation budget) by the worst finite value."""
    f = np.asarray(f, dtype=float)
    finite = np.isfinite(f)
    if finite.all():
        return f
    worst = f[finite].max() if finite.any() else 0.0
    return np.where(finite, f, worst)


def tournament_selection(f, n, rng, k=3):
    """Draw k individuals at random and keep the one with the lowest f; repeat
    n times. A larger tournament size k means stronger selection pressure."""
    contenders = rng.integers(0, len(f), size=(n, k))
    winners = np.argmin(np.asarray(f)[contenders], axis=1)
    return contenders[np.arange(n), winners]


def roulette_selection(f, n, rng):
    """Fitness-proportionate (roulette-wheel) selection.

    Roulette needs "bigger is better" weights, so each individual's slice of the
    wheel is how far it sits below the worst individual: w_i = f_max - f_i
    (Goldberg's "windowing"). The worst individual gets a zero-width slice.
    """
    f = _finite(f)
    weights = f.max() - f
    total = weights.sum()
    if total <= 0:  # every individual is equally fit
        return rng.integers(0, len(f), size=n)
    return rng.choice(len(f), size=n, p=weights / total)


def rank_selection(f, n, rng, pressure=1.5):
    """Linear ranking selection (Baker, 1985).

    Probabilities depend only on the order of f, not on its scale, so a single
    outstanding individual cannot take over the population. ``pressure`` (in
    [1, 2]) is the expected number of offspring of the best individual:
        p(rank r) = (2 - s)/N + 2 r (s - 1) / (N (N - 1)),  r = 0 (worst) .. N-1 (best)
    """
    N = len(f)
    order = np.argsort(_finite(f), kind="stable")  # best first
    rank = np.empty(N)
    rank[order] = np.arange(N)[::-1]  # best gets rank N-1
    p = (2 - pressure) / N + 2 * rank * (pressure - 1) / (N * (N - 1))
    return rng.choice(N, size=n, p=p)


# --------------------------------------------------------------------------- #
# Crossover: two parent arrays (m, d) -> two child arrays (m, d)
# --------------------------------------------------------------------------- #


def sbx_crossover(P1, P2, rng, lower, upper, eta=15.0):
    """Simulated Binary Crossover, SBX (Deb & Agrawal, 1995).

    Mimics single-point crossover on binary strings for real numbers: each pair
    of children is spread symmetrically around the parents (c1 + c2 = p1 + p2),
    with spread factor beta drawn so that children close to the parents are
    more likely. A larger distribution index eta keeps children closer.
    Each gene is crossed with probability 0.5; the others are copied.
    """
    u = rng.random(P1.shape)
    beta = np.where(
        u <= 0.5,
        (2 * u) ** (1 / (eta + 1)),
        (1 / (2 * (1 - u))) ** (1 / (eta + 1)),
    )
    crossed = rng.random(P1.shape) < 0.5
    beta = np.where(crossed, beta, 1.0)  # beta = 1 copies the parent genes
    C1 = 0.5 * ((1 + beta) * P1 + (1 - beta) * P2)
    C2 = 0.5 * ((1 - beta) * P1 + (1 + beta) * P2)
    return np.clip(C1, lower, upper), np.clip(C2, lower, upper)


def blx_alpha_crossover(P1, P2, rng, lower, upper, alpha=0.5):
    """Blend crossover, BLX-alpha (Eshelman & Schaffer, 1993).

    Each child gene is drawn uniformly from the interval spanned by the two
    parent genes, widened by alpha times its length on both sides, so children
    can explore slightly beyond their parents.
    """
    lo, hi = np.minimum(P1, P2), np.maximum(P1, P2)
    reach = alpha * (hi - lo)
    lo, hi = lo - reach, hi + reach
    C1 = lo + rng.random(P1.shape) * (hi - lo)
    C2 = lo + rng.random(P1.shape) * (hi - lo)
    return np.clip(C1, lower, upper), np.clip(C2, lower, upper)


def arithmetic_crossover(P1, P2, rng, lower, upper):
    """Whole arithmetic crossover: children are weighted averages of the
    parents, c1 = l*p1 + (1-l)*p2 and c2 = (1-l)*p1 + l*p2, with l ~ U(0, 1).
    Children always lie on the segment between the parents (never outside)."""
    lam = rng.random((len(P1), 1))
    return lam * P1 + (1 - lam) * P2, (1 - lam) * P1 + lam * P2


# --------------------------------------------------------------------------- #
# Mutation: each gene of X (n, d) is perturbed with probability `rate`
# --------------------------------------------------------------------------- #


def polynomial_mutation(X, rng, lower, upper, rate, eta=20.0):
    """Polynomial mutation (Deb & Goyal, 1996), in the bounded form used by NSGA-II.

    Small changes are much more likely than large ones; the distribution index
    eta controls how concentrated they are. The perturbation is scaled by the
    distance to the nearest bound, so mutated genes stay inside the domain.
    """
    span = upper - lower
    d1 = (X - lower) / span  # relative distance to the lower bound
    d2 = (upper - X) / span  # relative distance to the upper bound
    u = rng.random(X.shape)
    p = 1 / (eta + 1)
    delta = np.where(
        u < 0.5,
        (2 * u + (1 - 2 * u) * (1 - d1) ** (eta + 1)) ** p - 1,
        1 - (2 * (1 - u) + 2 * (u - 0.5) * (1 - d2) ** (eta + 1)) ** p,
    )
    mutate = rng.random(X.shape) < rate
    return np.clip(np.where(mutate, X + delta * span, X), lower, upper)


def gaussian_mutation(X, rng, lower, upper, rate, sigma=0.1):
    """Add normal noise N(0, (sigma * range)^2) to the selected genes."""
    noise = rng.normal(0.0, sigma, X.shape) * (upper - lower)
    mutate = rng.random(X.shape) < rate
    return np.clip(np.where(mutate, X + noise, X), lower, upper)


def uniform_mutation(X, rng, lower, upper, rate):
    """Random resetting: a selected gene is replaced by a fresh uniform value."""
    fresh = lower + rng.random(X.shape) * (upper - lower)
    mutate = rng.random(X.shape) < rate
    return np.where(mutate, fresh, X)


SELECTIONS = ("tournament", "roulette", "rank")
CROSSOVERS = ("sbx", "blx", "arithmetic")
MUTATIONS = ("polynomial", "gaussian", "uniform")
