import itertools

import numpy as np
import pytest

from evoopt import GeneticAlgorithm, MemeticAlgorithm, Problem
from evoopt.local_search import LOCAL_SEARCHES
from evoopt.ma import LEARNING_MODELS


def test_ma_without_learning_is_exactly_the_ga():
    ga = GeneticAlgorithm().run(Problem("griewank", 5, 5_000), seed=3)
    ma = MemeticAlgorithm(ls_best=False, ls_rate=0.0).run(Problem("griewank", 5, 5_000), seed=3)
    np.testing.assert_array_equal(ga.best_x, ma.best_x)
    assert ga.history == ma.history
    assert ma.stats["ls_calls"] == 0


def test_ma_beats_ga_on_rosenbrock():
    ga = [GeneticAlgorithm().run(Problem("rosenbrock", 10), seed=s).error for s in range(3)]
    ma = [MemeticAlgorithm().run(Problem("rosenbrock", 10), seed=s).error for s in range(3)]
    assert max(ma) < min(ga)
    assert np.median(ma) < np.median(ga) / 100


def test_ma_solves_sphere_in_10d():
    assert MemeticAlgorithm().run(Problem("sphere", 10), seed=0).error < 1e-6


def test_ma_spends_exactly_the_budget_including_local_search():
    problem = Problem("rastrigin", 5, max_evals=4_321)
    result = MemeticAlgorithm(ls_rate=0.2).run(problem, seed=0)
    assert result.n_evals == problem.n_evals == 4_321
    assert 0 < result.stats["ls_evals"] < result.n_evals
    assert result.stats["ls_share"] == pytest.approx(result.stats["ls_evals"] / 4_321)


def test_same_seed_gives_identical_runs():
    for local_search in LOCAL_SEARCHES:
        a = MemeticAlgorithm(local_search=local_search).run(Problem("ackley", 5, 5_000), seed=7)
        b = MemeticAlgorithm(local_search=local_search).run(Problem("ackley", 5, 5_000), seed=7)
        np.testing.assert_array_equal(a.best_x, b.best_x)


def test_lamarckian_population_always_matches_its_fitness():
    def check(state):
        pop, fit = state["population"], state["fitness"]
        ok = np.isfinite(fit)
        np.testing.assert_allclose(fit[ok], problem.function(pop[ok]))

    problem = Problem("rosenbrock", 4, 8_000)
    MemeticAlgorithm(ls_rate=0.3).run(problem, seed=0, callback=check)


def learn_once(learning):
    problem = Problem("rastrigin", 3)
    ma = MemeticAlgorithm(learning=learning, ls_rate=1.0, pop_size=10)
    ma.cfg = ma.config.resolved(problem.dim)
    ma.reset_learning()
    rng = np.random.default_rng(0)
    pop = problem.random_points(10, rng)
    fit = problem.evaluate(pop)
    new_pop, new_fit = ma.learn(problem, pop, fit, rng)
    return problem, pop, fit, new_pop, new_fit


def test_lamarckian_learning_writes_the_improved_genes_back():
    problem, pop, fit, new_pop, new_fit = learn_once("lamarckian")
    assert np.all(new_fit <= fit) and np.any(new_fit < fit)
    assert not np.array_equal(new_pop, pop)
    np.testing.assert_allclose(new_fit, problem.function(new_pop))


def test_baldwinian_learning_keeps_the_genes_and_improves_only_fitness():
    problem, pop, fit, new_pop, new_fit = learn_once("baldwinian")
    np.testing.assert_array_equal(new_pop, pop)
    assert np.all(new_fit <= fit) and np.any(new_fit < fit)
    assert np.all(new_fit <= problem.function(new_pop))  # fitness is the learned value
    # the best point reached by learning is still kept by the problem
    assert problem.best_f == pytest.approx(new_fit.min())


def test_search_state_is_kept_for_refined_individuals():
    problem = Problem("sphere", 3)
    ma = MemeticAlgorithm(ls_rate=0.0, pop_size=10)
    ma.cfg = ma.config.resolved(problem.dim)
    ma.reset_learning()
    rng = np.random.default_rng(0)
    pop = problem.random_points(10, rng)
    new_pop, new_fit = ma.learn(problem, pop, problem.evaluate(pop), rng)
    best = new_pop[np.argmin(new_fit)]
    assert best.tobytes() in ma._steps  # its search can resume next generation
    assert set(ma._steps) <= {row.tobytes() for row in new_pop}


@pytest.mark.parametrize("local_search,learning", list(itertools.product(LOCAL_SEARCHES, LEARNING_MODELS)))
def test_every_local_search_and_learning_model_runs(local_search, learning):
    problem = Problem("griewank", 4, max_evals=4_000)
    result = MemeticAlgorithm(local_search=local_search, learning=learning, ls_rate=0.1).run(problem, seed=0)
    assert result.n_evals == 4_000
    assert np.all(result.best_x >= problem.lower) and np.all(result.best_x <= problem.upper)
    assert result.best_f == pytest.approx(problem.function(result.best_x)[0])
    assert result.stats["ls_calls"] > 0


@pytest.mark.parametrize("bad", [dict(local_search="newton"), dict(learning="darwinian"), dict(ls_rate=1.5)])
def test_invalid_settings_are_rejected(bad):
    with pytest.raises(ValueError):
        MemeticAlgorithm(**bad)
