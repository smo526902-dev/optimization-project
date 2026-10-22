import numpy as np
import pytest

from evoopt import operators as ops

LOWER = np.array([-5.0, -1.0, 0.0])
UPPER = np.array([5.0, 3.0, 10.0])


def population(n, rng):
    return LOWER + rng.random((n, 3)) * (UPPER - LOWER)


# ------------------------------------------------------------------ selection
@pytest.mark.parametrize(
    "select",
    [ops.tournament_selection, ops.roulette_selection, ops.rank_selection],
    ids=["tournament", "roulette", "rank"],
)
def test_selection_favours_low_objective_values(select):
    f = np.arange(20, dtype=float)  # individual 0 is the best, 19 the worst
    picks = select(f, 20_000, np.random.default_rng(0))
    assert picks.min() >= 0 and picks.max() < 20
    counts = np.bincount(picks, minlength=20)
    assert counts[0] > counts[10] > counts[19]


def test_tournament_of_whole_population_size_mostly_picks_the_best():
    f = np.array([5.0, 1.0, 3.0, 4.0])
    picks = ops.tournament_selection(f, 1000, np.random.default_rng(0), k=20)
    assert np.mean(picks == 1) > 0.99


def test_roulette_never_picks_the_worst_and_handles_equal_fitness():
    rng = np.random.default_rng(0)
    assert 3 not in ops.roulette_selection(np.array([1.0, 2.0, 3.0, 9.0]), 5000, rng)
    picks = ops.roulette_selection(np.ones(5), 5000, rng)
    assert set(picks) == set(range(5))


def test_selection_ignores_unevaluated_points():
    f = np.array([1.0, 2.0, np.inf, np.inf])
    for select in (ops.roulette_selection, ops.rank_selection):
        picks = select(f, 1000, np.random.default_rng(0))
        assert picks.max() < 4


def test_rank_probabilities_follow_the_selection_pressure():
    f = np.array([3.0, 1.0, 2.0])  # ranks: idx1 best, idx2 middle, idx0 worst
    picks = ops.rank_selection(f, 60_000, np.random.default_rng(0), pressure=2.0)
    freq = np.bincount(picks, minlength=3) / len(picks)
    # with s = 2 and N = 3: p = 0, 1/3, 2/3 for worst, middle, best
    np.testing.assert_allclose(freq, [0, 2 / 3, 1 / 3], atol=0.01)


# ------------------------------------------------------------------ crossover
CROSSOVERS = {
    "sbx": ops.sbx_crossover,
    "blx": ops.blx_alpha_crossover,
    "arithmetic": ops.arithmetic_crossover,
}


@pytest.mark.parametrize("name", CROSSOVERS)
def test_crossover_children_have_the_right_shape_and_stay_in_bounds(name):
    rng = np.random.default_rng(0)
    P1, P2 = population(200, rng), population(200, rng)
    C1, C2 = CROSSOVERS[name](P1, P2, rng, LOWER, UPPER)
    for C in (C1, C2):
        assert C.shape == P1.shape
        assert np.all(C >= LOWER) and np.all(C <= UPPER)


@pytest.mark.parametrize("name", CROSSOVERS)
def test_crossing_identical_parents_gives_the_same_parents_back(name):
    rng = np.random.default_rng(0)
    P = population(50, rng)
    C1, C2 = CROSSOVERS[name](P, P.copy(), rng, LOWER, UPPER)
    np.testing.assert_allclose(C1, P)
    np.testing.assert_allclose(C2, P)


def test_sbx_children_are_symmetric_around_the_parents():
    rng = np.random.default_rng(0)
    wide = np.full(3, 1e9)  # no clipping, so the identity holds exactly
    P1, P2 = population(100, rng), population(100, rng)
    C1, C2 = ops.sbx_crossover(P1, P2, rng, -wide, wide)
    np.testing.assert_allclose(C1 + C2, P1 + P2)


def test_arithmetic_children_lie_between_their_parents():
    rng = np.random.default_rng(0)
    P1, P2 = population(100, rng), population(100, rng)
    C1, _ = ops.arithmetic_crossover(P1, P2, rng, LOWER, UPPER)
    lo, hi = np.minimum(P1, P2), np.maximum(P1, P2)
    assert np.all(C1 >= lo - 1e-12) and np.all(C1 <= hi + 1e-12)


# ------------------------------------------------------------------- mutation
MUTATIONS = {
    "polynomial": ops.polynomial_mutation,
    "gaussian": ops.gaussian_mutation,
    "uniform": ops.uniform_mutation,
}


@pytest.mark.parametrize("name", MUTATIONS)
def test_mutation_keeps_genes_in_bounds(name):
    rng = np.random.default_rng(0)
    X = population(500, rng)
    Y = MUTATIONS[name](X, rng, LOWER, UPPER, rate=1.0)
    assert Y.shape == X.shape
    assert np.all(Y >= LOWER) and np.all(Y <= UPPER)


@pytest.mark.parametrize("name", MUTATIONS)
def test_mutation_rate_controls_how_many_genes_change(name):
    rng = np.random.default_rng(0)
    X = population(2000, rng)
    np.testing.assert_array_equal(MUTATIONS[name](X, rng, LOWER, UPPER, rate=0.0), X)
    changed = np.mean(MUTATIONS[name](X, rng, LOWER, UPPER, rate=0.25) != X)
    assert 0.2 < changed < 0.3


def test_polynomial_mutation_mostly_makes_small_steps():
    rng = np.random.default_rng(0)
    X = np.tile((LOWER + UPPER) / 2, (5000, 1))
    step = np.abs(ops.polynomial_mutation(X, rng, LOWER, UPPER, rate=1.0, eta=20) - X) / (UPPER - LOWER)
    assert np.median(step) < 0.05
