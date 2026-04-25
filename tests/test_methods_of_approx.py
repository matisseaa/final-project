import pytest
from numerical_workbench.methods_of_approx import (
    central_difference,
    trapezoidal_rule,
    simpson_rule
)
from numerical_workbench.functions import Polynomial
from numerical_workbench.models import Interval
from numerical_workbench.exceptions import ValidationError

# central_difference tests

def test_central_difference_basic():
    p = Polynomial([0, 0, 1])  # x^2 derivative = 2x
    result = central_difference(p, 2)

    assert result == pytest.approx(4, rel = 1e-3)


def test_central_difference_zero_h():
    p = Polynomial([1, 2])

    with pytest.raises(ZeroDivisionError):
        central_difference(p, 1, h = 0.0)


def test_central_difference_negative_h():
    p = Polynomial([1, 2])

    with pytest.raises(ValidationError):
        central_difference(p, 1, h = -0.1)

# trapezoidal_rule tests

def test_trapezoidal_rule_basic():
    p = Polynomial([0, 1])  # f(x) = x
    interval = Interval(0, 1)

    result = trapezoidal_rule(p, interval, n_steps = 100)

    # ∫x dx from 0 to 1 = 0.5
    assert result == pytest.approx(0.5, rel = 1e-2)


def test_trapezoidal_rule_constant_function():
    p = Polynomial([5])  # f(x) = 5
    interval = Interval(0, 2)

    result = trapezoidal_rule(p, interval, n_steps = 50)

    # integral = 5 * width = 10
    assert result == pytest.approx(10, rel = 1e-2)


def test_trapezoidal_rule_invalid_steps():
    p = Polynomial([1])
    interval = Interval(0, 1)

    with pytest.raises(ValidationError):
        trapezoidal_rule(p, interval, n_steps = 0)

# simpson_rule tests

def test_simpson_rule_basic():
    p = Polynomial([0, 0, 1])  # x^2
    interval = Interval(0, 1)

    result = simpson_rule(p, interval, n_steps = 100)

    # ∫x^2 dx from 0 to 1 = 1/3
    assert result == pytest.approx(1/3, rel = 1e-3)


def test_simpson_rule_constant_function():
    p = Polynomial([3])  # f(x) = 3
    interval = Interval(0, 2)

    result = simpson_rule(p, interval, n_steps = 50)

    # integral = 3 * 2 = 6
    assert result == pytest.approx(6, rel = 1e-2)


def test_simpson_rule_invalid_steps_too_small():
    p = Polynomial([1])
    interval = Interval(0, 1)

    with pytest.raises(ValidationError):
        simpson_rule(p, interval, n_steps = 1)


def test_simpson_rule_invalid_steps_odd():
    p = Polynomial([1])
    interval = Interval(0, 1)

    with pytest.raises(ValidationError):
        simpson_rule(p, interval, n_steps = 3)

# extra edge cases

def test_trapezoidal_rule_negative_interval():
    p = Polynomial([0, 1])  # x
    interval = Interval(-1, 1)

    result = trapezoidal_rule(p, interval, n_steps = 100)

    # integral of x from -1 to 1 = 0
    assert result == pytest.approx(0, abs = 1e-2)


def test_simpson_rule_negative_interval():
    p = Polynomial([0, 1])  # x
    interval = Interval(-1, 1)

    result = simpson_rule(p, interval, n_steps = 100)

    assert result == pytest.approx(0, abs = 1e-3)