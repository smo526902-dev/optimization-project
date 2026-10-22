import numpy as np
import pytest

from evoopt import Problem
from evoopt.local_search import LOCAL_SEARCHES, MIN_STEP, hooke_jeeves


def start(problem, seed=0):
    rng = np.random.default_rng(seed)
    x = problem.random_points(1, rng)[0]
    return x, problem.evaluate_one(x), rng


@pytest.mark.parametrize("name", LOCAL_SEARCHES)
def test_local_search_solves_sphere(name):
    p = Problem("sphere", 5)
    x, fx, rng = start(p)
    _, f_best, _ = LOCAL_SEARCHES[name](p, x, fx, 0.1 * p.span, 5_000, rng)
    assert f_best < 1e-8


def test_hooke_jeeves_follows_the_rosenbrock_valley():
    p = Problem("rosenbrock", 2)
    x = np.array([-1.2, 1.0])  # the classic starting point
    _, f_best, _ = hooke_jeeves(p, x, p.evaluate_one(x), 0.1 * p.span, 5_000)
    assert f_best < 1e-8


@pytest.mark.parametrize("name", LOCAL_SEARCHES)
@pytest.mark.parametrize("key,d", [("rastrigin", 4), ("schwefel", 3), ("eggholder", 2)])
def test_result_is_consistent_in_bounds_and_never_worse(name, key, d):
    p = Problem(key, d)
    x, fx, rng = start(p, seed=3)
    x_best, f_best, _ = LOCAL_SEARCHES[name](p, x, fx, 0.1 * p.span, 400, rng)
    assert f_best <= fx
    assert f_best == pytest.approx(p.function(x_best)[0])
    assert np.all(x_best >= p.lower) and np.all(x_best <= p.upper)


@pytest.mark.parametrize("name", LOCAL_SEARCHES)
def test_per_call_budget_is_respected(name):
    p = Problem("ackley", 6)
    x, fx, rng = start(p)
    used_before = p.n_evals
    LOCAL_SEARCHES[name](p, x, fx, 0.1 * p.span, 37, rng)
    assert p.n_evals - used_before <= 37


@pytest.mark.parametrize("name", LOCAL_SEARCHES)
def test_global_budget_is_respected(name):
    p = Problem("ackley", 6, max_evals=50)
    x, fx, rng = start(p)
    LOCAL_SEARCHES[name](p, x, fx, 0.1 * p.span, 1_000, rng)
    assert p.n_evals == 50


@pytest.mark.parametrize("name", LOCAL_SEARCHES)
def test_converged_search_costs_nothing(name):
    p = Problem("sphere", 3)
    x, fx, rng = start(p)
    used_before = p.n_evals
    LOCAL_SEARCHES[name](p, x, fx, 0.1 * MIN_STEP * p.span, 100, rng)
    assert p.n_evals == used_before


@pytest.mark.parametrize("name", LOCAL_SEARCHES)
def test_step_shrinks_near_a_minimum(name):
    p = Problem("sphere", 3)
    rng = np.random.default_rng(0)
    x = np.full(3, 1e-3)
    _, _, step = LOCAL_SEARCHES[name](p, x, p.evaluate_one(x), 0.1 * p.span, 300, rng)
    assert np.all(step < 0.1 * p.span)
