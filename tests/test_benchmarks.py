import numpy as np
import pytest

from evoopt import CATEGORIES, FUNCTIONS, Problem, get_function

SCALABLE_TEST_DIMS = (2, 5, 10, 30)


CASES = [
    pytest.param(fn, d, id=f"{key}-{d}d")
    for key, fn in FUNCTIONS.items()
    for d in fn.dims or SCALABLE_TEST_DIMS
]


@pytest.mark.parametrize("fn,d", CASES)
def test_known_minimiser_gives_known_minimum(fn, d):
    x_star = fn.x_star(d)
    if x_star is None:
        pytest.skip("minimiser not published for this dimension")
    np.testing.assert_allclose(fn(x_star), fn.f_star(d), atol=1e-8)


@pytest.mark.parametrize("fn,d", CASES)
def test_minimiser_lies_inside_domain(fn, d):
    x_star = fn.x_star(d)
    if x_star is None:
        pytest.skip("minimiser not published for this dimension")
    lower, upper = fn.bounds(d)
    assert np.all(x_star >= lower) and np.all(x_star <= upper)


@pytest.mark.parametrize("fn,d", CASES)
def test_no_random_point_beats_the_minimum(fn, d):
    rng = np.random.default_rng(0)
    lower, upper = fn.bounds(d)
    X = lower + rng.random((20_000, d)) * (upper - lower)
    assert fn(X).min() >= fn.f_star(d) - 1e-9


@pytest.mark.parametrize("fn,d", CASES)
def test_minimiser_is_a_local_minimum(fn, d):
    x_star = fn.x_star(d)
    if x_star is None:
        pytest.skip("minimiser not published for this dimension")
    rng = np.random.default_rng(1)
    lower, upper = fn.bounds(d)
    for x in x_star:
        X = np.clip(x + rng.normal(scale=1e-4 * (upper - lower), size=(500, d)), lower, upper)
        assert fn(X).min() >= fn.f_star(d) - 1e-9


@pytest.mark.parametrize("fn,d", CASES)
def test_vectorised_call_matches_row_by_row(fn, d):
    rng = np.random.default_rng(2)
    lower, upper = fn.bounds(d)
    X = lower + rng.random((6, d)) * (upper - lower)
    values = fn(X)
    assert values.shape == (6,)
    np.testing.assert_allclose(values, [fn(row)[0] for row in X])


def test_all_six_sfu_categories_are_covered():
    assert {fn.category for fn in FUNCTIONS.values()} == set(CATEGORIES)


def test_fixed_dimension_functions_reject_other_dimensions():
    with pytest.raises(ValueError):
        get_function("easom").bounds(3)
    with pytest.raises(ValueError):
        Problem("michalewicz", 7)


def test_unknown_key_is_rejected():
    with pytest.raises(KeyError):
        get_function("not-a-function")
