import itertools

import numpy as np
import pytest

from evoopt import GAConfig, GeneticAlgorithm, Problem
from evoopt import operators as ops


def test_ga_solves_sphere_in_10d():
    result = GeneticAlgorithm().run(Problem("sphere", 10), seed=0)
    assert result.error < 1e-6


def test_ga_spends_exactly_the_budget():
    problem = Problem("rastrigin", 5, max_evals=3_333)
    result = GeneticAlgorithm().run(problem, seed=0)
    assert result.n_evals == problem.n_evals == 3_333


def test_same_seed_gives_identical_runs_and_different_seeds_do_not():
    a = GeneticAlgorithm().run(Problem("ackley", 5, 5_000), seed=7)
    b = GeneticAlgorithm().run(Problem("ackley", 5, 5_000), seed=7)
    c = GeneticAlgorithm().run(Problem("ackley", 5, 5_000), seed=8)
    np.testing.assert_array_equal(a.best_x, b.best_x)
    assert a.best_f == b.best_f
    assert a.best_f != c.best_f


def test_elitism_never_loses_the_best_individual():
    result = GeneticAlgorithm(elitism=1).run(Problem("rastrigin", 10, 20_000), seed=0)
    pop_best = np.array(result.history["pop_best"])
    assert np.all(np.diff(pop_best) <= 0)
    np.testing.assert_allclose(pop_best[-1], result.best_f)


@pytest.mark.parametrize(
    "selection,crossover,mutation",
    list(itertools.product(ops.SELECTIONS, ops.CROSSOVERS, ops.MUTATIONS)),
)
def test_every_operator_combination_runs_and_improves(selection, crossover, mutation):
    problem = Problem("griewank", 4, max_evals=3_000)
    ga = GeneticAlgorithm(selection=selection, crossover=crossover, mutation=mutation)
    result = ga.run(problem, seed=0)
    assert np.all(result.best_x >= problem.lower) and np.all(result.best_x <= problem.upper)
    assert result.best_f < result.history["pop_mean"][0]  # better than the random start


def test_population_snapshots_are_recorded_on_request():
    result = GeneticAlgorithm(record_population=True, pop_size=30).run(Problem("easom", 2, 900), seed=0)
    assert len(result.snapshots) == result.generations + 1
    assert all(s.shape == (30, 2) for s in result.snapshots)


def test_callback_can_stop_the_run():
    seen = []
    result = GeneticAlgorithm().run(
        Problem("sphere", 2), seed=0, callback=lambda s: seen.append(s["generation"]) or len(seen) == 5
    )
    assert seen == [1, 2, 3, 4, 5]
    assert result.generations == 5


def test_target_error_stops_early():
    result = GeneticAlgorithm(target_error=1e-3).run(Problem("sphere", 2), seed=0)
    assert result.error <= 1e-3
    assert result.n_evals < result.max_evals


def test_defaults_depend_on_dimension():
    assert GAConfig().resolved(2).pop_size == 50
    assert GAConfig().resolved(30).pop_size == 100
    assert GAConfig().resolved(4).mutation_rate == 0.25


@pytest.mark.parametrize(
    "bad",
    [dict(selection="best"), dict(pop_size=1), dict(elitism=10, pop_size=10), dict(crossover_rate=1.5)],
)
def test_invalid_settings_are_rejected(bad):
    with pytest.raises(ValueError):
        GeneticAlgorithm(**bad)
