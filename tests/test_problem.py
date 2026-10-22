import numpy as np

from evoopt import EVALS_PER_DIM, Problem


def test_default_budget_is_10000_per_dimension():
    assert Problem("rastrigin", 10).max_evals == 10 * EVALS_PER_DIM


def test_every_evaluation_is_counted():
    p = Problem("sphere", 3, max_evals=100)
    p.evaluate(np.zeros((5, 3)))
    p.evaluate_one(np.ones(3))
    assert p.n_evals == 6
    assert p.remaining == 94


def test_budget_is_a_hard_limit():
    p = Problem("sphere", 2, max_evals=10)
    f = p.evaluate(np.ones((15, 2)))
    assert np.all(np.isfinite(f[:10])) and np.all(np.isinf(f[10:]))
    assert p.n_evals == 10 and p.exhausted
    assert np.all(np.isinf(p.evaluate(np.zeros((3, 2)))))
    assert p.n_evals == 10
    assert p.best_f == 2.0  # the free point at the origin was never evaluated


def test_best_solution_and_trace_are_recorded():
    p = Problem("sphere", 2, max_evals=100)
    p.evaluate([[2, 0], [1, 0], [3, 0]])  # f = 4, 1, 9
    p.evaluate([[5, 0]])  # f = 25, no improvement
    p.evaluate([[0.5, 0]])  # f = 0.25
    assert p.best_f == 0.25
    np.testing.assert_array_equal(p.best_x, [0.5, 0])
    assert p.trace == [(2, 1.0), (5, 0.25)]
    np.testing.assert_array_equal(p.best_at([0, 1, 2, 4, 5, 99]), [np.inf, np.inf, 1, 1, 0.25, 0.25])


def test_error_is_measured_from_the_known_minimum():
    p = Problem("easom", 2)
    p.evaluate([[np.pi, np.pi]])
    assert p.f_star == -1.0
    assert abs(p.best_error) < 1e-12


def test_random_points_stay_inside_the_domain():
    p = Problem("six_hump_camel", 2)
    X = p.random_points(1000, np.random.default_rng(0))
    assert X.shape == (1000, 2)
    assert np.all(X >= p.lower) and np.all(X <= p.upper)
    assert p.n_evals == 0  # sampling is free; only evaluate() costs budget
