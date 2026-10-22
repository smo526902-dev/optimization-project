import numpy as np

from experiments.analyze import apply_error_floor, compare, holm
from experiments.config import ERROR_FLOOR


def test_errors_below_the_floor_become_zero():
    errors = np.array([0.0, 4e-16, 9.9e-9, ERROR_FLOOR, 1e-3, np.inf])
    np.testing.assert_array_equal(apply_error_floor(errors), [0, 0, 0, ERROR_FLOOR, 1e-3, np.inf])


def test_rounding_noise_no_longer_counts_as_a_loss():
    # The Easom case: DE hits exactly 0 in 22 runs and fails (error 1) in 8;
    # the MA reaches 4e-16 in all 30 runs.
    de = np.array([0.0] * 22 + [1.0] * 8)
    ma = np.full(30, 4e-16)
    assert compare(ma, de)[1] == "-"  # raw errors: rounding noise ranks the MA lower
    # with the floor both reach 0 in 22+ runs; 8 failures out of 30 are not significant
    assert compare(apply_error_floor(ma), apply_error_floor(de))[1] == "="


def test_two_solved_samples_tie():
    a, b = apply_error_floor(np.full(30, 1e-19)), apply_error_floor(np.full(30, 3e-12))
    assert compare(a, b) == (1.0, "=")


def test_holm_adjusts_p_values_step_down():
    np.testing.assert_allclose(holm([0.01, 0.04, 0.03]), [0.03, 0.06, 0.06])
