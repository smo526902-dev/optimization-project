import numpy as np

from evoopt import Problem, RandomSearch, ScipyDE
from experiments.config import ABLATIONS, MAIN_ALGORITHMS, MODES, main_problems
from experiments.run import build_jobs, run_key


def test_random_search_spends_exactly_the_budget_and_is_reproducible():
    a = RandomSearch().run(Problem("rastrigin", 5, max_evals=1_234), seed=0)
    b = RandomSearch().run(Problem("rastrigin", 5, max_evals=1_234), seed=0)
    assert a.n_evals == 1_234
    np.testing.assert_array_equal(a.best_x, b.best_x)


def test_scipy_de_stays_within_the_budget_and_solves_sphere():
    problem = Problem("sphere", 5)
    result = ScipyDE().run(problem, seed=0)
    assert result.n_evals <= problem.max_evals
    assert result.error < 1e-8


def test_scipy_de_stops_exactly_when_the_budget_runs_out():
    problem = Problem("rastrigin", 4, max_evals=3_000)
    result = ScipyDE().run(problem, seed=0)
    assert result.n_evals == 3_000
    assert np.all(result.best_x >= problem.lower) and np.all(result.best_x <= problem.upper)


def test_main_suite_covers_every_problem_and_algorithm():
    jobs = build_jobs("main", "full")
    n_problems = len(list(main_problems()))
    assert n_problems == 30
    assert len(jobs) == n_problems * len(MAIN_ALGORITHMS) * len(MODES["full"]["seeds"])
    assert {j["max_evals"] for j in jobs if j["dim"] == 10} == {100_000}


def test_equivalent_settings_are_run_only_once():
    jobs = [j for j in build_jobs("ablations", "quick") if j["function"] == "rastrigin" and j["seed"] == 0]
    keys = {(j["experiment"], j["config"]): run_key(j) for j in jobs}
    default_ga = keys[("selection", "tournament")]
    assert keys[("crossover", "sbx")] == default_ga
    assert keys[("pop_size", "100")] == default_ga
    assert keys[("mutation_rate", "1/d")] == default_ga
    assert keys[("local_search", "Hooke-Jeeves")] == keys[("mutation", "MA polynomial")]
    assert keys[("selection", "roulette")] != default_ga
    assert len(set(keys.values())) < len(keys) == sum(len(c) for c in ABLATIONS.values())
